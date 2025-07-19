

import os
import io
import base64
import logging
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import config
from src.agents.google_ads_agent import create_google_ads_agent
from src.tools.google_ads import GoogleAdsTool
from langchain_openai import ChatOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar la API de OpenAI con tu clave de API
client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)
llm = ChatOpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def generate_campaigns_summary(data):
    summary = "Resumen de las Campañas de Google Ads:\n"
    for row in data:
        campaign = row.campaign
        metrics = row.metrics
        summary += (
            f"Campaña: {campaign.name}\n"
            f" - ID: {campaign.id}\n"
            f" - Impresiones: {metrics.impressions}\n"
            f" - Clics: {metrics.clicks}\n"
            f" - Costo: {metrics.cost_micros / 1e6} USD\n"
            f" - CPC Promedio: {metrics.average_cpc / 1e6} USD\n"
            f" - Conversiones: {metrics.conversions}\n\n"
        )
    return summary

def google_ads_resumen(credentials, customer_id, query, user_id, db):
    
    google_ads_tool = GoogleAdsTool(credentials)
    google_ads_agent = create_google_ads_agent(llm, google_ads_tool)
    
    agent_input = f"""
    Analyze the Google Ads data for customer ID {customer_id} with the following query: {query}.
    The user ID is {user_id}.
    Please provide a summary of the campaign performance and recommendations for improvement.
    """
    
    try:
        result = google_ads_agent.invoke({
            "input": agent_input
        })
        answer = result["output"]
        data = []
    except Exception as e:
        logger.error("Error invoking Google Ads agent: %s", e)
        answer = 'Oops, I encountered an error. Please try a different question. If the problem persists, please try again later.'
        data = []

    return answer, data

def generate_graph(data):
    if not data:
        return None
        
    campaign_names = [row.campaign.name for row in data]
    impressions = [row.metrics.impressions for row in data]
    clicks = [row.metrics.clicks for row in data]
    costs = [row.metrics.cost_micros / 1e6 for row in data]

    fig, ax = plt.subplots(3, 1, figsize=(10, 15))

    ax[0].barh(campaign_names, impressions, color='skyblue')
    ax[0].set_title('Impressions per Campaign')
    ax[0].set_xlabel('Impressions')

    ax[1].barh(campaign_names, clicks, color='lightgreen')
    ax[1].set_title('Clicks per Campaign')
    ax[1].set_xlabel('Clicks')

    ax[2].barh(campaign_names, costs, color='salmon')
    ax[2].set_title('Cost per Campaign')
    ax[2].set_xlabel('Cost (USD)')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return f'data:image/png;base64,{image_base64}'
