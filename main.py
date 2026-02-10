import os
import smtplib
import sys
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración Básica
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Motor de Redacción (Estrategia: Clásico -> Respaldo Manual)
def generar_propuesta_blindada(datos_lead):
    # Intentamos primero con la IA "Clásica" (gemini-pro) que es más compatible
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        system_instruction = """
        Eres Carlos Chozas, consultor senior en Elevare.
        Redacta un correo corto y directo para ofrecer gestión de fondos CORFO 'Desarrolla Inversión'.
        Puntos clave:
        - Cofinanciamiento del 60% para su proyecto.
        - Tope $50.000.000.
        - Experiencia en Región del Biobío.
        - Si es rubro Metalmecánico, menciona el éxito de Chirino Steel SpA.
        - Ofrece una reunión de diagnóstico de 15 min.
        """
        prompt = f"{system_instruction}\n\nCliente: {datos_lead['empresa']}, Rubro: {datos_lead['rubro']}"
        
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Alerta: IA no disponible ({e}). Usando plantilla de respaldo.")
        # SI LA IA FALLA, USA ESTE TEXTO PRE-ESCRITO DE ALTA CALIDAD
        # Así el cliente nunca recibe un error.
        return f"""
Estimado/a {datos_lead['representante']},

Le escribo desde Elevare Consulting. Hemos analizado el perfil de {datos_lead['empresa']} y detectamos que su proyecto de inversión podría calificar para el programa "Desarrolla Inversión" de CORFO.

Este fondo permite cofinanciar hasta el 60% de activos fijos con un tope de $50 millones. En la Región del Biobío ya hemos apoyado exitosamente a empresas del sector {datos_lead['rubro']} (como Chirino Steel SpA) para adjudicarse estos recursos.

Me gustaría agendar una breve llamada de 10 minutos para validar su elegibilidad técnica sin costo.

Quedo atento,

Carlos Chozas O.
Ingeniero Civil Industrial (MBA)
Elevare Consulting
        """

# 3. Validación Técnica (Simplificada para evitar errores)
def evaluar_aptitud(datos_lead):
    es_apto = True
    notas = []
    
    # Si no es Biobío, marcamos observación pero NO detenemos el proceso
    if "Biobío" not in datos_lead.get("region", "") and "Biobio" not in datos_lead.get("region", ""):
        es_apto = False
        notas.append("Ubicación fuera de zona preferente.")

    return {"apto": es_apto, "notas": notas}

# 4. Envío de Correo (Tu conexión SMTP ya funciona perfecto)
def enviar_correo(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
            smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
        return "CORREO_ENVIADO_OK"
    except Exception as e:
        return f"ERROR_SMTP: {str(e)}"

# 5. Ejecución
if __name__ == "__main__":
    # Datos de prueba
    lead = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER")
    }

    print("--- 1. Generando Propuesta ---")
    # Esta función NUNCA devolverá error, devolverá texto de IA o texto manual
    cuerpo_final = generar_propuesta_blindada(lead)

    print("--- 2. Enviando Correo ---")
    resultado = enviar_correo(lead["correo"], f"Oportunidad CORFO: {lead['empresa']}", cuerpo_final)
    
    print(f"RESULTADO: {resultado}")
    
    if "ERROR" in resultado:
        sys.exit(1)
