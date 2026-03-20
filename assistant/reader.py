"""
reader.py — Loads emails either from a JSON file (mock) or Gmail (real).

load_emails()        → reads from a local JSON file (original mock version)
load_emails_gmail()  → reads real unread emails from Gmail API
"""

import json
import base64
from pathlib import Path
from assistant.gmail_auth import get_gmail_service


def load_emails(path: str = "data/sample_emails.json") -> list[dict]:
    """Read all emails from the JSON source file (mock/demo mode)."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"Email source not found: {path}")

    with open(file, encoding="utf-8") as f:
        emails = json.load(f)

    print(f"[reader] Loaded {len(emails)} emails from {path}")
    return emails


def load_emails_gmail(max_results: int = 10) -> list[dict]:
    """Read unread emails from the real Gmail inbox."""
    service = get_gmail_service()

    # Fetch list of unread emails in the inbox
    result = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        print("[reader] No unread emails found.")
        return []

    emails = []
    for msg_ref in messages:
        # msg_ref only has the ID — fetch the full email
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

        emails.append({
            "id":      msg["id"],
            "sender":  headers.get("From", ""),
            "subject": headers.get("Subject", ""),
            "date":    headers.get("Date", ""),
            "body":    _extract_body(msg["payload"])
        })

    print(f"[reader] Loaded {len(emails)} unread emails from Gmail")
    return emails


def _extract_body(payload: dict) -> str:
    """Pull plain text body out of Gmail's nested payload format."""
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    data = payload.get("body", {}).get("data", "")
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
