import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency

# =========================================================
# 1. CONFIGURACIÓN GENERAL
# =========================================================
st.set_page_config(
    page_title="Calidad del aire en Colombia",
    page_icon="🌎",
    layout="wide"
)

# Estilos visuales
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }

    h1 {
        color: #17365D;
        font-weight: 700;
    }

    h2, h3 {
        color: #24527A;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #dce5ef;
        padding: 16px;
        border-radius: 10px;
    }

    div[data-testid="stMetricLabel"] {
        color: #526579;
    }

    .nota {
        background-color: #eaf2f8;
        padding: 12px;
        border-radius: 8px;
        color: #24445f;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌎 Análisis de la calidad del aire en Colombia")
st.subheader("Exploración de datos de estaciones de monitoreo — Promedio anual")

st.markdown("""
Dashboard interactivo para explorar los registros de contaminantes
y otros indicadores ambientales por departamento, variable y periodo.
""")

# =========================================================
# 2. CARGA Y PREPARACIÓN DE DATOS
# =========================================================
@st.cache_data
def cargar_datos():
    datos = pd.read_csv("dataset.csv")

# Limpiar nombres de departamentos
if "Nombre del Departamento" in datos.columns:
    datos["Nombre del Departamento"] = (
        datos["Nombre del Departamento"]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )


       columnas_numericas = [
        "Promedio", "Suma", "No. de datos", "Mediana",
        "Percentil 98", "Máximo", "Mínimo"
    ]

    for columna in columnas_numericas:
        if columna in datos.columns:
            datos[columna] = pd.to_numeric(
                datos[columna].astype(str).str.replace(",", "", regex=False),
                errors="coerce"
            )

    if "Año" in datos.columns:
        datos["Año"] = pd.to_numeric(
            datos["Año"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    return datos


try:
    df = cargar_datos()

except FileNotFoundError:
    st.error(
        "No se encontró dataset.csv. Verifica que esté guardado "
        "en la misma carpeta que app.py."
    )
    st.stop()

except Exception as error:
    st.error(f"No fue posible cargar el dataset: {error}")
    st.stop()


columnas_requeridas = [
    "Nombre del Departamento",
    "Variable",
    "Promedio",
    "Año",
    "Tipo de Estación"
]

faltantes = [col for col in columnas_requeridas if col not in df.columns]

if faltantes:
    st.error(f"Faltan columnas necesarias en el CSV: {', '.join(faltantes)}")
    st.stop()
# Limpiar nombres de departamentos
df["Nombre del Departamento"] = (
    df["Nombre del Departamento"]
    .astype("string")


# =========================================================
# 3. FILTROS INTERACTIVOS
# =========================================================
with st.sidebar:
    st.header("🔎 Filtros del análisis")

    # Normalizar nombres de departamentos
df["Nombre del Departamento"] = (
    df["Nombre del Departamento"]
    .astype("string")
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    .str.upper()
)

# Crear lista de departamentos sin duplicados
departamentos = sorted(
    df["Nombre del Departamento"].dropna().unique()
)

    departamento_seleccionado = st.selectbox(
        "Departamento",
        ["Todos"] + departamentos
    )

    variables = sorted(df["Variable"].dropna().unique())

    variable_seleccionada = st.selectbox(
        "Contaminante o variable",
        ["Todas"] + variables
    )

    anios = sorted(
        df["Año"].dropna().unique().astype(int).tolist()
    )

    anio_seleccionado = st.selectbox(
        "Año",
        ["Todos"] + anios
    )

    valores_promedio = df["Promedio"].dropna()

    if valores_promedio.empty:
        st.error("No hay valores numéricos disponibles en la columna Promedio.")
        st.stop()

    minimo = float(valores_promedio.min())
    maximo = float(valores_promedio.max())

    if minimo == maximo:
        rango_promedio = (minimo, maximo)
        st.info(f"El promedio disponible es {minimo:.2f}.")
    else:
        rango_promedio = st.slider(
            "Rango del promedio",
            min_value=minimo,
            max_value=maximo,
            value=(minimo, maximo),
            step=max((maximo - minimo) / 500, 0.01),
            help="Selecciona el intervalo de valores promedio que deseas analizar."
        )

    st.divider()

    st.caption(
        "Los indicadores, la tabla y los gráficos de exploración "
        "se actualizan según los filtros seleccionados."
    )


# Aplicar filtros
df_filtrado = df.copy()

if departamento_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Nombre del Departamento"] == departamento_seleccionado
    ]

if variable_seleccionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["Variable"] == variable_seleccionada
    ]

if anio_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Año"] == anio_seleccionado
    ]

df_filtrado = df_filtrado[
    df_filtrado["Promedio"].between(
        rango_promedio[0],
        rango_promedio[1]
    )
]


# =========================================================
# 4. EXPLORACIÓN DE DATOS Y MÉTRICAS
# =========================================================
st.header("1. Exploración de datos")

st.markdown("""
<div class="nota">
Los siguientes indicadores y la tabla corresponden a los registros
que cumplen los filtros seleccionados.
</div>
""", unsafe_allow_html=True)

promedios = df_filtrado["Promedio"].dropna()

conteo = len(df_filtrado)
media = promedios.mean() if not promedios.empty else 0
desviacion = promedios.std() if len(promedios) > 1 else 0

c1, c2, c3 = st.columns(3)

c1.metric(
    "Cantidad de registros",
    f"{conteo:,}"
)

c2.metric(
    "Promedio de los valores",
    f"{media:,.2f}" if conteo else "Sin datos"
)

c3.metric(
    "Desviación estándar",
    f"{desviacion:,.2f}" if conteo > 1 else "No disponible"
)

st.subheader("Tabla de registros")

st.dataframe(
    df_filtrado,
    width="stretch",
    hide_index=True
)

# Descargar registros filtrados
archivo_csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="⬇️ Descargar datos filtrados en CSV",
    data=archivo_csv,
    file_name="datos_calidad_aire_filtrados.csv",
    mime="text/csv"
)


