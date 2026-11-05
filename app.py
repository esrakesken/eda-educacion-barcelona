"""Dashboard: ¿Dónde estudian los niños de Barcelona? (pública, concertada o privada)

Uso:
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

CARPETA_DATOS = Path(__file__).parent / "data" / "processed"
ORDEN_TIPOS = ["Pública", "Concertada", "Privada"]
ORDEN_ETAPAS = ["Infantil (P3-P5)", "Primaria", "ESO"]
COLORES_TIPO = {"Pública": "#4C72B0", "Concertada": "#55A868", "Privada": "#DD8452"}
COLOR_NEUTRO = "#8172B3"
AZUL_OSCURO = "#1F3A5F"
# Distritos con renta y % muy parecidos: movemos su etiqueta para que no se solape
POSICION_ETIQUETA = {"Sants - Montjuïc": "middle left", "Sant Andreu": "top left"}


@st.cache_data
def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    matriculas = pd.read_csv(CARPETA_DATOS / "matriculas_bcn_limpio.csv")
    renta = pd.read_csv(CARPETA_DATOS / "renta_distrito.csv")
    return matriculas, renta


def formato_es(numero: float, decimales: int = 0) -> str:
    """12345.6 → '12.345,6' (formato español)."""
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def aplicar_estilo(fig):
    """Textos de los gráficos más grandes, en negrita y en azul oscuro (formato español)."""
    fuente_ejes = dict(size=14, weight="bold", color=AZUL_OSCURO)
    fig.update_layout(separators=",.", font=dict(size=14, color=AZUL_OSCURO))
    fig.update_xaxes(tickfont=fuente_ejes, title_font=fuente_ejes)
    fig.update_yaxes(tickfont=fuente_ejes, title_font=fuente_ejes)
    return fig


st.set_page_config(page_title="Escuelas de Barcelona", page_icon="🏫", layout="wide")

st.markdown(f"""
<style>
/* Todos los títulos: azul oscuro y en negrita */
h1, h2, h3 {{ color: {AZUL_OSCURO} !important; font-weight: 700 !important; }}

/* Filtros más abajo y con más espacio entre ellos */
[data-testid="stSidebarUserContent"] {{ padding-top: 3rem; }}
[data-testid="stSidebar"] [data-testid="stSelectbox"],
[data-testid="stSidebar"] [data-testid="stMultiSelect"] {{ margin-top: 1.2rem; }}

/* Títulos de los filtros: más grandes y en negrita */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    font-size: 1.45rem; font-weight: 700; color: {AZUL_OSCURO};
}}
/* Opciones dentro de los filtros, un poco más grandes */
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] ~ div *,
[data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] ~ div * {{
    font-size: 1.15rem !important; font-weight: 700 !important;
}}
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] ~ div * {{ color: {AZUL_OSCURO}; }}

/* KPIs en cajas con fondo azul claro */
[data-testid="stMetric"] {{
    background-color: #EAF2FB; border: 1px solid #C9DCF2;
    border-radius: 10px; padding: 12px 16px;
}}
[data-testid="stMetricLabel"] p {{ font-size: 1.1rem; font-weight: 700; color: {AZUL_OSCURO}; }}

