from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from src.tools.google_search_console_tool import GoogleSearchConsoleTool

def create_google_search_console_agent(llm: ChatOpenAI, tool: GoogleSearchConsoleTool):
    """Creates a Google Search Console agent."""
    return initialize_agent(
        tools=[tool],
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )