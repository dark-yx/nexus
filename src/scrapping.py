import openai
import pandas as pd
import requests
from bs4 import BeautifulSoup
import config
from db import check_user_credits, get_user_preferred_language
from openai import OpenAI
from urllib.parse import urlparse
from utils import get_language_context, get_user_display_name, get_base_system_message

client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_system_message(db, user_id):
    # Obtener el contexto de idioma y nombre del usuario
    lang_context = get_language_context(db, user_id)
    display_name = get_user_display_name(db, user_id)

    # Construir el mensaje del sistema
    base_message = get_base_system_message(display_name, lang_context['name'])
    expert_message = (
        "Eres un asistente muy útil, profesional y experto en marketing digital y growth hacking con un alto nivel de experiencia, PNL, Branding, SEO, PPC CRO y "
        "conocimientos en neuromarketing. Tu prioridad es ayudar a las empresas a aumentar el ROI del canal digital."
    )
    
    return base_message + " " + expert_message

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Función de scraping 
def scrape_website(url):
    if not is_valid_url(url):
        raise ValueError("La URL proporcionada no es válida")

    try:
        # Realizar solicitud al sitio web
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Asegurarse de que la solicitud fue exitosa
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extraer información relevante
        title = soup.title.string if soup.title else "No title found"
        metatitle = soup.find("meta", {"name": "title"})["content"] if soup.find("meta", {"name": "title"}) else None

        headers = {header.name: header.get_text(strip=True) for header in soup.find_all(['h1', 'h2', 'h3', 'h4'])}

        alts = [img.get("alt") for img in soup.find_all("img") if img.get("alt")]

        keywords = [meta.get("content") for meta in soup.find_all("meta", {"name": "keywords"}) if meta.get("content")]

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]

        links = {a['href']: a.text.strip() for a in soup.find_all('a', href=True) if a.text.strip()}

        scraped_data = {
            "title": title,
            "metatitle": metatitle,
            "headers": headers,
            "alts": alts,
            "keywords": keywords,
            "paragraphs": paragraphs,
            "links": links
        }

        return scraped_data

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al acceder a la URL: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error al procesar la página web: {str(e)}")

def display_website_analysis(scraped_data):
    data_tuples = [(tag, value) for tag, value in scraped_data.items()]
    df_scraping_result = pd.DataFrame(data_tuples, columns=['Índice', 'Valor'])
    return df_scraping_result

def get_gpt_analysis(scraped_data, db, user_id):
    # Verificar créditos
    has_credits, message = check_user_credits(db, user_id, 2)
    if not has_credits:
        return message
    
    messages = [
        {"role": "system", "content": get_system_message(db, user_id)},
        {"role": "user", "content": f"Analiza los siguientes datos de la página web y proporcióna una respuesta que contenga resumen, observciones sobre su mercado desde la perspectiva del marketing, sugerencias de marketing digital, anuncios, embudos y acciónes especificas:\n{scraped_data}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al analizar la página web: {str(e)}"

def analizar_web(url, user_id, db):
    """
    Analiza una página web y devuelve un resumen del análisis.
    
    Args:
        url: URL de la página web a analizar
        user_id: ID del usuario
        db: Conexión a la base de datos
        
    Returns:
        str: Resumen del análisis
    """
    try:
        # Realizar el scraping
        scraped_data = scrape_website(url)
        
        # Generar el análisis con GPT
        analysis = get_gpt_analysis(scraped_data, db, user_id)
        
        if analysis.startswith("Error"):
            return analysis
            
        return analysis

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error al analizar la página web: {str(e)}"