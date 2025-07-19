import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import config
from db import get_user_preferred_language

# Cargar variables de entorno del archivo .env
load_dotenv()
PAGESPEED_API_KEY = os.environ.get("PAGESPEED_API_KEY")

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_system_message(db, user_id):
    # Obtener el idioma preferido del usuario
    preferred_language = get_user_preferred_language(db, user_id)
    if not preferred_language:
        preferred_language = 'en'  # Default to English

    # Mapear el código de idioma a un nombre legible
    language_names = {
        "en": "English",
        "es": "Spanish",
        "pt": "Portuguese",
        "fr": "French"
    }
    lang_name = language_names.get(preferred_language, "English")

    # Obtener el nombre del usuario
    try:
        cursor = db.connection.cursor()
        cursor.execute("SELECT display_name FROM users WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            display_name = result[0]
        else:
            display_name = "User"
    except Exception as e:
        display_name = "User"

    # Construir el mensaje del sistema con el idioma y nombre del usuario
    system_message = (
        "My name is DEREK, and I am a virtual digital marketing consultant. I was developed in the Digital R&D laboratory. "
        "I specialize in marketing, product development, and online sales strategies. I will answer questions as an expert in Digital Marketing, "
        "Growth Hacking, Branding, SEO, PPC, Social Media, CRO, Neuromarketing, and web traffic generation. My priority is to help companies "
        "increase the ROI of their websites, mobile applications, and digital strategies. I was initially programmed by Jonnathan Peña as part of the "
        "Nexus Metrics project 'An AI-powered Unified Marketing Platform', which was conceived on January 2, 2024. For more information about the company, "
        "our current research projects, and to hire Weblifetech's services, please contact marketing@weblifetech.com, call +593982541659, or visit weblifetech.com. "
        "You must provide short answers. Also, please note that the user's name is {} and they prefer that all responses be in {}. Please, always respond in {}. "
        "Eres un experto en marketing digital, desarrollo web, UX/UI, growth hacking y optimización de sitios web. "
        "Tu tarea es proporcionar un análisis exhaustivo, detallado y profesional basado en los datos proporcionados. "
        "Incluye observaciones profundas, recomendaciones concretas y estrategias efectivas para mejorar la optimización del sitio, "
        "corregir errores y potenciar la experiencia de usuario. Tu análisis debe ser extenso y sustancioso, ofreciendo información de valor."
    ).format(display_name, lang_name, lang_name)

    return system_message

def call_pagespeed_api(url, strategy="mobile", category=["performance", "accessibility", "best-practices", "seo"]):
    """
    Llama a la API de PageSpeed Insights para la URL especificada usando la API key.
    Maneja errores y verifica que la respuesta contenga los datos necesarios.
    """
    endpoint = "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed"
    params = {
        "url": url,
        "strategy": strategy,
        "category": category,  # Usa el parámetro recibido
        "key": PAGESPEED_API_KEY
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()  # Lanza error si la respuesta no es 200
        data = response.json()
        if "lighthouseResult" not in data:
            raise ValueError("La respuesta de la API no contiene 'lighthouseResult'.")
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error al llamar a la API de PageSpeed Insights: {e}")
    except ValueError as ve:
        raise Exception(f"Error en la respuesta de la API: {ve}")

def generate_info_table(pagespeed_data):
    """
    Extrae la información clave de la respuesta de la API y genera una tabla HTML
    con datos sobre rendimiento, accesibilidad, SEO, best practices y otras métricas relevantes.
    """
    lighthouse = pagespeed_data.get("lighthouseResult", {})
    
    # Datos generales
    requested_url = lighthouse.get("requestedUrl", "N/A")
    final_url = lighthouse.get("finalUrl", "N/A")
    fetch_time = lighthouse.get("fetchTime", "N/A")
    analysis_timestamp = pagespeed_data.get("analysisUTCTimestamp", "N/A")
    
    # Puntuaciones de categorías
    categories = lighthouse.get("categories", {})
    performance_score = categories.get("performance", {}).get("score", "N/A")
    accessibility_score = categories.get("accessibility", {}).get("score", "N/A")
    best_practices_score = categories.get("best-practices", {}).get("score", "N/A")
    seo_score = categories.get("seo", {}).get("score", "N/A")
    
    # Métricas de auditoría
    audits = lighthouse.get("audits", {})
    fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
    speed_index = audits.get("speed-index", {}).get("displayValue", "N/A")
    interactive = audits.get("interactive", {}).get("displayValue", "N/A")
    tbt = audits.get("total-blocking-time", {}).get("displayValue", "N/A")
    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
    
    # Datos de experiencia de carga (CrUX)
    loading_experience = pagespeed_data.get("loadingExperience", {})
    overall_category = loading_experience.get("overall_category", "N/A")
    origin_loading_experience = pagespeed_data.get("originLoadingExperience", {}).get("overall_category", "N/A")
    
    # Función para formatear puntuaciones en porcentaje
    def format_score(score):
        if isinstance(score, (float, int)):
            return f"{score * 100:.1f}%"
        return "N/A" if score is None else score

    performance_score = format_score(performance_score)
    accessibility_score = format_score(accessibility_score)
    best_practices_score = format_score(best_practices_score)
    seo_score = format_score(seo_score)
    
    table_html = f"""
    <h2>Información Detallada</h2>
    <table border="1" cellspacing="0" cellpadding="5">
      <tr><th>Métrica</th><th>Valor</th></tr>
      <tr><td>Requested URL</td><td>{requested_url}</td></tr>
      <tr><td>Final URL</td><td>{final_url}</td></tr>
      <tr><td>Fetch Time</td><td>{fetch_time}</td></tr>
      <tr><td>Performance Score</td><td>{performance_score}</td></tr>
      <tr><td>Accessibility Score</td><td>{accessibility_score}</td></tr>
      <tr><td>Best Practices Score</td><td>{best_practices_score}</td></tr>
      <tr><td>SEO Score</td><td>{seo_score}</td></tr>
      <tr><td>First Contentful Paint</td><td>{fcp}</td></tr>
      <tr><td>Largest Contentful Paint</td><td>{lcp}</td></tr>
      <tr><td>Speed Index</td><td>{speed_index}</td></tr>
      <tr><td>Time to Interactive</td><td>{interactive}</td></tr>
      <tr><td>Total Blocking Time</td><td>{tbt}</td></tr>
      <tr><td>Cumulative Layout Shift</td><td>{cls}</td></tr>
      <tr><td>Loading Experience (CrUX)</td><td>{overall_category}</td></tr>
      <tr><td>Origin Loading Experience (CrUX)</td><td>{origin_loading_experience}</td></tr>
      <tr><td>Análisis Timestamp</td><td>{analysis_timestamp}</td></tr>
    </table>
    """
    return table_html

def generate_analysis_with_openai(pagespeed_data, db=None, user_id=None):
    """
    Construye un prompt con todos los datos extraídos de PageSpeed Insights para que GPT-4o-mini
    genere un análisis completo y estructurado en Markdown, que incluya observaciones, recomendaciones
    y sugerencias de optimización, corrección de errores y mejoras en la experiencia de usuario.
    Se formatean los valores de score a porcentaje (por ejemplo, 0.63 se convierte en 63%).
    """
    lighthouse = pagespeed_data.get("lighthouseResult", {})
    
    requested_url = lighthouse.get("requestedUrl", "N/A")
    final_url = lighthouse.get("finalUrl", "N/A")
    fetch_time = lighthouse.get("fetchTime", "N/A")
    analysis_timestamp = pagespeed_data.get("analysisUTCTimestamp", "N/A")
    
    categories = lighthouse.get("categories", {})
    performance_score = categories.get("performance", {}).get("score", "N/A")
    accessibility_score = categories.get("accessibility", {}).get("score", "N/A")
    best_practices_score = categories.get("best-practices", {}).get("score", "N/A")
    seo_score = categories.get("seo", {}).get("score", "N/A")
    
    # Función interna para formatear los score a porcentaje
    def format_score(score):
        if isinstance(score, (float, int)):
            return f"{score * 100:.0f}%"
        return "N/A"
    
    # Convertir los valores a porcentaje
    performance_score = format_score(performance_score)
    accessibility_score = format_score(accessibility_score)
    best_practices_score = format_score(best_practices_score)
    seo_score = format_score(seo_score)
    
    audits = lighthouse.get("audits", {})
    fcp = audits.get("first-contentful-paint", {}).get("displayValue", "N/A")
    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
    speed_index = audits.get("speed-index", {}).get("displayValue", "N/A")
    interactive = audits.get("interactive", {}).get("displayValue", "N/A")
    tbt = audits.get("total-blocking-time", {}).get("displayValue", "N/A")
    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")
    
    loading_experience = pagespeed_data.get("loadingExperience", {})
    overall_category = loading_experience.get("overall_category", "N/A")
    origin_loading_experience = pagespeed_data.get("originLoadingExperience", {}).get("overall_category", "N/A")
    
    # Obtener el idioma preferido del usuario si tenemos db y user_id
    lang_name = "English"  # Default
    if db and user_id:
        preferred_language = get_user_preferred_language(db, user_id)
        if preferred_language:
            language_names = {
                "en": "English",
                "es": "Spanish",
                "pt": "Portuguese",
                "fr": "French"
            }
            lang_name = language_names.get(preferred_language, "English")
    
    # Mensaje de sistema para orientar la respuesta
    system_message = (
        "Eres un experto en marketing digital, desarrollo web, UX/UI, growth hacking y optimización de sitios web. "
        "Tu tarea es proporcionar un análisis exhaustivo, detallado y profesional basado en los datos proporcionados. "
        "Incluye observaciones profundas, recomendaciones concretas y estrategias efectivas para mejorar la optimización del sitio, "
        "corregir errores y potenciar la experiencia de usuario. Tu análisis debe ser extenso y sustancioso, ofreciendo información de valor."
    )
    
    # Si tenemos db y user_id, usamos el mensaje del sistema personalizado
    if db and user_id:
        system_message = get_system_message(db, user_id)
    
    # Construcción del prompt en Markdown
    prompt = (
        f"Realiza un análisis exhaustivo de la siguiente URL basándote en los datos proporcionados. "
        f"IMPORTANTE: Debes responder en {lang_name}.\n\n"
        f"Tu análisis debe estar organizado en secciones claras y utilizar formato Markdown para estructurarlo. "
        f"Evalúa cada una de las siguientes áreas y proporciona observaciones detalladas, recomendaciones concretas y sugerencias para mejorar la optimización del sitio web:\n\n"
        f"### 1. Rendimiento\n"
        f"- Analiza la puntuación de Rendimiento. Evalúa métricas como First Contentful Paint, Largest Contentful Paint, Speed Index, Time to Interactive, Total Blocking Time y Cumulative Layout Shift.\n\n"
        f"### 2. Accesibilidad\n"
        f"- Analiza la puntuación de Accesibilidad. Evalúa las métricas claves y sugiere mejoras para asegurar que el sitio sea utilizable para todos los usuarios.\n\n"
        f"### 3. SEO\n"
        f"- Evalúa la puntuación de SEO. Revisa la optimización para motores de búsqueda y proporciona recomendaciones para mejorar la visibilidad y el posicionamiento.\n\n"
        f"### 4. Buenas Prácticas\n"
        f"- Analiza la puntuación de Buenas Prácticas. Examina el cumplimiento de las mejores prácticas y detecta posibles áreas de corrección de errores o de optimización en la web.\n\n"
        f"Incluye en tu respuesta conclusiones y recomendaciones generales para mejorar la experiencia de usuario y la optimización global del sitio.\n\n"
        f"**Datos Extraídos:**\n\n"
        f"- **Requested URL:** {requested_url}\n"
        f"- **Final URL:** {final_url}\n"
        f"- **Fetch Time:** {fetch_time}\n"
        f"- **Análisis Timestamp:** {analysis_timestamp}\n\n"
        f"**Métricas de Categorías (0% a 100%):**\n"
        f"- Performance: {performance_score}\n"
        f"- Accessibility: {accessibility_score}\n"
        f"- Best Practices: {best_practices_score}\n"
        f"- SEO: {seo_score}\n\n"
        f"**Métricas de Auditoría:**\n"
        f"- First Contentful Paint: {fcp}\n"
        f"- Largest Contentful Paint: {lcp}\n"
        f"- Speed Index: {speed_index}\n"
        f"- Time to Interactive: {interactive}\n"
        f"- Total Blocking Time: {tbt}\n"
        f"- Cumulative Layout Shift: {cls}\n\n"
        f"**Experiencia de Carga (CrUX):**\n"
        f"- Loading Experience: {overall_category}\n"
        f"- Origin Loading Experience: {origin_loading_experience}\n\n"
        f"Proporciona un análisis detallado, con explicaciones claras y recomendaciones específicas para cada área, "
        f"incluyendo posibles correcciones y mejoras en la optimización general del sitio web."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error en la llamada a OpenAI: {str(e)}")

def analyze_url(url, user_id=None, db=None):
    pagespeed_data = call_pagespeed_api(url)
    analysis = generate_analysis_with_openai(pagespeed_data, db, user_id)
    table_html = generate_info_table(pagespeed_data)
    
    result = {
        "analysis": analysis,
        "table": table_html,
        "raw_data": pagespeed_data
    }
    return result

def analyze_page_speed(url, user_id, db):
    """Analiza la velocidad de carga de una página web usando OpenAI."""
    try:
        # Obtener el idioma preferido del usuario
        preferred_language = get_user_preferred_language(db, user_id)
        if not preferred_language:
            preferred_language = 'en'  # Default to English

        # Map the language code to a human-readable name
        language_names = {
            "en": "English",
            "es": "Spanish",
            "pt": "Portuguese",
            "fr": "French"
        }
        lang_name = language_names.get(preferred_language, "English")

        prompt = f"""
        Analiza la velocidad de carga de la siguiente URL: {url}
        
        Por favor, proporciona:
        1. Análisis de rendimiento
        2. Problemas identificados
        3. Recomendaciones de optimización
        4. Prioridades de mejora

        IMPORTANTE: Responde en {lang_name}.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Como experto en Optimización de Rendimiento Web, proporciona un análisis detallado de la velocidad de carga. Responde en {lang_name}."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al analizar la velocidad de la página: {str(e)}"
