from src.carga import construir_filtro


def test_construir_filtro():
    filtro = construir_filtro(["2023/2024", "2024/2025"])
    assert filtro == "nom_municipi='Barcelona' AND curs IN ('2023/2024','2024/2025')"