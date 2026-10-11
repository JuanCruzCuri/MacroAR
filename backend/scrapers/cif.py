"""
MacroAR - Scraper CIF-UTDT (Centro de Investigación en Finanzas)
=================================================================
Scraping de indicadores del CIF de la Universidad Torcuato Di Tella.
La página principal (utdt.edu/cif) muestra los 3 indicadores principales:
- Encuesta de Expectativas de Inflación (EI)
- Índice de Confianza del Consumidor (ICC)
- Índice Líder (IL)
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

CIF_BASE_URL = "https://www.utdt.edu"
CIF_HOME_URL = f"{CIF_BASE_URL}/cif"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}


async def fetch_page(url: str) -> Optional[str]:
    """Descarga una página HTML."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"⚠️ Error fetching CIF {url}: {e}")
        return None


def parse_indicators(html: str) -> List[Dict[str, Any]]:
    """
    Extrae los 3 indicadores principales del CIF.
    La estructura en la página es:
    - Links con nombre del indicador, período y valor
    Ejemplo: "Encuesta de Expectativas de Inflación (EI) / Septiembre 2026 / 29,8%"
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar todos los links que contienen información de indicadores
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        text = safe_text(link)
        
        if not text or len(text) < 10:
            continue
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Buscar Encuesta de Expectativas de Inflación
        if 'expectativas' in text.lower() and 'inflación' in text.lower() or 'inflacion' in text.lower():
            for line in lines:
                value = clean_numeric_value(line)
                if value is not None and value > 5:  # Expectativas de inflación > 5%
                    # Buscar período
                    period = ''
                    for l in lines:
                        if re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}', l.lower()):
                            period = l
                            break
                    
                    indicators.append({
                        "indicator_key": "expectativas_inflacion",
                        "name": "Expectativas de Inflación",
                        "value": value,
                        "value_raw": str(value),
                        "unit": "%",
                        "period": period,
                        "source": "CIF-UTDT",
                        "source_url": f"{CIF_BASE_URL}{href}" if not href.startswith('http') else href,
                        "category": "inflacion"
                    })
                    break
        
        # Buscar Índice de Confianza del Consumidor
        elif 'confianza' in text.lower() and 'consumidor' in text.lower():
            for line in lines:
                value = clean_numeric_value(line)
                if value is not None and abs(value) < 50:  # Rango razonable
                    period = ''
                    for l in lines:
                        if re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}', l.lower()):
                            period = l
                            break
                    
                    indicators.append({
                        "indicator_key": "icc",
                        "name": "Índice Confianza del Consumidor",
                        "value": value,
                        "value_raw": str(value),
                        "unit": "%",
                        "period": period,
                        "source": "CIF-UTDT",
                        "source_url": f"{CIF_BASE_URL}{href}" if not href.startswith('http') else href,
                        "category": "financiero"
                    })
                    break
        
        # Buscar Índice Líder
        elif 'índice líder' in text.lower() or 'indice lider' in text.lower():
            for line in lines:
                value = clean_numeric_value(line)
                if value is not None and abs(value) < 10:  # Variación mensual pequeña
                    period = ''
                    for l in lines:
                        if re.search(r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+\d{4}', l.lower()):
                            period = l
                            break
                    
                    indicators.append({
                        "indicator_key": "indice_lider",
                        "name": "Índice Líder (CIF)",
                        "value": value,
                        "value_raw": str(value),
                        "unit": "%",
                        "period": period,
                        "source": "CIF-UTDT",
                        "source_url": f"{CIF_BASE_URL}{href}" if not href.startswith('http') else href,
                        "category": "actividad"
                    })
                    break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones (PDFs) del CIF."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar links a PDFs
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        text = safe_text(link)
        
        if 'download.php' in href or href.endswith('.pdf'):
            if href not in seen_urls and len(text) > 5:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{CIF_BASE_URL}{href}"
                
                publications.append({
                    "title": text[:500] if len(text) > 5 else "Informe CIF-UTDT",
                    "date": datetime.now(),
                    "source": "CIF-UTDT",
                    "url": full_url,
                    "type": "reporte",
                    "description": f"Publicación del Centro de Investigación en Finanzas - UTDT"
                })
    
    return publications[:10]


async def scrape_cif() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para CIF-UTDT."""
    result = {"indicators": [], "publications": []}
    
    html = await fetch_page(CIF_HOME_URL)
    if html:
        result["indicators"] = parse_indicators(html)
        result["publications"] = parse_publications(html)
    
    print(f"✅ CIF-UTDT: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
