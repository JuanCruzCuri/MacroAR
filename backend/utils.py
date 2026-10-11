"""
MacroAR - Utilidades de Limpieza de Datos
==========================================
Funciones robustas para limpiar datos extraídos de HTML/PDFs:
- Manejo de símbolos ($, %, comas)
- Separadores de miles/decimales (formato argentino)
- Fechas inconsistentes
- Valores nulos
"""
import re
from datetime import datetime
from typing import Optional, Tuple


def clean_numeric_value(raw_value: str) -> Optional[float]:
    """
    Limpia un valor numérico de strings con formato argentino.
    
    Maneja:
    - "$1.234,56" → 1234.56
    - "1.234,56%" → 1234.56
    - "1,234.56" → 1234.56 (formato internacional)
    - "1234" → 1234.0
    - "N/D", "-", "" → None
    
    Formato argentino: punto = miles, coma = decimal
    Formato internacional: coma = miles, punto = decimal
    """
    if raw_value is None:
        return None
    
    # Limpiar espacios y caracteres no relevantes
    cleaned = str(raw_value).strip()
    
    # Valores nulos o no disponibles
    if cleaned in ('', '-', 'N/D', 'n/d', 'N/A', 'n/a', 's/d', 'S/D', '—', '–'):
        return None
    
    # Remover símbolos monetarios y porcentajes
    cleaned = cleaned.replace('$', '').replace('%', '').replace('US$', '')
    cleaned = cleaned.replace('ARS', '').replace('USD', '').strip()
    
    # Remover espacios internos
    cleaned = cleaned.replace(' ', '')
    
    try:
        # Detectar formato argentino vs internacional
        # Formato argentino: 1.234,56 (punto=miles, coma=decimal)
        # Formato internacional: 1,234.56 (coma=miles, punto=decimal)
        
        has_comma = ',' in cleaned
        has_dot = '.' in cleaned
        
        if has_comma and has_dot:
            # Determinar cuál es el separador decimal (el último)
            last_comma = cleaned.rfind(',')
            last_dot = cleaned.rfind('.')
            
            if last_comma > last_dot:
                # Formato argentino: 1.234,56
                cleaned = cleaned.replace('.', '')  # Remover separador de miles
                cleaned = cleaned.replace(',', '.')  # Coma decimal → punto
            else:
                # Formato internacional: 1,234.56
                cleaned = cleaned.replace(',', '')  # Remover separador de miles
        
        elif has_comma and not has_dot:
            # Solo coma: podría ser decimal argentino o miles
            # Si hay un solo dígito después de la coma, es decimal
            parts = cleaned.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Probablemente decimal: "4,1" → 4.1
                cleaned = cleaned.replace(',', '.')
            elif len(parts) == 2 and len(parts[1]) == 3:
                # Probablemente miles: "1,234" → 1234
                cleaned = cleaned.replace(',', '')
            else:
                # Múltiples comas = separadores de miles
                cleaned = cleaned.replace(',', '')
        
        elif has_dot and not has_comma:
            # Solo punto: podría ser decimal o miles
            parts = cleaned.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Decimal: "4.1" → 4.1 (ya está bien)
                pass
            elif len(parts) == 2 and len(parts[1]) == 3:
                # Ambiguo, asumimos decimal si es < 1000 antes del punto
                if len(parts[0]) <= 3:
                    pass  # "1.234" → 1.234 como decimal
                else:
                    cleaned = cleaned.replace('.', '')  # Miles
            else:
                # Múltiples puntos = separadores de miles
                cleaned = cleaned.replace('.', '')
        
        result = float(cleaned)
        return result
        
    except (ValueError, TypeError):
        return None


def clean_percentage(raw_value: str) -> Tuple[Optional[float], str]:
    """
    Extrae un valor numérico de un string con porcentaje.
    Retorna (valor, unidad).
    """
    if raw_value is None:
        return None, '%'
    
    cleaned = str(raw_value).strip()
    has_percent = '%' in cleaned
    value = clean_numeric_value(cleaned)
    unit = '%' if has_percent else ''
    
    return value, unit


def parse_argentine_date(date_str: str) -> Optional[datetime]:
    """
    Parsea fechas en formatos comunes argentinos.
    
    Maneja:
    - "Mayo 2025"
    - "mayo de 2025"
    - "15/06/2025"
    - "2025-06-15"
    - "Junio 2025"
    - "Q1 2025" → primer día del trimestre
    - "1er trimestre 2025"
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip()
    
    # Meses en español
    months_es = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    try:
        # Formato: "Mayo 2025" o "mayo de 2025"
        for month_name, month_num in months_es.items():
            pattern = rf'{month_name}\s*(?:de\s*)?(\d{{4}})'
            match = re.search(pattern, date_str.lower())
            if match:
                year = int(match.group(1))
                return datetime(year, month_num, 1)
        
        # Formato: "Q1 2025" o "1er trimestre 2025"
        quarter_match = re.search(r'[Qq](\d)\s*(\d{4})', date_str)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            month = (quarter - 1) * 3 + 1
            return datetime(year, month, 1)
        
        # Formato: "1er trimestre 2025"
        trimester_match = re.search(r'(\d)(?:er|do|ro)?\s*trimestre\s*(\d{4})', date_str.lower())
        if trimester_match:
            quarter = int(trimester_match.group(1))
            year = int(trimester_match.group(2))
            month = (quarter - 1) * 3 + 1
            return datetime(year, month, 1)
        
        # Formato DD/MM/YYYY
        dmy_match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_str)
        if dmy_match:
            day, month, year = int(dmy_match.group(1)), int(dmy_match.group(2)), int(dmy_match.group(3))
            return datetime(year, month, day)
        
        # Formato YYYY-MM-DD
        iso_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
        if iso_match:
            year, month, day = int(iso_match.group(1)), int(iso_match.group(2)), int(iso_match.group(3))
            return datetime(year, month, day)
        
        # Formato: Solo mes y año (buscar número de mes)
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
            for month_name, month_num in months_es.items():
                if month_name in date_str.lower():
                    return datetime(year, month_num, 1)
        
        return None
        
    except (ValueError, TypeError):
        return None


def extract_text_between(html_text: str, start_marker: str, end_marker: str) -> Optional[str]:
    """Extrae texto entre dos marcadores en un string HTML."""
    try:
        start_idx = html_text.find(start_marker)
        if start_idx == -1:
            return None
        start_idx += len(start_marker)
        end_idx = html_text.find(end_marker, start_idx)
        if end_idx == -1:
            return None
        return html_text[start_idx:end_idx].strip()
    except Exception:
        return None


def safe_text(element) -> str:
    """Extrae texto de un elemento BeautifulSoup de forma segura."""
    if element is None:
        return ''
    try:
        return element.get_text(strip=True)
    except Exception:
        return str(element).strip()
