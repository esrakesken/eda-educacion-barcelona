# Informe de calidad de datos

**Proyecto:** ¿Dónde estudian los niños de Barcelona? (pública, concertada o privada)
**Periodo analizado:** cursos 2020/21 – 2024/25

Este informe resume los problemas de calidad que encontramos en los datos, cómo los tratamos y qué limitaciones quedan. Todos los detalles y el código están en el notebook (`notebooks/01_eda_educacion_bcn.ipynb`), y la limpieza se puede repetir con `python pipeline.py`.

---

## 1. Fuentes de datos

| Fuente | Dataset | Acceso | Tamaño original |
|---|---|---|---|
| Generalitat de Catalunya | Alumnes matriculats per ensenyament i unitats dels centres docents (`xvme-26kg`) | API Socrata (paginada) | 42.611 filas × 35 columnas |
| Ajuntament de Barcelona (Open Data BCN) | Renda disponible de les llars per persona (`renda-disponible-llars-bcn`) | API CKAN, años 2020 – 2023 | 4.272 filas × 7 columnas |

**Alcance:** nos quedamos con Infantil segundo ciclo (P3-P5), Primaria y ESO, las etapas de 3 a 16 años. Resultado: **19.289 filas × 17 columnas**.

> **Principio de limpieza:** solo eliminamos filas por **alcance** (etapas que no responden a la pregunta), nunca por problemas de calidad. Si un dato no sirve para un análisis concreto, lo excluimos **solo de ese análisis**, no de todo el dataset.

---

## 2. Resumen por dimensión de calidad

| Dimensión | Estado | Comentario |
|---|---|---|
| **Completitud** | 🟢 Buena | Los vacíos de `concertada` en centros públicos son estructurales (la pregunta no aplica). En nuestro alcance, 0 centros privados sin información de concierto. |
| **Validez** | 🟡 Corregida | 460 filas con coordenadas fuera de Barcelona o vacías → corregidas. Todas las columnas llegaban como texto → convertidas sin crear nulos nuevos. |
| **Consistencia** | 🟡 Corregida | Distritos y titularidad escritos de varias formas → unificados. `chicas + chicos = alumnos_total` en el 100% de las filas. |
| **Unicidad** | 🟢 Buena | 26 duplicados en el dataset original, todos de Escoles Oficials d'Idiomes (fuera de alcance). 0 duplicados después del filtro. |
| **Actualidad** | 🟡 Aceptable | La renta llega hasta 2023: para el curso 2024/25 usamos la de 2023. La renta de 2023 tiene un salto anómalo (ver 3.8). |

---

## 3. Problemas encontrados y tratamiento

### 3.1 Tipos de datos
- **Problema:** la API devuelve todas las columnas como texto, incluidas las numéricas.
- **Tratamiento:** conversión con `pd.to_numeric(errors="coerce")` y comprobación antes/después: **0 nulos nuevos**. Usamos `Int64` para los enteros con vacíos (`nivel` tiene 107 vacíos, ver 3.4).

