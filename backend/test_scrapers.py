"""
MacroAR - Test de Scraping (Script independiente)
===================================================
Ejecutar para probar los scrapers sin necesidad de la API:
    python test_scrapers.py
"""
import asyncio
import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.indec import scrape_indec
from scrapers.cif import scrape_cif
from scrapers.ipc_caba import scrape_ipc_caba
from scrapers.real_m2 import scrape_real_m2


async def main():
    print("=" * 60)
    print("🧪 MacroAR - Test de Scrapers")
    print("=" * 60)
    
    # Test INDEC
    print("\n📊 Probando scraper INDEC...")
    try:
        result = await scrape_indec()
        print(f"   Indicadores: {len(result['indicators'])}")
        print(f"   Publicaciones: {len(result['publications'])}")
        for ind in result['indicators'][:3]:
            print(f"   → {ind['name']}: {ind.get('value', 'N/A')} {ind.get('unit', '')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test CIF-UTDT
    print("\n🎓 Probando scraper CIF-UTDT...")
    try:
        result = await scrape_cif()
        print(f"   Indicadores: {len(result['indicators'])}")
        print(f"   Publicaciones: {len(result['publications'])}")
        for ind in result['indicators'][:3]:
            print(f"   → {ind['name']}: {ind.get('value', 'N/A')} {ind.get('unit', '')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test IPC CABA
    print("\n🏙️ Probando scraper IPC CABA...")
    try:
        result = await scrape_ipc_caba()
        print(f"   Indicadores: {len(result['indicators'])}")
        print(f"   Publicaciones: {len(result['publications'])}")
        for ind in result['indicators'][:3]:
            print(f"   → {ind['name']}: {ind.get('value', 'N/A')} {ind.get('unit', '')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Real M2
    print("\n📈 Probando scraper Real M2 (UCEMA)...")
    try:
        result = await scrape_real_m2()
        print(f"   Indicadores: {len(result['indicators'])}")
        print(f"   Publicaciones: {len(result['publications'])}")
        for ind in result['indicators'][:3]:
            print(f"   → {ind['name']}: {ind.get('value', 'N/A')} {ind.get('unit', '')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Tests completados")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
