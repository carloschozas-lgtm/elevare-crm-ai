import os
import smtplib
import sys
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Usamos el modelo estándar. Al actualizar Python a 3.10 en el workflow, esto funcionará.
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. IA Generativa (Prompt Elevare)
def analizar_lead(datos_lead):
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting.
    Analiza prospectos para CORFO 'Desarrolla Inversión'.
    REGLAS:
    1. Cofinanciamiento: 60%.
    2. Tope: $50 millones.
    3. Foco: Región del Biobío.
    4. Casos de Éxito:
       - Metalmecánico: Chirino Steel SpA ($61.2MM).
       - Otros: Ingeniería Quantum ($32.5MM).
    5. Firma: Carlos Chozas O.
    """
    prompt = f"{system_instruction}\n\nRedacta propuesta para: {datos_lead}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Si falla la IA, devolvemos el error técnico para verlo en el correo
        return f"Error generando IA: {str(e)}"

# 3. Validación Técnica
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []
    
    region = datos_lead.get("region", "").lower()
    if "biobío" not in region and "biobio" not in region:
        es_apto = False
        observaciones.append("Fuera de región Biobío.")

    try:
        inversion = float(datos_lead.get("inversion", 0))
        if (inversion * 0.60) > 50000000:
            observaciones.append("Subsidio supera tope $50MM.")
    except:
        observaciones.append("Error en formato de monto.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Envío de Correo (Ya validado y funcionando)
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
        return "EXITO"
    except Exception as e:
        return f"ERROR_SMTP: {str(e)}"

# 5. Ejecución Principal
if __name__ == "__main__":
    lead_test = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") 
    }

    print("--- 1. Generando Propuesta con IA ---")
    cuerpo = analizar_lead(lead_test)

    print("--- 2. Enviando Correo ---")
    resultado = enviar_correo_crm(lead_test["correo"], f"Propuesta CORFO {lead_test['empresa']}", cuerpo)
    
    print(f"RESULTADO FINAL: {resultado}")
    
    if "ERROR_SMTP" in resultado:
        sys.exit(1)
