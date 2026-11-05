import pandas as pd

from src.limpieza import coordenadas_validas, corregir_coordenadas


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