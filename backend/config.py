"""
MacroAR - Configuración de la aplicación
Carga variables de entorno desde .env
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/macroar"
    )
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SCRAPE_DAY_OF_WEEK: str = os.getenv("SCRAPE_DAY_OF_WEEK", "*")  # '*' = todos los días
    SCRAPE_HOUR: int = int(os.getenv("SCRAPE_HOUR", "18"))
    SCRAPE_MINUTE: int = int(os.getenv("SCRAPE_MINUTE", "0"))
    SCRAPE_TIMEZONE: str = os.getenv("SCRAPE_TIMEZONE", "America/Argentina/Buenos_Aires")
    # Token para POST /api/scrape (header X-Scrape-Token). Vacío = endpoint deshabilitado.
    SCRAPE_TOKEN: str = os.getenv("SCRAPE_TOKEN", "")
    # Si al iniciar el último scraping tiene más de N horas, se ejecuta uno de inmediato
    # (cubre las ejecuciones perdidas mientras el servidor estaba dormido/apagado).
    SCRAPE_STALE_HOURS: int = int(os.getenv("SCRAPE_STALE_HOURS", "24"))

    class Config:
        env_file = ".env"


settings = Settings()
