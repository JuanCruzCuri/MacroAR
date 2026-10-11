"""
MacroAR - Scraper INDEC
========================
Scraping de indicadores del INDEC.

IMPORTANTE: las URLs públicas del INDEC (indec.gob.ar/indec/web/Nivel3-Tema-3-5)
devuelven solo el "shell" de la página; el contenido se carga por AJAX desde
fragmentos HTML (indec.gob.ar/Nivel3/Tema/3/5). Este scraper consulta
directamente esos fragmentos.

Dos tipos de bloques se extraen de los fragmentos:
- Tarjetas destacadas (.indicadores-inicio): nombre, valor, medida, período y serie.
  Es la fuente principal y la más estable.
- Informes técnicos (.item-n3): fecha, título, resumen y PDF. Se usan para el
  feed de publicaciones y para indicadores que solo aparecen en el resumen.

Indicadores monitoreados:
- IPC, IPIM (precios mayoristas), ICC (costo de la construcción)
- EMAE, IPI Manufacturero, IPI Minero, ISAC (variación mensual desestacionalizada)
- UCII (capacidad instalada)
- Exportaciones, Importaciones, Saldo comercial (USD millones)
- Desocupación (EPH)
- Pobreza (hogares y personas) e Indigencia (personas)
- Índice de Salarios (mensual, interanual, acumulado)
- Dotación de Personal APN (variación interanual)
"""
import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import parse_ar_number, normalize_period, safe_text

INDEC_BASE_URL = "https://www.indec.gob.ar"

# Fragmentos HTML (se cargan por AJAX en el sitio). Clave → ruta del fragmento.
INDEC_PAGES = {
    # Nivel 3: tarjetas destacadas + último informe del tema
    "precios": "Nivel3/Tema/3/5",
    "cuentas_nacionales": "Nivel3/Tema/3/9",
    "industria": "Nivel3/Tema/3/6",
    "construccion": "Nivel3/Tema/3/3",
    "comercio_exterior": "Nivel3/Tema/3/2",
    "trabajo": "Nivel3/Tema/4/31",
    "pobreza": "Nivel3/Tema/4/46",
    "mineria": "Nivel3/Tema/3/7",
    # Nivel 4: informe técnico específico de cada indicador
    "ipc": "Nivel4/Tema/3/5/31",
    "ipim": "Nivel4/Tema/3/5/32",
    "icc": "Nivel4/Tema/3/5/33",
    "emae": "Nivel4/Tema/3/9/48",
    "ipi_manufacturero": "Nivel4/Tema/3/6/14",
    "ucii": "Nivel4/Tema/3/6/15",
    "balanza": "Nivel4/Tema/3/2/40",
    "mercado_trabajo": "Nivel4/Tema/4/31/58",
    "salarios": "Nivel4/Tema/4/31/61",
    "personal_apn": "Nivel4/Tema/3/10/102",
}

