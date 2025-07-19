plans = {
    "Starter": {
        "price": 300.00,
        "tools": [
            "Business ideas",
            "Marketing Strategies",
            "Metrics Calculator"
        ]
    },
    "Plus": {
        "price": 650.00,
        "tools": [
            "Business ideas",
            "Marketing Strategies",
            "Metrics Calculator",
            "CRO Funnel",
            "WEB Analysis",
            "SEO Analysis"
        ]
    },
    "Growth+": {
        "price": 1500.00,
        "tools": [
            "Business ideas",
            "Marketing Strategies",
            "Metrics Calculator",
            "CRO Funnel",
            "WEB Analysis",
            "SEO Analysis",
            "Google Ads Analysis",
            "Meta Ads Analysis",
            "Traffic Analysis"
        ]
    }
}


class User:
    def __init__(self, username, plan=None):
        self.username = username
        self.plan = plan
        self.tools = self.assign_tools(plan) if plan else []

    def assign_tools(self, plan):
        if plan in plans:
            return plans[plan]["tools"]
        return []

    def update_plan(self, new_plan):
        if new_plan in plans:
            self.plan = new_plan
            self.tools = self.assign_tools(new_plan)

    def has_access_to(self, tool):
        return tool in self.tools

