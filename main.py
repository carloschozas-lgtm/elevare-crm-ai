import os
import smtplib
import sys
import google.generativeai as genai
from email.message import EmailMessage
from dotenv import load_dotenv

# 1. Configuración de Entorno
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 2. Selección de Modelo (Prioridad: Flash -> Pro)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# 3. EL CEREBRO DE ELEVARE (Integración del Prompt Maestro)
def analizar_lead(datos_lead):
    # AQUÍ ESTÁ LA MAGIA: El Prompt de NotebookLM
    system_instruction = """
    🤖 ROL: Eres el Consultor Senior de Elevare Consulting, experto en subsidios CORFO (Biobío).
    
    BASE DE CONOCIMIENTO Y REGLAS DE NEGOCIO:
    1. FILTROS:
       - Foco: Empresas ventas 2.400 UF - 100.000 UF (PyME).
       - Inversión Mínima: $12.000.000 CLP.
       - Región: Prioridad Biobío.
    
    2. OFERTA DE VALOR (Brochure 2025):
       - Subsidio: 60% cofinanciamiento.
       - Tope: $50.000.000.
       - Beneficio: Opción de anticipo para flujo de caja.
    
    3. MODELO TÉCNICO (Estándar "Quantum"):
       - No vendas "máquinas", vende "soluciones productivas" (Eficiencia Energética, Reducción de Costos).
       - Usa keywords: "Ley 21.305", "Aumento de productividad".
    
    4. ESTRUCTURA COMERCIAL:
       - Paso 1: Diagnóstico de Elegibilidad (30 min, Gratis).
       - Honorarios: $1.000.000 + IVA (Fijo) + 10% Success Fee (Éxito).
       - Garantía: Repostulación gratuita si no adjudica.
    
    5. CASOS DE ÉXITO:
       - Menciona: Cister Energy, Chirino Steel ($61.2MM), Ingeniería Quantum ($32.5MM).
       - Total adjudicado histórico: +$225 Millones.
    
    TAREA: Redacta un correo persuasivo para el cliente analizando sus datos.
    TONO: Ejecutivo, experto, orientado a resultados.
    """
    
    prompt = f"{system_instruction}\n\nDATOS DEL LEAD A ANALIZAR:\n{datos_lead}"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Alerta IA: {e}. Usando respaldo.")
        return f"""
Estimado/a {datos_lead.get('representante', 'Cliente')},

Le escribo desde Elevare Consulting. Según nuestro análisis preliminar, su empresa podría calificar para el subsidio "Desarrolla Inversión" de CORFO (Tope $50MM, cofinanciamiento 60%).

En Elevare hemos gestionado más de $225 millones en adjudicaciones, incluyendo casos de éxito en su sector. Nuestro modelo incluye un Diagnóstico de Elegibilidad gratuito y garantía de repostulación costo cero.

Me gustaría agendar una breve reunión de 15 minutos para validar si su nivel de ventas y proyecto cumplen con los requisitos técnicos.

Atentamente,
Carlos Chozas O.
Elevare Consulting
"""

# 4. Validación Técnica (Reglas de Negocio Duras)
def evaluar_aptitud(datos_lead):
    es_apto = True
    notas = []
    
    # Regla 1: Territorialidad (Biobío)
    region = datos_lead.get("region", "").lower()
    if "biobío" not in region and "biobio" not in region:
        es_apto = False
        notas.append("Fuera de zona preferente (Biobío).")

    # Regla 2: Piso de Inversión ($12MM según Prompt Maestro)
    try:
        inversion = float(datos_lead.get("inversion", 0))
        if inversion < 12000000:
            es_apto = False # Ojo: Aquí marcamos como NO APTO si es muy poco
            notas.append("Inversión bajo el mínimo rentable ($12MM).")
        
        # Cálculo informativo del subsidio
        subsidio = min(inversion * 0.60, 50000000)
        notas.append(f"Subsidio potencial: ${subsidio:,.0f}")
        
    except:
        notas.append("Error en formato de monto.")

    return {"apto": es_apto, "notas": notas}

# 5. Motor de Envío (SMTP)
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
        return "EXITO: Correo enviado correctamente."
    except Exception as e:
        return f"ERROR CRITICO SMTP: {str(e)}"

# 6. Ejecución de Prueba
if __name__ == "__main__":
    # Lead de Prueba (Datos Reales para validar el Prompt)
    lead = {
        "empresa": "Maestranza Biobío Limitada",
        "representante": "Roberto González",
        "rubro": "Metalmecánico",
        "ventas_uf": 5000, # Dato nuevo para validar filtro PyME
        "inversion": 60000000,
        "region": "Región del Biobío",
        "correo": os.getenv("EMAIL_USER") 
    }

    print(f"--- 1. Analizando Aptitud: {lead['empresa']} ---")
    evaluacion = evaluar_aptitud(lead)
    print(f"Resultado Técnico: {evaluacion}")

    print("--- 2. Consultor Senior Redactando Propuesta ---")
    cuerpo_final = analizar_lead(lead)

    if evaluacion['apto']:
        print("--- 3. Enviando Correo ---")
        resultado = enviar_correo(lead["correo"], f"Evaluación CORFO: {lead['empresa']}", cuerpo_final)
        print(resultado)
    else:
        print("ALERTA: El lead no cumple criterios mínimos. No se envió correo.")
        
    if "ERROR CRITICO" in str(evaluacion) or (evaluacion['apto'] and "ERROR" in resultado):
        sys.exit(1)
