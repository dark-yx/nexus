"""Google Ads tools."""
from __future__ import annotations
import json
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, List
from src.auth.google_auth import get_google_credentials
import os
import yaml
from tabulate import tabulate

# --- Input Schemas ---
class ListAccessibleCustomersInput(BaseModel):
    pass

class SearchGoogleAdsInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    query: str = Field(description="The Google Ads Query Language (GAQL) query.")

class CreateCampaignInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    campaign_name: str = Field(description="The name of the new campaign.")
    advertising_channel_type: str = Field(description="The advertising channel type (e.g., 'SEARCH', 'DISPLAY').")
    status: str = Field(description="The status of the campaign (e.g., 'PAUSED', 'ENABLED').")
    budget_amount_micros: int = Field(description="The daily budget for the campaign in micros.")

class GetCampaignPerformanceInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    date_range: str = Field(description="The date range for the report (e.g., 'LAST_7_DAYS', 'LAST_30_DAYS', 'THIS_MONTH').", default="LAST_30_DAYS")

class UpdateCampaignStatusInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    campaign_id: str = Field(description="The ID of the campaign to update.")
    status: str = Field(description="The new status for the campaign (e.g., 'PAUSED', 'ENABLED').")

class GetAdGroupPerformanceInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    date_range: str = Field(description="The date range for the report (e.g., 'LAST_7_DAYS', 'LAST_30_DAYS', 'THIS_MONTH').", default="LAST_30_DAYS")


# --- Tool Implementations ---

