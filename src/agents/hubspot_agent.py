from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from src.tools.hubspot_tool import HubSpotTool

def create_hubspot_agent(llm: ChatOpenAI, tool: HubSpotTool):
    """Creates a HubSpot agent."""
    return initialize_agent(
        tools=tool.get_tools(),
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )