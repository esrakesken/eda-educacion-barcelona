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

ETAPAS = {"EINFLOE 2C": "Infantil (P3-P5)", "EPRILOE": "Primaria", "ESO LOE": "ESO"}

COLUMNAS = {
    "curs": "curso",
    "codi_centre": "codigo_centro",
    "denominaci_completa": "nombre_centro",
    "nom_naturalesa": "naturaleza",
    "matr_cula_concertada": "concertada",
    "nom_titularitat": "titularidad",
    "nom_dm": "distrito",
    "coordenades_geo_y": "latitud",
    "coordenades_geo_x": "longitud",
    "nivell": "nivel",
    "modalitat": "modalidad",
    "matr_cules_total": "alumnos_total",
    "matr_cules_dones": "chicas",
    "matr_cules_homes": "chicos",
    "unitats": "grupos",
}
COLUMNAS_ENTERAS = ["nivel", "alumnos_total", "chicas", "chicos", "grupos"]
COLUMNAS_DECIMALES = ["latitud", "longitud"]

# Centros sin ninguna coordenada válida en ningún curso (corregidos a mano)
COORDENADAS_MANUALES = {"Institut Escola Coves d'en Cimany": (41.420676, 2.152548)}

TITULARIDAD = {
    "Departament d'Ensenyament": "Generalitat",
    "Departament d'Educació": "Generalitat",
    "Departament d'Educació i Formació Professional": "Generalitat",
    "Corporacions Locals": "Ayuntamiento",
    "Ordes i Congregacions Catòlics": "Orden religiosa católica",
    "Església Catòlica": "Iglesia católica",
    "Altres Confesions Religioses": "Otras confesiones religiosas",
    "Fundacions": "Fundación",
    "Societats Mercantils": "Sociedad mercantil",
    "Cooperatives": "Cooperativa",
    "Associacions": "Asociación",
    "Persones Físiques": "Persona física",
    "Persones Jurídiques Estrangeres": "Entidad extranjera",
    "Altres estats UE": "Estado extranjero (UE)",
}

TITULARIDAD_GRUPO = {
    "Generalitat": "Administración pública",
    "Ayuntamiento": "Administración pública",
    "Orden religiosa católica": "Religiosa",
    "Iglesia católica": "Religiosa",
    "Otras confesiones religiosas": "Religiosa",
    "Fundación": "Fundación",
    "Sociedad mercantil": "Empresa",
    "Cooperativa": "Cooperativa",
    "Asociación": "Otros",
    "Persona física": "Otros",
    "Entidad extranjera": "Extranjera",
    "Estado extranjero (UE)": "Extranjera",
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
        df[col] = df[col].where(validas, df["codigo_centro"].map(coords_por_centro[col]))
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


def limpiar_matriculas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica toda la limpieza del Paso 3 del notebook a los datos crudos de la API."""
    df = df[df["codi_ensenyament"].isin(ETAPAS.keys())].copy()
    df["etapa"] = df["codi_ensenyament"].map(ETAPAS)
    df = df[list(COLUMNAS.keys()) + ["etapa"]].rename(columns=COLUMNAS)

    for col in COLUMNAS_ENTERAS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in COLUMNAS_DECIMALES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = corregir_coordenadas(df)
    for nombre, (lat, lon) in COORDENADAS_MANUALES.items():
        df.loc[df["nombre_centro"] == nombre, ["latitud", "longitud"]] = [lat, lon]

    df["sistema_extranjero"] = df["modalidad"] == "ESTRANGERS"
    df["distrito"] = limpiar_distrito(df["distrito"])
    df["codigo_distrito"] = df["distrito"].map(CODIGOS_DISTRITO)
    df["titularidad"] = df["titularidad"].map(TITULARIDAD)
    df["titularidad_grupo"] = df["titularidad"].map(TITULARIDAD_GRUPO)
    df["tipo_centro"] = asignar_tipo_centro(df)

    return df.drop(columns=["modalidad", "naturaleza", "concertada"])


def renta_media_distrito(renta: pd.DataFrame) -> pd.DataFrame:
    """Calcula la renta media de cada distrito y año a partir de las secciones censales."""
    return (
        renta.groupby(["Any", "Codi_Districte"], as_index=False)["Import_Euros"].mean()
        .rename(columns={"Any": "anio_renta", "Codi_Districte": "codigo_distrito",
                         "Import_Euros": "renta_media"})
    )