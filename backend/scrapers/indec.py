"""
MacroAR - Scraper INDEC
========================
Scraping de indicadores del INDEC.
Scrapea el homepage (que tiene los indicadores principales) y páginas
específicas para indicadores adicionales.

Indicadores monitoreados:
- IPC (Índice de Precios al Consumidor)
- EMAE (Estimador Mensual de Actividad Económica)
- Desocupación (EPH)
- IPI Manufacturero (Producción Industrial)
- IPI Minero (Producción Industrial Minera)
- ISAC (Actividad de la Construcción)
- Balanza Comercial (Intercambio Comercial)
- UCII (Capacidad Instalada en la Industria)
- Pobreza e Indigencia (EPH)
- ICC (Índice del Costo de la Construcción)
- Índice de Salarios
- Dotación de Personal APN (Administración Pública)
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from utils import clean_numeric_value, safe_text

INDEC_BASE_URL = "https://www.indec.gob.ar"
INDEC_HOME_URL = f"{INDEC_BASE_URL}/"

# URLs específicas para indicadores que no aparecen en el homepage
INDEC_URLS = {
    "balanza_comercial": f"{INDEC_BASE_URL}/indec/web/Nivel4-Tema-3-2-40",
    "ucii": f"{INDEC_BASE_URL}/indec/web/Nivel3-Tema-3-7",
    "pobreza": f"{INDEC_BASE_URL}/indec/web/Nivel3-Tema-4-46",
    "icc": f"{INDEC_BASE_URL}/indec/web/Nivel4-Tema-3-5-33",
    "salarios": f"{INDEC_BASE_URL}/indec/web/Nivel4-Tema-4-31-61",
    "personal_apn": f"{INDEC_BASE_URL}/indec/web/Nivel4-Tema-3-10-102",
}

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


def extract_period_from_text(text: str) -> str:
    """
    Extrae un período (mes/año) de un texto.
    Busca patrones como 'Agosto 2026', 'julio de 2026', 'Q2 2026', etc.
    """
    months = r'(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'
    
    # Patrón: "Mes de Año" o "Mes Año"
    match = re.search(rf'({months})\s+(?:de\s+)?(\d{{4}})', text, re.IGNORECASE)
    if match:
        return f"{match.group(1).capitalize()} {match.group(2)}"
    
    # Patrón: "X trimestre de YYYY" o "QX YYYY"
    match = re.search(r'(\d)(?:er|do|ro|to)?\s*trimestre\s+(?:de\s+)?(\d{4})', text, re.IGNORECASE)
    if match:
        return f"Q{match.group(1)} {match.group(2)}"
    
    match = re.search(r'[Qq](\d)\s*(\d{4})', text)
    if match:
        return f"Q{match.group(1)} {match.group(2)}"
    
    # Patrón: "semestre de YYYY"
    match = re.search(r'(\d)(?:er|do)?\s*semestre\s+(?:de\s+)?(\d{4})', text, re.IGNORECASE)
    if match:
        return f"S{match.group(1)} {match.group(2)}"
    
    # Solo año
    match = re.search(r'(\d{4})', text)
    if match:
        return match.group(1)
    
    return ""


def clean_usd_value(text: str) -> Optional[float]:
    """
    Limpia valores en USD con formatos como:
    - "USD 8.883 millones"
    - "USD 6.696 millones"
    - "8.883 millones"
    Retorna el valor en millones.
    """
    if not text:
        return None
    
    cleaned = text.strip()
    
    # Remover prefijos de moneda
    cleaned = re.sub(r'USD\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'US\$\s*', '', cleaned)
    cleaned = re.sub(r'ARS\s*', '', cleaned)
    cleaned = re.sub(r'\$\s*', '', cleaned)
    
    # Remover sufijos
    cleaned = re.sub(r'\s*millones?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*mil\s*millones?', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    value = clean_numeric_value(cleaned)
    return value


def parse_home_indicators(html: str) -> List[Dict[str, Any]]:
    """
    Extrae los indicadores principales del homepage del INDEC.
    La homepage muestra bloques con: valor, nombre del indicador, período, y link al PDF.
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link.get('href', '')
        text = safe_text(link)
        
        if not text or len(text) < 5:
            continue
        
        # Solo procesar links a informes de prensa (PDFs)
        if '/uploads/informesdeprensa/' not in href or not href.endswith('.pdf'):
            continue
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) < 2:
            continue
        
        # Buscar valor numérico y período en las líneas
        value_text = ''
        period = ''
        name = ''
        
        for line in lines:
            # Buscar línea con valor numérico (contiene % o es un número con coma/punto)
            if re.search(r'-?\d+[.,]\d+\s*%?', line):
                value_text = line
            # Buscar período (mes + año)
            elif re.search(r'(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|trimestre|semestre)\s+\d{4}', line, re.IGNORECASE):
                period = extract_period_from_text(line)
            # El resto es el nombre
            elif len(line) > 3 and not line.startswith('http') and not line.startswith('!'):
                name = line
        
        if not value_text:
            continue
        
        value = clean_numeric_value(value_text)
        if value is None:
            continue
        
        # Determinar el indicador por el nombre o URL
        href_lower = href.lower()
        name_lower = name.lower()
        
        indicator_key = None
        indicator_name = name
        category = 'actividad'
        unit = '%'
        
        if 'ipc' in href_lower or ('precios' in name_lower and 'consumidor' in name_lower):
            indicator_key = 'ipc_mensual'
            indicator_name = 'IPC Mensual (Nacional)'
            category = 'inflacion'
        elif 'emae' in href_lower or 'actividad económica' in name_lower:
            indicator_key = 'emae_mom_sa'
            indicator_name = 'EMAE (MoM Desestacionalizada)'
            category = 'actividad'
        elif 'trabajo' in href_lower or 'desocupacion' in href_lower or 'desocupación' in name_lower:
            indicator_key = 'desocupacion'
            indicator_name = 'Tasa de Desocupación'
            category = 'laboral'
        elif 'ipi' in href_lower and 'manufacturero' in href_lower:
            indicator_key = 'ipi_manufacturero_mom_sa'
            indicator_name = 'IPI Manufacturero (MoM Desestacionalizada)'
            category = 'actividad'
        elif 'ipi' in href_lower and 'minero' in href_lower:
            indicator_key = 'ipi_minero_mom_sa'
            indicator_name = 'IPI Minero (MoM Desestacionalizada)'
            category = 'actividad'
        elif 'isac' in href_lower or ('construcci' in name_lower and 'actividad' in name_lower):
            indicator_key = 'isac_mom_sa'
            indicator_name = 'ISAC Construcción (MoM Desestacionalizada)'
            category = 'actividad'
        
        if indicator_key:
            full_url = href if href.startswith('http') else f"{INDEC_BASE_URL}{href}"
            indicators.append({
                "indicator_key": indicator_key,
                "name": indicator_name,
                "value": value,
                "value_raw": value_text,
                "unit": unit,
                "period": period,
                "source": "INDEC",
                "source_url": full_url,
                "category": category
            })
    
    return indicators