/* Pestañas con aspecto de botón (la seleccionada, en azul oscuro) */
[data-testid="stTab"] {{
    background-color: #EAF2FB; border-radius: 8px;
    padding: 12px 28px; margin-right: 14px;
}}
[data-testid="stTab"] p {{ font-size: 1.3rem; font-weight: 700; color: {AZUL_OSCURO}; }}
[data-testid="stTab"][aria-selected="true"] {{ background-color: {AZUL_OSCURO}; }}
[data-testid="stTab"][aria-selected="true"] p {{ color: white; }}
</style>
""", unsafe_allow_html=True)

if not (CARPETA_DATOS / "matriculas_bcn_limpio.csv").exists():
    st.error("No se encuentran los datos. Ejecuta primero: `python pipeline.py`")
    st.stop()

matriculas, renta = cargar_datos()

# ---------- Filtros ----------
st.sidebar.header("🔎 Elige qué quieres ver")
st.sidebar.caption("Selecciona el curso, las etapas y los distritos.")
cursos = sorted(matriculas["curso"].unique())
curso = st.sidebar.selectbox("Curso", cursos, index=len(cursos) - 1)
etapas = st.sidebar.multiselect("Etapa", ORDEN_ETAPAS, default=ORDEN_ETAPAS)
distritos = st.sidebar.multiselect("Distrito", sorted(matriculas["distrito"].unique()),
                                   placeholder="Todos los distritos")

filtro = (matriculas["curso"] == curso) & matriculas["etapa"].isin(etapas)
if distritos:
    filtro &= matriculas["distrito"].isin(distritos)
datos = matriculas[filtro]

st.title("🏫 ¿Dónde estudian los niños de Barcelona?")
st.caption(f"Alumnos de Infantil (P3-P5), Primaria y ESO · curso {curso} · "
           "Fuentes: Generalitat de Catalunya y Open Data BCN")

if datos.empty:
    st.warning("No hay datos con estos filtros.")
    st.stop()

# ---------- KPIs ----------
total = datos["alumnos_total"].sum()
por_tipo = datos.groupby("tipo_centro")["alumnos_total"].sum().reindex(ORDEN_TIPOS, fill_value=0)

texto_etapas = "todas las etapas" if len(etapas) == len(ORDEN_ETAPAS) else ", ".join(etapas)
texto_distritos = "toda Barcelona" if not distritos else ", ".join(distritos)
st.subheader(f"📌 Curso {curso} · {texto_etapas} · {texto_distritos}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de alumnos", formato_es(total))
for col, tipo in zip([col2, col3, col4], ORDEN_TIPOS):
    col.metric(f"% {tipo}", f"{formato_es(por_tipo[tipo] / total * 100, 1)}%")

st.write("")
st.markdown("**👇 Elige una vista:**")
tab_mapa, tab_distritos, tab_renta, tab_tendencias = st.tabs(
    ["🗺️ Mapa", "📊 Distritos", "💶 Renta", "📈 Tendencias"])

# ---------- Mapa ----------
with tab_mapa:
    centros = (datos.groupby(["codigo_centro", "nombre_centro", "tipo_centro", "titularidad",
                              "distrito", "latitud", "longitud"], as_index=False)["alumnos_total"].sum())
    fig = px.scatter_map(
        centros, lat="latitud", lon="longitud", color="tipo_centro", size="alumnos_total",
        size_max=18, zoom=11, height=600, color_discrete_map=COLORES_TIPO,
        center={"lat": 41.395, "lon": 2.165},
        category_orders={"tipo_centro": ORDEN_TIPOS},
        hover_name="nombre_centro",
        hover_data={"distrito": True, "titularidad": True, "alumnos_total": True,
                    "latitud": False, "longitud": False, "tipo_centro": False},
        labels={"tipo_centro": "Tipo de centro", "alumnos_total": "Alumnos",
                "distrito": "Distrito", "titularidad": "Titularidad"},
        map_style="carto-positron",
    )
    fig.update_layout(separators=",.", margin=dict(l=0, r=0, t=0, b=0),
                      legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01))
    st.plotly_chart(aplicar_estilo(fig), width="stretch")
    st.caption(f"{formato_es(centros['codigo_centro'].nunique())} centros. "
               "El tamaño del punto indica el número de alumnos.")

# ---------- Distritos ----------
with tab_distritos:
    pct_distrito = (pd.crosstab(datos["distrito"], datos["tipo_centro"], values=datos["alumnos_total"],
                                aggfunc="sum", normalize="index").mul(100)
                    .reindex(columns=ORDEN_TIPOS, fill_value=0).sort_values("Pública"))
    largo = pct_distrito.reset_index().melt(id_vars="distrito", var_name="tipo_centro", value_name="porcentaje")
    fig = px.bar(largo, x="porcentaje", y="distrito", color="tipo_centro", orientation="h",
                 color_discrete_map=COLORES_TIPO, category_orders={"tipo_centro": ORDEN_TIPOS},
                 text=largo["porcentaje"].map(lambda v: f"{formato_es(v, 1)}%" if v >= 4 else ""),
                 labels={"porcentaje": "% de alumnos", "distrito": "", "tipo_centro": "Tipo de centro"},
                 height=500)
    fig.update_traces(hovertemplate="%{y}: %{x:.1f}%")
    fig.update_layout(separators=",.", xaxis=dict(range=[0, 100.5], dtick=20),
                      legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title_text=""),
                      margin=dict(l=190, t=60))
    st.subheader("% de alumnos por tipo de centro en cada distrito")
    st.plotly_chart(aplicar_estilo(fig), width="stretch")

# ---------- Renta ----------
with tab_renta:
    st.caption("Todos los distritos y todas las etapas del curso seleccionado (no depende de los filtros de etapa "
               "y distrito). La renta de 2024/25 usa el último año disponible (2023).")
    anio_renta = min(int(curso[:4]), renta["anio_renta"].max())
    pct_todos = (pd.crosstab([matriculas.loc[matriculas["curso"] == curso, "codigo_distrito"],
                              matriculas.loc[matriculas["curso"] == curso, "distrito"]],
                             matriculas.loc[matriculas["curso"] == curso, "tipo_centro"],
                             values=matriculas.loc[matriculas["curso"] == curso, "alumnos_total"],
                             aggfunc="sum", normalize="index").mul(100).reset_index())
    pct_todos["pct_no_publica"] = 100 - pct_todos["Pública"]
    renta_anio = renta[renta["anio_renta"] == anio_renta]
    distritos_renta = pct_todos.merge(renta_anio, on="codigo_distrito", validate="one_to_one")
    r = distritos_renta["renta_media"].corr(distritos_renta["pct_no_publica"])

    fig = px.scatter(distritos_renta, x="renta_media", y="pct_no_publica", text="distrito",
                     labels={"renta_media": f"Renta disponible media por persona (€, {anio_renta})",
                             "pct_no_publica": "% de alumnos en concertada o privada"},
                     height=550)
    fig.update_traces(marker=dict(size=14, color=AZUL_OSCURO, line=dict(width=1, color="white")),
                      textposition=distritos_renta["distrito"].map(POSICION_ETIQUETA).fillna("top center"),
                      textfont=dict(size=14, weight="bold", color=AZUL_OSCURO),
                      hovertemplate="%{text}<br>Renta: %{x:,.0f} €<br>No pública: %{y:.1f}%")
    fig.update_layout(separators=",.", yaxis_range=[0, 100])
    st.subheader(f"Renta del distrito y % de alumnos fuera de la pública (Pearson: {formato_es(r, 2)})")
    st.plotly_chart(aplicar_estilo(fig), width="stretch")

# ---------- Tendencias ----------
with tab_tendencias:
    st.caption("Aquí se muestran todos los cursos (2020/21 – 2024/25): el filtro de curso no se aplica.")
    filtro_tendencia = matriculas["etapa"].isin(etapas)
    if distritos:
        filtro_tendencia &= matriculas["distrito"].isin(distritos)
    cuota = (pd.crosstab(matriculas.loc[filtro_tendencia, "curso"], matriculas.loc[filtro_tendencia, "tipo_centro"],
                         values=matriculas.loc[filtro_tendencia, "alumnos_total"], aggfunc="sum",
                         normalize="index").mul(100).reindex(columns=ORDEN_TIPOS, fill_value=0))
    fig = px.line(cuota.reset_index().melt(id_vars="curso", var_name="tipo_centro", value_name="porcentaje"),
                  x="curso", y="porcentaje", color="tipo_centro", markers=True,
                  color_discrete_map=COLORES_TIPO, category_orders={"tipo_centro": ORDEN_TIPOS},
                  labels={"curso": "Curso", "porcentaje": "% de alumnos", "tipo_centro": "Tipo de centro"},
                  height=420)
    fig.update_traces(hovertemplate="%{x}: %{y:.1f}%")
    fig.update_layout(separators=",.", yaxis_range=[0, 100])
    st.subheader("Cuota de cada tipo de centro (todos los cursos)")
    st.plotly_chart(aplicar_estilo(fig), width="stretch")

    p3 = matriculas[(matriculas["etapa"] == "Infantil (P3-P5)") & (matriculas["nivel"] == 1)]
    if distritos:
        p3 = p3[p3["distrito"].isin(distritos)]
    p3_curso = p3.groupby("curso", as_index=False)["alumnos_total"].sum()
    fig = px.bar(p3_curso, x="curso", y="alumnos_total", text_auto=True,
                 labels={"curso": "Curso", "alumnos_total": "Alumnos de P3"}, height=400)
    fig.update_traces(marker_color=COLOR_NEUTRO, texttemplate="%{y:,.0f}")
    fig.update_layout(separators=",.")
    st.subheader("Niños que empiezan P3 cada año")
    st.plotly_chart(aplicar_estilo(fig), width="stretch")
