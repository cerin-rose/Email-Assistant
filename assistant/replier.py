"""
replier.py — Drafts a reply suggestion for each email using GPT-4o.

The draft is a starting point — the user always reviews and edits
before sending anything. Nothing is sent automatically.
"""

from openai import OpenAI

client = OpenAI()

SYSTEM_PROMPT = """You are a professional email assistant helping someone manage their inbox.
Write a concise, polite draft reply to the email below.

Guidelines:
- Keep it to 2 sentences maximum. Be direct and professional.
- Match the tone of the original (formal for work, casual for family)
- For newsletters or billing notifications, write a brief note explaining
  why no reply is needed, or suggest an action (e.g. "No reply needed — archive this.")
- For security alerts, draft a short acknowledgment or escalation note
- Start with a greeting, end with a sign-off
- Do NOT include a subject line
-Always end every reply with: 'Best regards, [Your Name]"""


def draft_reply(email: dict, analysis: dict) -> str:
    """Ask GPT-4o to draft a reply for this email."""
    email_text = (
        f"From: {email['from']}\n"
        f"Subject: {email['subject']}\n\n"
        f"{email['body']}"
    )

    context = (
        f"Email type: {analysis['type']}\n"
        f"Priority: {analysis['priority']}\n"
        f"Summary: {analysis['summary']}\n\n"
        f"---\n{email_text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=512,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
    )

    draft = response.choices[0].message.content.strip()
    print(f"[replier] Draft ready for '{email['subject'][:50]}'")
    return draft
