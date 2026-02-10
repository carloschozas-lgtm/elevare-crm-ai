import os
import smtplib
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración
load_dotenv()
# Configura la API con la clave guardada en GitHub Secrets
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# CORRECCIÓN DEFINITIVA: Usamos el nombre estándar del modelo para evitar el error 404
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Lógica de Negocio (IA)
def analizar_lead(datos_lead):
    # Instrucciones limpias basadas en el Brochure 2025
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting.
    Analiza prospectos para el fondo CORFO 'Desarrolla Inversión'.
    REGLAS:
    - Cofinanciamiento: 60% del proyecto.
    - Tope: $50 millones.
    - Foco: Región del Biobío.
    - Garantía: Menciona la Repostulación Gratuita.
    - Caso de Éxito Metalmecánico: Chirino Steel SpA ($61.2MM).
    - Firma: Carlos Chozas O., Ingeniero Civil Industrial (MBA).
    """
    prompt = f"{system_instruction}\n\nAnaliza este lead: {datos_lead}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar propuesta IA: {str(e)}"

# 3. Lógica de Validación (Matemática)
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []

    # Validación Regional
    if "Biobío" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("Fuera de la Región del Biobío.")

    # Validación Financiera (CORREGIDO: Sin caracteres extraños)
    inversion = float(datos_lead.get("inversion", 0))
    subsidio_estimado = inversion * 0.60
    
    if subsidio_estimado > 50000000:
        observaciones.append(f"El subsidio calculado (${subsidio_estimado:,.0f}) supera el tope de $50MM.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Envío de Correo
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
            smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        return "Correo enviado exitosamente"
    except Exception as e:
        return f"Error de envío: {str(e)}"

# 5. Ejecución de Prueba
if __name__ == "__main__":
    # Datos de prueba reales (Maestranza Biobío)
    lead_ejemplo = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") # Se envía a tu propio correo para validar
    }

    print(f"1. Evaluando aptitud para {lead_ejemplo['empresa']}...")
    aptitud = evaluar_aptitud_corfo(lead_ejemplo)
    print(f"Resultado técnico: {aptitud}")

    print("2. Redactando correo con IA...")
    cuerpo_mail = analizar_lead(lead_ejemplo)

    print("3. Enviando correo...")
    asunto = f"Propuesta CORFO: {lead_ejemplo['empresa']}"
    resultado = enviar_correo_crm(lead_ejemplo["correo"], asunto, cuerpo_mail)
    
    print(f"--- {resultado} ---")
