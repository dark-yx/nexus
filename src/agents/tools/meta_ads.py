from langchain_core.tools import tool
import requests
import pandas as pd

class MetaAdsTool:
    def __init__(self, access_token: str):
        self.access_token = access_token

    @tool
    def get_campaign_insights(self, ad_account_id: str, start_date: str, end_date: str) -> list:
        """
        Retrieves and returns Facebook Ads data.
        """
        url = f"https://graph.facebook.com/v22.0/{ad_account_id}/insights"
        params = {
            'level': 'campaign',
            'time_range': f'{{"since":"{start_date}","until":"{end_date}"}}',
            'fields': 'campaign_id,campaign_name,objective,spend,impressions,cpm,clicks,cpc,reach,actions,action_values,cost_per_action_type',
            'access_token': self.access_token
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Error getting data from Facebook API: {response.json()}")
        return response.json().get('data', [])

    @tool
    def transform_campaign_data(self, data: list) -> pd.DataFrame:
        """
        Transforms raw campaign data into a pandas DataFrame.
        """
        campaigns = []
        for campaign in data:
            campaign_dict = {
                'campaign_id': campaign.get('campaign_id'),
                'campaign_name': campaign.get('campaign_name'),
                'objective': campaign.get('objective'),
                'clicks': campaign.get('clicks', 0),
                'cpc': campaign.get('cpc', 0),
                'impressions': campaign.get('impressions', 0),
                'cpm': campaign.get('cpm', 0),
                'reach': campaign.get('reach', 0),
                'spend': campaign.get('spend', 0),
                'leads': 0,
                'cost_per_lead': None,
                'messages': None,
                'cost_per_message': None,
                'interactions': None,
                'cost_per_interaction': None,
                'date_start': campaign.get('date_start'),
                'date_stop': campaign.get('date_stop')
            }
            for action in campaign.get('actions', []):
                action_type = action['action_type']
                action_value = int(action['value'])
                if action_type in ['lead', 'leadgen_grouped', 'onsite_conversion.lead_grouped']:
                    campaign_dict['leads'] += action_value
                elif action_type == 'onsite_conversion.messaging_conversation_started_7d':
                    campaign_dict['messages'] = action_value
                elif action_type == 'post_engagement':
                    campaign_dict['interactions'] = action_value
                campaign_dict[f'action_{action_type}'] = action_value
            for cpa in campaign.get('cost_per_action_type', []):
                cpa_type = cpa['action_type']
                cpa_value = cpa['value']
                if cpa_type in ['lead', 'leadgen_grouped', 'onsite_conversion.lead_grouped']:
                    campaign_dict['cost_per_lead'] = cpa_value
                elif cpa_type == 'onsite_conversion.messaging_conversation_started_7d':
                    campaign_dict['cost_per_message'] = cpa_value
                elif cpa_type == 'post_engagement':
                    campaign_dict['cost_per_interaction'] = cpa_value
                campaign_dict[f'cost_per_{cpa_type}'] = cpa_value
            campaigns.append(campaign_dict)
        return pd.DataFrame(campaigns)