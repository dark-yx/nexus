
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.tools.google_ads import ListAccessibleCustomersTool, SearchGoogleAdsTool, CreateCampaignTool, GetCampaignPerformanceTool
from src.tools.google_analytics_4 import GetRealtimeActiveUsersTool, RunReportTool, GetBigQuerySchemaTool, ExecuteBigQuerySQLTool, GetEventAndConversionDataTool
from src.tools.google_search_console import ListSitesTool, GetSearchAnalyticsTool, GetSitemapsTool, GetUrlInspectionTool, GetPerformanceDataTool
from src.tools.hubspot import GetContactsTool, CreateContactTool, GetTotalOpenDealsTool, GetTotalClosedDealsTool, GetTotalClosedSalesValueTool, CreateCompanyTool, CreateDealTool, GetDealPerformanceTool
from src.tools.meta_ads import ListAdAccountsTool, GetCampaignsTool, GetAdSetsTool, GetAdsTool, GetCampaignInsightsTool, GetAdCreativeTool

class LangchainChatAgent:
    def __init__(self, db, user_id):
        self.db = db
        self.user_id = user_id
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI marketing assistant named Derek.",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.tools = [
            ListAccessibleCustomersTool(),
            SearchGoogleAdsTool(),
            CreateCampaignTool(),
            GetCampaignPerformanceTool(),
            GetRealtimeActiveUsersTool(),
            RunReportTool(),
            GetBigQuerySchemaTool(),
            ExecuteBigQuerySQLTool(),
            GetEventAndConversionDataTool(),
            ListSitesTool(),
            GetSearchAnalyticsTool(),
            GetSitemapsTool(),
            GetUrlInspectionTool(),
            GetPerformanceDataTool(),
            GetContactsTool(),
            CreateContactTool(),
            GetTotalOpenDealsTool(),
            GetTotalClosedDealsTool(),
            GetTotalClosedSalesValueTool(),
            CreateCompanyTool(),
            CreateDealTool(),
            GetDealPerformanceTool(),
            ListAdAccountsTool(),
            GetCampaignsTool(),
            GetAdSetsTool(),
            GetAdsTool(),
            GetCampaignInsightsTool(),
            GetAdCreativeTool(),
        ]
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        self.chat_history = []

    def run(self, user_input):
        response = self.agent_executor.invoke(
            {
                "input": user_input,
                "chat_history": self.chat_history,
            }
        )
        self.chat_history.extend([HumanMessage(content=user_input), response["output"]])
        return response["output"]
