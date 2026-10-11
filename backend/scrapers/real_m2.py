"""
MacroAR - Scraper Real M2 Report (UCEMA)
==========================================
Scraping del reporte de M2 Real de la Universidad del CEMA.
IMPORTANTE: El "M2 Real" de UCEMA es un índice de precios de metros
cuadrados de departamentos en CABA (no es el agregado monetario M2).
URL: https://ucema.edu.ar/indices-y-bases-de-datos

La página tiene varias tarjetas con la misma estructura (.cifras-destacadas),
p. ej. también la Canasta del Profesional Ejecutivo (CPE). Solo se lee la
tarjeta cuyo link apunta a un informe M2 (/indices-y-bases-de-datos/m2-MMYYYY).
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import parse_ar_number, normalize_period, safe_text

UCEMA_BASE_URL = "https://ucema.edu.ar"
UCEMA_INDICES_URL = f"{UCEMA_BASE_URL}/indices-y-bases-de-datos"

M2_LINK = re.compile(r'/indices-y-bases-de-datos/m2-(\d{2})(\d{4})')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

# (regex sobre el texto de la cifra, key, nombre)
FIGURE_SPECS = [
    (r'promedio', "m2_real_indice", "M2 Real — Índice M² CABA"),
    (r'acumulada', "m2_real_acumulado", "M2 Real — Variación Acumulada CABA"),
]


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


def full_url(href: str) -> str:
    return href if href.startswith('http') else f"{UCEMA_BASE_URL}{href}"


def find_m2_card(soup: BeautifulSoup):
    """Devuelve el contenedor de la tarjeta "Último informe" del M2 Real."""
    for figures in soup.select('.cifras-destacadas'):
        node = figures
        for _ in range(8):
            node = node.parent
            if node is None:
                break
            if node.find('a', href=M2_LINK):
                return node
    return None


def parse_real_m2(html: str) -> List[Dict[str, Any]]:
    """Extrae las cifras destacadas del último informe M2 Real."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    card = find_m2_card(soup)
    if card is None:
        print("⚠️ UCEMA: no se encontró la tarjeta del M2 Real")
        return indicators

    period = normalize_period(safe_text(card.select_one('.views-field-field-mes-ano')))
    source_url = full_url(card.find('a', href=M2_LINK)['href'])

    for wrapper in card.select('.cifra-destacada-wrapper'):
        label = safe_text(wrapper.select_one('.cifra-destacada-texto'))
        raw_value = safe_text(wrapper.select_one('.cifra-destacada'))
        value = parse_ar_number(raw_value)
        if value is None:
            continue
        for pattern, key, name in FIGURE_SPECS:
            if re.search(pattern, label, re.IGNORECASE):
                indicators.append({
                    "indicator_key": key,
                    "name": name,
                    "value": value,
                    "value_raw": raw_value,
                    "unit": "%",
                    "period": period,
                    "source": "UCEMA",
                    "source_url": source_url,
                    "category": "inmobiliario",
                })
                break

    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae los informes M2 Real (último + anteriores). Fecha = mes del informe."""
    publications = {}
    soup = BeautifulSoup(html, 'lxml')

    for link in soup.find_all('a', href=M2_LINK):
        title = safe_text(link)
        url = full_url(link['href'])
        if url in publications or len(title) < 10:  # descarta "Ver informe"
            continue
        match = M2_LINK.search(link['href'])
        publications[url] = {
            "title": title[:500],
            "date": datetime(int(match.group(2)), int(match.group(1)), 1),
            "source": "UCEMA",
            "url": url,
            "type": "reporte",
            "description": "Informe M2 Real de la Universidad del CEMA. Índice de precios reales de metros cuadrados de departamentos en CABA.",
        }

    return list(publications.values())[:5]


async def scrape_real_m2() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para Real M2 Report (UCEMA)."""
    result = {"indicators": [], "publications": []}

    html = await fetch_page(UCEMA_INDICES_URL)
    if html:
        result["indicators"] = parse_real_m2(html)
        result["publications"] = parse_publications(html)

    print(f"✅ UCEMA Real M2: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
