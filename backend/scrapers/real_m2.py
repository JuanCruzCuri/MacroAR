"""
MacroAR - Scraper Real M2 Report (UCEMA)
==========================================
Scraping del reporte de M2 Real de la Universidad del CEMA.
IMPORTANTE: El "M2 Real" de UCEMA es un índice de precios de metros
cuadrados de departamentos en CABA (no es el agregado monetario M2).
URL: https://ucema.edu.ar/indices-y-bases-de-datos
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

UCEMA_BASE_URL = "https://ucema.edu.ar"
UCEMA_INDICES_URL = f"{UCEMA_BASE_URL}/indices-y-bases-de-datos"

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
    """
    Extrae el indicador de M2 Real (metro cuadrado real) de UCEMA.
    La página tiene una estructura con:
    - "Cifra destacada": valor del índice promedio
    - "Cifra destacada 2": variación acumulada
    - "Mes/Año": período
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar la sección de M2 Real
    # Estructura: "Cifra destacada" seguido del valor
    cifra_destacada = soup.find_all(string=re.compile(r'Cifra destacada', re.I))
    
    if cifra_destacada:
        for elem in cifra_destacada:
            parent = elem.find_parent()
            if parent:
                # Buscar el siguiente elemento con un valor numérico
                next_elem = parent.find_next_sibling()
                if next_elem:
                    text = safe_text(next_elem)
                    value = clean_numeric_value(text)
                    if value is not None:
                        # Determinar si es índice promedio o variación
                        label = safe_text(parent)
                        if 'promedio' in label.lower() or 'indice' in label.lower():
                            indicators.append({
                                "indicator_key": "m2_real_indice",
                                "name": "M2 Real — Índice M² CABA",
                                "value": value,
                                "value_raw": text,
                                "unit": "%",
                                "period": "",  # Se completa abajo
                                "source": "UCEMA",
                                "source_url": UCEMA_INDICES_URL,
                                "category": "inmobiliario"
                            })
                        elif 'variación' in label.lower() or 'acumulada' in label.lower():
                            indicators.append({
                                "indicator_key": "m2_real_acumulado",
                                "name": "M2 Real — Variación Acumulada CABA",
                                "value": value,
                                "value_raw": text,
                                "unit": "%",
                                "period": "",
                                "source": "UCEMA",
                                "source_url": UCEMA_INDICES_URL,
                                "category": "inmobiliario"
                            })
    
    # Buscar período (Mes/Año)
    mes_anio = re.search(r'(Mes/Año|Período).*?(\w+\s+\d{4})', all_text, re.DOTALL | re.IGNORECASE)
    if mes_anio and indicators:
        period = mes_anio.group(2).strip()
        for ind in indicators:
            ind["period"] = period
    
    # Fallback: buscar valores en texto general
    if not indicators:
        # Buscar patrón "0,XX%" que es el índice promedio
        match = re.search(r'(\d+[.,]\d+)\s*%', all_text)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None and value < 5:
                indicators.append({
                    "indicator_key": "m2_real_indice",
                    "name": "M2 Real — Índice M² CABA",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": datetime.now().strftime("%B %Y"),
                    "source": "UCEMA",
                    "source_url": UCEMA_INDICES_URL,
                    "category": "inmobiliario"
                })
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones del M2 Real de UCEMA."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar links a PDFs de M2 Real
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = safe_text(link)
        
        if ('m2' in href.lower() or 'm2' in title.lower() or 
            'metro' in title.lower() or 'real' in title.lower()):
            if href not in seen_urls and ('pdf' in href.lower() or 'm2-' in href.lower()):
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{UCEMA_BASE_URL}{href}"
                
                pub_title = title if len(title) > 5 else "Informe M2 Real - UCEMA"
                
                publications.append({
                    "title": pub_title[:500],
                    "date": datetime.now(),
                    "source": "UCEMA",
                    "url": full_url,
                    "type": "reporte",
                    "description": "Informe M2 Real de la Universidad del CEMA. Índice de precios reales de metros cuadrados de departamentos en CABA."
                })
    
    return publications[:5]


async def scrape_real_m2() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para Real M2 Report (UCEMA)."""
    result = {"indicators": [], "publications": []}
    
    html = await fetch_page(UCEMA_INDICES_URL)
    if html:
        result["indicators"] = parse_real_m2(html)
        result["publications"] = parse_publications(html)
    
    # Si no encontramos datos en la página de índices, intentar la página específica del último informe
    if not result["indicators"]:
        # Buscar el link al último informe M2
        if html:
            soup = BeautifulSoup(html, 'lxml')
            m2_links = soup.find_all('a', href=re.compile(r'm2-\d+'))
            if m2_links:
                last_m2_url = m2_links[0].get('href', '')
                if last_m2_url:
                    full_url = last_m2_url if last_m2_url.startswith('http') else f"{UCEMA_BASE_URL}{last_m2_url}"
                    m2_html = await fetch_page(full_url)
                    if m2_html:
                        result["indicators"] = parse_real_m2(m2_html)
    
    print(f"✅ UCEMA Real M2: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
