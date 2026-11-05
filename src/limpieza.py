"""Funciones de limpieza del EDA de educación en Barcelona."""

import pandas as pd

LAT_BCN = (41.3, 41.5)
LON_BCN = (2.0, 2.3)


def coordenadas_validas(df: pd.DataFrame) -> pd.Series:
    """Devuelve True en las filas cuyas coordenadas están dentro de Barcelona."""
    return df["latitud"].between(*LAT_BCN) & df["longitud"].between(*LON_BCN)



def corregir_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """Sustituye las coordenadas no válidas por la mediana de las válidas del mismo centro.

    Si un centro no tiene ninguna coordenada válida, quedan vacías (NaN).
    """
    df = df.copy()
    validas = coordenadas_validas(df)
    coords_por_centro = (
        df[validas]
        .groupby("codigo_centro")[["latitud", "longitud"]]
        .median()
    )

    for col in ["latitud", "longitud"]:
        df.loc[~validas, col] = df.loc[~validas, "codigo_centro"].map(coords_por_centro[col])
    return df
