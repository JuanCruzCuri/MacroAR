"""
MacroAR - Scraper IPC CABA (Instituto de Estadística y Censos de la Ciudad)
===========================================================================
Scraping del IPC de la Ciudad de Buenos Aires (IPCBA).
Publicaciones disponibles en estadisticaciudad.gob.ar

La portada muestra contadores animados (Elementor): el HTML trae "0 %" y el
valor real está en el atributo data-to-value del contador.
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import normalize_period, safe_text

CABA_BASE_URL = "https://www.estadisticaciudad.gob.ar"
CABA_EYC_URL = f"{CABA_BASE_URL}/eyc/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

CONTAINER_CLASS = re.compile(r'e-con-inner|elementor-widget-wrap|elementor-column')


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


def upload_date(url: str) -> Optional[datetime]:
    """Fecha aproximada desde la ruta de WordPress: /wp-content/uploads/2026/10/... → 2026-10-01."""
    match = re.search(r'/uploads/(\d{4})/(\d{2})/', url)
    return datetime(int(match.group(1)), int(match.group(2)), 1) if match else None


def ipcba_pdf_links(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Links a PDFs cuyo texto menciona IPCBA, deduplicados por URL."""
    links = {}
    for link in soup.find_all('a', href=re.compile(r'\.pdf$', re.I)):
        title = safe_text(link)
        href = link['href']
        if 'ipcba' in title.lower() and href not in links:
            url = href if href.startswith('http') else f"{CABA_BASE_URL}{href}"
            links[href] = {"url": url, "title": title}
    return list(links.values())


def parse_ipc_caba(html: str) -> List[Dict[str, Any]]:
    """Extrae el IPCBA mensual del contador de la portada."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    pdfs = ipcba_pdf_links(soup)

    for counter in soup.select('[data-to-value]'):
        container = counter.find_parent(class_=CONTAINER_CLASS)
        label = safe_text(container)
        if not re.match(r'IPCBA\b', label):
            continue
        try:
            value = float(counter['data-to-value'])
        except ValueError:
            continue
        indicators.append({
            "indicator_key": "ipc_caba",
            "name": "IPCBA Mensual",
            "value": value,
            "value_raw": counter['data-to-value'],
            "unit": "%",
            "period": normalize_period(label),
            "source": "IPC CABA - DGEC",
            "source_url": pdfs[0]["url"] if pdfs else CABA_EYC_URL,
            "category": "inflacion",
        })
        break

    return indicators


def parse_publications(html: str, period: str = '') -> List[Dict[str, Any]]:
    """Extrae los informes IPCBA (PDF) de la portada."""
    soup = BeautifulSoup(html, 'lxml')
    return [
        {
            "title": f"{pdf['title']} — {period}" if period else pdf['title'],
            "date": upload_date(pdf["url"]),
            "source": "DGEC - GCBA",
            "url": pdf["url"],
            "type": "informe",
            "description": "Informe IPC Ciudad de Buenos Aires",
        }
        for pdf in ipcba_pdf_links(soup)[:5]
    ]


async def scrape_ipc_caba() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para IPC CABA."""
    result = {"indicators": [], "publications": []}

    html = await fetch_page(CABA_EYC_URL)
    if html:
        result["indicators"] = parse_ipc_caba(html)
        period = result["indicators"][0]["period"] if result["indicators"] else ''
        result["publications"] = parse_publications(html, period)

    print(f"✅ IPC CABA: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
