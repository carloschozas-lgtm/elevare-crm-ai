import os
import smtplib
import sys
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Selección del Modelo (Usamos el nombre técnico oficial y estable)
# NOTA: Usamos 'gemini-1.5-flash' porque es el estándar actual para API.
# Si este fallara por alguna razón, el bloque try/except usará un respaldo manual.
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# 3. Función de Inteligencia (Con respaldo de seguridad)
def analizar_lead(datos_lead):
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting.
    Objetivo: Redactar correo para ofrecer gestión de fondos CORFO 'Desarrolla Inversión'.
    Datos clave a incluir:
    - Cofinanciamiento: 60%.
    - Tope: $50.000.000.
    - Foco: Región del Biobío.
    - Caso de éxito: Chirino Steel SpA (si es metalmecánico).
    - Llamada a la acción: Reunión de 15 min.
    """
    prompt = f"{system_instruction}\n\nCliente: {datos_lead}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Alerta Técnica: {e}. Usando mensaje de respaldo.")
        # Si la IA falla, enviamos este mensaje profesional automáticamente
        return f"""
Estimado/a {datos_lead.get('representante', 'Cliente')},

Le escribo desde Elevare Consulting. Hemos detectado que su empresa podría calificar para el fondo "Desarrolla Inversión" de CORFO, el cual cofinancia hasta el 60% de activos fijos (Tope $50MM).

En la Región del Biobío hemos gestionado exitosamente estos fondos para empresas de su sector. Me gustaría agendar una breve reunión para evaluar su elegibilidad sin costo.

Atentamente,
Carlos Chozas O.
Elevare Consulting
"""

# 4. Validación Técnica
def evaluar_aptitud(datos_lead):
    es_apto = True
    notas = []
    
    # Validación simple de región
    if "Biobío" not in datos_lead.get("region", "") and "Biobio" not in datos_lead.get("region", ""):
        es_apto = False
        notas.append("Fuera de zona preferente.")
        
    return {"apto": es_apto, "notas": notas}

# 5. Envío de Correo (SMTP)
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
        return "EXITO: Correo enviado"
    except Exception as e:
        return f"ERROR CRITICO SMTP: {str(e)}"

# 6. Ejecución Principal
if __name__ == "__main__":
    # Datos del Lead (Maestranza Biobío)
    lead = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") 
    }

    print("--- Generando Propuesta ---")
    cuerpo_final = analizar_lead(lead)

    print("--- Enviando Correo ---")
    resultado = enviar_correo(lead["correo"], f"Oportunidad CORFO: {lead['empresa']}", cuerpo_final)
    
    print(resultado)
    
    # Forzamos error en GitHub solo si falla el envío del correo (lo importante)
    if "ERROR CRITICO" in resultado:
        sys.exit(1)
