import os
import smtplib
import sys # Vital para reportar errores a GitHub
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
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
        return f"Error IA: {str(e)}"

# 3. Validación Técnica
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []
    
    if "Biobío" not in datos_lead.get("region", "") and "Biobio" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("Fuera de región Biobío.")

    try:
        inversion = float(datos_lead.get("inversion", 0))
        if (inversion * 0.60) > 50000000:
            observaciones.append("Subsidio supera tope $50MM.")
    except:
        observaciones.append("Error en monto.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Envío de Correo (Con Reporte de Error Real)
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    try:
        print(f"Conectando a servidor SMTP...")
        # Aquí se usa la Contraseña de Aplicación que pusiste en Secrets
        with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
            smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        return "EXITO"
    except Exception as e:
        # Imprime el error para que lo leamos en los logs
        print(f"ERROR DETALLADO: {e}")
        return "FALLO"

# 5. Ejecución
if __name__ == "__main__":
    lead_test = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") 
    }

    print("--- 1. Evaluando ---")
    evaluacion = evaluar_aptitud_corfo(lead_test)
    
    print("--- 2. Generando Texto ---")
    cuerpo = analizar_lead(lead_test)

    print("--- 3. Enviando Correo ---")
    resultado = enviar_correo_crm(lead_test["correo"], f"Test CORFO {lead_test['empresa']}", cuerpo)
    
    print(f"RESULTADO FINAL: {resultado}")

    # SI FALLÓ, OBLIGAMOS A GITHUB A MARCAR ERROR ROJO
    if resultado == "FALLO":
        sys.exit(1)
