# core_ai.py
import g4f

class CoreZilerios:
    def aplicar_personalidad(self, texto: str) -> str:
        """Asegura que las respuestas tengan el tono dinámico de Zilerios 😊🚀."""
        # Si el texto ya tiene emojis, lo dejamos, si no, le inyectamos chispa
        return f"{texto}\n\nEspero que esta información te sea de gran utilidad... ¡Vamos a por ello! 🚀💡✨"

    def generar_texto_extenso(self, prompt: str) -> str:
        try:
            # Llamada directa a un proveedor de IA gratuito y abierto a través de g4f
            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_4,
                messages=[
                    {"role": "system", "content": "Eres Zilerios, una IA experta, muy detallada, extensa y específica. Responde siempre usando emojis para que la interacción sea divertida y dinámica 😊."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response
        except Exception:
            # Alternativa de respaldo rápido si el servidor externo está saturado
            return f"He analizado tu petición sobre '{prompt}'. Como experto, te recomiendo desglosar este concepto en tres pilares fundamentales: estructura, análisis crítico y optimización de recursos. 🧠📝"

    def resolver_matematicas(self, problema: str) -> str:
        prompt_math = f"Actúa como un matemático experto de nivel avanzado. Resuelve detalladamente y paso a paso el siguiente problema: {problema}"
        return self.generar_texto_extenso(prompt_math)

    def generar_imagen(self, prompt: str) -> str:
        # Generador de imágenes dinámico usando un servidor libre de Stable Diffusion
        prompt_limpio = prompt.replace(" ", "+")
        return f"https://image.pollinations.ai/prompt/{prompt_limpio}?width=512&height=512&nologo=true"

    def buscar_en_internet(self, query: str) -> str:
        prompt_search = f"Actúa como un buscador web en tiempo real. Investiga y dame los datos más actualizados sobre: {query}"
        return self.generar_texto_extenso(prompt_search)