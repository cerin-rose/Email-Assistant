# Email Assistant — Modifications To Do

Work through these one at a time. Check off each one when done.

---

## Mod 5 — Show The Email Date In The Report
- [ ] Done

1. Open `main.py`
2. Find `print_report()` and find this block:
   ```
   print(f"   From:    {email['sender']}")
   print(f"   Subject: {email['subject']}")
   ```
3. Add one line below Subject:
   ```
   print(f"   Date:    {email['date']}")
   ```
4. Save and run `py -3.12 main.py`

---

## Mod 6 — Count And Display Total API Calls
- [ ] Done

1. Open `main.py`
2. Add `api_calls = 0` before the for loop
3. Add `api_calls += 1` after `analyze_email()` and again after `draft_reply()`:
   ```python
   api_calls = 0
   for email in emails:
       analysis = analyze_email(email)
       api_calls += 1
       draft = draft_reply(email, analysis)
       api_calls += 1
       save_email(email, analysis, draft)
   ```
4. Add this line just before `print_report(processed)`:
   ```python
   print(f"\n[main] Total API calls made: {api_calls}")
   ```
5. Save and run `py -3.12 main.py`

---

## Mod 7 — Filter Report To High Priority Only
- [ ] Done

1. Open `main.py`
2. Find these two lines at the bottom of `main()`:
   ```python
   processed = get_all_emails()
   print_report(processed)
   ```
3. Replace with:
   ```python
   processed = get_all_emails()
   high_only = [e for e in processed if e["priority"] == "high"]
   print_report(high_only)
   ```
4. Save and run `py -3.12 main.py`

---

## Mod 8 — Add A Processed Timestamp To The Database
- [ ] Done

1. Open `assistant/storage.py`
2. Add `import datetime` at the top
3. In `init_db()` add `processed_at TEXT` as a new column
4. In `save_email()` add `datetime.datetime.now().isoformat()` as the last value in the INSERT and add `processed_at` to the column list
5. Open `main.py` and add inside `print_report()`:
   ```python
   print(f"   Processed: {email['processed_at']}")
   ```
6. Delete `emails.db` so it rebuilds with the new column
7. Save and run `py -3.12 main.py`

---

## Mod 9 — Save The Report To A Text File
- [ ] Done

1. Open `main.py`
2. Add this new function above `main()`:
   ```python
   def save_report(emails: list[dict]):
       with open("report.txt", "w", encoding="utf-8") as f:
           f.write("EMAIL ASSISTANT REPORT\n")
           f.write("=" * 40 + "\n\n")
           for email in emails:
               f.write(f"[{email['priority'].upper()}] {email['subject']}\n")
               f.write(f"From: {email['sender']}\n")
               f.write(f"Summary: {email['summary']}\n")
               f.write(f"Draft:\n{email['draft_reply']}\n")
               f.write("-" * 40 + "\n\n")
       print("[main] Report saved to report.txt")
   ```
3. Add `save_report(processed)` at the bottom of `main()` after `print_report()`
4. Save and run `py -3.12 main.py`
5. Check your folder — `report.txt` will appear

---

## Mod 10 — Add A CLI Priority Flag
- [ ] Done

1. Open `main.py`
2. Add `import sys` at the very top
3. Find these two lines at the bottom of `main()`:
   ```python
   processed = get_all_emails()
   print_report(processed)
   ```
4. Replace with:
   ```python
   processed = get_all_emails()
   priority_filter = sys.argv[1] if len(sys.argv) > 1 else None
   if priority_filter in ("high", "medium", "low"):
       processed = [e for e in processed if e["priority"] == priority_filter]
       print(f"[main] Showing {priority_filter} priority only\n")
   print_report(processed)
   ```
5. Save and test all three ways:
   ```
   py -3.12 main.py
   py -3.12 main.py high
   py -3.12 main.py low
   ```

---

# Real-World Upgrades

These go beyond small modifications — each one makes the project more like a real tool you'd actually use.

> **Design rule (applies to all Gmail upgrades):** The assistant only processes **unread, incoming emails**. It never re-processes emails it has already seen. This is enforced two ways:
> 1. The Gmail query filters for `UNREAD` label — so only new emails are fetched
> 2. Upgrade B (deduplication) skips anything whose ID is already in the database — safety net in case the same email appears twice

---

## Upgrade A — Connect To A Real Inbox (IMAP)
- [ ] Done

Replace the JSON file with a live inbox using Python's built-in `imaplib`.

**Only unread emails are fetched.** The `mail.search(None, "UNSEEN")` call on step 2 does this — UNSEEN is the IMAP flag for unread. Once the Gmail API version is built, it uses `labelIds=["INBOX", "UNREAD"]` for the same effect.

1. Install nothing — `imaplib` and `email` are built into Python
2. In `assistant/reader.py`, add a new function `load_emails_imap()`:
   ```python
   import imaplib
   import email as emaillib

   def load_emails_imap(host, user, password, folder="INBOX", limit=10):
       mail = imaplib.IMAP4_SSL(host)
       mail.login(user, password)
       mail.select(folder)
       _, ids = mail.search(None, "UNSEEN")
       email_ids = ids[0].split()[-limit:]
       emails = []
       for eid in email_ids:
           _, data = mail.fetch(eid, "(RFC822)")
           msg = emaillib.message_from_bytes(data[0][1])
           body = ""
           if msg.is_multipart():
               for part in msg.walk():
                   if part.get_content_type() == "text/plain":
                       body = part.get_payload(decode=True).decode()
                       break
           else:
               body = msg.get_payload(decode=True).decode()
           emails.append({
               "id": eid.decode(),
               "sender": msg["From"],
               "subject": msg["Subject"],
               "date": msg["Date"],
               "body": body
           })
       mail.logout()
       return emails
   ```
