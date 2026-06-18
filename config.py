# config.py
import os

# UI/UX Placeholders
RUTA_LOGO = "isotipo_zilerios.png"
NOMBRE_COMPANIA = "Zilerios Tech Corp"

# Configuración de Rendimiento
TIMEOUT_LIMIT = 10.0  # Límite estricto de 10 segundos

# API Keys (Simuladas - Reemplazar con variables de entorno reales)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "tu_api_key_aquí")