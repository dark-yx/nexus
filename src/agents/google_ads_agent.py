from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from src.tools.google_ads import GoogleAdsTool

def create_google_ads_agent(llm: ChatOpenAI, tool: GoogleAdsTool):
    """Creates a Google Ads agent."""
    return initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
