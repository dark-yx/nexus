# reviews.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from flask import current_app as app
import logging
import db

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.WARNING)

ACCOUNT_ID = "11877736616708637164"
LOCATION_ID = "13584117045524461427"

def refresh_google_credentials(credentials_dict):
    credentials = Credentials(
        token=credentials_dict['access_token'],
        token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret']
    )

    if credentials.expired:
        credentials.refresh(Request())
        db.save_tokens_to_db(credentials_dict['email'], credentials.token)
        
    return credentials

def submit_google_review(credentials_dict, review):
    try:
        credentials = refresh_google_credentials(credentials_dict)
        service = build('mybusinessbusinessinformation', 'v1', credentials=credentials)
        
        place_id = get_place_id(service)
        review_link = f"https://search.google.com/local/writereview?placeid={place_id}"
        
        return review_link
    except Exception as e:
        raise ValueError(f"Error submitting review: {e}")

def get_place_id(service):
    response = service.accounts().locations().get(
        name=f'accounts/{ACCOUNT_ID}/locations/{LOCATION_ID}',
        readMask='metadata'
    ).execute()
    return response.get("metadata", {}).get("placeId", "")
