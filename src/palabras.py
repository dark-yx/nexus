import pandas as pd
import matplotlib.pyplot as plt
import openai
import base64
import io
from google.ads.googleads.errors import GoogleAdsException
from openai import OpenAI


# Configuración de OpenAI
OPENAI_SYSTEM_MESSAGE = {
    "role": "system",
    "content": "Tu nombre es WLT 2.0, asistente experto en marketing digital, growth hacking, SEO, PPC y neuromarketing."
}

# Reemplazar la línea de configuración de la API key
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)


def initialize_google_ads_client(credentials):
    """Inicializa el cliente de Google Ads."""
    from google.ads.googleads.client import GoogleAdsClient
    return GoogleAdsClient.load_from_dict(credentials)


def fig_to_base64(fig):
    """Convierte un gráfico Matplotlib a formato base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return base64_img


def map_locations_ids_to_resource_names(client, location_ids):
    """Mapea IDs de ubicación a nombres de recursos."""
    geo_service = client.get_service("GeoTargetConstantService")
    return [geo_service.geo_target_constant_path(location_id) for location_id in location_ids]


def generate_keyword_ideas(client, customer_id, location_ids, language_id, keyword_texts=None, page_url=None):
    """Genera ideas de palabras clave utilizando la API de Google Ads."""
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    request = client.get_type("GenerateKeywordIdeasRequest")
    
    # Configuración del request
    request.customer_id = customer_id
    request.language = client.get_service("GoogleAdsService").language_constant_path(language_id)
    request.geo_target_constants = map_locations_ids_to_resource_names(client, location_ids)
    request.include_adult_keywords = False
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS

    # Configuración de semillas (keywords o URL)
    if keyword_texts:
        request.keyword_seed.keywords.extend(keyword_texts)
    elif page_url:
        request.url_seed.url = page_url
    else:
        raise ValueError("Se requiere al menos una semilla: palabras clave o URL.")

    try:
        response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        return [
            {
                "text": idea.text,
                "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
                "competition": idea.keyword_idea_metrics.competition.name
            }
            for idea in response.results
        ]
    except GoogleAdsException as ex:
        raise RuntimeError(f"Error en la API de Google Ads: {ex.request_id} - {ex.error.message}")


def create_charts(df_ideas):
    """Genera gráficos de barras y pastel con las ideas de palabras clave."""
    charts = {}

    # Gráfico de barras
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df_ideas['text'][:10], df_ideas['avg_monthly_searches'][:10], color='skyblue')
    ax.set_xlabel('Búsquedas Mensuales Promedio')
    ax.set_ylabel('Término')
    ax.set_title('Palabras Clave Más Populares')
    charts["bar_chart"] = fig_to_base64(fig)

    # Gráfico de pastel
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        df_ideas['avg_monthly_searches'][:10],
        labels=df_ideas['text'][:10],
        autopct='%1.1f%%',
        startangle=140
    )
    ax.set_title("Distribución de Búsquedas")
    charts["pie_chart"] = fig_to_base64(fig)

    return charts


def get_openai_recommendations(df_ideas):
    """Obtiene recomendaciones de OpenAI basadas en el análisis de palabras clave."""
    try:
        user_message = {
            "role": "user",
            "content": f"Analizar palabras clave:\n{df_ideas.to_string(index=False)}"
        }
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[OPENAI_SYSTEM_MESSAGE, user_message]
        )
        return response.choices[0].message.content.replace('\n', '<br>')
    except Exception as e:
        return f"Error al obtener recomendaciones: {str(e)}"
