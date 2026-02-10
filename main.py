import os
import smtplib
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración Inicial
load_dotenv()
# Configuramos la API Key desde los Secrets de GitHub
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Cambiamos a 'gemini-1.5-flash-latest' o 'gemini-pro' para asegurar compatibilidad
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Función de Inteligencia (IA)
def analizar_lead(datos_lead):
    # [cite_start]Instrucciones basadas en el Brochure 2025 de Elevare Consulting [cite: 1, 2, 44, 47, 56]
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting. Tu misión es analizar prospectos para el programa CORFO 'Desarrolla Inversión'.
    REGLAS DE NEGOCIO:
    - [cite_start]Cofinanciamiento: Máximo 60% del proyecto[cite: 44, 45].
    - [cite_start]Tope de Subsidio: $50 millones de pesos[cite: 47].
    - [cite_start]Foco Geográfico: Región del Biobío[cite: 6, 56].
    - [cite_start]Casos de Éxito: Si el rubro es Metalmecánico, cita a Chirino Steel SpA ($61.2MM adjudicados)[cite: 55, 61, 67].
    - [cite_start]Garantía: Menciona la 'Repostulación Gratuita'[cite: 23, 24].
    - [cite_start]Firma: Carlos Chozas O., Ingeniero Civil Industrial (MBA)[cite: 76, 77].
    """
    prompt = f"{system_instruction}\n\nAnaliza este prospecto y genera una respuesta persuasiva: {datos_lead}"
    response = model.generate_content(prompt)
    return response.text

# 3. Función de Evaluación Técnica
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []
    
    # [cite_start]Validación de Región [cite: 6, 56]
    if "Biobío" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("La empresa no registra domicilio en la Región del Biobío.")

    # [cite_start]Validación de Monto de Subsidio [cite: 44, 47]
    # Se corrige error de sintaxis previo: inversión es un número directo.
    inversion = datos_lead.get("inversion", 0)
    subsidio_estimado = inversion * 0.60
    
    if subsidio_estimado > 50000000:
        observaciones.append(f"El subsidio proyectado (${subsidio_estimado:,.0f}) excede el tope de $50MM.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Función de Envío de Correo
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    # Conexión usando los Secrets configurados
    with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    return "Envío exitoso"

# 5. Ejecución de Prueba
if __name__ == "__main__":
    lead_ejemplo = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") # Se envía a ti mismo para la prueba
    }
    
    print("Iniciando evaluación...")
    aptitud = evaluar_aptitud_corfo(lead_ejemplo)
    
    print("Generando propuesta con IA...")
    cuerpo_mail = analizar_lead(lead_ejemplo)
    
    print("Despachando correo...")
    resultado = enviar_correo_crm(lead_ejemplo["correo"], "Propuesta Elevare - CORFO", cuerpo_mail)
    print(f"Resultado final: {resultado}")
