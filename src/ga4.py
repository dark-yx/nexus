import os
import numpy as np
import pandas as pd
from datetime import date, timedelta
from openai import OpenAI
import config
from utils import get_language_context
from src.agents.tools.bigquery import BigQueryTool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool

# Configuración de credenciales y cliente
base_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(base_dir, 'static', 'ga4-apponepum.json')

# Inicializar clientes
openai_client = OpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)
llm = ChatOpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)
bigquery_tool = BigQueryTool(credentials_path)

def get_ga4_data_from_bigquery(property_id, start_date, end_date, dimensions, metrics, table):
    """
    Obtiene datos de GA4 desde BigQuery.
    """
    query = f"""
    SELECT
        {', '.join(dimensions)},
        {', '.join(metrics)}
    FROM
        `{table}`
    WHERE
        _TABLE_SUFFIX BETWEEN '{start_date.replace('-', '')}' AND '{end_date.replace('-', '')}'
        AND property_id = '{property_id}'
    GROUP BY
        {', '.join(dimensions)}
    """
    return bigquery_tool.run_query(query)

def get_daily_traffic(property_id, start_date, end_date):
    """
    Obtiene el tráfico diario de GA4 desde BigQuery.
    """
    dimensions = ['date']
    metrics = ['COUNT(DISTINCT user_pseudo_id) as activeUsers', 'COUNTIF(event_name = \'session_start\') as sessions', 'COUNTIF(event_name = \'first_visit\') as newUsers', 'COUNTIF(event_name = \'page_view\') as pageviews']
    table = f'your_project.your_dataset.events_*'; # Reemplazar con tu tabla de BigQuery
    return get_ga4_data_from_bigquery(property_id, start_date, end_date, dimensions, metrics, table)

def create_ga4_analysis_agent(llm: ChatOpenAI) -> AgentExecutor:
    """
    Creates a LangChain agent for GA4 analysis.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strategic consultant specializing in web traffic analysis and conversion optimization. Your specialty is turning data into detailed, actionable plans."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    tools = [] # No tools needed for this agent as it only uses the LLM
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def generate_traffic_summary(traffic_data, db, user_id):
    try:
        language_context = get_language_context(db, user_id)
        formatted_data = format_traffic_data(traffic_data)
        
        prompt = f"""# ... (el mismo prompt que antes)
        """
        
        ga4_agent = create_ga4_analysis_agent(llm)
        result = ga4_agent.invoke({"input": prompt})
        analysis = result["output"]
        
        if not analysis or not isinstance(analysis, str):
            raise Exception("The generated analysis is not valid")
            
        return analysis
        
    except Exception as e:
        print(f"[ERROR] Error in generate_traffic_summary: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback completo:\n{traceback.format_exc()}")
        raise

# ... (el resto de las funciones de formato y visualización adaptadas a BigQuery)

