# moderation.py

# Lista negra básica para la demostración (en producción usar una API de moderación dedicada)
PROFANITY_LIST = ["insulto1", "palabratajo", "ofensa", "mierda"] 

def contiene_lenguaje_inapropiado(texto: str) -> bool:
    """Verifica si el usuario ha introducido términos prohibidos."""
    if not texto:
        return False
    texto_minuscula = texto.lower()
    return any(palabra in texto_minuscula for palabra in PROFANITY_LIST)

def obtener_mensaje_bloqueo() -> str:
    return "Lo siento, pero he detectado lenguaje inapropiado. Como IA, estoy programada para mantener un entorno de respeto, por lo que no puedo responder a este tipo de mensajes."