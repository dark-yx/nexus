import requests
import openai
from openai import OpenAI
import config
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'f047510a3bd443a1bcd22d27b63dfe11')

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def fetch_news():
    url = (f'https://newsapi.org/v2/everything?'
           f'q=marketing digital OR growth hacking OR growth marketing OR publicidad digital OR ventas online OR ads OR seo OR sem OR ecommerce&'
           f'language=es&'
           f'apiKey={NEWS_API_KEY}')
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles[:5]  # Limitar a los primeros 5 artículos

def generate_summary(articles, max_characters=1800):
    # Preparar títulos y descripciones con límite de caracteres
    total_characters = 0
    titles_and_descriptions = []

    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '')

        # Limitar cada título o descripción a 150 y 200 caracteres máximo
        title = title[:150]
        description = description[:200]

        # Calcular el total acumulado
        combined_text = f"Título: {title}\nResumen: {description}"
        total_characters += len(combined_text)

        if total_characters > max_characters:
            break

        titles_and_descriptions.append(combined_text)

    # Concatenar los títulos y descripciones
    prompt = (
        "Resumen de noticias actuales sobre marketing digital basadas en los siguientes "
        "títulos y descripciones:\n\n" + "\n\n".join(titles_and_descriptions) +
        "\n\nPor favor, genera un resumen breve y conciso que incluya los puntos más importantes."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un reportero de noticias de marketing digital, ventas online y growth hacking, y tu trabajo es proporcionar un análisis inteligente sobre el estado del marketing e internet basado en las noticias. Y al finalizar invita a las personas a visitar las fuentes de las noticias dando clic en los títulos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        summary = f"Error al generar el resumen: {str(e)}"

    return summary
