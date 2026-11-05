import pandas as pd

from src.limpieza import (
    asignar_tipo_centro,
    coordenadas_validas,
    corregir_coordenadas,
    limpiar_distrito,
    limpiar_matriculas,
)


def test_coordenadas_validas_detecta_puntos_fuera_de_barcelona():
    df = pd.DataFrame({
        "latitud":  [41.40, 40.42, 41.40, None],   # BCN, Madrid, BCN, vacío
        "longitud": [2.17, -3.70, 3.50, None],      # BCN, Madrid, mar, vacío
    })
    assert coordenadas_validas(df).tolist() == [True, False, False, False]


def test_corregir_coordenadas_usa_las_del_mismo_centro():
    df = pd.DataFrame({
        "codigo_centro": ["A", "A", "B", "C"],
        "latitud":  [41.40, 40.42, 41.38, 40.00],
        "longitud": [2.17, -3.70, 2.15, -3.00],
    })
    resultado = corregir_coordenadas(df)

    assert resultado["latitud"].tolist()[:3] == [41.40, 41.40, 41.38]
    assert resultado["longitud"].tolist()[:3] == [2.17, 2.17, 2.15]
    assert resultado[["latitud", "longitud"]].iloc[3].isnull().all()


def test_corregir_coordenadas_no_modifica_el_original():
    df = pd.DataFrame({
        "codigo_centro": ["A", "A"],
        "latitud":  [41.40, 40.42],
        "longitud": [2.17, -3.70],
    })
    corregir_coordenadas(df)
    assert df["latitud"].tolist() == [41.40, 40.42]


def test_limpiar_distrito_quita_prefijo_y_corrige_mayusculas():
    serie = pd.Series(["DM VIII - Nou Barris", "Ciutat vella", "Eixample", "DM X - Sant Martí"])
    assert limpiar_distrito(serie).tolist() == ["Nou Barris", "Ciutat Vella", "Eixample", "Sant Martí"]


def test_asignar_tipo_centro():
    df = pd.DataFrame({
        "naturaleza": ["Públic", "Privat", "Privat", "Privat"],
        "concertada": [None, "SI", "NO", None],
    })
    resultado = asignar_tipo_centro(df)

    assert resultado.tolist()[:3] == ["Pública", "Concertada", "Privada"]
    assert pd.isna(resultado.iloc[3])


def fila_cruda(**cambios):
    """Una fila con el formato de la API; cambiamos solo lo que interesa en cada test."""
    fila = {
        "curs": "2024/2025", "codi_centre": "08000001", "denominaci_completa": "Escola Prova",
        "nom_naturalesa": "Públic", "matr_cula_concertada": None,
        "nom_titularitat": "Departament d'Educació", "nom_dm": "DM VIII - Nou Barris",
        "coordenades_geo_y": "41.44", "coordenades_geo_x": "2.17",
        "codi_ensenyament": "EPRILOE", "nivell": "1", "modalitat": "ORDINARI",
        "matr_cules_total": "25", "matr_cules_dones": "12", "matr_cules_homes": "13", "unitats": "1",
    }
    fila.update(cambios)
    return fila


def test_limpiar_matriculas():
    crudo = pd.DataFrame([
        fila_cruda(),
        fila_cruda(codi_centre="08000002", nom_naturalesa="Privat", matr_cula_concertada="SI",
                   nom_dm="Ciutat vella", codi_ensenyament="ESO LOE"),
        fila_cruda(codi_centre="08000003", codi_ensenyament="BATXLOE"),  # fuera de alcance
    ])
    limpio = limpiar_matriculas(crudo)

    assert len(limpio) == 2
    assert limpio["etapa"].tolist() == ["Primaria", "ESO"]
    assert limpio["tipo_centro"].tolist() == ["Pública", "Concertada"]
    assert limpio["distrito"].tolist() == ["Nou Barris", "Ciutat Vella"]
    assert limpio["codigo_distrito"].tolist() == [8, 1]
    assert limpio["alumnos_total"].dtype == "Int64"
    assert "modalidad" not in limpio.columns