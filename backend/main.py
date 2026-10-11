"""
MacroAR - FastAPI Application
==============================
API REST para servir datos macroeconómicos al frontend React.

Endpoints:
- GET /api/indicators → Snapshot actual de indicadores
- GET /api/publications → Feed de publicaciones
- GET /api/health → Health check
- POST /api/scrape → Trigger manual de scraping (solo dev)
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from config import settings
from database import get_db, init_db
from models import IndicatorSnapshot, PublicationFeed
from scheduler import start_scheduler, run_scraping_job

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
async def get_indicators(db: Session = Depends(get_db)):
    """
    Obtiene el snapshot actual de todos los indicadores.
    Retorna solo el último valor de cada indicador (sin histórico).
    """
    indicators = db.query(IndicatorSnapshot).order_by(IndicatorSnapshot.category).all()
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
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Obtiene el feed de publicaciones ordenadas por fecha (más reciente primero).
    Opcionalmente filtra por fuente.
    """
    query = db.query(PublicationFeed)
    
    if source:
        query = query.filter(PublicationFeed.source == source)
    
    publications = query.order_by(PublicationFeed.date.desc()).limit(limit).all()
    return [pub.to_dict() for pub in publications]


@app.post("/api/scrape")
async def trigger_scrape():
    """
    Trigger manual del proceso de scraping.
    Útil para testing o actualización inmediata.
    Nota: En producción, considerar agregar autenticación.
    """
    try:
        # Ejecutar en un thread para no bloquear
        import threading
        thread = threading.Thread(target=run_scraping_job)
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
