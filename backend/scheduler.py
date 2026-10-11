"""
MacroAR - Scheduler (APScheduler)
===================================
Ejecuta el scraping automáticamente (por defecto todos los días a las 18:00 ART).
Usa APScheduler con BackgroundScheduler para no bloquear el event loop.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import pytz
import threading
from typing import Optional

from config import settings
from database import SessionLocal
from models import IndicatorSnapshot, PublicationFeed
from scrapers import scrape_indec, scrape_cif, scrape_ipc_caba, scrape_real_m2

import asyncio

# Evita que el job programado y el trigger manual corran a la vez
_job_lock = threading.Lock()

# Keys que existieron en versiones anteriores y ya no se generan.
# Se eliminan de la DB para que no queden como snapshots huérfanos.
RETIRED_INDICATOR_KEYS = [
    "emae", "ipi_manufacturero", "ipi_minero", "isac",   # renombrados a *_mom_sa
    "icc",                                                # chocaba entre INDEC y CIF
    "personal_apn", "personal_apn_variacion",             # reemplazados por personal_apn_yoy
    "balanza_saldo_yoy",                                  # el INDEC no publica este dato
]


def run_scraping_job() -> bool:
    """
    Job principal de scraping.
    Ejecuta todos los scrapers y actualiza la base de datos (upsert).
    Retorna False si ya había un scraping en curso.
    """
    if not _job_lock.acquire(blocking=False):
        print("⏭️ Scraping ya en curso, se omite esta ejecución")
        return False
    try:
        _run_scraping_job()
    finally:
        _job_lock.release()
    return True


def _run_scraping_job():
    print(f"\n{'='*60}")
    print(f"🔄 Iniciando scraping - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    
    # Crear event loop para las funciones async
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Ejecutar todos los scrapers
        all_indicators = []
        all_publications = []
        
        # INDEC
        try:
            indec_result = loop.run_until_complete(scrape_indec())
            all_indicators.extend(indec_result.get("indicators", []))
            all_publications.extend(indec_result.get("publications", []))
        except Exception as e:
            print(f"❌ Error scraper INDEC: {e}")
        
        # CIF-UTDT
        try:
            cif_result = loop.run_until_complete(scrape_cif())
            all_indicators.extend(cif_result.get("indicators", []))
            all_publications.extend(cif_result.get("publications", []))
        except Exception as e:
            print(f"❌ Error scraper CIF: {e}")
        
        # IPC CABA
        try:
            caba_result = loop.run_until_complete(scrape_ipc_caba())
            all_indicators.extend(caba_result.get("indicators", []))
            all_publications.extend(caba_result.get("publications", []))
        except Exception as e:
            print(f"❌ Error scraper IPC CABA: {e}")
        
        # Real M2 (UCEMA)
        try:
            m2_result = loop.run_until_complete(scrape_real_m2())
            all_indicators.extend(m2_result.get("indicators", []))
            all_publications.extend(m2_result.get("publications", []))
        except Exception as e:
            print(f"❌ Error scraper Real M2: {e}")
        
        # Actualizar base de datos
        now = datetime.now(pytz.utc)
        db = SessionLocal()
        try:
            # Upsert indicadores (sobrescribir snapshot)
            for indicator_data in all_indicators:
                existing = db.query(IndicatorSnapshot).filter(
                    IndicatorSnapshot.indicator_key == indicator_data["indicator_key"]
                ).first()
                
                if existing:
                    # Actualizar valores existentes
                    existing.name = indicator_data.get("name", existing.name)
                    existing.value = indicator_data.get("value")
                    existing.value_raw = indicator_data.get("value_raw")
                    existing.unit = indicator_data.get("unit", existing.unit)
                    existing.period = indicator_data.get("period", existing.period)
                    existing.source = indicator_data.get("source", existing.source)
                    existing.source_url = indicator_data.get("source_url", existing.source_url)
                    existing.category = indicator_data.get("category", existing.category)
                    existing.updated_at = now
                else:
                    # Insertar nuevo indicador
                    new_indicator = IndicatorSnapshot(
                        indicator_key=indicator_data["indicator_key"],
                        name=indicator_data.get("name", ""),
                        value=indicator_data.get("value"),
                        value_raw=indicator_data.get("value_raw"),
                        unit=indicator_data.get("unit"),
                        period=indicator_data.get("period"),
                        source=indicator_data.get("source", ""),
                        source_url=indicator_data.get("source_url"),
                        category=indicator_data.get("category"),
                        updated_at=now,
                    )
                    db.add(new_indicator)
            
            # Upsert publicaciones (por URL)
            for pub_data in all_publications:
                existing_pub = db.query(PublicationFeed).filter(
                    PublicationFeed.url == pub_data["url"]
                ).first()
                
                if existing_pub:
                    # Actualizar si hay cambios
                    existing_pub.title = pub_data.get("title", existing_pub.title)
                    existing_pub.description = pub_data.get("description", existing_pub.description)
                    if pub_data.get("date"):
                        existing_pub.date = pub_data["date"]
                    existing_pub.updated_at = now
                else:
                    # Insertar nueva publicación. Si la fuente no informa fecha,
                    # se usa la fecha en que se detectó por primera vez.
                    new_pub = PublicationFeed(
                        title=pub_data.get("title", ""),
                        date=pub_data.get("date") or datetime.now(pytz.timezone(settings.SCRAPE_TIMEZONE)).replace(tzinfo=None),
                        source=pub_data.get("source", ""),
                        url=pub_data.get("url", ""),
                        type=pub_data.get("type"),
                        description=pub_data.get("description"),
                    )
                    db.add(new_pub)

            # Eliminar snapshots de keys retiradas
            db.query(IndicatorSnapshot).filter(
                IndicatorSnapshot.indicator_key.in_(RETIRED_INDICATOR_KEYS)
            ).delete(synchronize_session=False)

            db.commit()
            print(f"\n✅ DB actualizada: {len(all_indicators)} indicadores, {len(all_publications)} publicaciones")
            
        except Exception as e:
            db.rollback()
            print(f"❌ Error actualizando DB: {e}")
        finally:
            db.close()
    
    except Exception as e:
        print(f"❌ Error general en scraping job: {e}")
    finally:
        loop.close()
    
    print(f"{'='*60}")
    print(f"✅ Scraping completado - {datetime.now().isoformat()}")
    print(f"{'='*60}\n")


def get_last_scrape() -> Optional[datetime]:
    """Fecha del último scraping (máximo updated_at de los indicadores), en UTC."""
    from sqlalchemy import func
    db = SessionLocal()
    try:
        last = db.query(func.max(IndicatorSnapshot.updated_at)).scalar()
    finally:
        db.close()
    if last is not None and last.tzinfo is None:
        last = pytz.utc.localize(last)  # SQLite no guarda zona horaria
    return last


def run_if_stale():
    """
    Ejecuta un scraping en background si el último tiene más de SCRAPE_STALE_HOURS.
    Se llama al iniciar la app: en hostings que duermen el servidor (p. ej. Render free)
    el job programado no corre mientras está dormido, así que se recupera al despertar.
    """
    last = get_last_scrape()
    if last is None or datetime.now(pytz.utc) - last > timedelta(hours=settings.SCRAPE_STALE_HOURS):
        print(f"⏰ Último scraping: {last or 'nunca'} → ejecutando scraping de recuperación")
        threading.Thread(target=run_scraping_job, daemon=True).start()


def start_scheduler():
    """
    Inicia el scheduler de APScheduler.
    Configura el job según SCRAPE_DAY_OF_WEEK / SCRAPE_HOUR / SCRAPE_MINUTE
    (por defecto todos los días a las 18:00 ART).
    """
    scheduler = BackgroundScheduler(timezone=settings.SCRAPE_TIMEZONE)

    trigger = CronTrigger(
        day_of_week=settings.SCRAPE_DAY_OF_WEEK,  # '*' = todos los días
        hour=settings.SCRAPE_HOUR,
        minute=settings.SCRAPE_MINUTE,
        timezone=settings.SCRAPE_TIMEZONE
    )
    
    scheduler.add_job(
        run_scraping_job,
        trigger=trigger,
        id="scraping_job",
        name="Scraping Macroeconómico",
        replace_existing=True,
        misfire_grace_time=3600,  # Tolerancia de 1 hora si el servidor estaba apagado
        coalesce=True,            # Si se perdieron varias ejecuciones, correr solo una
        max_instances=1,
    )

    scheduler.start()
    days = "todos los días" if settings.SCRAPE_DAY_OF_WEEK == "*" else f"días '{settings.SCRAPE_DAY_OF_WEEK}'"
    next_run = scheduler.get_job("scraping_job").next_run_time
    print(f"📅 Scheduler iniciado: {days} a las {settings.SCRAPE_HOUR:02d}:{settings.SCRAPE_MINUTE:02d} "
          f"{settings.SCRAPE_TIMEZONE} (próxima: {next_run.isoformat()})")
    
    return scheduler
