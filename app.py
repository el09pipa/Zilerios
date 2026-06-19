# app.py
import streamlit as st
from moderation import contiene_lenguaje_inapropiado, obtener_mensaje_bloqueo
from core_ai import CoreZilerios

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Zilerios AI", page_icon="🤖", layout="wide")

st.title("🤖 Zilerios AI")
st.caption("Chat libre, sin registros ni complicaciones. ¡Pregúntame lo que quieras! ⚡")

# --- INICIALIZAR EL MOTOR DE LA IA ---
if "ai_core" not in st.session_state:
    st.session_state.ai_core = CoreZilerios()

# --- HISTORIAL EN MEMORIA LOCAL ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes anteriores del chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- ENTRADA DEL USUARIO ---
prompt_usuario = st.chat_input("Escribe aquí tu petición para Zilerios...")

if prompt_usuario:
    with st.chat_message("user"):
        st.write(prompt_usuario)
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    
    # Moderación de insultos
    if contiene_lenguaje_inapropiado(prompt_usuario):
        mensaje_bloqueo = obtener_mensaje_bloqueo()
        with st.chat_message("assistant"):
            st.error(mensaje_bloqueo)
        st.session_state.messages.append({"role": "assistant", "content": mensaje_bloqueo})
    else:
        with st.chat_message("assistant"):
            with st.spinner("Zilerios está pensando... 🧠"):
                respuesta = st.session_state.ai_core.generar_texto_extenso(prompt_usuario)
                
                # --- LIMPIADOR AUTOMÁTICO DE ESPACIOS RAROS ---
                respuesta = respuesta.replace(" ,", ",").replace(" .", ".").replace(" !", "!").replace(" ?", "?")
                respuesta = respuesta.replace(" á", "á").replace(" é", "é").replace(" í", "í").replace(" ó", "ó").replace(" ú", "ú")
                respuesta = respuesta.replace("consec uencias", "consecuencias")
                # ----------------------------------------------

                st.write(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})