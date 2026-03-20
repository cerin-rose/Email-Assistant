"""
gmail_sender.py — Sends a reply email via the Gmail API.

Called only after the user approves the draft in Telegram.
Nothing is sent automatically without approval.
"""

import base64
from email.mime.text import MIMEText
from assistant.gmail_auth import get_gmail_service


def send_reply(email: dict, draft: str):
    """Send the approved draft as a reply to the original sender."""
    service = get_gmail_service()

    msg = MIMEText(draft)
    msg["to"] = email["sender"]
    msg["subject"] = f"Re: {email['subject']}"

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print(f"[sender] Reply sent to {email['sender']}")
