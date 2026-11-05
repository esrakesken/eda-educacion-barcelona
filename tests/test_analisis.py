import pandas as pd

from src.analisis import limites_iqr


def test_limites_iqr_calcula_bien():
    # Q1 = 20, Q3 = 40, IQR = 20 → límites: 20 - 30 = -10 y 40 + 30 = 70
    serie = pd.Series([10, 20, 30, 40, 50])
    assert limites_iqr(serie) == (-10, 70)