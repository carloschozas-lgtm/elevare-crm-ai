import os
import smtplib
from email.message import EmailMessage
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Configuración Inicial
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Función de Inteligencia (IA)
def analizar_lead(datos_lead):
    # Basado en Brochure 2025 y validaciones previas
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting. 
    Analiza prospectos para CORFO 'Desarrolla Inversión'.
    Reglas: 60% cofinanciamiento, Tope $50MM, Foco Biobío.
    """
    prompt = f"{system_instruction}\n\nAnaliza este lead: {datos_lead}"
    response = model.generate_content(prompt)
    return response.text

# 3. La función que me consultaste (Envío de Correo)
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    # Usa los Secrets que configuramos: EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD
    with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    return "Correo enviado con éxito"

# 4. Ejemplo de ejecución lógica
# Aquí es donde el CRM une las piezas para leads como Roberto González
# lead_ejemplo = {...} 
# respuesta = analizar_lead(lead_ejemplo)
# enviar_correo_crm("cliente@correo.com", "Propuesta Elevare", respuesta)

# --- BLOQUE DE PRUEBA REAL ---
if __name__ == "__main__":
    # 1. Datos del Lead de prueba (Biobío)
    lead_test = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "correo": "TU_CORREO_DE_PRUEBA@ejemplo.com" # Cambia esto por tu correo para probar
    }

    print("Generando propuesta con IA...")
    propuesta = analizar_lead(lead_test)
    
    print("Enviando correo...")
    # El asunto incluye la personalización que vimos en AI Studio
    asunto_test = f"Impulsa {lead_test['empresa']}: Financiamiento CORFO"
    
    resultado = enviar_correo_crm(lead_test['correo'], asunto_test, propuesta)
    print(resultado)

def evaluar_aptitud_corfo(datos_lead):
    # Criterios basados en el Brochure 2025
    es_apto = True
    observaciones = []

    # 1. Validación de Región (Foco Biobío)
    if "Biobío" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("Fuera de la Región del Biobío (Foco principal de la consultora).") [cite: 6, 56]

    # 2. Validación de Monto (Tope $50MM de subsidio)
    subsidio_estimado = datos_lead.get("inversion", 0) * 0.60 [cite: 44, 45]
    if subsidio_estimado > 50000000:
        observaciones.append(f"Subsidio estimado (${subsidio_estimado:,.0f}) supera el tope de $50MM.") [cite: 47]

    # 3. Validación de Rubro Estratégico
    rubros_exito = ["Metalmecánico", "Energético"] [cite: 55]
    if datos_lead.get("rubro") not in rubros_exito:
        observaciones.append("Rubro no coincide con casos de éxito recientes (requiere análisis manual).") [cite: 51, 55]

    return {
        "apto": es_apto,
        "puntuacion": "ALTA" if es_apto else "REVISIÓN",
        "notas": observaciones
    }
