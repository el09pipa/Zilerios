# app.py
import streamlit as st
import time
import os
import pandas as pd
import json
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from moderation import contiene_lenguaje_inapropiado, obtener_mensaje_bloqueo
from core_ai import CoreZilerios

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Zilerios AI", page_icon="🤖", layout="wide")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Configura la conexión segura con tu Excel en la nube
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# --- FUNCIONES PARA GUARDAR Y CARGAR CHATS DE LA NUBE ---
def cargar_chats_usuario(correo):
    """Busca en el Excel si este usuario ya tiene chats guardados"""
    if conn is None:
        return {"Conversación 1": {"pinned": False, "messages": []}}
    try:
        # Lee la pestaña llamada "Chats"
        df = conn.read(worksheet="Chats", ttl=0)
        # Filtrar solo las filas de este usuario
        df_user = df[df["usuario"] == correo]
        
        if df_user.empty:
            return {"Conversación 1": {"pinned": False, "messages": []}}
        
        # El último registro guardado contiene el JSON de sus chats
        ultimo_registro = df_user.iloc[-1]["historial_json"]
        return json.loads(ultimo_registro)
    except Exception:
        return {"Conversación 1": {"pinned": False, "messages": []}}

def guardar_chats_usuario(correo, chats_dict):
    """Guarda todo el historial de chats del usuario en el Excel"""
    if conn is None:
        return
    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        chats_json = json.dumps(chats_dict, ensure_ascii=False)
        
        # Crear la nueva fila de datos
        nueva_fila = pd.DataFrame([{
            "fecha": fecha_actual,
            "usuario": correo,
            "historial_json": chats_json
        }])
        
        # Leer los datos existentes para no borrarlos
        try:
            df_existente = conn.read(worksheet="Chats", ttl=0)
            df_total = pd.concat([df_existente, nueva_fila], ignore_index=True)
        except Exception:
            df_total = nueva_fila
            
        # Subir la tabla actualizada al Excel
        conn.update(worksheet="Chats", data=df_total)
    except Exception as e:
        print(f"Error al guardar en la nube: {e}")

# --- CONTROL DE ACCESO MEDIANTE FORMULARIO ---
if "usuario_identificado" not in st.session_state:
    st.session_state["usuario_identificado"] = False
if "correo_usuario" not in st.session_state:
    st.session_state["correo_usuario"] = ""

if not st.session_state["usuario_identificado"]:
    st.title("🤖 ¡Bienvenido a Zilerios AI!")
    st.subheader("Acceso Público y Gratuito")
    
    with st.form("registro_entrada"):
        input_correo = st.text_input("Introduce tu Nombre o Correo:", placeholder="Ej: juan@gmail.com o Carlos")
        boton_entrar = st.form_submit_button("🚀 Desbloquear Zilerios AI")
        
        if boton_entrar:
            if input_correo.strip() != "":
                correo_limpio = input_correo.strip().lower()
                st.session_state["correo_usuario"] = correo_limpio
                st.session_state["usuario_identificado"] = True
                
                # ¡MAGIA! Cargamos sus chats guardados en cuanto pone su nombre
                st.session_state["chats"] = cargar_chats_usuario(correo_limpio)
                # Seleccionar el primer chat disponible
                st.session_state["chat_actual"] = list(st.session_state["chats"].keys())[0]
                
                st.success("¡Acceso concedido! Recuperando tus conversaciones...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("⚠️ Por favor, introduce un nombre o correo válido.")
    st.stop()

usuario_actual = st.session_state["correo_usuario"]

# Inicializar componentes del sistema
if "ai_core" not in st.session_state:
    st.session_state.ai_core = CoreZilerios()

RUTA_LOGO = "isotipo_zilerios.png"
NOMBRE_COMPANIA = "Zilerios"

# --- MENÚ LATERAL (SIDEBAR) ---
with st.sidebar:
    col_logo, col_name = st.columns([1, 4])
    with col_logo:
        st.markdown("### 🤖")
    with col_name:
        st.subheader(NOMBRE_COMPANIA)
    
    st.caption(f"Usuario: {usuario_actual} 👤")
    st.divider()
    
    if st.button("➕ Nueva Conversación", use_container_width=True):
        nuevo_numero = len(st.session_state.chats) + 1
        nuevo_nombre = f"Conversación {nuevo_numero}"
        st.session_state.chats[nuevo_nombre] = {"pinned": False, "messages": []}
        st.session_state.chat_actual = nuevo_nombre
        guardar_chats_usuario(usuario_actual, st.session_state.chats) # Guardar cambio en la nube
        st.rerun()

    st.markdown("### 💬 Mis Chats")

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
                    guardar_chats_usuario(usuario_actual, st.session_state.chats)
                    st.rerun()
                
                if st.button(f"🗑️ Borrar", key=f"del_{nombre_chat}"):
                    if len(st.session_state.chats) > 1:
                        del st.session_state.chats[nombre_chat]
                        st.session_state.chat_actual = list(st.session_state.chats.keys())[0]
                        guardar_chats_usuario(usuario_actual, st.session_state.chats) # Actualizar nube
                    else:
                        st.warning("No puedes borrar todos los chats.")
                    st.rerun()

# --- PANTALLA PRINCIPAL ---
st.title(f"⚡ {st.session_state.chat_actual}")

# Renderizar mensajes
for i, msg in enumerate(st.session_state.chats[st.session_state.chat_actual]["messages"]):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "image" in msg:
            st.image(msg["image"])

# Entrada de texto del usuario
prompt_usuario = st.chat_input("Escribe tu petición para Zilerios...")

if prompt_usuario:
    with st.chat_message("user"):
        st.write(prompt_usuario)
    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "user", "content": prompt_usuario})
    
    if contiene_lenguaje_inapropiado(prompt_usuario):
        mensaje_bloqueo = obtener_mensaje_bloqueo()
        with st.chat_message("assistant"):
            st.error(mensaje_bloqueo)
        st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": mensaje_bloqueo})
    else:
        with st.chat_message("assistant"):
            with st.spinner("Zilerios está procesando... 🧠"):
                texto_lower = prompt_usuario.lower()
                if "resolver" in texto_lower or "matematica" in texto_lower or "calcula" in texto_lower:
                    respuesta = st.session_state.ai_core.resolver_matematicas(prompt_usuario)
                elif "imagen" in texto_lower or "dibuja" in texto_lower or "genera un dibujo" in texto_lower:
                    url_img = st.session_state.ai_core.generar_imagen(prompt_usuario)
                    respuesta = "Imagen generada: 🎨"
                    st.image(url_img)
                    st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta, "image": url_img})
                    guardar_chats_usuario(usuario_actual, st.session_state.chats)
                    st.rerun()
                else:
                    respuesta = st.session_state.ai_core.generar_texto_extenso(prompt_usuario)
                
                st.write(respuesta)
                st.session_state.chats[st.session_state.chat_actual]["messages"].append({"role": "assistant", "content": respuesta})
    
    # ¡Guardamos automáticamente en el Excel al terminar la respuesta!
    guardar_chats_usuario(usuario_actual, st.session_state.chats)
    st.rerun()