### 3.2 Coordenadas
- **Problema:** **434 filas** con coordenadas fuera de Barcelona (casi todas del curso 2021/22) y **26 vacías**.
- **Tratamiento:** sustituidas por la mediana de las coordenadas válidas del **mismo centro en otros cursos**. Un centro (Institut Escola Coves d'en Cimany) no tenía ninguna coordenada válida y se corrigió a mano.
- **Resultado:** 0 filas con coordenadas no válidas. Necesario para el mapa del dashboard.

### 3.3 Nombres de distrito
- **Problema:** el mismo distrito aparece con varios nombres ("DM VIII - Nou Barris" y "Nou Barris"; "Ciutat vella" y "Ciutat Vella"). Además, la fuente de renta escribe los nombres de otra forma ("Sarrià-St. Gervasi").
- **Tratamiento:** limpieza con una expresión regular y un código oficial de distrito (1–10). El merge con la renta se hace **por código**, no por nombre.
- **Resultado:** de 11 valores a **10 distritos**, 0 filas sin código. Merge: 50 filas (5 cursos × 10 distritos), 0 sin renta.

### 3.4 Centros con sistema educativo extranjero
- **Problema:** 107 filas (por ejemplo, el Lycée Français) con valores muy altos de alumnos (hasta 1.037 en una fila), sin `nivel` y con 0 grupos. No es un error: estos centros declaran el **total de la etapa**, no cada nivel.
- **Tratamiento:** marcadas con la columna `sistema_extranjero`. Se **incluyen** en los recuentos por tipo de centro y distrito, y se **excluyen** de los análisis por nivel y por grupo.

### 3.5 Registros con 0 grupos
- **Problema:** 348 filas con `grupos = 0` (sin contar el sistema extranjero). Son **grupos mixtos**: por ejemplo, P3 y P4 en la misma aula, con los grupos registrados en un solo nivel.
- **Tratamiento:** calculamos los alumnos por grupo a nivel de **centro + etapa + curso**. Solo **61 de 4.436 combinaciones (1,4%)** siguen sin grupos → excluidas **solo** del análisis de alumnos por grupo (pregunta 3).

### 3.6 Titularidad
- **Problema:** el titular público aparece con **3 nombres distintos** según el curso (cambios de nombre del departamento de educación).
- **Tratamiento:** traducción con un diccionario y unificación como "Generalitat". La comprobación de valores sin traducir encontró dos titulares inesperados (entidades extranjeras y estados de la UE), agrupados como "Extranjera".

### 3.7 Concierto distinto según el nivel
- **Problema:** en **88 combinaciones centro-etapa-curso**, unos niveles son concertados y otros no (por ejemplo, P3 privado y P4-P5 concertados).
- **Interpretación:** no es un error. Los conciertos se firman **por unidad escolar** (Real Decreto 2377/1985, art. 16). Los niveles no concertados tienen de media **9,5 alumnos**, frente a **18,3** en los concertados.
- **Caso especial:** en 2021/22, **15 centros concertados** tienen su grupo de P3 registrado como privado. Esto hace que la privada parezca crecer mucho ese año en P3 (ver notebook, 7.2).
- **Tratamiento:** mantenemos el dato tal como está y lo señalamos al interpretar los resultados.

### 3.8 Salto en la renta de 2023
- **Problema:** la renta media sube alrededor de un 5% al año hasta 2022, pero un **+13,5% en 2023** (en Sarrià - Sant Gervasi, **+29,6%**). Puede ser un cambio real o un cambio de metodología de la fuente.
- **Tratamiento:** comparamos **distritos dentro del mismo año**, no años entre sí. Comprobación de robustez con la renta de 2022: la correlación casi no cambia (**Pearson 0,92 → 0,91; Spearman 0,77 → 0,77**).

### 3.9 Valores atípicos (outliers)
- **Problema:** **61 combinaciones centro-etapa** con un número de alumnos por grupo atípico según el método IQR (60 por debajo, 1 por encima).
- **Tratamiento:** **se mantienen**: son centros pequeños reales, no errores. Para comparar usamos la **mediana**, más robusta que la media.

---

## 4. Comprobaciones automáticas

| Comprobación | Dónde | Resultado |
|---|---|---|
| Nulos nuevos al convertir tipos | Notebook 3.4 | 0 |
| Duplicados después del filtro | Notebook 3.2 | 0 |
| Coordenadas fuera de Barcelona después de corregir | Notebook 3.6 | 0 |
| Filas sin código de distrito / sin tipo de centro / sin titularidad traducida | Notebook 3.9 – 3.11 | 0 / 0 / 0 |
| `chicas + chicos = alumnos_total` | Notebook 5.4 | 0 filas incoherentes |
| Merge con renta (`validate="many_to_one"`) | Notebook 6.4 | 50 filas, 0 sin renta |
| Tests unitarios de las funciones de limpieza (`pytest`) | `tests/` | 9 tests en verde |
| Pipeline frente al notebook | `pipeline.py` | Mismo resultado: 19.289 filas × 17 columnas |

Los tests cubren también casos que no aparecen en los datos actuales, por ejemplo un curso en el que todas las coordenadas ya sean válidas. Así el pipeline no falla si se ejecuta con datos nuevos.

---

## 5. Limitaciones

- **Cada fila es un centro + nivel + curso.** Si sumamos varios cursos, el mismo alumno se cuenta varias veces. Por eso las cifras absolutas se dan siempre **por curso**.
- **La renta es por distrito** (media de las secciones censales), no por familia. Solo podemos hablar de relación entre **zonas**, no de que las familias con más renta elijan la concertada.
- **Solo 10 distritos:** las correlaciones se calculan con 10 puntos. Las relaciones fuertes (renta ↔ tipo de centro) son claras, pero las débiles pueden salir por casualidad.
- **El sexo está registrado solo de forma binaria** (chicas / chicos).
- **El origen religioso de la concertada es una estimación:** el dato oficial solo identifica a los titulares religiosos; las fundaciones con nombre religioso se han detectado por palabras clave.
- **No tenemos datos de natalidad:** la relación entre la bajada de P3 y la natalidad es una interpretación, no un dato del dataset.
