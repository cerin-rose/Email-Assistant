"""
main.py — Entry point for the Email Assistant.

Pipeline:
  1. Read emails from data/sample_emails.json
  2. Analyze each one (summarize + classify) using GPT-4o
  3. Draft a reply suggestion using GPT-4o
  4. Save everything to emails.db
  5. Print a clean summary report to the terminal
"""

from dotenv import load_dotenv
load_dotenv()

from assistant.reader import load_emails
from assistant.analyzer import analyze_email
from assistant.replier import draft_reply
from assistant.storage import init_db, save_email, get_all_emails


PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def print_report(emails: list[dict]):
    """Print a human-readable summary of all processed emails."""
    print("\n" + "=" * 65)
    print("  EMAIL ASSISTANT — INBOX REPORT")
    print("=" * 65)

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

    # Step 2: Load emails from source
    emails = load_emails("data/sample_emails.json")

    # Step 3: Process each email
    print()
    for email in emails:
        analysis = analyze_email(email)
        draft = draft_reply(email, analysis)
        save_email(email, analysis, draft)

    # Step 4: Load all processed emails and print report
    processed = get_all_emails()
    print_report(processed)


if __name__ == "__main__":
    main()