async def scrape_balanza_comercial(html: str) -> List[Dict[str, Any]]:
    """
    Extrae la variación interanual (YoY) del saldo de la balanza comercial.
    
    Formato esperado:
    "El superávit comercial alcanzó USD 2.187 millones en agosto de 2026,
     lo que representa una variación de X% respecto a igual mes del año anterior."
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar variación interanual del saldo/superávit/déficit
    variacion_saldo_patterns = [
        r'saldo\s*(?:comercial)?.*?variación.*?(\d+[.,]\d+)\s*%',
        r'superávit.*?variación.*?(\d+[.,]\d+)\s*%',
        r'balanza.*?variación.*?(\d+[.,]\d+)\s*%',
        r'superávit\s*(?:comercial)?.*?(\d+[.,]\d+)\s*%.*?(?:interanual|anual|respecto)',
        r'(\d+[.,]\d+)\s*%.*?(?:interanual|anual).*?(?:superávit|saldo|balanza)',
    ]
    
    for pattern in variacion_saldo_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and abs(value) < 200:  # Variación razonable
                # Determinar signo basado en contexto
                context = all_text[max(0, match.start()-100):match.end()]
                is_negative = any(word in context.lower() for word in ['caída', 'baja', 'reducción', 'disminución', 'retroceso'])
                if is_negative:
                    value = -value
                
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "balanza_saldo_yoy",
                    "name": "Saldo Comercial (YoY)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["balanza_comercial"],
                    "category": "comercio_exterior"
                })
                break
    
    return indicators


async def scrape_ucii(html: str) -> List[Dict[str, Any]]:
    """
    Extrae la Utilización de la Capacidad Instalada en la Industria (UCII).
    Es un porcentaje que mide la proporción utilizada de la capacidad productiva.
    
    Formato esperado: "La UCII se ubicó en X,X% en [período]"
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar el valor de UCII
    ucii_patterns = [
        r'(?:UCII|capacidad\s*instalada).*?(\d+[.,]\d+)\s*%',
        r'utilizaci[oó]n.*?capacidad.*?(\d+[.,]\d+)\s*%',
        r'capacidad\s*instalada.*?(\d+[.,]\d+)\s*%',
        r'(\d+[.,]\d+)\s*%.*?(?:UCII|capacidad\s*instalada)',
    ]
    
    for pattern in ucii_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            # UCII típicamente está entre 40% y 80%
            if value is not None and 30 < value < 90:
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "ucii",
                    "name": "UCII (Capacidad Instalada Industria)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["ucii"],
                    "category": "actividad"
                })
                break
    
    return indicators