# =========================================================
# 5. VISUALIZACIONES DINÁMICAS
# =========================================================
st.header("2. Visualizaciones")

if df_filtrado.empty:
    st.warning(
        "No hay registros para la combinación de filtros seleccionada. "
        "Modifica los filtros para visualizar los gráficos."
    )

else:
    col_g1, col_g2 = st.columns(2)

    # Evolución anual
    with col_g1:
        st.subheader("Evolución anual del promedio")

        datos_anuales = (
            df_filtrado.dropna(subset=["Año", "Promedio"])
            .groupby("Año", as_index=False)["Promedio"]
            .mean()
            .sort_values("Año")
        )

        if not datos_anuales.empty:
            fig, ax = plt.subplots(figsize=(8, 4))

            ax.plot(
                datos_anuales["Año"],
                datos_anuales["Promedio"],
                marker="o",
                linewidth=2
            )

            ax.set_xlabel("Año")
            ax.set_ylabel("Promedio registrado")
            ax.set_title("Cambio del promedio a través de los años")
            ax.grid(alpha=0.25)
            plt.xticks(rotation=45)

            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        else:
            st.info("No hay datos anuales disponibles.")

    # Departamentos
    with col_g2:
        st.subheader("Departamentos con mayores promedios")

        datos_departamento = (
            df_filtrado.dropna(
                subset=["Nombre del Departamento", "Promedio"]
            )
            .groupby("Nombre del Departamento")["Promedio"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .sort_values()
        )

        if not datos_departamento.empty:
            fig, ax = plt.subplots(figsize=(8, 4))

            datos_departamento.plot(
                kind="barh",
                ax=ax
            )

            ax.set_xlabel("Promedio registrado")
            ax.set_ylabel("Departamento")
            ax.set_title("Diez departamentos con mayor promedio")

            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        else:
            st.info("No hay datos suficientes para comparar departamentos.")

    # Distribución
    st.subheader("Distribución de los valores promedio")

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.hist(
        promedios,
        bins=30,
        edgecolor="black"
    )

    ax.set_xlabel("Promedio registrado")
    ax.set_ylabel("Número de registros")
    ax.set_title("Distribución de los valores promedio")
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# =========================================================
# 6. VALIDACIÓN ESTADÍSTICA: CHI-CUADRADO
# =========================================================
st.header("3. Validación estadística")

st.markdown("""
**Prueba Chi-cuadrado de independencia**

Se evalúa si existe asociación entre el tipo de variable ambiental
registrada y el tipo de estación de monitoreo.
""")

# Esta prueba conserva el análisis global de la Tarea 3.
# No depende de los filtros del panel lateral.
datos_chi2 = df[
    ["Variable", "Tipo de Estación"]
].dropna()

tabla_contingencia = pd.crosstab(
    datos_chi2["Variable"],
    datos_chi2["Tipo de Estación"]
)

if (
    tabla_contingencia.shape[0] > 1
    and tabla_contingencia.shape[1] > 1
):
    chi2, p_value, grados_libertad, frecuencias_esperadas = (
        chi2_contingency(tabla_contingencia)
    )

    frecuencia_minima = frecuencias_esperadas.min()

    s1, s2, s3, s4 = st.columns(4)

    s1.metric(
        "Estadístico Chi-cuadrado",
        f"{chi2:,.4f}"
    )

    s2.metric(
        "Valor p",
        f"{p_value:.3e}"
    )

    s3.metric(
        "Grados de libertad",
        str(grados_libertad)
    )

    s4.metric(
        "Frecuencia esperada mínima",
        f"{frecuencia_minima:.2f}"
    )

    if p_value < 0.05:
        st.success("""
        **Conclusión:** se encontró evidencia estadística de una asociación
        entre la variable ambiental registrada y el tipo de estación.
        La distribución de los registros no es igual para todas las
        clasificaciones de estación.
        """)
    else:
        st.info("""
        **Conclusión:** no se encontró evidencia estadística suficiente
        para afirmar que exista una asociación entre las dos variables.
        """)

    st.caption("""
    Esta prueba se calcula con todos los registros válidos del dataset,
    igual que en la Tarea 3. No cambia al modificar los filtros del panel
    lateral. La asociación estadística no demuestra causalidad.
    """)

else:
    st.warning(
        "No hay suficientes categorías para calcular la prueba Chi-cuadrado."
    )


# =========================================================
# 7. HALLAZGOS Y RECOMENDACIONES
# =========================================================
st.header("4. Hallazgos y recomendaciones")

with st.expander("¿Qué analicé?", expanded=True):
    st.write("""
    Se analizó un conjunto de datos de monitoreo de la calidad del aire
    en Colombia. La información reúne registros de distintas estaciones
    ubicadas en departamentos y municipios del país. Incluye diferentes
    variables ambientales, sus valores promedio, el año de medición y la
    clasificación de cada estación.

    El propósito es facilitar la exploración de estos registros y observar
    cómo se distribuye la información entre lugares, años y tipos de medición.
    """)

with st.expander("¿Qué encontré?"):
    st.write("""
    Los registros permiten comparar los valores promedio entre departamentos
    y observar su comportamiento a lo largo del tiempo. También muestran que
    se recopilan distintos tipos de variables ambientales y que las estaciones
    se clasifican como fijas o indicativas.

    La prueba estadística encontró una asociación entre la variable ambiental
    registrada y el tipo de estación de monitoreo. Esto señala que la
    composición de los registros cambia según la clasificación de la estación.
    """)

with st.expander("¿Qué significa?"):
    st.write("""
    Para interpretar la información ambiental es importante tener en cuenta
    qué se está midiendo, dónde se realiza la medición y qué tipo de estación
    recoge los datos.

    Una comparación directa entre departamentos debe considerar también que
    no todos tienen necesariamente la misma cantidad de estaciones, mediciones
    o variables. Por eso, un promedio aislado no explica por sí solo toda la
    situación ambiental de un territorio.
    """)

with st.expander("¿Qué se recomendaría?"):
    st.write("""
    Se recomienda mantener actualizados los registros de las estaciones,
    revisar la disponibilidad de mediciones por departamento y facilitar
    comparaciones usando la misma variable y unidades equivalentes.

    También es conveniente priorizar la revisión de los lugares que presenten
    valores elevados o cambios importantes entre años, verificando primero
    la cantidad y calidad de los datos disponibles.

    Finalmente, los resultados deben utilizarse como apoyo para orientar
    el seguimiento ambiental y no como única evidencia para tomar decisiones.
    """)


# =========================================================
# 8. GRÁFICOS ESPECÍFICOS DE PM10 Y PM2.5
# =========================================================
st.header("5. Análisis específico de material particulado")

st.markdown("""
Estos gráficos se concentran en PM10 y PM2.5. Respetan los filtros de
departamento y año, pero no dependen de la variable seleccionada ni del
rango del promedio, para permitir comparar ambas partículas.
""")

# Filtros de departamento y año para estos gráficos
datos_particulas = df.copy()

if departamento_seleccionado != "Todos":
    datos_particulas = datos_particulas[
        datos_particulas["Nombre del Departamento"]
        == departamento_seleccionado
    ]

if anio_seleccionado != "Todos":
    datos_particulas = datos_particulas[
        datos_particulas["Año"] == anio_seleccionado
    ]


# PM10 y PM2.5 por año
st.subheader("Comportamiento anual de PM10 y PM2.5")

datos_particulas = datos_particulas[
    datos_particulas["Variable"].isin(["PM10", "PM2.5"])
].dropna(subset=["Año", "Promedio"])

if not datos_particulas.empty:

    anual_particulas = (
        datos_particulas.groupby(
            ["Año", "Variable"],
            as_index=False
        )["Promedio"]
        .mean()
        .sort_values("Año")
    )

    fig, ax = plt.subplots(figsize=(10, 4))

    for nombre_variable, grupo in anual_particulas.groupby("Variable"):
        ax.plot(
            grupo["Año"],
            grupo["Promedio"],
            marker="o",
            linewidth=2,
            label=nombre_variable
        )

    ax.set_xlabel("Año")
    ax.set_ylabel("Promedio registrado")
    ax.set_title("Comportamiento anual de PM10 y PM2.5")
    ax.legend(title="Variable")
    ax.grid(alpha=0.25)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

else:
    st.info(
        "No se encontraron registros suficientes de PM10 y PM2.5 "
        "para construir esta gráfica."
    )


# Comparación de departamentos para PM10
st.subheader("Comparación de departamentos para PM10")

datos_pm10 = df.copy()

if departamento_seleccionado != "Todos":
    datos_pm10 = datos_pm10[
        datos_pm10["Nombre del Departamento"]
        == departamento_seleccionado
    ]

if anio_seleccionado != "Todos":
    datos_pm10 = datos_pm10[
        datos_pm10["Año"] == anio_seleccionado
    ]

datos_pm10 = datos_pm10[
    datos_pm10["Variable"] == "PM10"
].dropna(
    subset=["Nombre del Departamento", "Promedio"]
)

if not datos_pm10.empty:

    top_pm10 = (
        datos_pm10.groupby("Nombre del Departamento")["Promedio"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(10, 4))

    top_pm10.plot(
        kind="barh",
        ax=ax
    )

    ax.set_xlabel("Promedio de PM10 registrado")
    ax.set_ylabel("Departamento")
    ax.set_title("Departamentos con mayores promedios registrados de PM10")

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

else:
    st.info(
        "No se encontraron registros de PM10 para elaborar esta comparación."
    )

# ---------------------------------------------------------
# CONCLUSIONES Y RECOMENDACIONES
# ---------------------------------------------------------

st.markdown("---")
st.header("Conclusiones y recomendaciones")

with st.expander("Ver interpretación de los resultados", expanded=True):

    st.markdown("### Hallazgos principales")

    st.markdown("""
    - El análisis permite explorar el comportamiento de los contaminantes
      atmosféricos en diferentes departamentos y años.
    - Los filtros facilitan la identificación de diferencias entre regiones,
      variables ambientales y periodos de tiempo.
    - Los gráficos de PM10 y PM2.5 permiten comparar la evolución anual
      de estos contaminantes y analizar su comportamiento.
    - La prueba Chi-cuadrado evidenció una asociación estadísticamente
      significativa entre la variable ambiental y el tipo de estación
      de monitoreo.
    """)

    st.markdown("### Conclusiones")

    st.markdown("""
    Los resultados evidencian la importancia del monitoreo de la calidad
    del aire en Colombia, ya que permiten identificar variaciones en las
    concentraciones de contaminantes y explorar diferencias entre las
    estaciones de monitoreo y las regiones analizadas.

    La herramienta desarrollada facilita la exploración, visualización
    e interpretación de los datos mediante filtros interactivos y
    representaciones gráficas, contribuyendo a una mejor comprensión
    de la información ambiental.

    La asociación identificada mediante la prueba Chi-cuadrado indica
    que existe una relación estadística entre las variables analizadas,
    sin que esto implique necesariamente una relación causal.
    """)

    st.markdown("### Recomendaciones")

    st.markdown("""
    - Fortalecer el monitoreo de la calidad del aire en las regiones
      con mayores concentraciones de contaminantes.
    - Promover estrategias de reducción de emisiones provenientes
      del transporte, las actividades industriales y otras fuentes.
    - Realizar análisis periódicos que permitan identificar tendencias
      y posibles cambios en la calidad del aire.
    - Utilizar herramientas de visualización de datos para facilitar
      la toma de decisiones ambientales.
    - Fomentar la educación y sensibilización ciudadana sobre los
      efectos de la contaminación atmosférica en la salud y el ambiente.
    """)

# =========================================================
# 9. FUENTE Y PIE DE PÁGINA
# =========================================================
st.divider()

st.caption(
    "Fuente: Calidad del Aire en Colombia (Promedio Anual). "
    "Los resultados descriptivos dependen de los filtros seleccionados. "
    "La prueba Chi-cuadrado reproduce el análisis global de la Tarea 3."
)

st.caption("Dashboard desarrollado con Python, Pandas, Streamlit y Matplotlib.")