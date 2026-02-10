import os
import smtplib
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración de Seguridad y API
load_dotenv()
# Se utilizan los Secrets configurados en GitHub 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Usamos la versión de producción más estable para evitar errores de modelo no encontrado [cite: 14, 17]
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 2. Inteligencia de Negocio para Elevare Consulting
def analizar_lead(datos_lead):
    # Instrucciones precisas extraídas de tu Brochure 2025 [cite: 1]
    system_instruction = """
    Eres el Asistente IA Senior de Elevare Consulting. Tu misión es analizar prospectos para el programa CORFO 'Desarrolla Inversión'.
    REGLAS ESTRICTAS:
    - Cofinanciamiento: Máximo 60% del proyecto[cite: 1].
    - Tope de Subsidio: $50 millones de pesos[cite: 1].
    - Región: Enfoque principal en la Región del Biobío[cite: 1].
    - Casos de Éxito: Para el rubro Metalmecánico, cita a Chirino Steel SpA ($61.2MM adjudicados)[cite: 1].
    - Garantía: Menciona siempre la 'Repostulación Gratuita'[cite: 1].
    - Firma: Carlos Chozas O., Ingeniero Civil Industrial (MBA).
    """
    prompt = f"{system_instruction}\n\nAnaliza este lead y genera una propuesta persuasiva: {datos_lead}"
    response = model.generate_content(prompt)
    return response.text

# 3. Evaluación Técnica de Aptitud
def evaluar_aptitud_corfo(datos_lead):
    # Los datos se validan según los estándares de Elevare [cite: 1, 3]
    es_apto = True
    observaciones = []
    
    # Validación de Región [cite: 1]
    if "Biobío" not in datos_lead.get("region", ""):
        es_apto = False
        observaciones.append("La empresa no registra domicilio en la Región del Biobío.")

    # Cálculo de Subsidio (Se asegura el manejo de números limpios) [cite: 1]
    inversion = float(datos_lead.get("inversion", 0))
    subsidio_estimado = inversion * 0.60
    
    if subsidio_estimado > 50000000:
        observaciones.append(f"El subsidio proyectado (${subsidio_estimado:,.0f}) excede el tope de $50MM.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Motor de Envío de Email Profesional
def enviar_correo_crm(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = asunto
    msg['From'] = os.getenv("EMAIL_USER")
    msg['To'] = destinatario

    # Conexión Segura vía SMTP SSL con tus credenciales 
    with smtplib.SMTP_SSL(os.getenv("EMAIL_HOST"), 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)
    return "Envío exitoso"

# 5. Ejecución del Flujo de Prueba Real
if __name__ == "__main__":
    # Lead basado en los datos del Analizador de Leads [cite: 3]
    lead_ejemplo = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") # Envío a tu propia cuenta para validar 
    }
    
    print(f"Evaluando aptitud para {lead_ejemplo['empresa']}...")
    aptitud = evaluar_aptitud_corfo(lead_ejemplo)
    
    print("Generando comunicación con IA...")
    cuerpo_mail = analizar_lead(lead_ejemplo)
    
    print("Despachando propuesta...")
    resultado = enviar_correo_crm(lead_ejemplo["correo"], "Propuesta Estratégica CORFO - Elevare", cuerpo_mail)
    print(f"Resultado Final: {resultado}")