async def scrape_pobreza(html: str) -> List[Dict[str, Any]]:
    """
    Extrae datos de Pobreza e Indigencia de la EPH.
    
    Formato esperado:
    "El porcentaje de hogares por debajo de la línea de pobreza (LP) 
     alcanzó el 24,4%. Dentro de estos hogares reside el 32,3% de las personas."
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar pobreza de personas
    pobreza_persona_patterns = [
        r'pobreza\s+(?:alcanz[oó]|lleg[oó]|fue)\s+(?:al\s+)?(\d+[.,]\d+)\s*%\s*(?:de\s+las?\s+)?personas',
        r'(?:del\s+)?(\d+[.,]\d+)\s*%\s*de\s+las?\s+personas.*?pobreza',
        r'personas\s+(?:bajo|por debajo).*?l[ií]nea.*?pobreza.*?(\d+[.,]\d+)\s*%',
        r'pobreza.*?(\d+[.,]\d+)\s*%\s*de\s+(?:la\s+)?poblaci',
    ]
    
    for pattern in pobreza_persona_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 10 < value < 60:  # Rango razonable para pobreza
                period = extract_period_from_text(all_text[:1000])
                indicators.append({
                    "indicator_key": "pobreza_personas",
                    "name": "Pobreza (% Personas)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["pobreza"],
                    "category": "social"
                })
                break
    
    # Buscar pobreza de hogares
    pobreza_hogar_patterns = [
        r'(?:hogares|porcentaje de hogares).*?(?:l[ií]nea\s+de\s+)?pobreza.*?(\d+[.,]\d+)\s*%',
        r'pobreza.*?(\d+[.,]\d+)\s*%\s*(?:de\s+)?(?:los\s+)?hogares',
        r'(\d+[.,]\d+)\s*%.*?hogares.*?pobreza',
    ]
    
    for pattern in pobreza_hogar_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 5 < value < 50:
                period = extract_period_from_text(all_text[:1000])
                indicators.append({
                    "indicator_key": "pobreza_hogares",
                    "name": "Pobreza (% Hogares)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["pobreza"],
                    "category": "social"
                })
                break
    
    # Buscar indigencia
    indigencia_patterns = [
        r'indigencia\s+(?:alcanz[oó]|lleg[oó]|fue)\s+(?:al\s+)?(\d+[.,]\d+)\s*%',
        r'indigencia.*?(\d+[.,]\d+)\s*%\s*(?:de\s+)?(?:la\s+)?poblaci',
        r'(\d+[.,]\d+)\s*%.*?indigencia',
    ]
    
    for pattern in indigencia_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 1 < value < 30:
                period = extract_period_from_text(all_text[:1000])
                indicators.append({
                    "indicator_key": "indigencia",
                    "name": "Indigencia (% Personas)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["pobreza"],
                    "category": "social"
                })
                break
    
    return indicators


async def scrape_icc(html: str) -> List[Dict[str, Any]]:
    """
    Extrae el Índice del Costo de la Construcción (ICC).
    
    Formato esperado:
    "El nivel general del índice del costo de la construcción (ICC) 
     en el Gran Buenos Aires correspondiente a agosto de 2026 
     registra una suba de 2,X%."
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar variación del ICC
    icc_patterns = [
        r'(?:ICC|costo\s+(?:de\s+la\s+)?construcci[oó]n).*?(?:suba|baja|variación|aumento|incremento|descenso)\s+(?:de\s+)?(\d+[.,]\d+)\s*%',
        r'(?:suba|baja|variación|aumento|incremento)\s+(?:de\s+)?(\d+[.,]\d+)\s*%.*?(?:ICC|costo.*?construcci)',
        r'costo.*?construcci.*?(\d+[.,]\d+)\s*%',
    ]
    
    for pattern in icc_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 0 < value < 50:  # Variación mensual razonable
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "icc",
                    "name": "ICC (Costo de la Construcción)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["icc"],
                    "category": "construccion"
                })
                break
    
    return indicators


