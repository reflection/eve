import os
import os.path
import pickle
import sqlite3

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI
from slack_sdk import WebClient

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
sqlite3_conn = sqlite3.connect(f"{SLACK_BOT_TOKEN}.db", check_same_thread=False)


def get_google_docs_service():
    """Sets up and returns a Google Docs service with proper authentication."""
    SCOPES = ["https://www.googleapis.com/auth/documents"]
    creds = None

    # Load saved credentials if they exist
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If no valid credentials available, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # Build and return the service
    service = build("docs", "v1", credentials=creds)
    return service


def get_groq_client():
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)


def get_slack_client():
    return WebClient(token=SLACK_BOT_TOKEN)


def get_sqlite3_cursor():
    return sqlite3_conn.cursor()
