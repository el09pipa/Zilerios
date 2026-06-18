# app.py
import streamlit as st
import time
import os
from moderation import contiene_lenguaje_inapropiado, obtener_mensaje_bloqueo
from core_ai import CoreZilerios

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Zilerios AI", page_icon="🤖", layout="wide")

# Inicializar el núcleo de la IA de forma segura en la sesión
if "ai_core" not in st.session_state:
    st.session_state.ai_core = CoreZilerios()

RUTA_LOGO = "isotipo_zilerios.png"
NOMBRE_COMPANIA = "Zilerios"

# --- 1. PANTALLA DE CARGA ---
if "app_inicializada" not in st.session_state:
    with st.spinner("Iniciando ecosistema Zilerios... 🚀"):
        time.sleep(1.0)
    st.session_state["app_inicializada"] = True

# --- GESTIÓN DEL HISTORIAL (CHATS INFINITOS) ---
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Conversación 1": {"pinned": False, "messages": []}
    }
if "chat_actual" not in st.session_state:
    st.session_state.chat_actual = "Conversación 1"

# --- 2. MENÚ LATERAL (SIDEBAR) ---
with st.sidebar:
    # Cabecera: Logo o Emoji
    col_logo, col_name = st.columns([1, 4])
    with col_logo:
        if os.path.exists(RUTA_LOGO):
            st.image(RUTA_LOGO, width=40)
        else:
            st.markdown("### 🤖")
    with col_name:
        st.subheader(NOMBRE_COMPANIA)
    
    st.divider()
    
    # Botón para añadir chats infinitos
    if st.button("➕ Nueva Conversación", use_container_width=True):
        nuevo_numero = len(st.session_state.chats) + 1
        nuevo_nombre = f"Conversación {nuevo_numero}"
        st.session_state.chats[nuevo_nombre] = {"pinned": False, "messages": []}
        st.session_state.chat_actual = nuevo_nombre
        st.rerun()

    st.markdown("### 💬 Mis Chats")

    # Listar chats en la barra lateral
    for nombre_chat, info in list(st.session_state.chats.items()):
        prefix = "📌 " if info["pinned"] else "💬 "
        col_btn, col_menu = st.columns([4, 1])
        
        with col_btn:
            tipo_boton = "primary" if st.session_state.chat_actual == nombre_chat else "secondary"
            if st.button(f"{prefix}{nombre_chat}", key=f"sidebar_sel_{nombre_chat}", use_container_width=True, type=tipo_boton):
                st.session_state.chat_actual = nombre_chat
                st.rerun()
        
        with col_menu:
            with st.popover("⋮"):
                label_pin = "Desfijar" if info["pinned"] else "Fijar"
                if st.button(f"📌 {label_pin}", key=f"pin_{nombre_chat}"):
                    st.session_state.chats[nombre_chat]["pinned"] = not info["pinned"]
                    st.rerun()
                
                if st.button(f"🗑️ Borrar", key=f"del_{nombre_chat}"):
                    if len(st.session_state.chats) > 1:
                        del st.session_state.chats[nombre_chat]
                        st.session_state.chat_actual = list(st.session_state.chats.keys())[0]
                    else:
                        st.warning("No puedes borrar todos los chats.")
                    st.rerun()

# --- 3. PANTALLA PRINCIPAL DEL CHAT ---
st.title(f"⚡ {st.session_state.chat_actual}")

# RENDERIZAR HISTORIAL DE MENSAJES GUARDADOS
# Usamos el nombre exacto del chat actual para evitar duplicación de llaves (keys)
for i, msg in enumerate(st.session_state.chats[st.session_state.chat_actual]["messages"]):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image" in msg:
            st.image(msg["image"])
        
        # Sistema de Feedback (Botones 👍 / 👎) con llaves 100% únicas
        if msg["role"] == "assistant":
            col_f1, col_f2, _ = st.columns([1, 1, 15])
            id_unico_boton = f"{st.session_state.chat_actual}_{i}"
            with col_f1:
                if st.button("👍", key=f"up_{id_unico_boton}"):
                    st.toast("¡Gracias! Guardamos tu valoración positiva. 😊")
            with col_f2:
                if st.button("👎", key=f"down_{id_unico_boton}"):
                    st.toast("Tomamos nota para mejorar la respuesta. 🛠️")

# Caja de herramientas multimedia (Cámara y Archivos)
with st.expander("📁 Adjuntar Archivos o usar Cámara", expanded=False):
    col_files, col_cam = st.columns(2)
    with col_files:
        archivo_subido = st.file_uploader("Sube PDF, Word o Imágenes", type=["pdf", "docx", "png", "jpg"])
    with col_cam:
        foto_camara = st.camera_input("Capturar desde la cámara")

# BARRA DE ENTRADA DE TEXTO (CHAT INPUT)
prompt_usuario = st.chat_input("Escribe tu petición para Zilerios...")

if prompt_usuario:
    # 1. Mostrar inmediatamente el mensaje del usuario en la pantalla y guardarlo
    with st.chat_message("user"):
        st.write(prompt_usuario)
    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "user", "content": prompt_usuario})
    
    # 2. Filtro de moderación
    if contiene_lenguaje_inapropiado(prompt_usuario):
        mensaje_bloqueo = obtener_mensaje_bloqueo()
        with st.chat_message("assistant"):
            st.error(mensaje_bloqueo)
        st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": mensaje_bloqueo})
    
    # 3. Procesar respuesta de la IA en tiempo real
    else:
        with st.chat_message("assistant"):
            with st.spinner("Zilerios está procesando tu solicitud... 🧠"):
                texto_lower = prompt_usuario.lower()
                
                # Enrutamiento de respuestas
                if "resolver" in texto_lower or "matematica" in texto_lower or "calcula" in texto_lower:
                    respuesta = st.session_state.ai_core.resolver_matematicas(prompt_usuario)
                    st.write(respuesta)
                    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta})
                
                elif "imagen" in texto_lower or "dibuja" in texto_lower or "genera un dibujo" in texto_lower:
                    url_img = st.session_state.ai_core.generar_imagen(prompt_usuario)
                    respuesta = "He procesado tu prompt y generado la siguiente imagen artística para ti: 🎨"
                    st.write(respuesta)
                    st.image(url_img)
                    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta, "image": url_img})
                
                elif "busca" in texto_lower or "internet" in texto_lower or "web" in texto_lower:
                    respuesta = st.session_state.ai_core.buscar_en_internet(prompt_usuario)
                    st.write(respuesta)
                    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta})
                
                else:
                    respuesta = st.session_state.ai_core.generar_texto_extenso(prompt_usuario)
                    st.write(respuesta)
                    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta})
    
    # Forzar recarga limpia para dibujar los nuevos botones de feedback con sus IDs correctos
    st.rerun()