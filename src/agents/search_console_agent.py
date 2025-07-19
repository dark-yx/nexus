from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_community import GoogleSearchConsoleTool

def create_search_console_agent(llm: ChatOpenAI, search_console_tool: GoogleSearchConsoleTool) -> AgentExecutor:
    """
    Creates a Search Console agent with the necessary tools.
    """
    tools = [search_console_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides information about Google Search Console."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(agent=agent, tools=tools, verbose=True)