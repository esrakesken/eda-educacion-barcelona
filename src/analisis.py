"""Funciones de análisis del EDA de educación en Barcelona."""

import pandas as pd


def limites_iqr(serie: pd.Series) -> tuple[float, float]:
    """Devuelve los límites inferior y superior para detectar outliers con el método IQR."""
    q1, q3 = serie.quantile([0.25, 0.75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr