"""
main.py — Entry point for the Email Assistant.

Pipeline:
  1. Fetch unread emails from Gmail
  2. Analyze each one (summarize + classify) using GPT-4o
  3. Draft a reply suggestion using GPT-4o
  4. Send alert to Telegram with the draft — wait for approval
  5. If approved: send the reply via Gmail
  6. Save everything to emails.db
  7. Print a clean summary report to the terminal

Run once:       py -3.12 main.py
Run on a loop:  py -3.12 main.py loop
Run loop every N min: py -3.12 main.py loop 10
"""

import sys
import time
from dotenv import load_dotenv
load_dotenv()

from assistant.reader import load_emails, load_emails_gmail
from assistant.analyzer import analyze_email
from assistant.replier import draft_reply
from assistant.storage import init_db, save_email, get_all_emails, is_already_processed
from assistant.telegram_notifier import send_approval_request
from assistant.gmail_sender import send_reply


PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def print_report(emails: list[dict]):
    """Print a human-readable summary of all processed emails."""
    print("\n" + "=" * 65)
    print("  EMAIL ASSISTANT — INBOX REPORT")
    print("=" * 65)

    if not emails:
        print("\n  No emails processed this run.\n")
        print("=" * 65 + "\n")
        return

    for email in emails:
        emoji = PRIORITY_EMOJI.get(email["priority"], "⚪")
        print(f"\n{emoji} [{email['priority'].upper()}] {email['type'].upper()}")
        print(f"   From:    {email['sender']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Date:    {email['date']}")
        print(f"   Summary: {email['summary']}")
        print(f"   Draft reply:\n")
        for line in email["draft_reply"].splitlines():
            print(f"     {line}")
        print("-" * 65)

    total = len(emails)
    high = sum(1 for e in emails if e["priority"] == "high")
    medium = sum(1 for e in emails if e["priority"] == "medium")
    low = sum(1 for e in emails if e["priority"] == "low")
    print(f"\nTotal: {total} emails  |  🚨 {high} high  📋 {medium} medium  💤 {low} low")
    print("=" * 65 + "\n")


def main():
    print("\n[main] Starting Email Assistant...\n")

    # Step 1: Set up the database
    init_db()

    # Step 2: Fetch unread emails from Gmail
    emails = load_emails_gmail(max_results=10)

    if not emails:
        print("[main] No new emails to process.")
        return

    # Step 3: Process each email
    print()
    processed_this_run = []

    for email in emails:
        # Skip if already processed in a previous run
        if is_already_processed(email["id"]):
            print(f"[main] Already processed: {email['subject'][:50]}")
            continue

        # Analyze and draft
        analysis = analyze_email(email)
        draft = draft_reply(email, analysis)

        # Send to Telegram — wait for approval
        approved = send_approval_request(email, analysis, draft)

        if approved:
            send_reply(email, draft)

        # Save to database regardless of approval (so we don't ask again)
        save_email(email, analysis, draft)
        processed_this_run.append(email["id"])

    # Step 4: Print report of everything in the database
    processed = get_all_emails()
    print_report(processed)


def run_loop(interval_minutes: int = 5):
    """Keep checking for new emails every N minutes."""
    print(f"[main] Polling every {interval_minutes} min. Press Ctrl+C to stop.\n")
    while True:
        main()
        print(f"[main] Sleeping {interval_minutes} min...\n")
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "loop":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_loop(interval)
    else:
        main()
