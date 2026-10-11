"""
MacroAR - Scraper INDEC
========================
Scraping de indicadores principales del INDEC.
La página de inicio (indec.gob.ar) tiene los últimos indicadores
en un formato estructurado con links a los PDFs.
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

INDEC_BASE_URL = "https://www.indec.gob.ar"
INDEC_HOME_URL = f"{INDEC_BASE_URL}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}


async def fetch_page(url: str) -> Optional[str]:
    """Descarga una página HTML de forma asíncrona."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.text
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None


def parse_home_indicators(html: str) -> List[Dict[str, Any]]:
    """
    Extrae los indicadores principales del homepage del INDEC.
    La estructura es:
    - Bloques con imagen, valor numérico, nombre del indicador y período
    - Links a PDFs de los informes
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar los bloques de indicadores en el homepage
    # Estructura: <a> con imagen, valor, nombre y período
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        text = safe_text(link)
        
        # Buscar links a informes de prensa (PDFs)
        if '/uploads/informesdeprensa/' in href and href.endswith('.pdf'):
            # Extraer información del texto del link
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            
            if len(lines) >= 2:
                # El último elemento suele ser el período
                period = lines[-1] if lines else ''
                # El valor numérico está típicamente antes del período
                value_text = ''
                name = ''
                
                for line in lines:
                    # Buscar línea con valor numérico (contiene % o es un número)
                    if re.search(r'\d+[.,]\d+\s*%?', line):
                        value_text = line
                    elif len(line) > 3 and not line.startswith('http'):
                        name = line
                
                if value_text:
                    value = clean_numeric_value(value_text)
                    
                    # Determinar el indicador por el nombre o URL
                    indicator_key = None
                    indicator_name = name
                    category = 'actividad'
                    
                    if 'ipc' in href.lower() or 'precios' in name.lower():
                        indicator_key = 'ipc_mensual'
                        indicator_name = 'IPC Mensual (Nacional)'
                        category = 'inflacion'
                    elif 'emae' in href.lower() or 'actividad' in name.lower():
                        indicator_key = 'emae'
                        indicator_name = 'EMAE (Actividad Económica)'
                        category = 'actividad'
                    elif 'trabajo' in href.lower() or 'desocupacion' in name.lower():
                        indicator_key = 'desocupacion'
                        indicator_name = 'Desocupación'
                        category = 'laboral'
                    elif 'ipi' in href.lower() and 'manufacturero' in href.lower():
                        indicator_key = 'ipi_manufacturero'
                        indicator_name = 'IPI Manufacturero'
                        category = 'actividad'
                    elif 'ipi' in href.lower() and 'minero' in href.lower():
                        indicator_key = 'ipi_minero'
                        indicator_name = 'IPI Minero'
                        category = 'actividad'
                    elif 'isac' in href.lower() or 'construcci' in name.lower():
                        indicator_key = 'isac'
                        indicator_name = 'ISAC (Construcción)'
                        category = 'actividad'
                    
                    if indicator_key and value is not None:
                        full_url = href if href.startswith('http') else f"{INDEC_BASE_URL}{href}"
                        indicators.append({
                            "indicator_key": indicator_key,
                            "name": indicator_name,
                            "value": value,
                            "value_raw": value_text,
                            "unit": "%",
                            "period": period,
                            "source": "INDEC",
                            "source_url": full_url,
                            "category": category
                        })
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones/noticias del homepage del INDEC."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar la sección de noticias
    all_links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in all_links:
        href = link.get('href', '')
        text = safe_text(link)
        
        # Links a informes de prensa (PDFs)
        if '/uploads/informesdeprensa/' in href and href.endswith('.pdf'):
            if href not in seen_urls and len(text) > 10:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{INDEC_BASE_URL}{href}"
                
                # Extraer título del texto
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                title = lines[0] if lines else 'Informe INDEC'
                description = ' '.join(lines[1:]) if len(lines) > 1 else ''
                
                # Determinar tipo
                pub_type = 'informe'
                
                publications.append({
                    "title": title[:500],
                    "date": datetime.now(),
                    "source": "INDEC",
                    "url": full_url,
                    "type": pub_type,
                    "description": description[:300] if description else f"Publicación del INDEC"
                })
    
    return publications[:10]


async def scrape_indec() -> Dict[str, List[Dict[str, Any]]]:
    """
    Función principal de scraping para INDEC.
    Scrapea el homepage que contiene los últimos indicadores.
    """
    result = {"indicators": [], "publications": []}
    
    html = await fetch_page(INDEC_HOME_URL)
    if html:
        result["indicators"] = parse_home_indicators(html)
        result["publications"] = parse_publications(html)
    
    print(f"✅ INDEC: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
