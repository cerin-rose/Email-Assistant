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
