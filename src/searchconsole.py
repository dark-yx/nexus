
import openai
import logging
from langchain_openai import ChatOpenAI
from src.agents.search_console_agent import create_search_console_agent
from langchain_google_community import GoogleSearchConsoleTool
import config

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.WARNING)

llm = ChatOpenAI(api_key=config.DevelopmentConfig.OPENAI_KEY)

def seo_resumen(credentials, site_url, start_date, end_date):
    
    search_console_tool = GoogleSearchConsoleTool(credentials=credentials, site_url=site_url)
    search_console_agent = create_search_console_agent(llm, search_console_tool)

    agent_input = f"""
    Analyze the Search Console data for site {site_url} from {start_date} to {end_date}.
    Please provide a summary of the SEO performance and recommendations for improvement.
    """

    try:
        result = search_console_agent.invoke({
            "input": agent_input
        })
        answer = result["output"]
    except Exception as e:
        logging.error(f"Error invoking Search Console agent: {e}")
        answer = 'Oops, I encountered an error. Please try a different question. If the problem persists, please try again later.'

    return answer