3. In `.env`, add:
   ```
   IMAP_HOST=imap.gmail.com
   IMAP_USER=you@gmail.com
   IMAP_PASS=your-app-password
   ```
   For Gmail: go to Google Account → Security → App Passwords to generate `IMAP_PASS`
4. In `main.py`, replace `load_emails()` with `load_emails_imap(...)`
5. Run `py -3.12 main.py` — it will read real unread emails

---

## Upgrade B — Deduplicate (Don't Re-Process Old Emails)
- [ ] Done

Right now every run processes every email again. This fix skips ones already in the database.

**This is the second layer of the "unread only" guarantee.** Upgrade A filters for unread at fetch time. Upgrade B catches anything that slips through (e.g. an email you manually marked unread again, or a retry after a crash mid-run). Together they ensure each email is processed exactly once.

1. Open `assistant/storage.py`
2. Add a new function:
   ```python
   def is_already_processed(email_id: str) -> bool:
       conn = sqlite3.connect("emails.db")
       cur = conn.cursor()
       cur.execute("SELECT 1 FROM emails WHERE id = ?", (email_id,))
       result = cur.fetchone()
       conn.close()
       return result is not None
   ```
3. Open `main.py` and update the loop:
   ```python
   from assistant.storage import is_already_processed

   for email in emails:
       if is_already_processed(email["id"]):
           print(f"[main] Skipping already processed: {email['subject']}")
           continue
       analysis = analyze_email(email)
       draft = draft_reply(email, analysis)
       save_email(email, analysis, draft)
   ```
4. Run twice — second run should skip all emails

---

## Upgrade C — Approve Before Sending
- [ ] Done

Instead of silently saving drafts, prompt yourself to approve, skip, or edit each one.

1. Open `main.py`
2. Add this function above `main()`:
   ```python
   def review_draft(email: dict, draft: str) -> str | None:
       print(f"\n--- DRAFT FOR: {email['subject']} ---")
       print(draft)
       print("---")
       choice = input("Send this draft? [y=yes / n=skip / e=edit]: ").strip().lower()
       if choice == "y":
           return draft
       elif choice == "e":
           print("Paste your edited reply (press Enter twice when done):")
           lines = []
           while True:
               line = input()
               if line == "":
                   break
               lines.append(line)
           return "\n".join(lines)
       else:
           return None
   ```
3. In the main loop, after `draft_reply()`, call `review_draft()`:
   ```python
   draft = draft_reply(email, analysis)
   approved = review_draft(email, draft)
   if approved:
       save_email(email, analysis, approved)
   ```
4. Run `py -3.12 main.py` and respond to each prompt

---

## Upgrade D — Schedule It To Run Automatically
- [ ] Done

Poll for new emails every N minutes without manually running the script.

1. Open `main.py`
2. Add `import time` at the top
3. Add a new entry point at the bottom of the file:
   ```python
   def run_loop(interval_minutes: int = 5):
       print(f"[main] Starting poll loop every {interval_minutes} min. Ctrl+C to stop.")
       while True:
           print("\n[main] Checking for new emails...")
           main()
           print(f"[main] Sleeping {interval_minutes} min...")
           time.sleep(interval_minutes * 60)

   if __name__ == "__main__":
       import sys
       if len(sys.argv) > 1 and sys.argv[1] == "loop":
           run_loop()
       else:
           main()
   ```
4. Run in polling mode:
   ```
   py -3.12 main.py loop
   ```
5. Press Ctrl+C to stop

---

## Upgrade E — Replace print() With Proper Logging
- [ ] Done

Writes logs to a file so you can see what happened in past runs.

1. Open `main.py`
2. Add at the top:
   ```python
   import logging
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s [%(levelname)s] %(message)s",
       handlers=[
           logging.FileHandler("assistant.log"),
           logging.StreamHandler()
       ]
   )
   logger = logging.getLogger(__name__)
   ```
3. Replace `print(...)` calls in `main.py` with `logger.info(...)`
4. Do the same in the other modules over time
5. After a run, open `assistant.log` to see a timestamped history

---

## Upgrade F — Simple Web UI With Gradio
- [ ] Done

See your emails and drafts in a browser instead of reading terminal output.

1. Install Gradio:
   ```
   pip install gradio
   ```
2. Create a new file `ui.py` in the project root:
   ```python
   import gradio as gr
   from main import main
   from assistant.storage import get_all_emails

   def run_and_show():
       main()
       emails = get_all_emails()
       rows = [[e["subject"], e["sender"], e["priority"], e["summary"]] for e in emails]
       return rows

   demo = gr.Interface(
       fn=run_and_show,
       inputs=[],
       outputs=gr.Dataframe(headers=["Subject", "From", "Priority", "Summary"]),
       title="Email Assistant",
       description="Click Run to process emails and see results."
   )

   demo.launch()
   ```
3. Run it:
   ```
   py -3.12 ui.py
   ```
4. Open the URL it prints (usually `http://127.0.0.1:7860`) in your browser
