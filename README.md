# 🎓 ¿Dónde estudian los niños de Barcelona?

Análisis exploratorio de datos (EDA) de la matrícula escolar en Barcelona: **¿los niños estudian en la escuela pública, concertada o privada, y depende del distrito en el que viven?**

Alumnos de 3 a 16 años (Infantil P3-P5, Primaria y ESO) · cursos 2020/21 – 2024/25 · 10 distritos.

🔗 **Dashboard interactivo:** [escuelas-barcelona.streamlit.app](https://escuelas-barcelona.streamlit.app/)

---

## 📌 Principales hallazgos

| | Hallazgo |
|---|---|
| 🏫 | **1 de cada 2 niños** estudia en la concertada (50,8%); la pública escolariza al 43,8% y la privada al 5,3%. |
| 🗺️ | En Sarrià - Sant Gervasi solo **1 de cada 10** niños va a la pública; en Ciutat Vella, **7 de cada 10**. |
| 💶 | Cuanto más renta tiene el distrito, menos alumnos van a la pública (correlación de Pearson **0,92**). |
| 👥 | La concertada **no tiene clases más pequeñas** que la pública; solo la privada. |
| ⛪ | Casi **2 de cada 3** alumnos de la concertada van a un centro de origen religioso (estimación). |
| 📉 | P3 baja un **9,2%** en cinco cursos; la pública pierde más (-11,1%) que la concertada (-8,1%). |
| 🎒 | La concertada pesa más en la ESO (57,4%): el 83,9% de sus centros con Primaria sigue hasta la ESO, frente al 12,8% de los públicos. |

Las respuestas completas a las 6 preguntas están en el **Paso 8: Conclusiones** del notebook.

---

## 📂 Entregables

| Entregable | Archivo |
|---|---|
| Notebook del análisis (en español, explicado paso a paso) | [`notebooks/01_eda_educacion_bcn.ipynb`](notebooks/01_eda_educacion_bcn.ipynb) |
| Informe ejecutivo (para dirección) | [`reports/informe_ejecutivo.md`](reports/informe_ejecutivo.md) · [PDF](reports/informe_ejecutivo.pdf) |
| Informe de calidad de datos | [`reports/calidad_datos.md`](reports/calidad_datos.md) |
| Dashboard interactivo (Streamlit) | [escuelas-barcelona.streamlit.app](https://escuelas-barcelona.streamlit.app/) · código en [`app.py`](app.py) |
| Pipeline reproducible | [`pipeline.py`](pipeline.py) + [`src/`](src/) |
| Tests unitarios | [`tests/`](tests/) |

---

## 🗂️ Estructura del proyecto

```
eda-educacion-barcelona/
├── app.py                      # Dashboard de Streamlit
├── pipeline.py                 # Descarga → limpieza → CSV procesados
├── requirements.txt
├── pytest.ini
├── data/
│   ├── raw/                    # Datos originales (no se suben a GitHub)
│   └── processed/              # Datos limpios (sí se suben, para el dashboard)
├── notebooks/
│   └── 01_eda_educacion_bcn.ipynb
├── reports/
│   ├── informe_ejecutivo.md
│   ├── informe_ejecutivo.pdf
│   ├── calidad_datos.md
│   ├── generar_figuras.py      # Genera los gráficos del informe ejecutivo
│   └── figuras/
├── src/
│   ├── carga.py                # Descarga desde las APIs (Socrata y CKAN)
│   ├── limpieza.py             # Funciones de limpieza
│   └── analisis.py             # Funciones de análisis (outliers IQR)
└── tests/                      # Tests de pytest
```

---

## ⚙️ Instalación

Requiere **Python 3.12**.

```bash
git clone https://github.com/esrakesken/eda-educacion-barcelona.git
cd eda-educacion-barcelona

python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Uso

| Qué | Comando |
|---|---|
| Descargar y limpiar los datos (pipeline completo) | `python pipeline.py` |
| Limpiar sin descargar (usa `data/raw/`) | `python pipeline.py --sin-descarga` |
| Abrir el dashboard | `streamlit run app.py` |
| Ejecutar los tests | `pytest` |
| Regenerar los gráficos del informe ejecutivo | `python reports/generar_figuras.py` |

Los datos limpios ya están en `data/processed/`, así que el dashboard funciona sin ejecutar el pipeline. El notebook descarga los datos de las APIs en el Paso 1.

---

## 🔬 Metodología

1. **Carga:** datos descargados desde las APIs oficiales (Socrata con paginación y CKAN).
2. **Exploración inicial:** tipos, nulos, duplicados y valores inconsistentes.
3. **Limpieza:** filtro de etapas, conversión de tipos, corrección de coordenadas, unificación de distritos y titularidad, y creación de la variable `tipo_centro` (pública / concertada / privada). Los problemas y su tratamiento están en el [informe de calidad](reports/calidad_datos.md).
4. **Análisis univariado y bivariado:** tipo de centro, etapas, alumnos por grupo (outliers con IQR), distritos, titulares y chicas/chicos.
5. **Enriquecimiento:** merge con la renta por distrito (Open Data BCN) y correlaciones de Pearson y Spearman, con una comprobación de robustez.
6. **Tendencias:** evolución de P3 (índice base 100), cuota por tipo de centro y mapa de calor de correlaciones.
7. **Conclusiones**, límites y próximos pasos.

**Decisiones técnicas:**
- **Desarrollo guiado por tests (TDD):** las funciones de `src/` se escribieron siguiendo el ciclo *rojo → verde → refactor*: primero el test que falla y después la función. Los tests no usan la red: comprueban funciones puras con datos pequeños creados en el propio test.
- **Pipeline reproducible:** `pipeline.py` usa las funciones de `src/` y produce exactamente el mismo CSV limpio que el notebook (19.289 filas × 17 columnas).
- **Gráficos:** el notebook usa **matplotlib y seaborn** (gráficos estáticos que se ven en GitHub). Los **gráficos interactivos con Plotly** están en el dashboard.
- **Git:** ramas `main`, `dev` y `feature/...`, con merge `--no-ff` y commits con prefijos (`feat:`, `fix:`, `docs:`, `chore:`).

---

## 📊 Dashboard

El dashboard de Streamlit permite filtrar por **curso, etapa y distrito** y tiene cuatro vistas:

- 🗺️ **Mapa:** todos los centros de la ciudad, por tipo y tamaño.
- 📊 **Distritos:** % de alumnos por tipo de centro en cada distrito.
- 💶 **Renta:** relación entre la renta del distrito y el % de alumnos fuera de la pública.
- 📈 **Tendencias:** evolución de la cuota de cada tipo de centro y de la matrícula de P3.

---

## 📚 Fuentes y licencias

| Fuente | Dataset | Licencia |
|---|---|---|
| Generalitat de Catalunya – Departament d'Educació | [Alumnes matriculats per ensenyament i unitats dels centres docents](https://analisi.transparenciacatalunya.cat/d/xvme-26kg) | Llicència oberta d'ús d'informació – Catalunya |
| Ajuntament de Barcelona – Open Data BCN | [Renda disponible de les llars per persona](https://opendata-ajuntament.barcelona.cat/data/es/dataset/renda-disponible-llars-bcn) | CC BY 4.0 |

Ambas licencias permiten reutilizar los datos citando la fuente. Los datos son agregados por centro y nivel: no contienen información personal.

---

## ⚠️ Limitaciones

- La renta es la media del **distrito**, no de cada familia.
- Solo hay **10 distritos**: las correlaciones débiles pueden salir por casualidad, y correlación no es causalidad.
- La relación entre la caída de P3 y la natalidad es una interpretación: el análisis no incluye datos de natalidad.

Más detalle en el [informe de calidad de datos](reports/calidad_datos.md).

---

## 👩‍💻 Autoría

**Esra Kesken** · Proyecto individual de EDA · Factoría F5
