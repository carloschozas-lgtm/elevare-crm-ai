import os
import smtplib
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración de Entorno
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# CORRECCIÓN FINAL: Usamos el nombre de modelo estándar para máxima estabilidad
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Inteligencia de Negocio (Prompt depurado)
def analizar_lead(datos_lead):
    system_instruction = """
    Eres el Asistente IA de Elevare Consulting.
    Analiza prospectos para el fondo CORFO 'Desarrolla Inversión'.
    
    REGLAS DE NEGOCIO:
    1. Cofinanciamiento: 60% del proyecto.
    2. Tope de Subsidio: $50 millones.
    3. Foco Geográfico: Región del Biobío.
    4. Garantía: Ofrecer siempre la 'Repostulación Gratuita'.
    5. Casos de Éxito:
       - Si es Metalmecánico: Mencionar a Chirino Steel SpA ($61.2MM).
       - Si es Energía/Otros: Mencionar Ingeniería Quantum ($32.5MM).
    6. Firma: Carlos Chozas O., Ingeniero Civil Industrial (MBA).
    """
    
    prompt = f"{system_instruction}\n\nAnaliza este lead y redacta el correo de propuesta: {datos_lead}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generando respuesta IA: {str(e)}"

# 3. Validación Técnica (Matemática limpia sin caracteres extraños)
def evaluar_aptitud_corfo(datos_lead):
    es_apto = True
    observaciones = []

    # Validación Regional
    region_cliente = datos_lead.get("region", "")
    if "Biobío" not in region_cliente and "Biobio" not in region_cliente:
        es_apto = False
        observaciones.append("Empresa fuera de la región foco (Biobío).")

    # Validación Financiera
    try:
        # Aseguramos que la inversión se trate como número puro
        inversion = float(datos_lead.get("inversion", 0))
        subsidio_estimado = inversion * 0.60
        
        if subsidio_estimado > 50000000:
            observaciones.append(f"El subsidio calculado (${subsidio_estimado:,.0f}) supera el tope de $50MM.")
    except ValueError:
        observaciones.append("Error en el formato del monto de inversión.")

    return {"apto": es_apto, "notas": observaciones}

# 4. Motor de Envío de Correos
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
        return f"Fallo en el envío: {str(e)}"

# 5. Ejecución de Prueba
if __name__ == "__main__":
    # Datos de prueba (Caso Real: Maestranza Biobío)
    lead_test = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") # Se envía a tu propio correo para validar
    }

    print(f"--- Iniciando CRM para {lead_test['empresa']} ---")
    
    # Paso 1: Evaluar
    evaluacion = evaluar_aptitud_corfo(lead_test)
    print(f"Estado de Aptitud: {'APTO' if evaluacion['apto'] else 'NO APTO'}")
    
    # Paso 2: Redactar
    print("Generando propuesta con IA...")
    propuesta = analizar_lead(lead_test)
    
    # Paso 3: Enviar
    print("Enviando correo...")
    asunto = f"Oportunidad CORFO para {lead_test['empresa']}"
    resultado = enviar_correo_crm(lead_test["correo"], asunto, propuesta)
    
    print(f"Resultado final: {resultado}")
