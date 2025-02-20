import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from groq import Groq

# centorno
load_dotenv()
qclient = Groq()

st.title("Predicción Electoral 💛💙💖")

# Subir 
uploaded_file = st.file_uploader("Sube un archivo Excel con los datos", type=["xlsx"])

if uploaded_file:
    # Leer datos
    df = pd.read_excel(uploaded_file)
    st.write("Datos cargados:", df.head())
    
    # Contar 
    voto_counts = df.iloc[:, 0].value_counts()
    
    # Mostrar 
    st.subheader("Resultados de votación")
    fig, ax = plt.subplots()
    voto_counts.plot(kind="bar", ax=ax, color=['blue', 'red', 'gray'])
    ax.set_xlabel("Opciones")
    ax.set_ylabel("Cantidad de votos")
    st.pyplot(fig)

    # Guardar en sesión para preguntas
    st.session_state["votos"] = voto_counts.to_dict()
    st.success("Análisis completado.")

# Chat interactivo
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input("Haz una pregunta sobre los votos"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        datos_votos = st.session_state.get("votos", {})
        texto_contexto = "Los votos son: " + str(datos_votos)
        
        stream_response = qclient.chat.completions.create(
            messages=[
                {"role": "system", "content": "Responde basado en los siguientes datos: " + texto_contexto},
                {"role": "user", "content": prompt},
            ],
            model="llama-3.3-70b-specdec",
            stream=True
        )
        
        response_text = "".join(chunk.choices[0].delta.content for chunk in stream_response if chunk.choices[0].delta.content)
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})