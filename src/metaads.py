
import os
import requests
import pandas as pd
import plotly.graph_objects as go
from openai import OpenAI
from utils import get_language_context
from functools import partial
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from src.agents.meta_ads_agent import create_meta_ads_agent
from src.agents.tools.meta_ads import MetaAdsTool
import config

llm = ChatOpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def load_prompt_from_file(file_path):
    with open(file_path, "r") as file:
        return file.read().strip()

def create_pie_chart(df, column):
    fig = go.Figure(data=[go.Pie(labels=df['campaign_name'], values=df[column], hole=.3)])
    fig.update_layout(title_text=f"Distribución de {column}")
    return fig.to_html(full_html=False)

def generate_analysis(access_token, ad_account_id, start_date, end_date, prompt_file, db=None, user_id=None):
    
    meta_ads_tool = MetaAdsTool(access_token)
    meta_ads_agent = create_meta_ads_agent(llm, meta_ads_tool)

    prompt = load_prompt_from_file(os.path.join("prompts", prompt_file))

    agent_input = f"""
    Analyze the Meta Ads data for ad account {ad_account_id} from {start_date} to {end_date}.
    {prompt}
    Return the campaign summary and the campaign data as a pandas DataFrame.
    """

    try:
        result = meta_ads_agent.invoke({
            "input": agent_input
        })
        campaign_summary = result["output"]["summary"]
        campaign_data = result["output"]["data"]
        
        pie_charts = {col: create_pie_chart(campaign_data, col) for col in ['spend', 'clicks', 'impressions', 'leads', 'messages']}

    except Exception as e:
        campaign_summary = f"Error al generar el resumen: {str(e)}"
        campaign_data = pd.DataFrame()
        pie_charts = {col: "" for col in ['spend', 'clicks', 'impressions', 'leads', 'messages']}
        
    return campaign_data, pie_charts['spend'], pie_charts['clicks'], pie_charts['impressions'], pie_charts['leads'], pie_charts['messages'], campaign_summary
