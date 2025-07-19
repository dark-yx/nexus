from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from src.tools.google_analytics_4_tool import GoogleAnalytics4Tool

def create_google_analytics_4_agent(llm: ChatOpenAI, tool: GoogleAnalytics4Tool):
    """Creates a Google Analytics 4 agent."""
    return initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )