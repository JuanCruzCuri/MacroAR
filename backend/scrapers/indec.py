"""
MacroAR - Scraper INDEC
========================
Scraping de indicadores principales del INDEC:
- IPC (Índice de Precios al Consumidor)
- EMAE (Estimador Mensual de Actividad Económica)
- Desocupación
- Salarios
"""
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, parse_argentine_date, safe_text

INDEC_BASE_URL = "https://www.indec.gob.ar"
INDEC_IPC_URL = f"{INDEC_BASE_URL}/indec/web/Institucional-Indec-IPC"
INDEC_EMAE_URL = f"{INDEC_BASE_URL}/indec/web/Institucional-Indec-EMAE"
INDEC_DESOCUPACION_URL = f"{INDEC_BASE_URL}/indec/web/Institucional-Indec-TasaDesocupacion"
INDEC_SALARIOS_URL = f"{INDEC_BASE_URL}/indec/web/Institucional-Indec-IS"

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


def parse_ipc(html: str) -> List[Dict[str, Any]]:
    """
    Extrae datos del IPC desde la página del INDEC.
    Busca la tabla o sección con el último dato publicado.
    """
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Estrategia 1: Buscar tablas con datos de IPC
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) >= 2:
            # Buscar headers relevantes
            headers = [safe_text(th) for th in rows[0].find_all(['th', 'td'])]
            
            # Si encontramos una tabla con datos de variación
            for row in rows[1:]:
                cells = [safe_text(td) for td in row.find_all(['td', 'th'])]
                if len(cells) >= 2:
                    # Intentar extraer período y valor
                    period_text = cells[0]
                    value_text = cells[1] if len(cells) > 1 else ''
                    
                    value = clean_numeric_value(value_text)
                    if value is not None and value > 0:
                        indicators.append({
                            "indicator_key": "ipc_mensual",
                            "name": "IPC Mensual",
                            "value": value,
                            "value_raw": value_text,
                            "unit": "%",
                            "period": period_text,
                            "source": "INDEC",
                            "source_url": INDEC_IPC_URL,
                            "category": "inflacion"
                        })
                        break  # Solo el último dato
    
    # Estrategia 2: Buscar en elementos con clases específicas
    if not indicators:
        # Buscar elementos que contengan "IPC" y valores numéricos
        all_text = soup.get_text()
        import re
        # Buscar patrones como "4,1%" o "Variación mensual: 4,1"
        ipc_patterns = [
            r'IPC.*?(\d+[.,]\d+)\s*%',
            r'Variación\s+mensual.*?(\d+[.,]\d+)',
            r'Nivel\s+general.*?(\d+[.,]\d+)',
        ]
        for pattern in ipc_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
            if match:
                value = clean_numeric_value(match.group(1))
                if value:
                    indicators.append({
                        "indicator_key": "ipc_mensual",
                        "name": "IPC Mensual",
                        "value": value,
                        "value_raw": match.group(1),
                        "unit": "%",
                        "period": datetime.now().strftime("%B %Y"),
                        "source": "INDEC",
                        "source_url": INDEC_IPC_URL,
                        "category": "inflacion"
                    })
                    break
    
    return indicators


def parse_emae(html: str) -> List[Dict[str, Any]]:
    """Extrae datos del EMAE."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    
    all_text = soup.get_text()
    import re
    
    # Buscar variación mensual del EMAE
    patterns = [
        r'EMAE.*?variación.*?(\d+[.,]\d+)\s*%',
        r'Actividad.*?(\d+[.,]\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, all_text, re.IGNORECASE | re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None:
                indicators.append({
                    "indicator_key": "emae",
                    "name": "EMAE (Actividad Económica)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": "",
                    "source": "INDEC",
                    "source_url": INDEC_EMAE_URL,
                    "category": "actividad"
                })
                break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae lista de publicaciones del INDEC."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar links a informes/publicaciones
    links = soup.find_all('a', href=True)
    seen_urls = set()
    
    for link in links:
        href = link.get('href', '')
        title = safe_text(link)
        
        # Filtrar solo links a publicaciones/informes
        if any(keyword in href.lower() for keyword in ['ipc', 'emae', 'desocupacion', 'salario', 'informe', 'publicacion']):
            if href not in seen_urls and len(title) > 10:
                seen_urls.add(href)
                full_url = href if href.startswith('http') else f"{INDEC_BASE_URL}{href}"
                
                publications.append({
                    "title": title[:500],
                    "date": datetime.now(),
                    "source": "INDEC",
                    "url": full_url,
                    "type": "informe",
                    "description": f"Publicación del INDEC: {title[:200]}"
                })
    
    return publications[:10]  # Limitar a 10 publicaciones


async def scrape_indec() -> Dict[str, List[Dict[str, Any]]]:
    """
    Función principal de scraping para INDEC.
    Retorna indicadores y publicaciones.
    """
    result = {"indicators": [], "publications": []}
    
    # Scrapear IPC
    ipc_html = await fetch_page(INDEC_IPC_URL)
    if ipc_html:
        result["indicators"].extend(parse_ipc(ipc_html))
        result["publications"].extend(parse_publications(ipc_html))
    
    # Scrapear EMAE
    emae_html = await fetch_page(INDEC_EMAE_URL)
    if emae_html:
        result["indicators"].extend(parse_emae(emae_html))
    
    print(f"✅ INDEC: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
