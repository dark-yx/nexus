"""Google Search Console tools."""
from __future__ import annotations
import json
from googleapiclient.discovery import build
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, List
from src.auth.google_auth import get_google_credentials
from tabulate import tabulate

# --- Input Schemas ---
class ListSitesInput(BaseModel):
    pass

class GetSearchAnalyticsInput(BaseModel):
    site_url: str = Field(description="The URL of the site.")
    start_date: str = Field(description="Start date in YYYY-MM-DD format.")
    end_date: str = Field(description="End date in YYYY-MM-DD format.")
    dimensions: List[str] = Field(description="The dimensions to include in the report.")

class GetSitemapsInput(BaseModel):
    site_url: str = Field(description="The URL of the site.")

class GetUrlInspectionInput(BaseModel):
    site_url: str = Field(description="The URL of the site.")
    inspection_url: str = Field(description="The URL to inspect.")

class GetPerformanceDataInput(BaseModel):
    site_url: str = Field(description="The URL of the site.")
    start_date: str = Field(description="Start date in YYYY-MM-DD format.")
    end_date: str = Field(description="End date in YYYY-MM-DD format.")

class GetPerformanceDataTableInput(GetPerformanceDataInput):
    pass

# --- Tool Implementations ---

class GoogleSearchConsoleLangchainTool(BaseTool):
    """A base tool for interacting with the Google Search Console API."""
    name: str = "google_search_console_base_tool"
    description: str = "A base tool for Google Search Console operations."
    service: any = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            credentials = get_google_credentials()
            self.service = build('searchconsole', 'v1', credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to initialize GoogleSearchConsole service: {e}")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class ListSitesTool(GoogleSearchConsoleLangchainTool):
    name: str = "list_gsc_sites"
    description: str = "Lists all sites the user has access to in Google Search Console."
    args_schema: Type[BaseModel] = ListSitesInput

    def _run(self) -> str:
        try:
            site_list = self.service.sites().list().execute()
            return json.dumps(site_list.get('siteEntry', []), indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetSearchAnalyticsTool(GoogleSearchConsoleLangchainTool):
    name: str = "get_gsc_search_analytics"
    description: str = "Gets search analytics data for a site. Useful for custom queries."
    args_schema: Type[BaseModel] = GetSearchAnalyticsInput

    def _run(self, site_url: str, start_date: str, end_date: str, dimensions: List[str]) -> str:
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
            }
            response = self.service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            return json.dumps(response, indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetSitemapsTool(GoogleSearchConsoleLangchainTool):
    name: str = "get_gsc_sitemaps"
    description: str = "Gets sitemaps for a site."
    args_schema: Type[BaseModel] = GetSitemapsInput

    def _run(self, site_url: str) -> str:
        try:
            response = self.service.sitemaps().list(siteUrl=site_url).execute()
            return json.dumps(response.get('sitemap', []), indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetUrlInspectionTool(GoogleSearchConsoleLangchainTool):
    name: str = "get_gsc_url_inspection"
    description: str = "Gets URL inspection data for a URL."
    args_schema: Type[BaseModel] = GetUrlInspectionInput

    def _run(self, site_url: str, inspection_url: str) -> str:
        try:
            request = {
                'inspectionUrl': inspection_url,
                'siteUrl': site_url,
            }
            response = self.service.urlInspection().index().inspect(body=request).execute()
            return json.dumps(response, indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetPerformanceDataTool(GoogleSearchConsoleLangchainTool):
    name: str = "get_gsc_performance_data"
    description: str = "Gets search performance data for a site (impressions, clicks, CTR, position)."
    args_schema: Type[BaseModel] = GetPerformanceDataInput

    def _run(self, site_url: str, start_date: str, end_date: str) -> str:
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['date', 'query', 'page', 'device', 'country'],
            }
            response = self.service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            return json.dumps(response.get('rows', []), indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetPerformanceDataTableTool(GoogleSearchConsoleLangchainTool):
    name: str = "get_gsc_performance_data_table"
    description: str = "Gets search performance data for a site and displays it in a formatted table."
    args_schema: Type[BaseModel] = GetPerformanceDataTableInput

    def _run(self, site_url: str, start_date: str, end_date: str) -> str:
        try:
            request = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': ['query', 'page'],
                'rowLimit': 20
            }
            response = self.service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            headers = ["Query", "Page", "Clicks", "Impressions", "CTR", "Position"]
            rows = []
            if 'rows' in response:
                for row in response['rows']:
                    rows.append(row['keys'] + [row['clicks'], row['impressions'], row['ctr'], row['position']])
            return tabulate(rows, headers=headers, tablefmt="grid")
        except Exception as e:
            return f"An error occurred: {e}"