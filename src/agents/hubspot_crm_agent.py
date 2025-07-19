from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.agents.tools.hubspot_crm import HubSpotTool

def create_hubspot_crm_agent(llm: ChatOpenAI, hubspot_tool: HubSpotTool) -> AgentExecutor:
    """
    Creates a HubSpot CRM agent with the necessary tools.
    """
    tools = [hubspot_tool.get_contacts, hubspot_tool.get_total_open_deals, hubspot_tool.get_total_closed_deals, hubspot_tool.get_total_closed_sales_value]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides information about HubSpot CRM."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)