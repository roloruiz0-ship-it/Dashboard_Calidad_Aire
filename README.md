# Análisis de la calidad del aire en Colombia

# 

# Dashboard interactivo para la exploración de los contaminantes PM10 y PM2.5

# 

# 1\. Descripción del proyecto

# 

# Este proyecto presenta un dashboard interactivo desarrollado con Python y Streamlit para explorar y analizar el conjunto de datos Calidad del Aire en Colombia (Promedio Anual). El análisis se enfoca en los contaminantes PM10 y PM2.5, con el propósito de identificar diferencias en sus valores promedio entre los departamentos y observar su comportamiento a lo largo de los años.

# 

# El conjunto de datos contiene información de estaciones de monitoreo, variables ambientales, años de medición, valores promedio y ubicación geográfica. Se seleccionó porque permite comparar los registros de calidad del aire entre departamentos y analizar el comportamiento de los contaminantes en Colombia.

# 

# La aplicación permite consultar la información mediante filtros por departamento, contaminante, año y rango de valores promedio. También presenta indicadores, gráficos y resultados de un análisis estadístico para facilitar la interpretación de los datos.

# 

# 2\. Dashboard publicado

# 

# El proyecto se encuentra disponible en Streamlit Community Cloud:

# 

# Enlace: https://dashboardcalidadaire-awiu3u6dpe2uyguvwsegd5.streamlit.app/

# 

# 3\. Captura de pantalla del dashboard

# 

# A continuación, se presenta una evidencia visual de la aplicación en funcionamiento.

# 

# !\[Dashboard de calidad del aire](https://github.com/roloruiz0-ship-it/Dashboard\_Calidad\_Aire/blob/main/capturas/dashboard.png?raw=true)



# 4\. Principales hallazgos del análisis exploratorio

# 

# Comparación por departamentos: Arauca presentó los mayores valores promedio tanto de PM10 como de PM2.5 entre los departamentos analizados.

# 

# Comportamiento de PM10: también se destacaron Norte de Santander, Cauca, Valle del Cauca y Bogotá.

# 

# Comportamiento de PM2.5: después de Arauca, sobresalieron Casanare, Chocó, Norte de Santander y Antioquia.

# 

# Comportamiento temporal: los valores promedio más altos se observaron entre 2011 y 2016. En los años posteriores se identificó una tendencia descendente.

# 

# Análisis estadístico: la prueba chi-cuadrado, aplicada a los registros de PM10 y PM2.5 con información disponible sobre el tipo de estación, obtuvo un estadístico de 6,3392 y un valor p de 0,01181. Esto evidencia una asociación estadísticamente significativa entre el contaminante y el tipo de estación, sin demostrar causalidad.

# 

# 5\. Tecnologías utilizadas

# 

# Python

# 

# Streamlit

# 

# Pandas

# 

# Matplotlib

# 

# SciPy

# 

# GitHub

# 

# Streamlit Community Cloud

# 

# 6\. Estructura del repositorio

# 

# Dashboard\_Calidad\_Aire/

# │

# ├── app.py

# ├── dataset.csv

# ├── requirements.txt

# ├── README.md

# └── capturas/

# &#x20;   └── dashboard.png

# 

# 7\. Instalación y ejecución local

# 

# Para ejecutar el proyecto en un equipo local, se deben seguir estos pasos:

# 

# Paso 1. Instalar Python 3.9 o una versión superior.

# 

# Paso 2. Descargar o clonar el repositorio de GitHub.

# 

# Paso 3. Abrir una terminal en la carpeta del proyecto.

# 

# Paso 4. Crear un entorno virtual (opcional, pero recomendado):

# 

# python -m venv venv

# 

# Paso 5. Activar el entorno virtual en Windows:

# 

# venv\\Scripts\\activate

# 

# Paso 6. Instalar las dependencias:

# 

# pip install -r requirements.txt

# 

# Paso 7. Ejecutar la aplicación:

# 

# python -m streamlit run app.py

# 

# Paso 8. Abrir en el navegador la dirección local que proporciona Streamlit, normalmente:

# 

# http://localhost:8501

# 

# 8\. Información académica

# 

# Estudiante: Edisson Rolando Ruiz García

# 

# Curso: Programación para el análisis de datos

# 

# Universidad: Universidad Nacional Abierta y a Distancia (UNAD)

# 

# Fecha: 26 de noviembre de 2026

# 

# 9\. Fuente de datos

# 

# Conjunto de datos Calidad del Aire en Colombia (Promedio Anual), suministrado para el desarrollo de la actividad académica.

