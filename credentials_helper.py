import os
import json
from google.oauth2 import service_account

SCOPES_GSC = ['https://www.googleapis.com/auth/webmasters.readonly']
SCOPES_GA4 = ['https://www.googleapis.com/auth/analytics.readonly']

CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service_account.json')

def get_credentials(scopes):
    """
    Retrieves Google Service Account credentials using:
    1. Environment variables (GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_CREDENTIALS)
    2. Local service_account.json file
    """
    env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_CREDENTIALS')
    if env_json:
        try:
            info = json.loads(env_json) if isinstance(env_json, str) else env_json
            return service_account.Credentials.from_service_account_info(info, scopes=scopes)
        except Exception as e:
            print(f"[Credentials] Error loading from environment variable: {e}")

    if os.path.exists(CREDENTIALS_FILE):
        try:
            return service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
        except Exception as e:
            print(f"[Credentials] Error loading from file {CREDENTIALS_FILE}: {e}")

    raise RuntimeError(
        "Google Service Account credentials not found! "
        "Please add 'GOOGLE_SERVICE_ACCOUNT_JSON' in Vercel Environment Variables or supply service_account.json locally."
    )
