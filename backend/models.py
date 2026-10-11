"""
MacroAR - Modelos SQLAlchemy
=============================
Dos tablas principales:
1. indicators_snapshot: Estado actual de cada indicador (upsert)
2. publications_feed: Feed cronológico de publicaciones

Diseño: No almacena datos históricos. Cada scraping sobrescribe los valores
anteriores (snapshot pattern).
"""
from sqlalchemy import (
    Column, String, Float, DateTime, Text, Integer,
    UniqueConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class IndicatorSnapshot(Base):
    """
    Snapshot del último valor publicado para cada indicador.
    Se actualiza (upsert) cada vez que se ejecuta el scraper.
    No almacena histórico — solo el valor más reciente.
    """
    __tablename__ = "indicators_snapshot"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    value = Column(Float, nullable=True)  # Valor numérico limpio
    value_raw = Column(String(100), nullable=True)  # Valor original tal como se extrajo
    unit = Column(String(50), nullable=True)  # %, $, pbs, etc.
    period = Column(String(100), nullable=True)  # "Mayo 2025", "Q1 2025", etc.
    source = Column(String(100), nullable=False)  # INDEC, CIF-UTDT, etc.
    source_url = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # inflacion, actividad, laboral, etc.
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_indicator_source', 'indicator_key', 'source'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "indicator_key": self.indicator_key,
            "name": self.name,
            "value": f"{self.value:.1f}" if self.value is not None else self.value_raw,
            "unit": self.unit or "",
            "period": self.period or "",
            "source": self.source,
            "source_url": self.source_url or "",
            "category": self.category or "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class PublicationFeed(Base):
    """
    Feed de publicaciones/scraped reports.
    Cada entrada es una publicación nueva encontrada.
    Se inserta si no existe (por URL) o se actualiza si ya existe.
    """
    __tablename__ = "publications_feed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    date = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(100), nullable=False)
    url = Column(Text, nullable=False, unique=True)
    type = Column(String(50), nullable=True)  # informe, reporte, analisis
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('ix_publication_date', 'date'),
        Index('ix_publication_source', 'source'),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "date": self.date.strftime("%Y-%m-%d") if self.date else None,
            "source": self.source,
            "url": self.url,
            "type": self.type or "",
            "description": self.description or ""
        }