async def scrape_salarios(html: str) -> List[Dict[str, Any]]:
    """
    Extrae el Índice de Salarios.
    
    Formato esperado:
    "En julio de 2026, el índice de salarios se incrementó 2,8% mensual 
     y 36,2% interanual. El indicador acumula una suba de 21,8% con 
     respecto a diciembre de 2025."
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar variación mensual
    mensual_patterns = [
        r'[íi]ndice\s+(?:de\s+)?salarios.*?(\d+[.,]\d+)\s*%\s*mensual',
        r'salarios.*?(?:increment[oó]|subi[oó]|creci[oó])\s+(\d+[.,]\d+)\s*%\s*mensual',
        r'(\d+[.,]\d+)\s*%\s*mensual.*?salarios',
    ]
    
    for pattern in mensual_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 0 < value < 30:
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "salarios_mensual",
                    "name": "Índice de Salarios (Mensual)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["salarios"],
                    "category": "laboral"
                })
                break
    
    # Buscar variación interanual
    interanual_patterns = [
        r'[íi]ndice\s+(?:de\s+)?salarios.*?(\d+[.,]\d+)\s*%\s*interanual',
        r'salarios.*?(\d+[.,]\d+)\s*%\s*interanual',
        r'(\d+[.,]\d+)\s*%\s*interanual.*?salarios',
    ]
    
    for pattern in interanual_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 10 < value < 200:
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "salarios_interanual",
                    "name": "Índice de Salarios (Interanual)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["salarios"],
                    "category": "laboral"
                })
                break
    
    # Buscar acumulado anual
    acumulado_patterns = [
        r'acumula\s+(?:una\s+)?suba\s+(?:de\s+)?(\d+[.,]\d+)\s*%',
        r'acumulado.*?(\d+[.,]\d+)\s*%.*?(?:diciembre|respecto)',
    ]
    
    for pattern in acumulado_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 5 < value < 100:
                period = extract_period_from_text(all_text[:500])
                indicators.append({
                    "indicator_key": "salarios_acumulado",
                    "name": "Índice de Salarios (Acumulado Año)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["salarios"],
                    "category": "laboral"
                })
                break
    
    return indicators


async def scrape_personal_apn(html: str) -> List[Dict[str, Any]]:
    """
    Extrae la variación interanual (YoY) de la Dotación de Personal APN.
    
    Formato esperado:
    "Al 31 de agosto de 2026, la dotación de personal fue de 269.025 personas;
     esto representa una caída interanual de X%."
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar variación interanual del personal
    variacion_patterns = [
        r'(?:representa|implica)\s+(?:una\s+)?(?:ca[ií]da|baja|reducci[oó]n|disminuci[oó]n)\s+(?:interanual\s+)?(?:de\s+)?(\d+[.,]\d+)\s*%',
        r'(?:ca[ií]da|baja|reducci[oó]n)\s+(?:interanual\s+)?(?:de\s+)?(\d+[.,]\d+)\s*%.*?(?:personal|dotaci)',
        r'(?:aumento|crecimiento|suba)\s+(?:interanual\s+)?(?:de\s+)?(\d+[.,]\d+)\s*%.*?(?:personal|dotaci)',
        r'(\d+[.,]\d+)\s*%.*?(?:interanual|anual).*?(?:personal|dotaci)',
    ]
    
    for pattern in variacion_patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and 0 < value < 30:
                # Determinar si es positivo o negativo
                context = all_text[max(0, match.start()-100):match.end()]
                is_negative = any(word in context.lower() for word in ['caída', 'baja', 'reducción', 'disminución', 'caida'])
                if is_negative:
                    value = -value
                
                period_match = re.search(r'Al\s+(\d+)\s+de\s+(\w+)\s+de\s+(\d{4})', all_text)
                if period_match:
                    period = f"{period_match.group(2).capitalize()} {period_match.group(3)}"
                else:
                    period = extract_period_from_text(all_text[:500])
                
                indicators.append({
                    "indicator_key": "personal_apn_yoy",
                    "name": "Dotación Personal APN (YoY)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": period,
                    "source": "INDEC",
                    "source_url": INDEC_URLS["personal_apn"],
                    "category": "sector_publico"
                })
                break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones/noticias del homepage del INDEC."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    all_links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in all_links:
        href = link.get('href', '')
        text = safe_text(link)
        
        if '/uploads/informesdeprensa/' in href and href.endswith('.pdf'):
            if href not in seen_urls and len(text) > 10:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{INDEC_BASE_URL}{href}"
                
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                title = lines[0] if lines else 'Informe INDEC'
                description = ' '.join(lines[1:]) if len(lines) > 1 else ''
                
                publications.append({
                    "title": title[:500],
                    "date": datetime.now(),
                    "source": "INDEC",
                    "url": full_url,
                    "type": "informe",
                    "description": description[:300] if description else "Publicación del INDEC"
                })
    
    return publications[:15]


