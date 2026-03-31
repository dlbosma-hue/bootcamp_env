"""
Fitbit OAuth 2.0 — one-time setup.

Run: python src/data_loaders/fitbit_auth.py

1. A browser opens. Click Allow on the Fitbit authorisation page.
2. You get redirected to a localhost URL that says "site cannot be reached" — this is expected.
3. Copy the full URL from your browser address bar and paste it into the terminal.
4. Tokens are saved to data/fitbit_tokens.json and auto-refresh from then on.

Prerequisite: Your Fitbit Developer app must have http://127.0.0.1:8080/ as a
registered Callback URL. Set this at https://dev.fitbit.com/apps — edit your app,
paste the callback URL, save.
"""

import json
import os
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

load_dotenv()

CLIENT_ID = os.environ["FITBIT_CLIENT_ID"]
CLIENT_SECRET = os.environ["FITBIT_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8080/"
AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
SCOPES = ["activity", "heartrate"]

TOKEN_FILE = Path(__file__).parent.parent.parent / "data" / "fitbit_tokens.json"


def run_auth_flow():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # allow http for localhost only

    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    auth_url, _ = oauth.authorization_url(AUTH_URL, prompt="login consent")

    print("\nOpening Fitbit authorisation page in your browser...")
    print("If the browser does not open, visit this URL manually:\n")
    print(auth_url)
    webbrowser.open(auth_url)

    print("\n--- After clicking Allow ---")
    print("You will be redirected to a localhost URL that shows 'site cannot be reached'.")
    print("Copy the FULL URL from your browser address bar and paste it below.\n")
    redirect_response = input("Paste the full redirect URL here: ").strip()

    # Extract authorisation code from the redirect URL
    parsed = urlparse(redirect_response)
    params = parse_qs(parsed.query)
    if "code" not in params:
        raise ValueError(
            "Could not find authorisation code in URL. "
            "Make sure you copied the full URL including '?code=...'"
        )

    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=CLIENT_SECRET,
        authorization_response=redirect_response,
    )

    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps(token, indent=2))
    print(f"\nTokens saved to {TOKEN_FILE}")
    print("Setup complete. You do not need to run this again — tokens auto-refresh.")
    return token


if __name__ == "__main__":
    run_auth_flow()
