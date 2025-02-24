import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from groq import Groq

# Cargar variables de entorno
load_dotenv()
qclient = Groq()

st.title("🗳️ Predicción Electoral 💛💙❤️")

# Subir archivo Excel
uploaded_file = st.file_uploader("📂 Sube un archivo Excel con los datos", type=["xlsx"])

if uploaded_file:
    # Leer datos del archivo
    df = pd.read_excel(uploaded_file)
    st.write("📊 Datos cargados:", df.head())

    # Función para etiquetar los votos
    def etiquetar_voto(keywords):
        if pd.isna(keywords):
            return "Voto Nulo"
        keywords = keywords.lower()
        if "noboa" in keywords or "noboistas" in keywords or "nobitas" in keywords:
            return "Voto Noboa"
        if "luisa" in keywords:
            return "Voto Luisa"
        return "Voto Nulo"

    # Aplicar la función a la columna 'keywords'
    df["Voto"] = df["keywords"].apply(etiquetar_voto)

    # Contar votos
    voto_counts = df["Voto"].value_counts()
    total_votos = voto_counts.sum()

    # Mostrar gráfico
    st.subheader("📊 Resultados de la Votación")
    fig, ax = plt.subplots(figsize=(10, 6))
    colores = {'Voto Noboa': 'blue', 'Voto Luisa': 'red', 'Voto Nulo': 'gray'}
    bars = ax.bar(voto_counts.index, voto_counts.values, color=[colores.get(x, 'black') for x in voto_counts.index])

    ax.set_xlabel("Opciones", fontsize=12)
    ax.set_ylabel("Cantidad de Votos", fontsize=12)
    ax.set_title("Distribución de Votos", fontsize=14, fontweight="bold")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        percentage = f"{(height / total_votos) * 100:.1f}%"
        ax.text(bar.get_x() + bar.get_width()/2, height, f"{height}\n({percentage})", 
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

    st.pyplot(fig)

    # Conclusión
    st.subheader("📝 Conclusión")
    votos_nulos = voto_counts.get('Voto Nulo', 0)
    st.write(f"📉 Votos Nulos: {votos_nulos}")
    if votos_nulos > 0:
        st.write("🔍 Los votos nulos pueden indicar un descontento o confusión entre los votantes.")
    else:
        st.write("🔍 No se registraron votos nulos, lo que indica una elección clara.")

    # Guardar en sesión para preguntas
    st.session_state["votos"] = voto_counts.to_dict()
    st.success("✅ Análisis completado.")

# Chat interactivo
st.subheader("🤖 Haz Preguntas sobre los Votos")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("Escribe tu pregunta aquí..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    datos_votos = st.session_state.get("votos", {})
    texto_contexto = f"Los votos contabilizados son: {datos_votos}"

    try:
        stream_response = qclient.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Responde con base en estos datos: {texto_contexto}"},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-specdec",
            stream=True
        )
        
        response_text = "".join(chunk.choices[0].delta.content for chunk in stream_response if chunk.choices[0].delta.content)
    except Exception as e:
        response_text = f"❌ Hubo un error al procesar la respuesta: {e}"

    with st.chat_message("assistant"):
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
