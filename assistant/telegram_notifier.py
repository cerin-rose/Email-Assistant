"""
telegram_notifier.py — Sends email alerts to Telegram and waits for approval.

Flow:
  1. Sends a message with the email summary + draft reply
  2. Shows two buttons: ✅ Send Reply / ❌ Skip
  3. Waits up to 5 minutes for you to tap a button
  4. Returns True (approved) or False (skipped / timed out)
"""

import os
import time
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_approval_request(email: dict, analysis: dict, draft: str) -> bool:
    """Send email details + draft to Telegram. Returns True if approved."""

    text = (
        f"New Email\n"
        f"From: {email['sender']}\n"
        f"Subject: {email['subject']}\n"
        f"Priority: {analysis['priority'].upper()}\n\n"
        f"Summary:\n{analysis['summary']}\n\n"
        f"Draft Reply:\n{draft}\n\n"
        f"Tap a button to respond:"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "Send Reply", "callback_data": "approve"},
            {"text": "Skip", "callback_data": "skip"}
        ]]
    }

    resp = requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": CHAT_ID,
        "text": text,
        "reply_markup": keyboard
    })

    if not resp.ok:
        print(f"[telegram] Failed to send message: {resp.text}")
        return False

    print(f"[telegram] Message sent — waiting up to 5 min for your response...")
    return _wait_for_response(timeout_seconds=300)


def _wait_for_response(timeout_seconds: int = 300) -> bool:
    """Poll Telegram for a button tap. Returns True if approved, False otherwise."""

    # Get current offset so we only see new updates
    resp = requests.get(f"{BASE_URL}/getUpdates").json()
    offset = 0
    if resp.get("result"):
        offset = resp["result"][-1]["update_id"] + 1

    deadline = time.time() + timeout_seconds

    while time.time() < deadline:
        remaining = int(deadline - time.time())
        poll_timeout = min(30, remaining)

        if poll_timeout <= 0:
            break

        resp = requests.get(f"{BASE_URL}/getUpdates", params={
            "offset": offset,
            "timeout": poll_timeout
        }).json()

        for update in resp.get("result", []):
            offset = update["update_id"] + 1

            if "callback_query" in update:
                callback = update["callback_query"]
                data = callback["data"]

                # Dismiss the loading spinner on the button
                requests.post(f"{BASE_URL}/answerCallbackQuery", json={
                    "callback_query_id": callback["id"]
                })

                if data == "approve":
                    print("[telegram] Approved — sending reply")
                    return True
                else:
                    print("[telegram] Skipped")
                    return False

    print("[telegram] No response in 5 min — skipping")
    return False
