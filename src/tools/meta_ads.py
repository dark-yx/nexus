"""Meta Ads tools."""
from __future__ import annotations
import json
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from langchain_core.tools import BaseTool
from pydantic.v1 import BaseModel, Field
from typing import Type, List
from src.auth.meta_ads_auth import get_meta_ads_credentials

# --- Input Schemas ---
class ListAdAccountsInput(BaseModel):
    pass

class GetCampaignsInput(BaseModel):
    ad_account_id: str = Field(description="The ID of the ad account.")

class GetAdSetsInput(BaseModel):
    campaign_id: str = Field(description="The ID of the campaign.")

class GetAdsInput(BaseModel):
    ad_set_id: str = Field(description="The ID of the ad set.")

class GetCampaignInsightsInput(BaseModel):
    campaign_id: str = Field(description="The ID of the campaign.")
    date_preset: str = Field(description="The date preset for the insights (e.g., 'last_28_days').")

class GetAdCreativeInput(BaseModel):
    ad_id: str = Field(description="The ID of the ad.")

class CreateCampaignInput(BaseModel):
    ad_account_id: str = Field(description="The ID of the ad account.")
    name: str = Field(description="The name of the campaign.")
    objective: str = Field(description="The objective of the campaign.")
    status: str = Field(description="The status of the campaign (e.g., 'PAUSED', 'ACTIVE').")

class UpdateCampaignStatusInput(BaseModel):
    campaign_id: str = Field(description="The ID of the campaign to update.")
    status: str = Field(description="The new status for the campaign (e.g., 'PAUSED', 'ACTIVE').")

# --- Tool Implementations ---

class MetaAdsLangchainTool(BaseTool):
    """A base tool for interacting with the Meta Ads API."""
    name: str = "meta_ads_base_tool"
    description: str = "A base tool for Meta Ads operations."
    api: FacebookAdsApi = None

    def __init__(self, **data):
        super().__init__(**data)
        try:
            credentials = get_meta_ads_credentials()
            self.api = FacebookAdsApi.init(
                app_id=credentials["app_id"],
                app_secret=credentials["app_secret"],
                access_token=credentials["access_token"],
            )
        except Exception as e:
            raise Exception(f"Failed to initialize MetaAds API: {e}")

    def _run(self, *args, **kwargs):
        raise NotImplementedError("This base tool should not be run directly.")

class ListAdAccountsTool(MetaAdsLangchainTool):
    name: str = "list_meta_ad_accounts"
    description: str = "Lists all ad accounts the user has access to."
    args_schema: Type[BaseModel] = ListAdAccountsInput

    def _run(self) -> str:
        try:
            me = User(fbid='me')
            ad_accounts = me.get_ad_accounts()
            return json.dumps([account.export_all_data() for account in ad_accounts], indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetCampaignsTool(MetaAdsLangchainTool):
    name: str = "get_meta_campaigns"
    description: str = "Gets all campaigns for an ad account."
    args_schema: Type[BaseModel] = GetCampaignsInput

    def _run(self, ad_account_id: str) -> str:
        try:
            ad_account = AdAccount(ad_account_id)
            campaigns = ad_account.get_campaigns(fields=[Campaign.Field.name, Campaign.Field.objective, Campaign.Field.status])
            return json.dumps([campaign.export_all_data() for campaign in campaigns], indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetAdSetsTool(MetaAdsLangchainTool):
    name: str = "get_meta_ad_sets"
    description: str = "Gets all ad sets for a campaign."
    args_schema: Type[BaseModel] = GetAdSetsInput

    def _run(self, campaign_id: str) -> str:
        try:
            campaign = Campaign(campaign_id)
            ad_sets = campaign.get_ad_sets(fields=[AdSet.Field.name, AdSet.Field.status])
            return json.dumps([ad_set.export_all_data() for ad_set in ad_sets], indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetAdsTool(MetaAdsLangchainTool):
    name: str = "get_meta_ads"
    description: str = "Gets all ads for an ad set."
    args_schema: Type[BaseModel] = GetAdsInput

    def _run(self, ad_set_id: str) -> str:
        try:
            ad_set = AdSet(ad_set_id)
            ads = ad_set.get_ads(fields=[Ad.Field.name, Ad.Field.status])
            return json.dumps([ad.export_all_data() for ad in ads], indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetCampaignInsightsTool(MetaAdsLangchainTool):
    name: str = "get_meta_campaign_insights"
    description: str = "Gets insights for a campaign."
    args_schema: Type[BaseModel] = GetCampaignInsightsInput

    def _run(self, campaign_id: str, date_preset: str) -> str:
        try:
            campaign = Campaign(campaign_id)
            insights = campaign.get_insights(params={'date_preset': date_preset})
            return json.dumps([insight.export_all_data() for insight in insights], indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class GetAdCreativeTool(MetaAdsLangchainTool):
    name: str = "get_meta_ad_creative"
    description: str = "Gets the creative for an ad."
    args_schema: Type[BaseModel] = GetAdCreativeInput

    def _run(self, ad_id: str) -> str:
        try:
            ad = Ad(ad_id)
            creative = ad.get_ad_creative(fields=[AdCreative.Field.name, AdCreative.Field.body, AdCreative.Field.image_url, AdCreative.Field.video_id])
            return json.dumps(creative.export_all_data(), indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class CreateCampaignTool(MetaAdsLangchainTool):
    name: str = "create_meta_campaign"
    description: str = "Creates a new campaign in Meta Ads."
    args_schema: Type[BaseModel] = CreateCampaignInput

    def _run(self, ad_account_id: str, name: str, objective: str, status: str) -> str:
        try:
            ad_account = AdAccount(ad_account_id)
            params = {
                'name': name,
                'objective': objective,
                'status': status,
                'special_ad_categories': []
            }
            campaign = ad_account.create_campaign(params=params)
            return json.dumps(campaign.export_all_data(), indent=4)
        except Exception as e:
            return f"An error occurred: {e}"

class UpdateCampaignStatusTool(MetaAdsLangchainTool):
    name: str = "update_meta_campaign_status"
    description: str = "Updates the status of a campaign in Meta Ads."
    args_schema: Type[BaseModel] = UpdateCampaignStatusInput

    def _run(self, campaign_id: str, status: str) -> str:
        try:
            campaign = Campaign(campaign_id)
            campaign.update({Campaign.Field.status: status})
            return json.dumps({'success': True, 'campaign_id': campaign_id, 'status': status}, indent=4)
        except Exception as e:
            return f"An error occurred: {e}"