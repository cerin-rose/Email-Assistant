"""
reader.py — Loads emails from a JSON file.

In the MVP we read from a local JSON file instead of a real inbox.
Later you could swap this out for the Gmail API or IMAP without
changing any other part of the system.
"""

import json
from pathlib import Path


def load_emails(path: str = "data/sample_emails.json") -> list[dict]:
    """Read all emails from the JSON source file."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"Email source not found: {path}")

    with open(file, encoding="utf-8") as f:
        emails = json.load(f)

    print(f"[reader] Loaded {len(emails)} emails from {path}")
    return emails
