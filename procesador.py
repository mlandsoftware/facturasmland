import io
import os
import PyPDF2
import json
import xml.etree.ElementTree as ET
from groq import Groq

from dotenv import load_dotenv

load_dotenv()

# Cambia la línea donde estaba tu clave por esto:
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def extraer_datos_xml(xml_bytes):
    """Extrae el contenido de un XML para análisis de la IA."""
    try:
        root = ET.fromstring(xml_bytes)
        return ET.tostring(root, encoding='unicode')
    except Exception:
        return None

def procesar_documento(contenido_bytes, nombre_archivo):
    """Detecta formato y extrae información contable completa de Ecuador."""
    texto_para_ia = ""
    
    # Lectura según el tipo de archivo
    if nombre_archivo.lower().endswith('.pdf'):
        pdf_file = io.BytesIO(contenido_bytes)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            texto_para_ia += page.extract_text() + "\n"
    elif nombre_archivo.lower().endswith('.xml'):
        texto_para_ia = extraer_datos_xml(contenido_bytes)
    
    if not texto_para_ia.strip():
        return {"error": "No se pudo leer el contenido del archivo."}

    # Prompt Premium para máxima extracción de datos
    prompt = f"""
    Actúa como un experto contable senior en Ecuador. Analiza el texto y devuelve un JSON con esta estructura exacta:
    - razon_social_emisor: Nombre legal del negocio.
    - ruc_emisor: RUC de 13 dígitos.
    - clave_acceso: Los 49 dígitos numéricos del SRI.
    - numero_factura: Formato 000-000-000000000.
    - fecha_emision: DD/MM/AAAA.
    - ruc_receptor: RUC o Cédula del cliente.
    - subtotal_15: Valor numérico de la base imponible con IVA.
    - subtotal_0: Valor numérico de la base 0%.
    - valor_iva: Monto del impuesto 15%.
    - importe_total: Valor final cobrado.
    - conceptos: Lista de objetos con [descripcion, cantidad, precio_unitario, total].

    Texto del documento:
    {texto_para_ia}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres un extractor contable especializado en el SRI de Ecuador. Solo respondes en JSON puro."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": f"Error en la IA: {str(e)}"}