"""
MacroAR - Scraper Real M2 Report (UCEMA)
==========================================
Scraping del reporte de M2 Real de la Universidad del CEMA.
Indicador clave de la demanda de dinero en relación al PBI.
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

UCEMA_BASE_URL = "https://www.ucema.edu.ar"
UCEMA_M2_URL = f"{UCEMA_BASE_URL}/u/real-m2"
# URL alternativa si la principal cambia
UCEMA_M2_ALT_URL = f"{UCEMA_BASE_URL}/areas/finanzas/real-m2"

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
        print(f"⚠️ Error fetching UCEMA {url}: {e}")
        return None


def parse_real_m2(html: str) -> List[Dict[str, Any]]:
    """Extrae el indicador de M2 Real."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar tablas con datos de M2
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        # Buscar la última fila con datos
        for row in reversed(rows):
            cells = [safe_text(td) for td in row.find_all(['td', 'th'])]
            if len(cells) >= 2:
                # Buscar valor de M2/PBI
                for cell in cells:
                    value = clean_numeric_value(cell)
                    if value is not None and 20 < value < 200:  # Rango razonable para M2/PBI
                        indicators.append({
                            "indicator_key": "real_m2",
                            "name": "M2 Real (Base Dic/2016)",
                            "value": value,
                            "value_raw": cell,
                            "unit": "% del PBI",
                            "period": datetime.now().strftime("%B %Y"),
                            "source": "UCEMA - Real M2 Report",
                            "source_url": UCEMA_BASE_URL,
                            "category": "monetario"
                        })
                        break
                if indicators:
                    break
        if indicators:
            break
    
    # Fallback: buscar en texto
    if not indicators:
        patterns = [
            r'M2.*?PBI.*?(\d+[.,]\d+)',
            r'M2\s*[Rr]eal.*?(\d+[.,]\d+)',
            r'Monetizaci[oó]n.*?(\d+[.,]\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
            if match:
                value = clean_numeric_value(match.group(1))
                if value is not None and 20 < value < 200:
                    indicators.append({
                        "indicator_key": "real_m2",
                        "name": "M2 Real (Base Dic/2016)",
                        "value": value,
                        "value_raw": match.group(1),
                        "unit": "% del PBI",
                        "period": datetime.now().strftime("%B %Y"),
                        "source": "UCEMA - Real M2 Report",
                        "source_url": UCEMA_BASE_URL,
                        "category": "monetario"
                    })
                    break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones del Real M2 Report."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar links a PDFs o reportes
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = safe_text(link)
        
        if any(keyword in href.lower() or keyword in title.lower() 
               for keyword in ['m2', 'real', 'report', 'pdf', 'monetari']):
            if href not in seen_urls and len(title) > 5:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{UCEMA_BASE_URL}{href}"
                
                publications.append({
                    "title": title[:500] if len(title) > 5 else "Real M2 Report - UCEMA",
                    "date": datetime.now(),
                    "source": "UCEMA",
                    "url": full_url,
                    "type": "reporte",
                    "description": "Reporte de M2 Real de la Universidad del CEMA. Análisis de la demanda de dinero y su relación con el PBI."
                })
    
    return publications[:5]


async def scrape_real_m2() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para Real M2 Report (UCEMA)."""
    result = {"indicators": [], "publications": []}
    
    # Intentar URL principal
    html = await fetch_page(UCEMA_M2_URL)
    
    # Si falla, intentar URL alternativa
    if not html:
        html = await fetch_page(UCEMA_M2_ALT_URL)
    
    if html:
        result["indicators"] = parse_real_m2(html)
        result["publications"] = parse_publications(html)
    
    print(f"✅ UCEMA Real M2: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
