"""
MacroAR - Scraper CIF-UTDT (Centro de Investigación en Finanzas)
=================================================================
Scraping de indicadores del CIF de la Universidad Torcuato Di Tella.
La página principal (utdt.edu/cif) muestra los 3 indicadores principales:
- Encuesta de Expectativas de Inflación (EI)
- Índice de Confianza del Consumidor (ICC)
- Índice Líder (IL)

Estructura de cada tarjeta:
  .indicesCuadros > a > h4 (nombre) + p.indicesFechas (período) + p.cif-stat-num (valor)
"""
import httpx
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from utils import parse_ar_number, normalize_period, parse_argentine_date, safe_text

CIF_BASE_URL = "https://www.utdt.edu"
CIF_HOME_URL = f"{CIF_BASE_URL}/cif"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

# (regex sobre el título de la tarjeta, key, nombre, categoría)
INDICATOR_SPECS = [
    (r'expectativas de inflaci', "expectativas_inflacion", "Expectativas de Inflación", "expectativas"),
    (r'confianza del consumidor', "confianza_consumidor", "Índice Confianza del Consumidor", "expectativas"),
    (r'[íi]ndice\s+l[íi]der', "indice_lider", "Índice Líder (CIF)", "actividad"),
]


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


def full_url(href: str) -> str:
    return href if href.startswith('http') else f"{CIF_BASE_URL}/{href.lstrip('/')}"


def parse_report_links(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Mapea título de sección → URL del PDF ("Descargar informe").
    El título es el primer encabezado que se encuentra subiendo desde el link.
    """
    links = {}
    for link in soup.find_all('a', href=re.compile(r'download\.php|\.pdf$', re.I)):
        node = link
        for _ in range(6):
            node = node.parent
            if node is None:
                break
            heading = node.find(['h2', 'h3', 'h4', 'h5', 'strong'])
            if heading:
                links.setdefault(safe_text(heading), full_url(link['href']))
                break
    return links


def parse_indicators(html: str) -> List[Dict[str, Any]]:
    """Extrae los 3 indicadores principales del CIF desde las tarjetas .indicesCuadros."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    report_links = parse_report_links(soup)

    for card in soup.select('.indicesCuadros'):
        title = safe_text(card.find('h4'))
        raw_value = safe_text(card.select_one('.cif-stat-num'))
        period = normalize_period(safe_text(card.select_one('.indicesFechas')))

        for pattern, key, name, category in INDICATOR_SPECS:
            if not re.search(pattern, title, re.IGNORECASE):
                continue
            value = parse_ar_number(raw_value)
            if value is None:
                break
            source_url = next(
                (url for heading, url in report_links.items() if re.search(pattern, heading, re.IGNORECASE)),
                CIF_HOME_URL,
            )
            indicators.append({
                "indicator_key": key,
                "name": name,
                "value": value,
                "value_raw": raw_value,
                "unit": "%",
                "period": period,
                "source": "CIF-UTDT",
                "source_url": source_url,
                "category": category,
            })
            break

    return indicators


def parse_publications(html: str, indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrae los informes (PDFs) del CIF. El título se toma del encabezado de la sección,
    y la fecha del período del indicador correspondiente (si existe).
    """
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    periods_by_url = {ind["source_url"]: ind["period"] for ind in indicators}

    for heading, url in parse_report_links(soup).items():
        period = periods_by_url.get(url, '')
        publications.append({
            "title": f"{heading} — {period}" if period else heading,
            "date": parse_argentine_date(period) if period else None,
            "source": "CIF-UTDT",
            "url": url,
            "type": "reporte",
            "description": "Publicación del Centro de Investigación en Finanzas - UTDT",
        })

    return publications[:10]


async def scrape_cif() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para CIF-UTDT."""
    result = {"indicators": [], "publications": []}

    html = await fetch_page(CIF_HOME_URL)
    if html:
        result["indicators"] = parse_indicators(html)
        result["publications"] = parse_publications(html, result["indicators"])

    print(f"✅ CIF-UTDT: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
