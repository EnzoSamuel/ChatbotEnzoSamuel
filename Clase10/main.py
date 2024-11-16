import streamlit as st
from groq import Groq
import json
import os

# Configuración inicial
clave_usuario = ""
MODELOS = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
IDIOMAS = {"Español": "es", "Inglés": "en", "Francés": "fr"}
HISTORIAL_FILE = "historial_chat.json"

# Crear cliente Groq
def crear_usuario_groq():
    clave_usuario = st.secrets["CLAVE_API"]
    return Groq(api_key=clave_usuario)

# Configurar el modelo
def configurar_modelo(cliente, modelo, mensajeDeEntrada, idioma):
    try:
        prompt = (
            f"Por favor responde en {idioma}. Usuario: {mensajeDeEntrada}"
            if idioma != "es" else mensajeDeEntrada
        )
        return cliente.chat.completions.create(
            model=modelo,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
    except Exception as e:
        st.error(f"Error en la API: {e}")
        return None

# Generar respuesta
def generar_respuesta(chat_completo):
    respuesta_completa = ""
    for frase in chat_completo:
        if frase.choices[0].delta.content:
            respuesta_completa += frase.choices[0].delta.content
            yield frase.choices[0].delta.content
    return respuesta_completa

# Guardar historial en archivo JSON
def guardar_historial():
    with open(HISTORIAL_FILE, "w") as f:
        json.dump(st.session_state.mensajes, f)

# Cargar historial desde archivo JSON
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            st.session_state.mensajes = json.load(f)

# Borrar historial
def borrar_historial():
    st.session_state.mensajes = []
    if os.path.exists(HISTORIAL_FILE):
        os.remove(HISTORIAL_FILE)

# Actualizar y mostrar historial
def actualizar_historial(rol, contenido, avatar):
    st.session_state.mensajes.append({"role": rol, "content": contenido, "avatar": avatar})
    guardar_historial()

def mostrar_historial():
    for mensaje in st.session_state.mensajes:
        style = "color: blue;" if mensaje["role"] == "user" else "color: green;"
        with st.chat_message(mensaje["role"], avatar=mensaje["avatar"]):
            st.markdown(f"<span style='{style}'>{mensaje['content']}</span>", unsafe_allow_html=True)

# Inicializar estado
def inicializar_estado():
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []
        cargar_historial()
    if "idioma" not in st.session_state:
        st.session_state.idioma = "es"  # Configuramos el idioma en español por defecto

# Configurar página
def configurar_pagina():
    st.set_page_config(page_title="Eudaimon IA", layout="wide")
    st.title("🤖 Eudaimon Chatbot by Enzo")
    
    # Barra lateral
    st.sidebar.title("Configuración")
    modelo_seleccionado = st.sidebar.selectbox("Seleccionar modelo", MODELOS, index=0)
    
    # No hay selección de idioma ya que está predeterminado en español
    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 **Consejo**: Estás interactuando en español.")
    
    # Botón para borrar historial
    if st.sidebar.button("🗑️ Borrar historial"):
        borrar_historial()
        st.sidebar.success("El historial ha sido eliminado.")
    
    # Historial de conversación
    with st.sidebar.expander("💬 Conversaciones anteriores", expanded=True):
        if "mensajes" in st.session_state and st.session_state.mensajes:
            for mensaje in st.session_state.mensajes:
                if mensaje["role"] == "user":
                    st.markdown(f"**Tú:** {mensaje['content']}")
                elif mensaje["role"] == "assistant":
                    st.markdown(f"**Eudaimon:** {mensaje['content']}")
        else:
            st.markdown("No hay mensajes previos.")
    
    return modelo_seleccionado

# Área de chat
def area_de_chat():
    with st.container():
        mostrar_historial()

# Aplicación principal
def main():
    inicializar_estado()
    usuario = crear_usuario_groq()
    modelo_actual = configurar_pagina()
    area_de_chat()

    # Entrada del usuario
    mensaje = st.chat_input("Escribe tu mensaje...")
    if mensaje:
        idioma_actual = st.session_state.idioma  # Idioma seleccionado, por defecto 'es' (español)
        actualizar_historial("user", mensaje, "😊")
        respuesta_chat_bot = configurar_modelo(usuario, modelo_actual, mensaje, idioma_actual)

        if respuesta_chat_bot:
            with st.chat_message("assistant", avatar="🤖"):
                respuesta_completa = st.write_stream(generar_respuesta(respuesta_chat_bot))
                actualizar_historial("assistant", respuesta_completa, "🤖")

if __name__ == "__main__":
    main()