class GoogleAdsLangchainTool(BaseTool):
    """A base tool for interacting with the Google Ads API."""
    name: str = "google_ads_base_tool"
    description: str = "A base tool for Google Ads operations."
    client: GoogleAdsClient = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            credentials = get_google_credentials()
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'google-ads.yaml')
            with open(config_path, 'r') as f:
                ads_config = yaml.safe_load(f)

            google_ads_config = {
                "developer_token": ads_config["developer_token"],
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "refresh_token": credentials.refresh_token,
                "use_proto_plus": True
            }
            self.client = GoogleAdsClient.load_from_dict(google_ads_config)
        except Exception as e:
            raise Exception(f"Failed to initialize GoogleAdsClient: {e}")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class ListAccessibleCustomersTool(GoogleAdsLangchainTool):
    name: str = "list_accessible_customers"
    description: str = "Returns a list of customer IDs accessible by the authenticated user. Useful for finding out which Google Ads accounts the user has access to."
    args_schema: Type[BaseModel] = ListAccessibleCustomersInput

    def _run(self) -> List[str]:
        try:
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = customer_service.list_accessible_customers()
            return [resource_name.split('/')[-1] for resource_name in accessible_customers.resource_names]
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class SearchGoogleAdsTool(GoogleAdsLangchainTool):
    name: str = "search_google_ads"
    description: str = "Performs a search query against the Google Ads API for a specific customer. Useful for retrieving detailed performance data with a custom GAQL query."
    args_schema: Type[BaseModel] = SearchGoogleAdsInput

    def _run(self, customer_id: str, query: str) -> str:
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            response = ga_service.search(customer_id=customer_id, query=query)
            return json.dumps([json.loads(row.to_json()) for row in response], indent=4)
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class CreateCampaignTool(GoogleAdsLangchainTool):
    name: str = "create_campaign"
    description: str = "Creates a new campaign in Google Ads. Useful for launching new advertising campaigns."
    args_schema: Type[BaseModel] = CreateCampaignInput

    def _run(self, customer_id: str, campaign_name: str, advertising_channel_type: str, status: str, budget_amount_micros: int) -> str:
        try:
            campaign_budget_service = self.client.get_service("CampaignBudgetService")
            campaign_service = self.client.get_service("CampaignService")

            budget_operation = self.client.get_type("CampaignBudgetOperation")
            budget = budget_operation.create
            budget.name = f"Budget for {campaign_name}"
            budget.delivery_method = self.client.enums.BudgetDeliveryMethodEnum.STANDARD
            budget.amount_micros = budget_amount_micros
            budget_response = campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[budget_operation]
            )
            budget_resource_name = budget_response.results[0].resource_name

            campaign_operation = self.client.get_type("CampaignOperation")
            campaign = campaign_operation.create
            campaign.name = campaign_name
            campaign.advertising_channel_type = self.client.enums.AdvertisingChannelTypeEnum[advertising_channel_type]
            campaign.status = self.client.enums.CampaignStatusEnum[status]
            campaign.campaign_budget = budget_resource_name
            campaign.network_settings.target_google_search = True
            campaign.network_settings.target_search_network = True

            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            return f"Successfully created campaign with resource name: {campaign_response.results[0].resource_name}"
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class UpdateCampaignStatusTool(GoogleAdsLangchainTool):
    name: str = "update_campaign_status"
    description: str = "Updates the status of a campaign in Google Ads (e.g., to 'PAUSED' or 'ENABLED')."
    args_schema: Type[BaseModel] = UpdateCampaignStatusInput

    def _run(self, customer_id: str, campaign_id: str, status: str) -> str:
        try:
            campaign_service = self.client.get_service("CampaignService")
            campaign_operation = self.client.get_type("CampaignOperation")

            campaign = campaign_operation.update
            campaign.resource_name = campaign_service.campaign_path(customer_id, campaign_id)
            campaign.status = self.client.enums.CampaignStatusEnum[status]

            field_mask = self.client.get_type("FieldMask")
            field_mask.paths.append("status")
            campaign_operation.update_mask.CopyFrom(field_mask)

            campaign_response = campaign_service.mutate_campaigns(
                customer_id=customer_id, operations=[campaign_operation]
            )
            return f"Successfully updated campaign {campaign_id} to status {status}."
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetCampaignPerformanceTool(GoogleAdsLangchainTool):
    name: str = "get_campaign_performance"
    description: str = "Retrieves performance metrics (impressions, clicks, cost, conversions) for all campaigns within a specified date range."
    args_schema: Type[BaseModel] = GetCampaignPerformanceInput

    def _run(self, customer_id: str, date_range: str = "LAST_30_DAYS") -> str:
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f'''
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE
                    segments.date DURING {date_range}
                ORDER BY
                    metrics.impressions DESC
            '''
            response = ga_service.search(customer_id=customer_id, query=query)
            results = []
            for row in response:
                metrics = row.metrics
                campaign = row.campaign
                results.append({
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "cost": metrics.cost_micros / 1_000_000,
                    "conversions": metrics.conversions
                })
            return json.dumps(results, indent=4)
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetAdGroupPerformanceTool(GoogleAdsLangchainTool):
    name: str = "get_ad_group_performance"
    description: str = "Retrieves performance metrics for all ad groups within a specified date range."
    args_schema: Type[BaseModel] = GetAdGroupPerformanceInput

    def _run(self, customer_id: str, date_range: str = "LAST_30_DAYS") -> str:
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f'''
                SELECT
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM ad_group
                WHERE
                    segments.date DURING {date_range}
                ORDER BY
                    metrics.impressions DESC
            '''
            response = ga_service.search(customer_id=customer_id, query=query)
            results = []
            for row in response:
                metrics = row.metrics
                ad_group = row.ad_group
                campaign = row.campaign
                results.append({
                    "ad_group_id": ad_group.id,
                    "ad_group_name": ad_group.name,
                    "campaign_id": campaign.id,
                    "campaign_name": campaign.name,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "cost": metrics.cost_micros / 1_000_000,
                    "conversions": metrics.conversions
                })
            return json.dumps(results, indent=4)
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

class GetCampaignPerformanceTableInput(BaseModel):
    customer_id: str = Field(description="The ID of the Google Ads customer.")
    date_range: str = Field(description="The date range for the report (e.g., 'LAST_7_DAYS', 'LAST_30_DAYS', 'THIS_MONTH').", default="LAST_30_DAYS")

class GetCampaignPerformanceTableTool(GoogleAdsLangchainTool):
    name: str = "get_campaign_performance_table"
    description: str = "Retrieves performance metrics for all campaigns within a specified date range and displays them in a formatted table."
    args_schema: Type[BaseModel] = GetCampaignPerformanceTableInput

    def _run(self, customer_id: str, date_range: str = "LAST_30_DAYS") -> str:
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f'''
                SELECT
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions
                FROM campaign
                WHERE
                    segments.date DURING {date_range}
                ORDER BY
                    metrics.impressions DESC
            '''
            response = ga_service.search(customer_id=customer_id, query=query)
            headers = ["Campaign ID", "Campaign Name", "Impressions", "Clicks", "Cost", "Conversions"]
            rows = []
            for row in response:
                metrics = row.metrics
                campaign = row.campaign
                rows.append([
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros / 1_000_000,
                    metrics.conversions
                ])
            return tabulate(rows, headers=headers, tablefmt="grid")
        except GoogleAdsException as ex:
            return f"Google Ads API error: {ex}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"