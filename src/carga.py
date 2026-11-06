"""Descarga de los datos de matrículas (Generalitat) y renta (Open Data BCN)."""

import pandas as pd
import requests

URL_MATRICULAS = "https://analisi.transparenciacatalunya.cat/resource/xvme-26kg.json"
URL_CKAN = "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show"
CURSOS = ["2020/2021", "2021/2022", "2022/2023", "2023/2024", "2024/2025"]
ANIOS_RENTA = [2020, 2021, 2022, 2023]
LIMITE = 10000


def construir_filtro(cursos: list[str]) -> str:
    """Crea el filtro $where de Socrata para Barcelona y los cursos indicados."""
    lista_cursos = ",".join(f"'{c}'" for c in cursos)
    return f"nom_municipi='Barcelona' AND curs IN ({lista_cursos})"


def descargar_matriculas(cursos: list[str] = CURSOS) -> pd.DataFrame:
    """Descarga las matrículas de Barcelona página a página (la API da como máximo LIMITE filas por petición)."""
    paginas = []
    offset = 0
    while True:
        params = {
            "$where": construir_filtro(cursos),
            "$limit": LIMITE,
            "$offset": offset,
            "$order": ":id",
        }
        respuesta = requests.get(URL_MATRICULAS, params=params, timeout=60)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not datos:
            break
        paginas.extend(datos)
        offset += LIMITE
    return pd.DataFrame(paginas)


def descargar_renta(anios: list[int] = ANIOS_RENTA) -> pd.DataFrame:
    """Descarga la renta disponible por sección censal de los años indicados."""
    respuesta = requests.get(URL_CKAN, params={"id": "renda-disponible-llars-bcn"}, timeout=60)
    respuesta.raise_for_status()
    recursos = respuesta.json()["result"]["resources"]

    urls_renta = {
        int(r["name"][:4]): r["url"]
        for r in recursos
        if r["format"].upper() == "CSV" and int(r["name"][:4]) in anios
    }
    return pd.concat([pd.read_csv(url) for url in urls_renta.values()], ignore_index=True)