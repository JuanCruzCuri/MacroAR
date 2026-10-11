"""
MacroAR - Scraper CIF-UTDT (Centro de Investigación en Finanzas)
=================================================================
Scraping de indicadores del CIF de la Universidad Torcuato Di Tella:
- Brecha cambiaria
- Riesgo país
- Resultado fiscal
- Reportes semanales
"""
import httpx
import re
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import clean_numeric_value, safe_text

CIF_BASE_URL = "https://www.utdt.edu/centro-investigacion-finanzas"
CIF_REPORTS_URL = "https://www.utdt.edu/centro-investigacion-finanzas/publicaciones"

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
        print(f"⚠️ Error fetching CIF {url}: {e}")
        return None


def parse_indicators(html: str) -> List[Dict[str, Any]]:
    """Extrae indicadores del CIF."""
    indicators = []
    soup = BeautifulSoup(html, 'lxml')
    all_text = soup.get_text()
    
    # Buscar brecha cambiaria
    brecha_patterns = [
        r'[Bb]recha\s*(?:cambiaria)?.*?(\d+[.,]\d+)\s*%?',
        r'[Dd]iferencial.*?(\d+[.,]\d+)',
    ]
    for pattern in brecha_patterns:
        match = re.search(pattern, all_text, re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None:
                indicators.append({
                    "indicator_key": "brecha_cambiaria",
                    "name": "Brecha Cambiaria",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "%",
                    "period": datetime.now().strftime("%B %Y"),
                    "source": "CIF-UTDT",
                    "source_url": CIF_BASE_URL,
                    "category": "cambiario"
                })
                break
    
    # Buscar riesgo país
    riesgo_patterns = [
        r'[Rr]iesgo\s*[Pp]a[íi]s.*?(\d{3,5})',
        r'EMBI.*?(\d{3,5})',
    ]
    for pattern in riesgo_patterns:
        match = re.search(pattern, all_text, re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None:
                indicators.append({
                    "indicator_key": "riesgo_pais",
                    "name": "Riesgo País",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "pbs",
                    "period": datetime.now().strftime("%B %Y"),
                    "source": "CIF-UTDT",
                    "source_url": CIF_BASE_URL,
                    "category": "financiero"
                })
                break
    
    # Buscar resultado fiscal
    fiscal_patterns = [
        r'[Rr]esultado\s*[Ff]iscal.*?(-?\d+[.,]\d+)\s*%?',
        r'[Ss]uper[áa]vit.*?(\d+[.,]\d+)',
        r'[Dd][ée]ficit.*?(\d+[.,]\d+)',
    ]
    for pattern in fiscal_patterns:
        match = re.search(pattern, all_text, re.DOTALL)
        if match:
            value = clean_numeric_value(match.group(1))
            if value is not None:
                indicators.append({
                    "indicator_key": "resultado_fiscal",
                    "name": "Resultado Fiscal (Sector Público)",
                    "value": value,
                    "value_raw": match.group(1),
                    "unit": "% PBI",
                    "period": datetime.now().strftime("%B %Y"),
                    "source": "CIF-UTDT",
                    "source_url": CIF_BASE_URL,
                    "category": "fiscal"
                })
                break
    
    return indicators


def parse_publications(html: str) -> List[Dict[str, Any]]:
    """Extrae publicaciones del CIF."""
    publications = []
    soup = BeautifulSoup(html, 'lxml')
    
    # Buscar artículos/publicaciones
    articles = soup.find_all(['article', 'div'], class_=re.compile(r'publicacion|reporte|articulo|post|entry', re.I))
    
    if not articles:
        articles = soup.find_all('article')
    
    for article in articles[:10]:
        title_elem = article.find(['h2', 'h3', 'h4', 'a'])
        if title_elem:
            title = safe_text(title_elem)
            link = article.find('a', href=True)
            url = link['href'] if link else CIF_BASE_URL
            
            if not url.startswith('http'):
                url = f"https://www.utdt.edu{url}"
            
            # Intentar extraer fecha
            date_elem = article.find(['time', 'span'], class_=re.compile(r'date|fecha|time', re.I))
            pub_date = None
            if date_elem:
                date_text = date_elem.get('datetime', safe_text(date_elem))
                try:
                    pub_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
                except:
                    pub_date = datetime.now()
            else:
                pub_date = datetime.now()
            
            # Descripción
            desc_elem = article.find(['p', 'div'], class_=re.compile(r'description|excerpt|summary|content', re.I))
            description = safe_text(desc_elem) if desc_elem else ""
            
            if len(title) > 5:
                publications.append({
                    "title": title[:500],
                    "date": pub_date,
                    "source": "CIF-UTDT",
                    "url": url,
                    "type": "reporte",
                    "description": description[:300] if description else "Reporte del Centro de Investigación en Finanzas - UTDT"
                })
    
    return publications


async def scrape_cif() -> Dict[str, List[Dict[str, Any]]]:
    """Función principal de scraping para CIF-UTDT."""
    result = {"indicators": [], "publications": []}
    
    html = await fetch_page(CIF_BASE_URL)
    if html:
        result["indicators"] = parse_indicators(html)
        result["publications"] = parse_publications(html)
    
    # También intentar la página de publicaciones
    reports_html = await fetch_page(CIF_REPORTS_URL)
    if reports_html:
        result["publications"].extend(parse_publications(reports_html))
    
    # Deduplicar publicaciones por URL
    seen_urls = set()
    unique_publications = []
    for pub in result["publications"]:
        if pub["url"] not in seen_urls:
            seen_urls.add(pub["url"])
            unique_publications.append(pub)
    result["publications"] = unique_publications[:10]
    
    print(f"✅ CIF-UTDT: {len(result['indicators'])} indicadores, {len(result['publications'])} publicaciones")
    return result
