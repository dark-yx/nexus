
from ..meta_ads_tool import MetaAdsTool

class MetaAdsAgent:
    def __init__(self, app_id, app_secret, access_token):
        self.tool = MetaAdsTool(app_id, app_secret, access_token)

    def run(self, task):
        # Logic to interpret the task and use the tool
        pass
