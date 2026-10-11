"""
MacroAR - Scraper IPC CABA (Dirección General de Estadística y Censos)
=======================================================================
Scraping del IPC de la Ciudad de Buenos Aires.
Fuente: https://www.estadisticaciudad.gob.ar/
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

CABA_BASE_URL = "https://www.estadisticaciudad.gob.ar"
CABA_IPC_URL = f"{CABA_BASE_URL}/eyc/?p=2627"
CABA_PUBLICACIONES_URL = f"{CABA_BASE_URL}/eyc/?cat=2627"

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
        print(f"⚠️ Error fetching CABA {url}: {e}")
        return None


def parse_ipc_caba(html: str) -> List[Dict[str, Any]]:
    """Extrae el IPC de CABA de la página."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar tablas con datos del IPC CABA
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = [safe_text(td) for td in row.find_all(['td', 'th'])]
            if len(cells) >= 2:
                # Buscar celdas con valores de variación
                for i, cell in enumerate(cells):
                    value = clean_numeric_value(cell)
                    if value is not None and 0 < value < 30:  # Rango razonable para IPC mensual
                        period = cells[0] if i > 0 else ""
                        indicators.append({
                            "indicator_key": "ipc_caba",
                            "name": "IPC CABA Mensual",
                            "value": value,
                            "value_raw": cell,
                            "unit": "%",
                            "period": period if period else datetime.now().strftime("%B %Y"),
                            "source": "IPC CABA - DGEC",
                            "source_url": CABA_BASE_URL,
                            "category": "inflacion"
                        })
                        break
                if indicators:
                    break
        if indicators:
            break
    
    # Fallback: buscar en texto
    if not indicators:
        patterns = [
            r'IPC.*?CABA.*?(\d+[.,]\d+)\s*%',
            r'Nivel\s*general.*?(\d+[.,]\d+)',
            r'Variación.*?(\d+[.,]\d+)\s*%',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
            if match:
                value = clean_numeric_value(match.group(1))
                if value is not None and 0 < value < 30:
                    indicators.append({
                        "indicator_key": "ipc_caba",
                        "name": "IPC CABA Mensual",
                        "value": value,
                        "value_raw": match.group(1),
                        "unit": "%",
                        "period": datetime.now().strftime("%B %Y"),
                        "source": "IPC CABA - DGEC",
                        "source_url": CABA_BASE_URL,
                        "category": "inflacion"
                    })
                    break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones del IPC CABA."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar links a informes de IPC
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = safe_text(link)
        
        if any(keyword in title.lower() for keyword in ['ipc', 'índice de precios', 'inflación']):
            if href not in seen_urls and len(title) > 10:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{CABA_BASE_URL}{href}"
                
                publications.append({
                    "title": title[:500],
                    "date": datetime.now(),
                    "source": "DGEC - GCBA",
                    "url": full_url,
                    "type": "informe",
                    "description": f"Informe IPC Ciudad de Buenos Aires: {title[:200]}"
                })
    
    return publications[:5]


async def scrape_ipc_caba() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para IPC CABA."""
    result = {"indicators": [], "publications": []}
    
    html = await fetch_page(CABA_IPC_URL)
    if html:
        result["indicators"] = parse_ipc_caba(html)
        result["publications"] = parse_publications(html)
    
    print(f"✅ IPC CABA: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
