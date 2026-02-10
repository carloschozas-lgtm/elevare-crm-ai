import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargar configuración segura
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Configurar el modelo (Gemini 1.5 Flash para eficiencia)
model = genai.GenerativeModel('gemini-1.5-flash')

def analizar_lead(datos_lead):
    # Instrucción maestra basada en el Brochure 2025
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting. Tu tarea es analizar prospectos para CORFO.
    REGLAS: Cofinanciamiento 60%, Tope $50MM, Foco en Activos Fijos y Región del Biobío.
    """
    prompt = f"{system_instruction}\n\nAnaliza este lead: {datos_lead}"
    response = model.generate_content(prompt)
    return response.text
