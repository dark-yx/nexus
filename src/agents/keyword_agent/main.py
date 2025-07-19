
from .tools.google_ads import keyword_research

def run_keyword_research(client, customer_id, location_ids, language_id, keyword_texts, page_url, user_id, db):
    return keyword_research(client, customer_id, location_ids, language_id, keyword_texts, page_url, user_id, db)
