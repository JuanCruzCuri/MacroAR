"""
MacroAR - Test de Scraping (Script independiente)
===================================================
Ejecutar para probar los scrapers contra los sitios reales, sin necesidad de la API:
    python test_scrapers.py

Verifica que cada scraper devuelva los indicadores esperados, con valor y período,
y que los valores estén en rangos razonables. Sale con código 1 si algo falla.
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

# Indicadores esperados por scraper y rango razonable de cada valor
EXPECTED = {
    "INDEC": (scrape_indec, {
        "ipc_mensual": (-5, 30), "ipim_mensual": (-5, 30), "icc_construccion": (-5, 30),
        "emae_mom_sa": (-15, 15), "ipi_manufacturero_mom_sa": (-20, 20), "ipi_minero_mom_sa": (-20, 20),
        "isac_mom_sa": (-20, 20), "ucii": (30, 95),
        "balanza_exportaciones": (1000, 30000), "balanza_importaciones": (1000, 30000), "balanza_saldo": (-10000, 10000),
        "desocupacion": (2, 30), "pobreza_personas": (5, 70), "pobreza_hogares": (5, 70), "indigencia": (0.5, 30),
        "salarios_mensual": (-10, 30), "salarios_interanual": (-50, 300), "salarios_acumulado": (-50, 300),
        "personal_apn_yoy": (-30, 30),
    }),
    "CIF-UTDT": (scrape_cif, {
        "expectativas_inflacion": (0, 300), "confianza_consumidor": (-50, 50), "indice_lider": (-20, 20),
    }),
    "IPC CABA": (scrape_ipc_caba, {"ipc_caba": (-5, 30)}),
    "UCEMA": (scrape_real_m2, {"m2_real_indice": (-30, 30), "m2_real_acumulado": (-50, 50)}),
}


async def main() -> int:
    print("=" * 60)
    print("🧪 MacroAR - Test de Scrapers")
    print("=" * 60)
    failures = []

    for source, (scraper, expected) in EXPECTED.items():
        print(f"\n📊 {source}")
        try:
            result = await scraper()
        except Exception as e:
            failures.append(f"{source}: excepción {e!r}")
            continue

        found = {ind["indicator_key"]: ind for ind in result["indicators"]}
        for ind in result["indicators"]:
            print(f"   → {ind['indicator_key']:26} {ind['value']!s:>9} {ind['unit']:13} {ind['period']}")

        for key, (low, high) in expected.items():
            ind = found.get(key)
            if ind is None:
                failures.append(f"{source}: falta {key}")
            elif ind["value"] is None or not (low <= ind["value"] <= high):
                failures.append(f"{source}: {key} = {ind['value']} fuera de rango [{low}, {high}]")
            elif not ind["period"]:
                failures.append(f"{source}: {key} sin período")

        if not result["publications"]:
            failures.append(f"{source}: sin publicaciones")
        for pub in result["publications"]:
            if not pub["title"] or not pub["url"]:
                failures.append(f"{source}: publicación incompleta {pub}")
        print(f"   Publicaciones: {len(result['publications'])}")

    print("\n" + "=" * 60)
    if failures:
        print(f"❌ {len(failures)} problema(s):")
        for failure in failures:
            print(f"   - {failure}")
        return 1
    print("✅ Todos los scrapers OK")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