# Indicadores que se leen de las tarjetas destacadas.
# card/measure: regex sobre el nombre y la medida de la tarjeta.
# report: página cuyo PDF se usa como source_url.
CARD_SPECS = [
    {"page": "precios", "card": r"precios al consumidor", "measure": r"mensual",
     "key": "ipc_mensual", "name": "IPC Mensual (Nacional)", "category": "inflacion", "report": "ipc"},
    {"page": "precios", "card": r"precios mayoristas", "measure": r"mensual",
     "key": "ipim_mensual", "name": "IPIM (Precios Mayoristas)", "category": "inflacion", "report": "ipim"},
    {"page": "precios", "card": r"costo de la construcci", "measure": r"mensual",
     "key": "icc_construccion", "name": "ICC (Costo de la Construcción)", "category": "inflacion", "report": "icc"},
    {"page": "cuentas_nacionales", "card": r"actividad econ", "measure": r"mensual",
     "key": "emae_mom_sa", "name": "EMAE (MoM Desestacionalizada)", "category": "actividad", "report": "emae"},
    {"page": "industria", "card": r"IPI manufacturero", "measure": r"mensual",
     "key": "ipi_manufacturero_mom_sa", "name": "IPI Manufacturero (MoM Desestacionalizada)", "category": "actividad", "report": "ipi_manufacturero"},
    {"page": "industria", "card": r"capacidad instalada", "measure": None,
     "key": "ucii", "name": "UCII (Capacidad Instalada Industria)", "category": "actividad", "report": "ucii"},
    {"page": "construccion", "card": r"actividad de la construcci", "measure": r"mensual",
     "key": "isac_mom_sa", "name": "ISAC Construcción (MoM Desestacionalizada)", "category": "actividad", "report": "construccion"},
    {"page": "comercio_exterior", "card": r"^exportaci", "measure": None,
     "key": "balanza_exportaciones", "name": "Exportaciones de Bienes", "category": "comercio_exterior", "report": "balanza"},
    {"page": "comercio_exterior", "card": r"^importaci", "measure": None,
     "key": "balanza_importaciones", "name": "Importaciones de Bienes", "category": "comercio_exterior", "report": "balanza"},
    {"page": "comercio_exterior", "card": r"^saldo", "measure": None,
     "key": "balanza_saldo", "name": "Saldo Comercial", "category": "comercio_exterior", "report": "balanza"},
    {"page": "trabajo", "card": r"desocupaci", "measure": None,
     "key": "desocupacion", "name": "Tasa de Desocupación", "category": "laboral", "report": "mercado_trabajo"},
    {"page": "pobreza", "card": r"poblaci.n bajo la l.nea de pobreza", "measure": None,
     "key": "pobreza_personas", "name": "Pobreza (% Personas)", "category": "social", "report": "pobreza"},
    {"page": "pobreza", "card": r"hogares bajo la l.nea de pobreza", "measure": None,
     "key": "pobreza_hogares", "name": "Pobreza (% Hogares)", "category": "social", "report": "pobreza"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

# Palabras que indican una variación negativa en los textos del INDEC
NEGATIVE_WORDS = r'(?:ca[íi]da|baja|reducci[óo]n|disminuci[óo]n|cay[óo]|baj[óo]|disminuy[óo]|redujo|retroceso|variaci[óo]n negativa)'
CHANGE_WORDS = rf'(?:suba|aumento|incremento|crecimiento|subi[óo]|creci[óo]|aument[óo]|variaci[óo]n positiva|{NEGATIVE_WORDS})'


def public_url(page_key: str) -> str:
    """URL pública (navegable) de un fragmento: Nivel3/Tema/3/5 → /indec/web/Nivel3-Tema-3-5."""
    return f"{INDEC_BASE_URL}/indec/web/{INDEC_PAGES[page_key].replace('/', '-')}"


async def fetch_page(client: httpx.AsyncClient, url: str) -> Optional[str]:
    """Descarga una página HTML de forma asíncrona."""
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None


def signed_value(verb: str, number: str) -> Optional[float]:
    """Aplica el signo según el verbo ('caída de 5,8%' → -5.8)."""
    value = parse_ar_number(number)
    if value is not None and re.fullmatch(NEGATIVE_WORDS, verb.strip(), re.IGNORECASE):
        value = -abs(value)
    return value


def parse_cards(html: str) -> List[Dict[str, str]]:
    """
    Extrae las tarjetas destacadas de un fragmento.
    Estructura: .indicadores-inicio > .col-md-3 con
      .font-2 (nombre), .font-1 (valor), .font-11 (medida), .font-33 (período), .font-111 (serie)
    """
    soup = BeautifulSoup(html, 'lxml')
    cards = []
    for card in soup.select('.indicadores-inicio [class*="col-"]'):
        value = card.select_one('.font-1')
        if value is None:
            continue
        cards.append({
            "name": safe_text(card.select_one('.font-2')),
            "value": safe_text(value),
            "measure": safe_text(card.select_one('.font-11')),
            "period": safe_text(card.select_one('.font-33')),
            "series": safe_text(card.select_one('.font-111')),
        })
    return cards


def parse_reports(html: str) -> List[Dict[str, Any]]:
    """
    Extrae los bloques de informes técnicos (.item-n3) de un fragmento.
    El título puede venir como "10/09/26. Índice de precios..." (Nivel 4) o con la
    fecha en un .card-text separado (Nivel 3).
    """
    soup = BeautifulSoup(html, 'lxml')
    reports = []
    for item in soup.select('.item-n3'):
        title = safe_text(item.select_one('.card-titulo3'))
        date_text = safe_text(item.select_one('.card-text'))

        match = re.match(r'(\d{1,2}/\d{1,2}/\d{2,4})\.?\s*(.*)', title)
        if match:
            date_text, title = match.group(1), match.group(2)

        pdf = item.find('a', href=re.compile(r'/?uploads/informesdeprensa/.*\.pdf$', re.I))
        pdf_url = None
        if pdf:
            href = pdf['href']
            pdf_url = href if href.startswith('http') else f"{INDEC_BASE_URL}/{href.lstrip('/')}"

        reports.append({
            "title": title,
            "date": parse_report_date(date_text),
            "text": safe_text(item.select_one('.card-texto3')),
            "pdf_url": pdf_url,
        })
    return reports


def parse_report_date(text: str) -> Optional[datetime]:
    """'10/09/26' o '07/10/2026' → datetime."""
    match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2,4})', text or '')
    if not match:
        return None
    day, month, year = (int(g) for g in match.groups())
    if year < 100:
        year += 2000
    try:
        return datetime(year, month, day)
    except ValueError:
        return None


