"""Pipeline reproducible: descarga los datos, los limpia y guarda los CSV procesados.

Uso:
    python pipeline.py                 # descarga los datos de las APIs
    python pipeline.py --sin-descarga  # usa los CSV ya guardados en data/raw/
"""

import argparse
from pathlib import Path

import pandas as pd

from src.carga import descargar_matriculas, descargar_renta
from src.limpieza import limpiar_matriculas, renta_media_distrito

CARPETA_DATOS = Path(__file__).parent / "data"
MATRICULAS_RAW = CARPETA_DATOS / "raw" / "matriculas_bcn_raw.csv"
RENTA_RAW = CARPETA_DATOS / "raw" / "renta_bcn_raw.csv"
MATRICULAS_LIMPIO = CARPETA_DATOS / "processed" / "matriculas_bcn_limpio.csv"
RENTA_DISTRITO = CARPETA_DATOS / "processed" / "renta_distrito.csv"


def main(descargar: bool = True) -> None:
    if descargar:
        print("1/3 Descargando datos...")
        matriculas = descargar_matriculas()
        renta = descargar_renta()
        matriculas.to_csv(MATRICULAS_RAW, index=False)
        renta.to_csv(RENTA_RAW, index=False)
    else:
        print("1/3 Leyendo datos de data/raw/...")
        matriculas = pd.read_csv(MATRICULAS_RAW, dtype=str)
        renta = pd.read_csv(RENTA_RAW)
    print(f"    Matrículas: {len(matriculas)} filas | Renta: {len(renta)} filas")

    print("2/3 Limpiando...")
    matriculas_limpio = limpiar_matriculas(matriculas)
    renta_distrito = renta_media_distrito(renta)

    print("3/3 Guardando en data/processed/...")
    matriculas_limpio.to_csv(MATRICULAS_LIMPIO, index=False)
    renta_distrito.to_csv(RENTA_DISTRITO, index=False)
    print(f"    {MATRICULAS_LIMPIO.name}: {matriculas_limpio.shape[0]} filas, {matriculas_limpio.shape[1]} columnas")
    print(f"    {RENTA_DISTRITO.name}: {renta_distrito.shape[0]} filas")
    print("Listo ✅")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline del EDA de educación en Barcelona")
    parser.add_argument("--sin-descarga", action="store_true", help="usar los CSV de data/raw/ en vez de descargar")
    args = parser.parse_args()
    main(descargar=not args.sin_descarga)