import pandas as pd
import matplotlib.pyplot as plt
import openai
import base64
import io
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import sys
import re
import time
import concurrent.futures
import itertools
import requests
import string
import json
from openai import OpenAI
import config
from db import get_user_preferred_language
from utils import get_language_context, get_user_display_name, get_base_system_message

# Configuración de OpenAI
system_message = {
    "role": "system",
    "content": "Tu nombre es WLT 2.0, asistente experto en marketing digital, growth hacking, SEO, PPC y neuromarketing."
}

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

# Función para convertir figura matplotlib a base64
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    base64_img = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return base64_img

# Mapear IDs de ubicación a nombres de recursos
def map_locations_ids_to_resource_names(client, location_ids):
    build_resource_name = client.get_service("GeoTargetConstantService").geo_target_constant_path
    return [build_resource_name(location_id) for location_id in location_ids]

# Obtener IDs de clientes accesibles
def get_customer_ids(google_ads_client):
    try:
        customer_service = google_ads_client.get_service("CustomerService")
        accessible_customers = customer_service.list_accessible_customers()
        customer_ids = [resource_name.split('/')[-1] for resource_name in accessible_customers.resource_names]
        return customer_ids
    except Exception as e:
        print(f"Error al obtener los IDs de clientes: {e}")
        raise

# Función principal para obtener ideas de palabras clave
def main(client, customer_id, location_ids, language_id, keyword_texts, page_url):
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    keyword_competition_level_enum = client.enums.KeywordPlanCompetitionLevelEnum
    keyword_annotation = [client.enums.KeywordPlanKeywordAnnotationEnum.KEYWORD_CONCEPT]
    keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH

    location_rns = map_locations_ids_to_resource_names(client, location_ids)
    language_rn = client.get_service("GoogleAdsService").language_constant_path(language_id)

    if not (keyword_texts or page_url):
        raise ValueError("Al menos una palabra clave o una URL es necesaria.")

    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = language_rn
    request.geo_target_constants = location_rns
    request.include_adult_keywords = False
    request.keyword_plan_network = keyword_plan_network
    request.keyword_annotation = keyword_annotation

    if keyword_texts and page_url:
        request.keyword_and_url_seed.url = page_url
        request.keyword_and_url_seed.keywords.extend(keyword_texts)
    elif keyword_texts:
        request.keyword_seed.keywords.extend(keyword_texts)
    elif page_url:
        request.url_seed.url = page_url

    keyword_ideas = list(keyword_plan_idea_service.generate_keyword_ideas(request=request))

    return keyword_ideas

# Análisis de palabras clave y generación de gráficos
def keyword_research(client, customer_id, location_ids, language_id, keyword_texts, page_url, user_id, db):
    ideas = main(client, customer_id, location_ids, language_id, keyword_texts, page_url)
    if not ideas:
        return {"error": "No se encontraron ideas de palabras clave."}

    data = [
        {
            "text": idea.text,
            "avg_monthly_searches": idea.keyword_idea_metrics.avg_monthly_searches,
            "competition": idea.keyword_idea_metrics.competition.name
        }
        for idea in ideas
    ]

    df_ideas = pd.DataFrame(data)
    charts = {}

    try:
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
            autopct='%1.1f%%', startangle=140
        )
        ax.set_title("Distribución de Búsquedas")
        charts["pie_chart"] = fig_to_base64(fig)

    except Exception as e:
        print(f"Error al generar gráficos: {str(e)}")

    # Generación de recomendaciones con OpenAI
    try:
        # Obtener el contexto de idioma
        lang_context = get_language_context(db, user_id)

        user_message = {
            "role": "user",
            "content": f"Analizar palabras clave:\n{df_ideas.to_string(index=False)}\n\nIMPORTANTE: Responde en {lang_context['name']}."
        }
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"Como experto en SEO y Análisis de Palabras Clave, proporciona recomendaciones detalladas basadas en los datos proporcionados. Responde en {lang_context['name']}."},
                user_message
            ]
        )
        recommendations = response.choices[0].message.content
        charts["recommendations"] = recommendations

    except Exception as e:
        print(f"Error al obtener recomendaciones: {str(e)}")

    return {
        'df_standard': df_ideas,
        'charts_standard': charts,
        'recommendations': recommendations,
    }

# Función para convertir anotaciones a diccionario (convert_to_dict)
def convert_to_dict(input_str):
    pattern = r'concepts {\n name: "(.*?)"\n (concept_group {\n .*?\n }\n)}'
    matches = re.findall(pattern, input_str, re.DOTALL)
    
    result = {"concepts": []}
    for match in matches:
        name = match[0]
        concept_group_str = match[1]
        
        pattern = r'name: "(.*?)"\n( type_: (.*?)\n)?'
        concept_group_matches = re.findall(pattern, concept_group_str, re.DOTALL)
        for cg_match in concept_group_matches:
            concept_group = {"name": cg_match[0]}
            if cg_match[1].strip():
                concept_group["type_"] = cg_match[1].strip()
        
            concept = {"name": name, "concept_group": concept_group}
            result["concepts"].append(concept)
    
    return result["concepts"]

# Función para analizar filas de palabras clave (keyword_row_parser)
def keyword_row_parser(data):
    """parse each response into a set of rows."""
    
    final_row = []
    base_keyword = data["exact_keyword"][0]["keyword"]
    base_montlysearch = data["exact_keyword"][0]["monthlysearch"]
    based_difficulty = data["exact_keyword"][0]["difficulty"]
    base_competition_score = data["exact_keyword"][0]["competition_score"]
    base_annotation = data["exact_keyword"][0]["annotation"]
    
    initial_data = {
        "base_keyword": base_keyword,
        "base_montly_search": base_montlysearch,
        "based_difficulty": based_difficulty,
        "base_competition_score": base_competition_score,
        "related_keyword": base_keyword,
        "rk_monthly_search": base_montlysearch,
        "difficulty": based_difficulty,
        "competition_score": base_competition_score,
        "annotation": base_annotation,
        "name": None,
        "concept_name": None,
        "concept_type": None,
    }
    
    final_row.append(initial_data)
    
    for item in data["related_keywords"]:
        related_keyword = item["keyword"]
        rk_monthly_search = item["monthlysearch"]
        difficulty = item["difficulty"]
        competition_score = item["competition_score"]
        
        annotation = item["annotation"]
        
        try:
            concept_list = convert_to_dict(annotation)
            for concept in concept_list:
                name = concept["name"]
                concept_name = concept["concept_group"]["name"]
                concept_type = concept["concept_group"]["type_"]
                
                data_row = {
                    "base_keyword": base_keyword,
                    "base_montly_search": base_montlysearch,
                    "based_difficulty": based_difficulty,
                    "base_competition_score": base_competition_score,
                    "related_keyword": related_keyword,
                    "rk_monthly_search": rk_monthly_search,
                    "difficulty": difficulty,
                    "competition_score": competition_score,
                    "annotation": annotation,
                    "name": name,
                    "concept_name": concept_name,
                    "concept_type": concept_type,
                }
                
                final_row.append(data_row)
        
        except:
            continue
    
    return final_row