def first_report(reports: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Primer informe de la página que tenga PDF."""
    return next((r for r in reports if r["pdf_url"]), None)


def make_indicator(key, name, value, value_raw, unit, period, source_url, category) -> Dict[str, Any]:
    return {
        "indicator_key": key,
        "name": name,
        "value": value,
        "value_raw": value_raw,
        "unit": unit,
        "period": period,
        "source": "INDEC",
        "source_url": source_url,
        "category": category,
    }


def indicators_from_cards(cards_by_page, report_urls) -> List[Dict[str, Any]]:
    """Mapea las tarjetas destacadas a indicadores según CARD_SPECS."""
    indicators = []
    for spec in CARD_SPECS:
        for card in cards_by_page.get(spec["page"], []):
            if not re.search(spec["card"], card["name"], re.IGNORECASE):
                continue
            if spec["measure"] and not re.search(spec["measure"], card["measure"], re.IGNORECASE):
                continue
            value = parse_ar_number(card["value"])
            if value is None:
                continue
            unit = '%' if '%' in card["value"] else (
                'USD millones' if 'millones de d' in card["measure"].lower() else card["measure"]
            )
            indicators.append(make_indicator(
                spec["key"], spec["name"], value, card["value"], unit,
                normalize_period(card["period"]),
                report_urls.get(spec["report"]) or public_url(spec["report"]),
                spec["category"],
            ))
            break
        else:
            print(f"⚠️ INDEC: no se encontró la tarjeta para {spec['key']}")
    return indicators


def indicators_from_reports(reports_by_page, report_urls) -> List[Dict[str, Any]]:
    """Indicadores que solo aparecen en el texto de los informes técnicos."""
    indicators = []

    def report_text(page):
        report = first_report(reports_by_page.get(page, []))
        return report["text"] if report else ''

    def url(page):
        return report_urls.get(page) or public_url(page)

    # IPI Minero: "el índice de la serie desestacionalizada muestra una suba de 1,9% respecto al mes anterior"
    text = report_text("mineria")
    match = re.search(
        rf'serie desestacionalizada\s+(?:muestra|registra|presenta)?\s*(?:una\s+)?({CHANGE_WORDS})\s+(?:de\s+)?(-?\d+(?:,\d+)?)\s*%',
        text, re.IGNORECASE)
    if match:
        indicators.append(make_indicator(
            "ipi_minero_mom_sa", "IPI Minero (MoM Desestacionalizada)",
            signed_value(match.group(1), match.group(2)), match.group(2), "%",
            normalize_period(text), url("mineria"), "actividad"))

    # Indigencia: "hay 5,6% de hogares por debajo de la línea de indigencia (LI), que incluyen al 7,5% de las personas"
    text = report_text("pobreza")
    match = re.search(r'indigencia.{0,80}?(\d+,\d+)\s*%\s+de\s+las\s+personas', text, re.IGNORECASE | re.DOTALL)
    if match:
        indicators.append(make_indicator(
            "indigencia", "Indigencia (% Personas)", parse_ar_number(match.group(1)), match.group(1), "%",
            normalize_period(text), url("pobreza"), "social"))

    # Salarios: "En julio de 2026, el índice de salarios se incrementó 2,8% mensual y 36,2% interanual.
    #            El indicador acumula una suba de 21,8% con respecto a diciembre de 2025."
    text = report_text("salarios")
    period = normalize_period(text)
    negative = re.search(rf'salarios\s+(?:se\s+)?{NEGATIVE_WORDS}', text, re.IGNORECASE) is not None
    for key, name, pattern in (
        ("salarios_mensual", "Índice de Salarios (Mensual)", r'(-?\d+,\d+)\s*%\s*mensual'),
        ("salarios_interanual", "Índice de Salarios (Interanual)", r'(-?\d+,\d+)\s*%\s*interanual'),
    ):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = parse_ar_number(match.group(1))
            indicators.append(make_indicator(
                key, name, -abs(value) if negative else value, match.group(1), "%",
                period, url("salarios"), "laboral"))
    match = re.search(rf'acumula\s+(?:una\s+)?({CHANGE_WORDS})\s+(?:de\s+)?(\d+,\d+)\s*%', text, re.IGNORECASE)
    if match:
        indicators.append(make_indicator(
            "salarios_acumulado", "Índice de Salarios (Acumulado Año)",
            signed_value(match.group(1), match.group(2)), match.group(2), "%",
            period, url("salarios"), "laboral"))

    # Personal APN: "Al 31 de agosto de 2026, la dotación ... fue de 269.025 personas; esto representa
    #               una caída de 5,8% respecto a igual mes del año anterior"
    text = report_text("personal_apn")
    match = re.search(rf'({CHANGE_WORDS})\s+de\s+(\d+,\d+)\s*%\s+respecto\s+(?:a|al|de)\s+igual\s+mes', text, re.IGNORECASE)
    if match:
        indicators.append(make_indicator(
            "personal_apn_yoy", "Dotación Personal APN (YoY)",
            signed_value(match.group(1), match.group(2)), match.group(2), "%",
            normalize_period(text), url("personal_apn"), "sector_publico"))

    return indicators


def publications_from_reports(reports_by_page) -> List[Dict[str, Any]]:
    """Feed: último informe técnico (con PDF) de cada página, deduplicado por URL."""
    publications = {}
    for reports in reports_by_page.values():
        report = first_report(reports)
        if not report or report["pdf_url"] in publications:
            continue
        description = report["text"].split('Escuchar Dato INDEC')[0].strip()
        publications[report["pdf_url"]] = {
            "title": report["title"][:500] or "Informe técnico INDEC",
            "date": report["date"],
            "source": "INDEC",
            "url": report["pdf_url"],
            "type": "informe",
            "description": description[:300] or "Informe técnico del INDEC",
        }
    return list(publications.values())


async def scrape_indec() -> Dict[str, List[Dict[str, Any]]]:
    """
    Función principal de scraping para INDEC.
    Descarga todos los fragmentos (máx. 4 en paralelo) y extrae tarjetas e informes.
    """
    semaphore = asyncio.Semaphore(4)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=HEADERS) as client:
        async def load(key):
            async with semaphore:
                return key, await fetch_page(client, f"{INDEC_BASE_URL}/{INDEC_PAGES[key]}")

        pages = dict(await asyncio.gather(*(load(key) for key in INDEC_PAGES)))

    cards_by_page = {key: parse_cards(html) for key, html in pages.items() if html}
    reports_by_page = {key: parse_reports(html) for key, html in pages.items() if html}
    report_urls = {
        key: report["pdf_url"]
        for key, reports in reports_by_page.items()
        if (report := first_report(reports))
    }

    result = {
        "indicators": indicators_from_cards(cards_by_page, report_urls)
                      + indicators_from_reports(reports_by_page, report_urls),
        "publications": publications_from_reports(reports_by_page),
    }

    print(f"✅ INDEC: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
