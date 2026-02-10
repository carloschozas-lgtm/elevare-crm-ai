import os
import smtplib
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración de Seguridad
load_dotenv()
# Se utiliza la API Key configurada en GitHub Secrets
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Usamos 'gemini-1.5-flash-latest' para asegurar la compatibilidad con la API v1beta
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. Inteligencia de Negocio (IA)
def analizar_lead(datos_lead):
    # Instrucciones precisas basadas en el Brochure 2025 de Elevare Consulting
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting. Tu misión es analizar prospectos para el programa CORFO 'Desarrolla Inversión'.
    REGLAS ESTABLECIDAS:
    - Cofinanciamiento: Hasta el 60% del proyecto.
    - Tope de Subsidio: $50 millones.
    - Ubicación: Foco en la Región del Biobío.
    - Prueba Social: Si es rubro Metalmecánico, cita a Chirino Steel SpA ($61.2MM adjudicados).
    - Garantía: Incluir siempre la política de 'Repostulación Gratuita'.
    - Firma: Carlos Chozas O., Ingeniero Civil Industrial (MBA).
    """
    prompt = f"{system_instruction}\n\nAnaliza este lead y genera el correo: {datos_lead}"
    response = model.generate_content(prompt)
    return response.text

# 3. Evaluación de Aptitud Técnica
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []
    
    # Validación Geográfica
    if "Biobío" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("La empresa no opera en la Región del Biobío.")

    # Cálculo de Subsidio (Se corrige sintaxis para evitar errores de 'float')
    inversion = datos_lead.get("inversion", 0)
    subsidio_estimado = inversion * 0.60
    
    if subsidio_estimado > 50000000:
        observaciones.append(f"El monto de subsidio (${subsidio_estimado:,.0f}) excede el límite de $50MM.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Motor de Envío de Email
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    # Conexión Segura vía SMTP SSL
    with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    return "Correo despachado con éxito"

# 5. Ejecución del Flujo de Prueba
if __name__ == "__main__":
    # Datos de Maestranza Biobío validados en el analizador
    lead_ejemplo = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") # Envío a tu propia cuenta para verificar
    }
    
    print(f"Iniciando evaluación para: {lead_ejemplo['empresa']}...")
    aptitud = evaluar_aptitud_corfo(lead_ejemplo)
    
    print("Generando propuesta personalizada con IA...")
    cuerpo_mail = analizar_lead(lead_ejemplo)
    
    print("Enviando comunicación...")
    # El asunto refleja el potencial de expansión en Coronel
    asunto_mail = f"Impulsa {lead_ejemplo['empresa']}: Financiamiento CORFO"
    resultado = enviar_correo_crm(lead_ejemplo["correo"], asunto_mail, cuerpo_mail)
    
    print(f"Estado Final: {resultado}")
