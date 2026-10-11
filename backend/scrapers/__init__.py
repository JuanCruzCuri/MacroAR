"""
MacroAR - Scrapers
==================
Módulo de scraping para las fuentes de datos macroeconómicos de Argentina.
"""
from scrapers.indec import scrape_indec
from scrapers.cif import scrape_cif
from scrapers.ipc_caba import scrape_ipc_caba
from scrapers.real_m2 import scrape_real_m2

__all__ = ['scrape_indec', 'scrape_cif', 'scrape_ipc_caba', 'scrape_real_m2']
