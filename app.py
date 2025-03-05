import streamlit as st
import pandas as pd

# Subir el archivo
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Cargar el archivo Excel
    df = pd.read_excel(uploaded_file, engine="openpyxl")

    # Mostrar las primeras filas para asegurarnos de que se cargó correctamente
    st.write("Datos cargados:", df.head())

    # Verificar y mostrar los nombres de las columnas
    st.write("Columnas disponibles:", df.columns)

    # Renombrar la columna 'Fecha y Hora' a 'Fecha' si lo prefieres más corto
    df.rename(columns={'Fecha y Hora': 'Fecha'}, inplace=True)

    # Convertir la columna de fechas y horas al formato datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    # Pregunta al usuario el nombre
    nombre = st.text_input("Introduce el nombre de la persona a consultar:")

    if nombre:
        # Filtrar los datos por el nombre
        asistencias = df[df['Nombre'].str.lower() == nombre.lower()]

        if not asistencias.empty:
            st.write(f"{nombre} asistió en las siguientes fechas:")
            st.write(asistencias)

            # Contar cuántas veces asistió ese mes
            asistencias['Mes'] = asistencias['Fecha'].dt.month
            asistencias['Año'] = asistencias['Fecha'].dt.year

            # Preguntar el mes y año para contar las asistencias
            mes_año = st.date_input("Selecciona un mes y año para ver la asistencia:", 
                                    min_value=pd.to_datetime('2025-01-01'), max_value=pd.to_datetime('2025-12-31'))

            mes = mes_año.month
            año = mes_año.year

            # Filtrar y contar las asistencias por mes y año
            asistencias_mes_año = asistencias[(asistencias['Mes'] == mes) & (asistencias['Año'] == año)]
            st.write(f"Cantidad de veces que {nombre} asistió en {mes}/{año}: {len(asistencias_mes_año)}")
        else:
            st.write(f"No se encontraron registros para {nombre}.")


