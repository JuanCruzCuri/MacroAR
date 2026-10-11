"""
MacroAR - Scheduler (APScheduler)
===================================
Ejecuta el scraping automáticamente cada viernes a las 18:00 ART.
Usa APScheduler con BackgroundScheduler para no bloquear el event loop.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz

from config import settings
from database import SessionLocal
from models import IndicatorSnapshot, PublicationFeed
from scrapers import scrape_indec, scrape_cif, scrape_ipc_caba, scrape_real_m2

import asyncio


def run_scraping_job():
    """
    Job principal de scraping.
    Ejecuta todos los scrapers y actualiza la base de datos (upsert).
    """
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
                    existing.updated_at = datetime.now(pytz.timezone(settings.SCRAPE_TIMEZONE))
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
                    existing_pub.updated_at = datetime.now(pytz.timezone(settings.SCRAPE_TIMEZONE))
                else:
                    # Insertar nueva publicación
                    new_pub = PublicationFeed(
                        title=pub_data.get("title", ""),
                        date=pub_data.get("date"),
                        source=pub_data.get("source", ""),
                        url=pub_data.get("url", ""),
                        type=pub_data.get("type"),
                        description=pub_data.get("description"),
                    )
                    db.add(new_pub)
            
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


def start_scheduler():
    """
    Inicia el scheduler de APScheduler.
    Configura el job para ejecutarse cada viernes a las 18:00 ART.
    """
    scheduler = BackgroundScheduler(timezone=settings.SCRAPE_TIMEZONE)
    
    # Configurar trigger: Viernes 18:00 Argentina Time
    trigger = CronTrigger(
        day_of_week=settings.SCRAPE_DAY_OF_WEEK,
        hour=settings.SCRAPE_HOUR,
        minute=settings.SCRAPE_MINUTE,
        timezone=settings.SCRAPE_TIMEZONE
    )
    
    scheduler.add_job(
        run_scraping_job,
        trigger=trigger,
        id="scraping_job",
        name="Scraping Macroeconómico Semanal",
        replace_existing=True,
        misfire_grace_time=3600  # Tolerancia de 1 hora si el servidor estaba apagado
    )
    
    scheduler.start()
    print(f"📅 Scheduler iniciado: Viernes {settings.SCRAPE_HOUR:02d}:{settings.SCRAPE_MINUTE:02d} {settings.SCRAPE_TIMEZONE}")
    
    return scheduler
