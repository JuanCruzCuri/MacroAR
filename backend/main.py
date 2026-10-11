"""
MacroAR - FastAPI Application
==============================
API REST para servir datos macroeconómicos al frontend React.

Endpoints:
- GET /api/indicators → Snapshot actual de indicadores
- GET /api/publications → Feed de publicaciones
- GET /api/health → Health check
- GET /api/meta/status → Último scraping y próxima ejecución programada
- POST /api/scrape → Trigger manual de scraping (requiere header X-Scrape-Token)
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional
import secrets

from config import settings
from database import get_db, init_db
from models import IndicatorSnapshot, PublicationFeed
from scheduler import start_scheduler, run_scraping_job, run_if_stale, get_last_scrape

# Variable global para el scheduler
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup y shutdown."""
    # Startup
    print("🚀 MacroAR API iniciando...")
    init_db()
    
    global scheduler
    scheduler = start_scheduler()
    run_if_stale()
    
    print(f"✅ API lista en http://0.0.0.0:8000")
    print(f"🌐 Frontend permitido: {settings.FRONTEND_URL}")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown(wait=False)
        print("👋 Scheduler detenido")


# Crear aplicación FastAPI
app = FastAPI(
    title="MacroAR API",
    description="API de datos macroeconómicos de Argentina. Scraping automático de INDEC, CIF-UTDT, IPC CABA y UCEMA.",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================
# CORS Configuration
# ============================================
# Permite requests desde el frontend (Vercel o localhost)
origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:3000",
    "https://macroar.vercel.app",
    # Agregar más dominios según sea necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - info de la API."""
    return {
        "name": "MacroAR API",
        "version": "1.0.0",
        "description": "Datos macroeconómicos de Argentina",
        "endpoints": {
            "indicators": "/api/indicators",
            "publications": "/api/publications",
            "health": "/api/health"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "scheduler_active": scheduler is not None and scheduler.running if scheduler else False
    }


@app.get("/api/indicators", response_model=List[dict])
async def get_indicators(
    category: str = None,
    source: str = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el snapshot actual de todos los indicadores.
    Retorna solo el último valor de cada indicador (sin histórico).
    
    Parámetros opcionales:
    - category: filtrar por categoría (inflacion, actividad, laboral, 
      comercio_exterior, social, expectativas, sector_publico, inmobiliario)
    - source: filtrar por fuente (INDEC, CIF-UTDT, IPC CABA - DGEC, UCEMA)
    """
    query = db.query(IndicatorSnapshot)
    
    if category:
        query = query.filter(IndicatorSnapshot.category == category)
    if source:
        query = query.filter(IndicatorSnapshot.source == source)
    
    indicators = query.order_by(IndicatorSnapshot.category).all()
    return [indicator.to_dict() for indicator in indicators]


@app.get("/api/indicators/{indicator_key}")
async def get_indicator(indicator_key: str, db: Session = Depends(get_db)):
    """Obtiene un indicador específico por su key."""
    indicator = db.query(IndicatorSnapshot).filter(
        IndicatorSnapshot.indicator_key == indicator_key
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    
    return indicator.to_dict()


@app.get("/api/publications", response_model=List[dict])
async def get_publications(
    source: str = None,
    type: str = None,
    latest_only: bool = False,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Obtiene el feed de publicaciones ordenadas por fecha (más reciente primero).
    
    Parámetros opcionales:
    - source: filtrar por fuente (INDEC, CIF-UTDT, DGEC - GCBA, UCEMA)
    - type: filtrar por tipo (informe, reporte, analisis)
    - latest_only: si es True, retorna solo la última publicación por fuente
    - limit: máximo de resultados (default 20)
    """
    query = db.query(PublicationFeed)
    
    if source:
        query = query.filter(PublicationFeed.source == source)
    if type:
        query = query.filter(PublicationFeed.type == type)
    
    if latest_only:
        # Obtener la última publicación por fuente
        from sqlalchemy import func
        subq = db.query(
            PublicationFeed.source,
            func.max(PublicationFeed.date).label('max_date')
        ).group_by(PublicationFeed.source).subquery()
        
        query = query.join(
            subq,
            (PublicationFeed.source == subq.c.source) &
            (PublicationFeed.date == subq.c.max_date)
        )
    
    publications = query.order_by(PublicationFeed.date.desc()).limit(limit).all()
    return [pub.to_dict() for pub in publications]


@app.get("/api/meta/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Retorna las categorías de indicadores disponibles."""
    categories = db.query(IndicatorSnapshot.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}


@app.get("/api/meta/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Retorna las fuentes de datos disponibles."""
    ind_sources = db.query(IndicatorSnapshot.source).distinct().all()
    pub_sources = db.query(PublicationFeed.source).distinct().all()
    all_sources = set([s[0] for s in ind_sources if s[0]] + [s[0] for s in pub_sources if s[0]])
    return {"sources": sorted(list(all_sources))}


@app.get("/api/meta/status")
async def get_status():
    """Último scraping y próxima ejecución programada (para mostrar en el frontend)."""
    last = get_last_scrape()
    job = scheduler.get_job("scraping_job") if scheduler else None
    next_run = job.next_run_time if job else None
    return {
        "last_scrape": last.isoformat() if last else None,
        "next_scrape": next_run.isoformat() if next_run else None,
        "timezone": settings.SCRAPE_TIMEZONE,
    }


@app.post("/api/scrape")
async def trigger_scrape(x_scrape_token: Optional[str] = Header(default=None)):
    """
    Trigger manual del proceso de scraping.
    Útil para testing, actualización inmediata o para un cron externo
    (ver .github/workflows/scrape.yml).
    Requiere el header X-Scrape-Token == SCRAPE_TOKEN. Si SCRAPE_TOKEN no está
    configurado, el endpoint queda deshabilitado.
    """
    if not settings.SCRAPE_TOKEN:
        raise HTTPException(status_code=403, detail="Trigger manual deshabilitado (SCRAPE_TOKEN no configurado)")
    if not x_scrape_token or not secrets.compare_digest(x_scrape_token, settings.SCRAPE_TOKEN):
        raise HTTPException(status_code=401, detail="Token inválido")

    try:
        # Ejecutar en un thread para no bloquear
        import threading
        from scheduler import _job_lock
        if _job_lock.locked():
            return {
                "status": "already_running",
                "message": "Ya hay un scraping en curso",
                "timestamp": datetime.now().isoformat()
            }
        thread = threading.Thread(target=run_scraping_job, daemon=True)
        thread.start()
        
        return {
            "status": "started",
            "message": "Scraping iniciado en background",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Run with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# ============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
