import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import unicodedata
import re
from scipy.stats import chi2_contingency

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Calidad del aire en Colombia",
    page_icon="🌎",
    layout="wide"
)

st.title("🌎 Análisis de la calidad del aire en Colombia")
st.subheader(
    "Exploración de datos de estaciones de monitoreo — Promedio anual"
)

st.markdown("""
Este dashboard permite explorar los registros de calidad del aire
en Colombia, comparar contaminantes y analizar su comportamiento
mediante indicadores, gráficos y herramientas estadísticas.
""")

# =====================================================
# FUNCIONES DE LIMPIEZA
# =====================================================
def clave_normalizada(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).replace("\u00a0", " ")
    texto = re.sub(r"\s+", " ", texto).strip().lower()

    texto = "".join(
        caracter
        for caracter in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caracter) != "Mn"
    )

    return texto


def limpiar_departamentos(serie):
    nombres_oficiales = {
        "amazonas": "Amazonas",
        "antioquia": "Antioquia",
        "arauca": "Arauca",
        "atlantico": "Atlántico",
        "bogota": "Bogotá",
        "bogota, d.c": "Bogotá, D.C.",
        "bolivar": "Bolívar",
        "boyaca": "Boyacá",
        "caldas": "Caldas",
        "caqueta": "Caquetá",
        "casanare": "Casanare",
        "cauca": "Cauca",
        "cesar": "Cesar",
        "choco": "Chocó",
        "cordoba": "Córdoba",
        "cundinamarca": "Cundinamarca",
        "guainia": "Guainía",
        "guaviare": "Guaviare",
        "huila": "Huila",
        "guajira": "La Guajira",
        "la guajira": "La Guajira",
        "magdalena": "Magdalena",
        "meta": "Meta",
        "narino": "Nariño",
        "norte de santander": "Norte de Santander",
        "putumayo": "Putumayo",
        "quindio": "Quindío",
        "risaralda": "Risaralda",
        "san andres": "San Andrés",
        "santander": "Santander",
        "sucre": "Sucre",
        "tolima": "Tolima",
        "valle del cauca": "Valle del Cauca",
        "vaupes": "Vaupés",
        "vichada": "Vichada"
    }

    def normalizar(valor):
        if pd.isna(valor):
            return pd.NA

        clave = clave_normalizada(valor).rstrip(".")
        clave = re.sub(r"\s+", " ", clave).strip()

        return nombres_oficiales.get(
            clave,
            str(valor).strip().title()
        )

    return serie.apply(normalizar)




# =====================================================
# CARGA DE DATOS
# =====================================================

@st.cache_data
def cargar_datos():
    datos = pd.read_csv("dataset.csv", encoding="utf-8-sig")
    st.write("Total de registros del dataset:", len(datos))
    datos.columns = datos.columns.str.strip()

    columnas_requeridas = [
        "Nombre del Departamento",
        "Variable",
        "Promedio",
        "Año",
        "Tipo de Estación"
    ]

    faltantes = [
        columna for columna in columnas_requeridas
        if columna not in datos.columns
    ]

    if faltantes:
        raise ValueError(
            "Faltan columnas en el CSV: " + ", ".join(faltantes)
        )

    # Limpiar departamentos
    datos["Nombre del Departamento"] = limpiar_departamentos(
        datos["Nombre del Departamento"]
    )

    # Limpiar variables y tipo de estación
    for columna in ["Variable", "Tipo de Estación"]:
        datos[columna] = (
            datos[columna]
            .astype("string")
            .str.strip()
        )

    # Convertir columnas numéricas
    columnas_numericas = [
        "Promedio", "Suma", "No. de datos", "Mediana",
        "Percentil 98", "Máximo", "Mínimo",
        "Excedencias limite actual",
        "Porcentaje excedencias limite actual",
        "Días de excedencias", "Año"
    ]

    for columna in columnas_numericas:
        if columna in datos.columns:
            datos[columna] = pd.to_numeric(
                datos[columna]
                .astype("string")
                .str.replace(",", "", regex=False),
                errors="coerce"
            )

    return datos


try:
    df = cargar_datos()

except FileNotFoundError:
    st.error(
        "No se encontró dataset.csv. "
        "Verifica que esté en la misma carpeta que app.py."
    )
    st.stop()

except Exception as error:
    st.error(f"No fue posible cargar el dataset: {error}")
    st.stop()


# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("🔎 Filtros del análisis")

departamentos = sorted(
    df["Nombre del Departamento"].dropna().unique().tolist()
)

variables = sorted(
    df["Variable"].dropna().unique().tolist()
)

anios = sorted(
    df["Año"].dropna().astype(int).unique().tolist()
)

promedios_validos = df["Promedio"].dropna()

if promedios_validos.empty:
    st.error("No hay valores numéricos disponibles en Promedio.")
    st.stop()

