"""Google Analytics 4 tools."""
from __future__ import annotations
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    RunRealtimeReportRequest,
    ListAudiencesRequest,
)
from google.cloud import bigquery
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, List
from src.auth.google_auth import get_google_credentials
from tabulate import tabulate

# --- Input Schemas ---
class GetRealtimeActiveUsersInput(BaseModel):
    property_id: str = Field(description="The ID of the Google Analytics 4 property.")

class RunReportInput(BaseModel):
    property_id: str = Field(description="The ID of the Google Analytics 4 property.")
    dimensions: List[str] = Field(description="The dimensions to include in the report.")
    metrics: List[str] = Field(description="The metrics to include in the report.")
    start_date: str = Field(description="The start date for the report (YYYY-MM-DD).")
    end_date: str = Field(description="The end date for the report (YYYY-MM-DD).")

class GetBigQuerySchemaInput(BaseModel):
    project_id: str = Field(description="The ID of the Google Cloud project.")
    dataset_id: str = Field(description="The ID of the BigQuery dataset.")
    table_id: str = Field(description="The ID of the BigQuery table.")

class ExecuteBigQuerySQLInput(BaseModel):
    query: str = Field(description="The SQL query to execute in BigQuery.")

class GetEventAndConversionDataInput(BaseModel):
    property_id: str = Field(description="The ID of the Google Analytics 4 property.")
    start_date: str = Field(description="The start date for the report (YYYY-MM-DD).")
    end_date: str = Field(description="The end date for the report (YYYY-MM-DD).")

class GetAudiencesInput(BaseModel):
    property_id: str = Field(description="The ID of the Google Analytics 4 property.")

class RunReportTableInput(RunReportInput):
    pass

# --- Tool Implementations ---

class GoogleAnalytics4LangchainTool(BaseTool):
    """A base tool for interacting with the Google Analytics 4 API."""
    name: str = "google_analytics_4_base_tool"
    description: str = "A base tool for Google Analytics 4 operations."
    data_client: BetaAnalyticsDataClient = None
    bigquery_client: bigquery.Client = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            credentials = get_google_credentials()
            self.data_client = BetaAnalyticsDataClient(credentials=credentials)
            self.bigquery_client = bigquery.Client(credentials=credentials)
        except Exception as e:
            raise Exception(f"Failed to initialize clients: {e}")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class GetRealtimeActiveUsersTool(GoogleAnalytics4LangchainTool):
    name: str = "get_realtime_active_users"
    description: str = "Returns the number of active users in the last 30 minutes. Useful for a quick snapshot of current site activity."
    args_schema: Type[BaseModel] = GetRealtimeActiveUsersInput

    def _run(self, property_id: str) -> str:
        try:
            request = RunRealtimeReportRequest(
                property=f"properties/{property_id}",
                metrics=[{"name": "activeUsers"}],
            )
            response = self.data_client.run_realtime_report(request)
            return f"Active users: {response.rows[0].metric_values[0].value}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class RunReportTool(GoogleAnalytics4LangchainTool):
    name: str = "run_ga4_report"
    description: str = "Runs a report on Google Analytics 4 data. Useful for getting detailed performance data."
    args_schema: Type[BaseModel] = RunReportInput

    def _run(self, property_id: str, dimensions: List[str], metrics: List[str], start_date: str, end_date: str) -> str:
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=met) for met in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            response = self.data_client.run_report(request)

            report_data = []
            for row in response.rows:
                row_data = {}
                for i, dimension_value in enumerate(row.dimension_values):
                    row_data[response.dimension_headers[i].name] = dimension_value.value
                for i, metric_value in enumerate(row.metric_values):
                    row_data[response.metric_headers[i].name] = metric_value.value
                report_data.append(row_data)

            return json.dumps(report_data, indent=4)
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class RunReportTableTool(GoogleAnalytics4LangchainTool):
    name: str = "run_ga4_report_table"
    description: str = "Runs a report on Google Analytics 4 data and displays it in a formatted table."
    args_schema: Type[BaseModel] = RunReportTableInput

    def _run(self, property_id: str, dimensions: List[str], metrics: List[str], start_date: str, end_date: str) -> str:
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[Dimension(name=dim) for dim in dimensions],
                metrics=[Metric(name=met) for met in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            response = self.data_client.run_report(request)

            headers = [h.name for h in response.dimension_headers] + [h.name for h in response.metric_headers]
            rows = []
            for row in response.rows:
                rows.append([v.value for v in row.dimension_values] + [v.value for v in row.metric_values])

            return tabulate(rows, headers=headers, tablefmt="grid")
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetBigQuerySchemaTool(GoogleAnalytics4LangchainTool):
    name: str = "get_bigquery_schema"
    description: str = "Returns the schema of a BigQuery table. Useful for understanding the structure of the data in BigQuery."
    args_schema: Type[BaseModel] = GetBigQuerySchemaInput

    def _run(self, project_id: str, dataset_id: str, table_id: str) -> str:
        try:
            table_ref = self.bigquery_client.dataset(dataset_id, project=project_id).table(table_id)
            table = self.bigquery_client.get_table(table_ref)
            return str(table.schema)
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class ExecuteBigQuerySQLTool(GoogleAnalytics4LangchainTool):
    name: str = "execute_bigquery_sql"
    description: str = "Executes a SQL query in BigQuery. Useful for complex analysis on BigQuery data."
    args_schema: Type[BaseModel] = ExecuteBigQuerySQLInput

    def _run(self, query: str) -> str:
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            return str([dict(row) for row in results])
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetEventAndConversionDataTool(GoogleAnalytics4lantool):
    name: str = "get_event_and_conversion_data"
    description: str = "Retrieves event and conversion data from Google Analytics 4."
    args_schema: Type[BaseModel] = GetEventAndConversionDataInput

    def _run(self, property_id: str, start_date: str, end_date: str) -> str:
        try:
            request = RunReportRequest(
                property=f"properties/{property_id}",
                dimensions=[
                    Dimension(name="eventName"),
                    Dimension(name="isConversionEvent"),
                ],
                metrics=[
                    Metric(name="eventCount"),
                ],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            )
            response = self.data_client.run_report(request)
            
            report_data = []
            for row in response.rows:
                report_data.append({
                    "eventName": row.dimension_values[0].value,
                    "isConversionEvent": row.dimension_values[1].value,
                    "eventCount": row.metric_values[0].value
                })

            return json.dumps(report_data, indent=4)
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetAudiencesTool(GoogleAnalytics4LangchainTool):
    name: str = "get_ga4_audiences"
    description: str = "Retrieves a list of all audiences for a Google Analytics 4 property."
    args_schema: Type[BaseModel] = GetAudiencesInput

    def _run(self, property_id: str) -> str:
        try:
            request = ListAudiencesRequest(parent=f"properties/{property_id}")
            response = self.data_client.list_audiences(request=request)
            
            audiences = []
            for audience in response.audiences:
                audiences.append({
                    "name": audience.name,
                    "displayName": audience.display_name,
                    "description": audience.description,
                    "membershipDurationDays": audience.membership_duration_days
                })

            return json.dumps(audiences, indent=4)
        except Exception as e:
            return f"An unexpected error occurred: {e}"