async def scrape_indec() -> Dict[str, List[Dict[str, Any]]]:
    """
    Función principal de scraping para INDEC.
    Scrapea el homepage + páginas específicas para indicadores adicionales.
    """
    result = {"indicators": [], "publications": []}
    
    # 1. Scrapear homepage (indicadores principales)
    html = await fetch_page(INDEC_HOME_URL)
    if html:
        result["indicators"].extend(parse_home_indicators(html))
        result["publications"].extend(parse_publications(html))
    
    # 2. Scrapear indicadores adicionales en páginas específicas
    # Balanza Comercial
    balanza_html = await fetch_page(INDEC_URLS["balanza_comercial"])
    if balanza_html:
        result["indicators"].extend(await scrape_balanza_comercial(balanza_html))
    
    # UCII
    ucii_html = await fetch_page(INDEC_URLS["ucii"])
    if ucii_html:
        result["indicators"].extend(await scrape_ucii(ucii_html))
    
    # Pobreza
    pobreza_html = await fetch_page(INDEC_URLS["pobreza"])
    if pobreza_html:
        result["indicators"].extend(await scrape_pobreza(pobreza_html))
    
    # ICC (Costo Construcción)
    icc_html = await fetch_page(INDEC_URLS["icc"])
    if icc_html:
        result["indicators"].extend(await scrape_icc(icc_html))
    
    # Salarios
    salarios_html = await fetch_page(INDEC_URLS["salarios"])
    if salarios_html:
        result["indicators"].extend(await scrape_salarios(salarios_html))
    
    # Personal APN
    apn_html = await fetch_page(INDEC_URLS["personal_apn"])
    if apn_html:
        result["indicators"].extend(await scrape_personal_apn(apn_html))
    
    # Deduplicar indicadores por key (quedarse con el último)
    seen_keys = {}
    for ind in result["indicators"]:
        seen_keys[ind["indicator_key"]] = ind
    result["indicators"] = list(seen_keys.values())
    
    print(f"✅ INDEC: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
