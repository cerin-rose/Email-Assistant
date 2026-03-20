"""
analyzer.py — Summarizes and classifies emails using GPT-4o.

For each email it produces:
  - summary:  1-2 sentence plain-English summary
  - type:     category label (work, personal, newsletter, etc.)
  - priority: high / medium / low
"""

import json
from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """You are an intelligent email assistant.
Analyze the email provided and return a JSON object with exactly these fields:
{
  "summary":  "<1-2 sentence summary of what the email is about>",
  "type":     "<one of: work | personal | newsletter | promotional | billing | security | partnership | spam>",
  "priority": "<one of: high | medium | low>"
}

Priority guidelines:
- high:   requires action soon, security alerts, hard deadlines
- medium: needs a response eventually, meeting requests, proposals
- low:    newsletters, invoices for info only, no-reply notifications
- spam:   always low priority

Return ONLY valid JSON. No extra text."""


def analyze_email(email: dict) -> dict:
    """Send one email to GPT-4o and get back summary + classification."""
    email_text = (
        f"From: {email['from']}\n"
        f"Subject: {email['subject']}\n"
        f"Date: {email['date']}\n\n"
        f"{email['body']}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text},
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if the model returns something unexpected
        result = {
            "summary": "Could not parse summary.",
            "type": "unknown",
            "priority": "low",
        }

    print(f"[analyzer] '{email['subject'][:50]}' → {result['type']} / {result['priority']}")
    return result