minimo = float(promedios_validos.min())
maximo = float(promedios_validos.max())

departamento_seleccionado = st.sidebar.selectbox(
    "Departamento",
    ["Todos"] + departamentos
)

variables_seleccionadas = st.sidebar.multiselect(
    "Contaminantes o variables",
    options=variables,
    default=[v for v in ["PM10", "PM2.5"] if v in variables]
)
anio_seleccionado = st.sidebar.selectbox(
    "Año",
    ["Todos"] + anios
)

if minimo < maximo:
    rango_promedio = st.sidebar.slider(
        "Rango del promedio",
        min_value=minimo,
        max_value=maximo,
        value=(minimo, maximo)
    )
else:
    rango_promedio = (minimo, maximo)
    st.sidebar.caption(f"Promedio disponible: {minimo:.2f}")


# =====================================================
# APLICAR FILTROS
# =====================================================

df_filtrado = df.copy()

if departamento_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["Nombre del Departamento"]
        == departamento_seleccionado
    ]

if variables_seleccionadas:
    df_filtrado = df_filtrado[
        df_filtrado["Variable"].isin(variables_seleccionadas)
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

st.subheader("Verificación de registros para chi-cuadrado")

st.write("Total de registros filtrados:", len(df_filtrado))

st.write(
    "Registros sin tipo de estación:",
    df_filtrado["Tipo de Estación"].isna().sum()
)

st.write(
    "Registros sin contaminante:",
    df_filtrado["Variable"].isna().sum()
)
# =====================================================
# EXPLORACIÓN DE DATOS
# =====================================================

st.header("1. Exploración de datos")

st.markdown("""
Los siguientes indicadores, la tabla y los gráficos
corresponden a los registros que cumplen los filtros seleccionados.
""")

promedios = df_filtrado["Promedio"].dropna()

conteo = len(df_filtrado)
media = promedios.mean() if not promedios.empty else 0
desviacion = promedios.std() if len(promedios) > 1 else 0

c1, c2, c3 = st.columns(3)

c1.metric("Cantidad de registros", f"{conteo:,}")
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
    use_container_width=True,
    hide_index=True
)

archivo_csv = df_filtrado.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="⬇️ Descargar datos filtrados en CSV",
    data=archivo_csv,
    file_name="datos_calidad_aire_filtrados.csv",
    mime="text/csv"
)


# =====================================================
# GRÁFICOS
# =====================================================

st.subheader("¿Qué departamentos presentan mayores valores de PM10 y PM2.5?")

datos_pm10 = df_filtrado[
    df_filtrado["Variable"].astype("string").str.strip().str.upper() == "PM10"
]

datos_pm25 = df_filtrado[
    df_filtrado["Variable"].astype("string").str.strip().str.upper() == "PM2.5"
]

resumen_pm10 = (
    datos_pm10.groupby("Nombre del Departamento")["Promedio"]
    .mean()
    .sort_values(ascending=True)
)

resumen_pm25 = (
    datos_pm25.groupby("Nombre del Departamento")["Promedio"]
    .mean()
    .sort_values(ascending=True)
)

if not resumen_pm10.empty or not resumen_pm25.empty:

    figura, (eje1, eje2) = plt.subplots(1, 2, figsize=(16, 10))

    # Gráfico PM10
    if not resumen_pm10.empty:
        resumen_pm10.plot(kind="barh", ax=eje1)

        eje1.set_title("Promedio de PM10 por departamento")
        eje1.set_xlabel("Promedio")
        eje1.set_ylabel("Departamento")

        for barra in eje1.patches:
            valor = barra.get_width()
            eje1.text(
                valor + 0.3,
                barra.get_y() + barra.get_height() / 2,
                f"{valor:.2f}",
                va="center",
                fontsize=8
            )

        eje1.set_xlim(0, resumen_pm10.max() * 1.12)

    # Gráfico PM2.5
    if not resumen_pm25.empty:
        resumen_pm25.plot(kind="barh", ax=eje2, color="darkorange")

        eje2.set_title("Promedio de PM2.5 por departamento")
        eje2.set_xlabel("Promedio")
        eje2.set_ylabel("Departamento")

        for barra in eje2.patches:
            valor = barra.get_width()
            eje2.text(
                valor + 0.3,
                barra.get_y() + barra.get_height() / 2,
                f"{valor:.2f}",
                va="center",
                fontsize=8
            )

        eje2.set_xlim(0, resumen_pm25.max() * 1.12)

    figura.tight_layout()
    st.pyplot(figura)
    plt.close(figura)

else:
    st.info("No hay registros de PM10 ni PM2.5 para realizar la comparación.")



# =====================================================
# ANÁLISIS ESTADÍSTICO CHI-CUADRADO
# =====================================================

