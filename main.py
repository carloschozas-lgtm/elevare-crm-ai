import os
import smtplib
import sys
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# FUNCIÓN ROBUSTA: Sistema de selección de modelo con respaldo
def obtener_modelo_activo():
    # Lista de prioridades: Intenta el más rápido primero, luego los respaldos
    modelos_a_probar = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-1.0-pro', 'gemini-pro']
    
    print(f"Probando disponibilidad de modelos IA...")
    for nombre_modelo in modelos_a_probar:
        try:
            # Intentamos instanciar y generar un "Hola" simple para ver si responde
            modelo = genai.GenerativeModel(nombre_modelo)
            modelo.generate_content("Test de conexión")
            print(f"--> ¡Conectado con éxito a {nombre_modelo}!")
            return modelo
        except Exception:
            print(f"--> {nombre_modelo} no disponible, probando siguiente...")
            continue
    
    # Si todo falla, devolvemos None (el código manejará el error sin caerse)
    return None

# Instanciamos el modelo ganador
model = obtener_modelo_activo()

# 2. Inteligencia de Negocio (Prompt Elevare)
def analizar_lead(datos_lead):
    if not model:
        return "Estimado cliente, hemos recibido sus datos y un consultor lo contactará pronto. (Error: Sistema IA en mantenimiento)"

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
        return f"Estimado cliente, gracias por su interés. Un consultor revisará su caso. (Detalle técnico: {str(e)})"

# 3. Validación Técnica
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []
    
    # Validaciones flexibles para evitar errores de tipeo
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

# 4. Envío de Correo (Blindado)
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

    print("--- 1. Evaluando Aptitud ---")
    evaluacion = evaluar_aptitud_corfo(lead_test)
    print(f"Estado: {evaluacion}")

    print("--- 2. Generando Propuesta ---")
    cuerpo = analizar_lead(lead_test)

    print("--- 3. Enviando Correo ---")
    resultado = enviar_correo_crm(lead_test["correo"], f"Propuesta CORFO {lead_test['empresa']}", cuerpo)
    
    print(f"RESULTADO FINAL: {resultado}")
    
    # Forzar error en GitHub solo si el correo NO salió
    if "ERROR_SMTP" in resultado:
        sys.exit(1)
