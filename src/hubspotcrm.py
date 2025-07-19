
import os
import requests
import json
from dotenv import load_dotenv
import hubspot
from hubspot.crm.contacts import ApiException
from hubspot.crm.deals import ApiException as DealsApiException
import openai
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
from utils import get_language_context
from functools import partial
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from src.agents.hubspot_crm_agent import create_hubspot_crm_agent
from src.agents.tools.hubspot_crm import HubSpotTool
import config

# Cargar variables de entorno
load_dotenv()

client_id = os.getenv("HUBSPOT_CLIENT_ID")
client_secret = os.getenv("HUBSPOT_CLIENT_SECRET")
redirect_uri = os.getenv("HUBSPOT_REDIRECT_URI")

llm = ChatOpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def get_authorization_url():
    return f"https://app.hubspot.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=crm.objects.contacts.read crm.objects.deals.read"

def exchange_code_for_tokens(code):
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al intercambiar el código por tokens: {e}")
        return None

def refresh_access_token(refresh_token):
    token_url = "https://api.hubapi.com/oauth/v1/token"
    data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'refresh_token': refresh_token,
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error al refrescar el token de acceso: {e}")
        return None

def generate_crm_summary(access_token, start_date, end_date, db=None, user_id=None):
    
    hubspot_tool = HubSpotTool(access_token)
    hubspot_agent = create_hubspot_crm_agent(llm, hubspot_tool)

    agent_input = f"""
    Analyze the HubSpot CRM data from {start_date} to {end_date}.
    Please provide a summary of the CRM performance and recommendations for improvement.
    """

    try:
        result = hubspot_agent.invoke({
            "input": agent_input
        })
        answer = result["output"]
    except Exception as e:
        logging.error(f"Error invoking HubSpot CRM agent: {e}")
        answer = 'Oops, I encountered an error. Please try a different question. If the problem persists, please try again later.'

    return answer
