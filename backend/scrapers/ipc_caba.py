"""
MacroAR - Scraper IPC CABA (Dirección General de Estadística y Censos)
=======================================================================
Scraping del IPC de la Ciudad de Buenos Aires.
Publicaciones disponibles en estadisticaciudad.gob.ar
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

CABA_BASE_URL = "https://www.estadisticaciudad.gob.ar"
CABA_EYC_URL = f"{CABA_BASE_URL}/eyc/"
CABA_BUSCADOR_URL = f"{CABA_BASE_URL}/eyc/buscador-publicaciones/"

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
    
    # Buscar links a publicaciones IPCBA
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '')
        text = safe_text(link)
        
        if 'ipcba' in href.lower() or 'ipcba' in text.lower():
            # Found IPCBA publication link
            full_url = href if href.startswith('http') else f"{CABA_BASE_URL}{href}"
            
            # Try to extract values from the text
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for line in lines:
                value = clean_numeric_value(line)
                if value is not None and 0 < value < 20:
                    indicators.append({
                        "indicator_key": "ipc_caba",
                        "name": "IPCBA Mensual",
                        "value": value,
                        "value_raw": line,
                        "unit": "%",
                        "period": datetime.now().strftime("%B %Y"),
                        "source": "IPC CABA - DGEC",
                        "source_url": full_url,
                        "category": "inflacion"
                    })
                    break
    
    # Fallback: buscar en texto de la página
    if not indicators:
        patterns = [
            r'[Vv]ariación\s+mensual\s+(\d+[.,]\d+)\s*%?',
            r'IPCBA.*?(\d+[.,]\d+)\s*%',
        ]
        for pattern in patterns:
            match = re.search(pattern, all_text, re.DOTALL)
            if match:
                value = clean_numeric_value(match.group(1))
                if value is not None and 0 < value < 20:
                    indicators.append({
                        "indicator_key": "ipc_caba",
                        "name": "IPCBA Mensual",
                        "value": value,
                        "value_raw": match.group(1),
                        "unit": "%",
                        "period": datetime.now().strftime("%B %Y"),
                        "source": "IPC CABA - DGEC",
                        "source_url": CABA_EYC_URL,
                        "category": "inflacion"
                    })
                    break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones del IPC CABA."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = safe_text(link)
        
        if ('ipcba' in href.lower() or 'ipcba' in title.lower() or 
            'ipc' in title.lower()) and len(title) > 10:
            if href not in seen_urls:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{CABA_BASE_URL}{href}"
                
                publications.append({
                    "title": title[:500],
                    "date": datetime.now(),
                    "source": "DGEC - GCBA",
                    "url": full_url,
                    "type": "informe",
                    "description": f"Informe IPC Ciudad de Buenos Aires"
                })
    
    return publications[:5]


async def scrape_ipc_caba() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para IPC CABA."""
    result = {"indicators": [], "publications": []}
    
    # Intentar la página principal del eyC
    html = await fetch_page(CABA_EYC_URL)
    if html:
        result["indicators"] = parse_ipc_caba(html)
        result["publications"] = parse_publications(html)
    
    # También intentar el buscador de publicaciones
    if not result["publications"]:
        html2 = await fetch_page(CABA_BUSCADOR_URL)
        if html2:
            result["publications"] = parse_publications(html2)
    
    print(f"✅ IPC CABA: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