st.header("3. Análisis estadístico")

st.markdown("""
Se utiliza la prueba chi-cuadrado para evaluar si existe
asociación estadística entre la variable de contaminación
y el tipo de estación de monitoreo.
""")

datos_chi2 = df_filtrado[
    ["Variable", "Tipo de Estación"]
].dropna()
st.write("Registros para chi-cuadrado:", len(datos_chi2))
st.write("Registros excluidos:", len(df_filtrado) - len(datos_chi2))

if len(datos_chi2) > 0:
    tabla_contingencia = pd.crosstab(
        datos_chi2["Variable"],
        datos_chi2["Tipo de Estación"]
    )

    if tabla_contingencia.shape[0] >= 2 and tabla_contingencia.shape[1] >= 2:
        chi2, p_valor, grados_libertad, frecuencias_esperadas = (
            chi2_contingency(tabla_contingencia)
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Chi-cuadrado", f"{chi2:.4f}")
        col2.metric("Valor p", f"{p_valor:.4e}")
        col3.metric("Grados de libertad", grados_libertad)

        st.subheader("Tabla de contingencia")
        st.dataframe(tabla_contingencia, use_container_width=True)

        if p_valor < 0.05:
            st.success(
                "Se rechaza la hipótesis nula: existe evidencia "
                "de asociación estadística entre las variables."
            )
        else:
            st.info(
                "No se rechaza la hipótesis nula: no se encontró "
                "evidencia suficiente de asociación estadística."
            )

        st.caption(
            "Nivel de significancia utilizado: α = 0.05. "
            "La asociación estadística no implica causalidad."
        )

    else:
        st.info(
            "Se necesitan al menos dos categorías en cada variable "
            "para realizar la prueba chi-cuadrado."
        )
else:
    st.info("No hay datos suficientes para realizar el análisis.")


# =====================================================
# CONCLUSIONES Y RECOMENDACIONES
# =====================================================

st.header("4. Narrativa de resultados: calidad del aire en Colombia")

st.subheader("1. ¿Qué analicé?")

st.markdown("""
Se analizaron los registros de calidad del aire de las estaciones de
monitoreo de Colombia, enfocándose en los contaminantes PM10 y PM2.5.
Se compararon sus valores promedio entre los departamentos y se
examinó su comportamiento a lo largo de los años. También se evaluó
la relación entre el contaminante registrado y el tipo de estación
de monitoreo mediante una prueba estadística chi-cuadrado.
""")

st.subheader("2. ¿Qué encontré?")

st.markdown("""
En el análisis por departamento, Arauca presentó los mayores valores
promedio tanto de PM10 como de PM2.5. Para PM10 también sobresalieron
Norte de Santander, Cauca, Valle del Cauca y Bogotá. En PM2.5 se
destacaron, después de Arauca, Casanare, Chocó, Norte de Santander
y Antioquia.

En el análisis temporal, los valores más altos se observaron entre
2011 y 2016. Posteriormente, los promedios registrados mostraron
una tendencia descendente.

Por otra parte, la prueba chi-cuadrado se realizó con 9.415 registros y se obtuvo un valor de 6,3392,
un valor p de 0,01181 y un grado de libertad. Esto indica una
asociación estadísticamente significativa entre el contaminante
registrado y el tipo de estación.
""")

st.subheader("3. ¿Qué significa?")

st.markdown("""
Los resultados muestran que los valores registrados de PM10 y PM2.5
presentan diferencias entre los departamentos y a lo largo del tiempo.
Arauca merece especial atención porque aparece entre los departamentos
con mayores promedios de ambos contaminantes.

La disminución observada después de 2016 representa una reducción
de los promedios registrados en los años posteriores. Sin embargo,
este comportamiento no permite afirmar por sí solo cuáles fueron
las causas de esa disminución.

La asociación encontrada mediante chi-cuadrado indica que la
distribución de los contaminantes está relacionada con el tipo
de estación de monitoreo, pero no demuestra una relación de causa
y efecto.
""")

st.subheader("4. ¿Qué se recomendaría?")

st.markdown("""
- Fortalecer el seguimiento de la calidad del aire en los departamentos
  que presentan mayores valores promedio.
- Prestar especial atención a Arauca, por sus resultados en ambos
  contaminantes.
- Mantener el monitoreo periódico de PM10 y PM2.5 para identificar
  cambios en sus concentraciones.
- Analizar las diferencias entre los tipos de estaciones de monitoreo
  para comprender mejor los resultados.
- Utilizar la información recopilada para orientar acciones de
  prevención y gestión de la calidad del aire.
""")


# =====================================================
# PIE DE PÁGINA
# =====================================================

st.divider()

st.caption(
    "Fuente: conjunto de datos de calidad del aire en Colombia. "
    "Dashboard desarrollado con Python y Streamlit."
)
