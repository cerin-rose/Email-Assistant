"""
gmail_auth.py — Handles Gmail OAuth login and returns a ready-to-use Gmail service.

First run: opens a browser window for you to approve access.
Every run after: silent — reads token.json automatically.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

# Read-only — the assistant can see emails but cannot send, delete, or modify anything
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


def get_gmail_service():
    """Login to Gmail and return a ready-to-use service object."""
    creds = None

    # If we've logged in before, load the saved tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid token, get one
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())                              # silent auto-refresh
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)                # opens browser once

        # Save tokens so next run is silent
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)
