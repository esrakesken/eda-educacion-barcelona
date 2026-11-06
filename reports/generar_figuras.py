"""Genera los gráficos del informe ejecutivo a partir de los datos limpios.

Uso (desde la carpeta del proyecto):
    python reports/generar_figuras.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RAIZ = Path(__file__).parent.parent
MATRICULAS_LIMPIO = RAIZ / "data" / "processed" / "matriculas_bcn_limpio.csv"
RENTA_DISTRITO = RAIZ / "data" / "processed" / "renta_distrito.csv"
CARPETA_FIGURAS = Path(__file__).parent / "figuras"

CURSO_ACTUAL = "2024/2025"
ORDEN_TIPOS = ["Pública", "Concertada", "Privada"]
COLORES_TIPO = {"Pública": "#4C72B0", "Concertada": "#55A868", "Privada": "#DD8452"}
AZUL_OSCURO = "#1F3A5F"
POSICION_ETIQUETA = {"Sants - Montjuïc": (10, -2, "left"), "Sant Martí": (10, -12, "left")}

plt.rcParams.update({"font.size": 12, "axes.titleweight": "bold", "axes.titlesize": 14,
                     "axes.spines.top": False, "axes.spines.right": False})


def formato_es(numero: float, decimales: int = 0) -> str:
    """12345.6 → '12.345,6' (formato español)."""
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def grafico_distritos(actual: pd.DataFrame) -> None:
    """Barras 100% apiladas: % de alumnos por tipo de centro en cada distrito."""
    pct = (pd.crosstab(actual["distrito"], actual["tipo_centro"], values=actual["alumnos_total"],
                       aggfunc="sum", normalize="index").mul(100)[ORDEN_TIPOS].sort_values("Pública"))

    fig, ax = plt.subplots(figsize=(10, 6))
    izquierda = pd.Series(0.0, index=pct.index)
    for tipo in ORDEN_TIPOS:
        ax.barh(pct.index, pct[tipo], left=izquierda, color=COLORES_TIPO[tipo], label=tipo)
        for distrito, valor in pct[tipo].items():
            if valor >= 6:
                ax.text(izquierda[distrito] + valor / 2, distrito, f"{formato_es(valor)}%",
                        ha="center", va="center", color="white", fontweight="bold", fontsize=10)
        izquierda += pct[tipo]

    ax.set_title("En Sarrià - Sant Gervasi, 1 de cada 10 niños va a la pública;\n"
                 "en Ciutat Vella, 7 de cada 10", loc="left", pad=35)
    ax.set_xlabel("% de alumnos (curso 2024/25)")
    ax.set_xlim(0, 100)
    ax.legend(ncols=3, loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False)
    fig.tight_layout()
    fig.savefig(CARPETA_FIGURAS / "1_distritos.png", dpi=150)
    plt.close(fig)


def grafico_renta(actual: pd.DataFrame, renta: pd.DataFrame) -> None:
    """Dispersión: renta del distrito y % de alumnos fuera de la pública."""
    pct = (pd.crosstab([actual["codigo_distrito"], actual["distrito"]], actual["tipo_centro"],
                       values=actual["alumnos_total"], aggfunc="sum", normalize="index")
           .mul(100).reset_index())
    pct["pct_no_publica"] = 100 - pct["Pública"]
    renta_ultima = renta[renta["anio_renta"] == renta["anio_renta"].max()]
    datos = pct.merge(renta_ultima, on="codigo_distrito", validate="one_to_one")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(datos["renta_media"], datos["pct_no_publica"], s=130, color=AZUL_OSCURO,
               edgecolor="white", linewidth=1.5, zorder=3)
    for _, fila in datos.iterrows():
        dx, dy, alineacion = POSICION_ETIQUETA.get(fila["distrito"], (8, 4, "left"))
        ax.annotate(fila["distrito"], (fila["renta_media"], fila["pct_no_publica"]),
                    xytext=(dx, dy), textcoords="offset points", ha=alineacion,
                    fontsize=10, fontweight="bold", color=AZUL_OSCURO)

    ax.set_title("Cuanto más renta tiene el distrito, menos niños van a la escuela pública", loc="left")
    ax.set_xlabel(f"Renta disponible media por persona ({renta_ultima['anio_renta'].iloc[0]})")
    ax.set_ylabel("% de alumnos en concertada o privada")
    ax.set_ylim(0, 100)
    ax.xaxis.set_major_formatter(lambda x, pos: f"{formato_es(x)} €")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA_FIGURAS / "2_renta.png", dpi=150)
    plt.close(fig)


def grafico_p3(matriculas: pd.DataFrame) -> None:
    """Barras: total de alumnos que empiezan P3 cada curso."""
    p3 = matriculas[(matriculas["etapa"] == "Infantil (P3-P5)") & (matriculas["nivel"] == 1)]
    p3_curso = p3.groupby("curso")["alumnos_total"].sum()
    cursos = [curso.replace("/20", "/") for curso in p3_curso.index]
    variacion = (p3_curso.iloc[-1] / p3_curso.iloc[0] - 1) * 100

    fig, ax = plt.subplots(figsize=(10, 5.5))
    barras = ax.bar(cursos, p3_curso, color=AZUL_OSCURO, width=0.6)
    ax.bar_label(barras, labels=[formato_es(v) for v in p3_curso], padding=4, fontweight="bold")

    ax.set_title(f"Cada año empiezan P3 menos niños: {formato_es(variacion, 1)}% en cinco cursos", loc="left")
    ax.set_ylabel("Alumnos de P3")
    ax.set_ylim(0, p3_curso.max() * 1.12)
    ax.yaxis.set_major_formatter(lambda y, pos: formato_es(y))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(CARPETA_FIGURAS / "3_p3.png", dpi=150)
    plt.close(fig)


def main() -> None:
    CARPETA_FIGURAS.mkdir(exist_ok=True)
    matriculas = pd.read_csv(MATRICULAS_LIMPIO)
    renta = pd.read_csv(RENTA_DISTRITO)
    actual = matriculas[matriculas["curso"] == CURSO_ACTUAL]

    grafico_distritos(actual)
    grafico_renta(actual, renta)
    grafico_p3(matriculas)
    print(f"Gráficos guardados en {CARPETA_FIGURAS}")


if __name__ == "__main__":
    main()
