"""Funciones de limpieza del EDA de educación en Barcelona."""

import numpy as np
import pandas as pd

LAT_BCN = (41.3, 41.5)
LON_BCN = (2.0, 2.3)
CODIGOS_DISTRITO = {
    "Ciutat Vella": 1,
    "Eixample": 2,
    "Sants - Montjuïc": 3,
    "Les Corts": 4,
    "Sarrià - Sant Gervasi": 5,
    "Gràcia": 6,
    "Horta - Guinardó": 7,
    "Nou Barris": 8,
    "Sant Andreu": 9,
    "Sant Martí": 10,
}


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


def limpiar_distrito(serie: pd.Series) -> pd.Series:
    """Quita el prefijo 'DM <número romano> - ' y unifica 'Ciutat vella' → 'Ciutat Vella'."""
    return (
        serie
        .str.replace(r"^DM [IVX]+ - ", "", regex=True)
        .str.replace("Ciutat vella", "Ciutat Vella")
    )


def asignar_tipo_centro(df: pd.DataFrame) -> pd.Series:
    """Clasifica cada fila en Pública, Concertada o Privada según naturaleza y concierto."""
    condiciones = [
        df["naturaleza"] == "Públic",
        (df["naturaleza"] == "Privat") & (df["concertada"] == "SI"),
        (df["naturaleza"] == "Privat") & (df["concertada"] == "NO"),
    ]
    tipos = ["Pública", "Concertada", "Privada"]
    return pd.Series(np.select(condiciones, tipos, default=None), index=df.index)