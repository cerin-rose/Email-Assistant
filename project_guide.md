# Email Assistant — Project Guide

---

## What This Project Does

This project is an automated email assistant. It connects to your real Gmail inbox, reads your unread emails, figures out what each one is about, decides how urgent it is, and writes a draft reply — all using AI.

Instead of manually reading every email and typing replies, you run one command and get a full report with summaries and ready-to-edit draft replies sorted by priority.

---

## How It Was Built

This project was built MVP-first. MVP stands for Minimum Viable Product — build the simplest version that works, then upgrade one piece at a time.

**Phase 1 (MVP):** Used a local JSON file as the email source to prove the core pipeline worked — load, analyze, reply, save, report.

**Phase 2 (current):** Replaced the JSON file with a real Gmail inbox using the Gmail API and OAuth 2.0 authentication. Everything else in the pipeline stayed the same — only `reader.py` changed and `gmail_auth.py` was added.

Still using:
- A terminal report as the interface
- SQLite as the database (built into Python, zero setup)

---

## Tech Stack

| Tool | What It Is | Why It Was Chosen |
|---|---|---|
| Python 3.12 | Programming language | Readable, beginner-friendly, great AI ecosystem |
| `openai` library | SDK to talk to GPT-4o | Official OpenAI SDK, simple API |
| `google-auth` + `google-api-python-client` | Gmail API access | Official Google libraries, handles OAuth tokens automatically |
| `python-dotenv` | Reads `.env` files | Keeps API keys out of code safely |
| `sqlite3` | Database | Built into Python, zero setup needed |
| Gmail API | Real email source | Reads live unread emails with read-only OAuth scope |
| Telegram Bot API | Approval notifications | Free, instant, no extra library needed |

---

## Folder Structure

```
email-assistant/
├── .env                        Secret API key (never share this)
├── .env.example                Template showing what .env should look like
├── requirements.txt            List of libraries to install
├── main.py                     Entry point — runs the full pipeline
├── emails.db                   Database file created automatically on first run
├── credentials.json            Gmail OAuth credentials — downloaded from Google Cloud Console (never commit)
├── token.json                  Auto-created after first Gmail login (never commit)
├── project_guide.md            This file
├── data/
│   └── sample_emails.json      Fake inbox for testing (mock mode)
└── assistant/
    ├── __init__.py             Makes the folder importable as a Python package
    ├── gmail_auth.py           Handles Gmail OAuth login and token management
    ├── reader.py               Loads emails from Gmail inbox (or JSON for testing)
    ├── analyzer.py             Sends emails to GPT-4o for classification
    ├── replier.py              Sends emails to GPT-4o for draft replies
    └── storage.py              Saves and retrieves results from SQLite
```

---

## How The Pipeline Works

Every email goes through these steps in order:

```
Gmail inbox (unread emails only)
      ↓
  gmail_auth.py  →  OAuth login / token refresh
      ↓
  reader.py      →  fetches emails from Gmail API
      ↓
  analyzer.py    →  asks GPT-4o: what type is this? how urgent?
      ↓
  replier.py     →  asks GPT-4o: write a draft reply
      ↓
  storage.py     →  saves everything to emails.db
      ↓
  terminal report  (sorted by priority)
```

---

## File By File Breakdown

---

### `.env`
- **Category:** Config
- **Role:** Stores your OpenAI API key privately on your computer
- **Remove it:** Everything crashes — no API key means every OpenAI call is rejected
- **Connects to:** `main.py` loads it via `load_dotenv()`, then `analyzer.py` and `replier.py` use the key automatically

---

### `.env.example`
- **Category:** Config
- **Role:** A safe public template showing what `.env` should look like, with no real key inside
- **Remove it:** Nothing breaks — it is only a guide for humans, not used by any code
- **Connects to:** Nothing

---

### `requirements.txt`
- **Category:** Config
- **Role:** The shopping list of external libraries pip needs to install
- **Remove it:** The code still runs if libraries are already installed, but fresh setups will fail
- **Connects to:** Nothing in the code — only used by the `pip install` command

---

### `main.py`
- **Category:** Logic
- **Role:** The entry point and conductor — calls every other part in the correct order
- **Remove it:** Nothing runs at all
- **Connects to:** Every file in the project

---

### `emails.db`
- **Category:** Data
- **Role:** The SQLite database file where all processed emails are saved permanently
- **Remove it:** Nothing crashes — it gets recreated automatically on next run, but all previous results are lost
- **Connects to:** Only `storage.py` reads and writes to it

---

### `data/sample_emails.json`
- **Category:** Data
- **Role:** The fake inbox — 6 realistic emails used to test the pipeline
- **Remove it:** `reader.py` crashes immediately trying to open a file that does not exist
- **Connects to:** Only `reader.py` opens this file

---

### `assistant/__init__.py`
- **Category:** Config
- **Role:** Empty file that tells Python this folder is a package you can import from
- **Remove it:** `main.py` crashes on the first import with `ModuleNotFoundError`
- **Connects to:** Nothing directly — it just enables all the other imports

---

### `assistant/gmail_auth.py`
- **Category:** Integration
- **Role:** Handles Gmail OAuth 2.0 login. On first run opens a browser for you to approve access. On every run after reads `token.json` silently. Auto-refreshes the token when it expires.
- **Remove it:** `reader.py` crashes on import, no Gmail connection possible
- **Connects to:** Reads `credentials.json`, writes `token.json`, called by `reader.py`

---

### `assistant/reader.py`
- **Category:** Logic
- **Role:** Fetches unread emails from the real Gmail inbox using the Gmail API. Also keeps the original `load_emails()` function for testing with the JSON mock.
- **Remove it:** `main.py` crashes on import, no emails are loaded
- **Connects to:** Calls `gmail_auth.py` to get the Gmail connection, returns emails to `main.py`

---

### `assistant/analyzer.py`
- **Category:** Integration
- **Role:** Sends each email to GPT-4o and gets back a summary, type, and priority in JSON format
- **Remove it:** `main.py` crashes on import, no classification happens
- **Connects to:** Receives emails from `main.py`, calls OpenAI API over the internet, returns analysis to `main.py`

---

### `assistant/replier.py`
- **Category:** Integration
- **Role:** Sends each email plus its analysis to GPT-4o and gets back a draft reply
- **Remove it:** `main.py` crashes on import, no draft replies are generated
- **Connects to:** Receives email and analysis from `main.py`, calls OpenAI API over the internet, returns draft text to `main.py`

---

### `assistant/storage.py`
- **Category:** Logic + Data
- **Role:** Creates the database, saves processed emails into it, and retrieves them for the report
- **Remove it:** `main.py` crashes on import, nothing is saved, no report is printed
- **Connects to:** Called three times by `main.py` — setup, save, and fetch. Reads and writes `emails.db`

---

## Key Functions and Logic

---

### `main.py` — `load_dotenv()`

```python
from dotenv import load_dotenv
load_dotenv()
```

Reads `.env` and loads the API key into memory. Must run before any OpenAI call.
Remove it and every API call fails with an authentication error.

---

### `main.py` — `main()`

```python
def main():
    init_db()
    emails = load_emails()
    for email in emails:
        analysis = analyze_email(email)
        draft = draft_reply(email, analysis)
        save_email(email, analysis, draft)
    processed = get_all_emails()
    print_report(processed)
```

The conductor. Calls every other function in the right order.
The `for` loop processes each email one at a time — analyze, reply, save — before moving to the next.

---

### `main.py` — `print_report(emails)`

```python
def print_report(emails: list[dict]):
```

- **Input:** List of processed email dictionaries
- **Output:** Prints coloured terminal report, nothing returned
- **Role:** Pure display — formats and shows the final results
- **Remove it:** No crash, just no visible report printed

---

### `reader.py` — `load_emails(path)`

```python
def load_emails(path: str = "data/sample_emails.json") -> list[dict]:
```

- **Input:** File path (defaults to sample emails if not provided)
- **Output:** List of email dictionaries
- **Key line:** `if not file.exists(): raise FileNotFoundError(...)` — gives a clear error instead of a confusing crash
- **Core logic:** Yes — nothing works without emails

---

### `analyzer.py` — `SYSTEM_PROMPT`

```python
SYSTEM_PROMPT = """You are an intelligent email assistant.
Return JSON with summary, type, priority..."""
```

Not a function — a constant. But critically important.
This is the instruction given to GPT before showing it the email.
Without it GPT replies conversationally instead of returning clean JSON.
Changing it changes how GPT responds — the most impactful thing to experiment with.

---

### `analyzer.py` — `analyze_email(email)`

```python
def analyze_email(email: dict) -> dict:
```

- **Input:** One email dictionary
- **Output:** `{"summary": "...", "type": "work", "priority": "high"}`
- **Key line:** `json.loads(raw)` — converts GPT's text response into a real Python dictionary
- **Error handling:** If GPT returns invalid JSON, falls back to `{"type": "unknown", "priority": "low"}` instead of crashing
- **Core logic:** Yes — this is where classification happens

The API call structure:
```python
messages=[
    {"role": "system", "content": SYSTEM_PROMPT},  # instruction to GPT
    {"role": "user", "content": email_text},        # the actual email
]
```

---

### `replier.py` — `draft_reply(email, analysis)`

```python
def draft_reply(email: dict, analysis: dict) -> str:
```

- **Input:** Original email + analysis from `analyze_email()`
- **Output:** Draft reply as a plain string
- **Key design:** Sends both the email AND its analysis to GPT so the reply matches the tone and context
- **Core logic:** Yes for draft replies — removing it means no drafts are generated

---

### `storage.py` — `init_db()`

```python
conn.execute("CREATE TABLE IF NOT EXISTS processed_emails (...)")
```

- **Input:** Nothing
- **Output:** Creates `emails.db` and the table structure on disk
- **Key phrase:** `IF NOT EXISTS` — safe to run multiple times, never wipes existing data
- **Core logic:** Yes — must run before any saves

---

### `storage.py` — `save_email(email, analysis, draft)`

```python
def save_email(email: dict, analysis: dict, draft: str):
```

- **Input:** Original email, analysis dict, draft reply string
- **Output:** Writes one row to the database, nothing returned
- **Key phrase:** `INSERT OR REPLACE` — if this email ID already exists, overwrite it instead of creating a duplicate
- **Core logic:** Yes — without it results are lost when the program stops

---

### `storage.py` — `get_all_emails()`

```python
def get_all_emails() -> list[dict]:
```

- **Input:** Nothing
- **Output:** List of all processed email dictionaries sorted by priority
- **Key logic:** Converts priority words to numbers for sorting:
```sql
CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
```
This is necessary because you cannot sort "high", "medium", "low" alphabetically — they need to be converted to 1, 2, 3 first so high priority appears at the top.

---

## Core Concepts You Must Understand

---

### 1. APIs (Application Programming Interface)
**Level:** Beginner

**Simple explanation:**
An API is a way for two programs to talk to each other over the internet. You send a request, you get a response back. Think of it like ordering food — you tell the kitchen what you want, the kitchen makes it, and sends it back to you. You never see the kitchen.

**Why it matters here:**
Your code has no AI inside it. All the intelligence comes from OpenAI's servers. Your code sends the email text to OpenAI over the internet and receives the summary back. Without the API your project is just a file reader.

**Where it appears:**
`analyzer.py` and `replier.py` — every `client.chat.completions.create(...)` call is an API request going out over the internet to OpenAI.

---

### 2. Authentication (API Keys)
**Level:** Beginner

**Simple explanation:**
Authentication means proving who you are. An API key is like a password that proves you have an OpenAI account. Every request you send includes this key. If the key is missing or wrong, OpenAI rejects the request immediately.

**Why it matters here:**
Without authentication nothing works. The API key is also how OpenAI knows which account to charge for usage.

**Where it appears:**
`.env` stores the key. `load_dotenv()` in `main.py` loads it. The `openai` library picks it up automatically from there and attaches it to every request.

**Golden rule:** Never put your API key directly in your code. Always use `.env`.

---

### 3. Environment Variables
**Level:** Beginner

**Simple explanation:**
An environment variable is a value stored on your computer's system — outside of your code files. Your program can read it at runtime. It is how you pass secrets (like API keys) to your program without writing them into the code itself.

**Why it matters here:**
If you wrote your API key directly in `analyzer.py` and shared the code with someone, they would have your key. Environment variables prevent that. The `.env` file stores the variable locally. `load_dotenv()` reads it into memory when the program starts.

**Where it appears:**
`.env` file, `.env.example` template, and `load_dotenv()` at the top of `main.py`.

---

### 4. JSON (JavaScript Object Notation)
**Level:** Beginner

**Simple explanation:**
JSON is a universal format for storing and sending structured data as text. It looks like a Python dictionary. It is how data travels between your code and OpenAI's servers — you send text, OpenAI sends back JSON.

**Why it matters here:**
Your emails are stored as JSON. When GPT responds with a classification, it returns JSON. Your code then parses that JSON into a Python dictionary so you can actually use the values.

**Where it appears:**
- `data/sample_emails.json` — email source stored as JSON
- `analyzer.py` — `json.loads(raw)` converts GPT's text response into a Python dictionary
- The `SYSTEM_PROMPT` explicitly tells GPT to return JSON

---

### 5. Prompt Engineering
**Level:** Intermediate

**Simple explanation:**
Prompt engineering is the skill of writing instructions to an AI model so it returns exactly what you need. The words you use, the format you ask for, and the examples you give all change the quality of the output dramatically.

**Why it matters here:**
This is the most impactful thing in the entire project. A badly written prompt makes GPT return random conversational text. A well written prompt makes it return clean structured JSON every time. The classification bug you saw (emails showing `unknown / low`) is a prompt engineering problem — GPT returned JSON in a slightly different format than expected.

**Where it appears:**
`SYSTEM_PROMPT` in `analyzer.py` and `replier.py`. These are the instructions given to GPT before it sees the email.

**The two roles:**
```python
{"role": "system", "content": SYSTEM_PROMPT}  # your instructions to GPT
{"role": "user", "content": email_text}        # the actual email to process
```

---

### 6. Classification
**Level:** Intermediate

**Simple explanation:**
Classification means putting something into a category. You give the AI an input and it assigns a label to it. In this project each email gets two labels — a type (work, personal, newsletter) and a priority (high, medium, low).

**Why it matters here:**
Classification is what makes the project useful. Without it every email looks equally important. With it you can sort, filter, and focus on what actually matters first.

**Where it appears:**
`analyzer.py` — the entire purpose of this file is classification. The `SYSTEM_PROMPT` defines the possible categories and the rules for choosing between them.

---

### 7. Summarization
**Level:** Intermediate

**Simple explanation:**
Summarization means taking a long piece of text and condensing it into the key point in one or two sentences. You are asking the AI to read and compress.

**Why it matters here:**
Instead of reading the full body of every email you see a one-line summary in the report. That is the entire point — saving you time.

**Where it appears:**
`analyzer.py` — the `summary` field in the JSON response from GPT. The `SYSTEM_PROMPT` instructs GPT to write a 1-2 sentence summary.

---

### 8. Workflow Logic (Pipeline)
**Level:** Beginner

**Simple explanation:**
A pipeline is a series of steps where the output of one step becomes the input of the next. Like an assembly line — each station does one job and passes the result forward.

**Why it matters here:**
The entire project is a pipeline. Email comes in → gets analyzed → gets a draft reply → gets saved → gets displayed. Each step depends on the previous one. If any step fails the pipeline stops.

**Where it appears:**
`main.py` — the `for` loop and the sequence of function calls inside it is the pipeline.

```
load → analyze → reply → save → report
```

---

### 9. Error Handling
**Level:** Beginner

**Simple explanation:**
Error handling means writing code that expects things to go wrong and deals with it gracefully instead of crashing. The `try/except` pattern in Python is the main tool for this.

**Why it matters here:**
GPT does not always return perfectly formatted JSON. Sometimes it adds extra text, sometimes it wraps the JSON in markdown. Without error handling one bad response crashes the whole program. With it the program catches the bad response, uses a safe fallback, and keeps running.

**Where it appears:**
`analyzer.py`:
```python
try:
    result = json.loads(raw)
except json.JSONDecodeError:
    result = {"summary": "Could not parse.", "type": "unknown", "priority": "low"}
```
`reader.py`:
```python
if not file.exists():
    raise FileNotFoundError(f"Email source not found: {path}")
```

---

### 10. Data Parsing
**Level:** Beginner

**Simple explanation:**
Parsing means reading raw text and converting it into a structured format your code can work with. GPT returns plain text. You need to convert that text into a Python dictionary before you can use the values inside it.

**Why it matters here:**
GPT is a text generator. It does not natively return Python objects — it returns strings. Parsing is the bridge between "text GPT returned" and "data your code can actually use."

**Where it appears:**
`analyzer.py` — `json.loads(raw)` converts the raw text string from GPT into a real Python dictionary.
`reader.py` — `json.load(f)` converts the JSON file into a Python list of dictionaries.

---

### 11. Separation of Concerns
**Level:** Intermediate

**Simple explanation:**
This is a design principle that says each file or function should do exactly one job. Reading emails is one job. Classifying them is another. Saving them is another. They should not be mixed together.

**Why it matters here:**
Because of this principle you can swap out any single piece without breaking the rest. Want to use Gmail instead of a JSON file? Change only `reader.py`. Want to swap the AI model? Change only `analyzer.py` and `replier.py`. Nothing else changes.

**Where it appears:**
The entire folder structure. Each file has one job. `reader.py` only reads. `analyzer.py` only analyzes. `storage.py` only stores.

---

### 12. Database Persistence
**Level:** Beginner

**Simple explanation:**
When a Python program stops running, everything stored in variables disappears. A database saves data permanently to disk so it survives after the program ends. You can read it back the next time the program runs.

**Why it matters here:**
Without the database you would lose all analysis and draft replies the moment `main.py` finishes. With it the results are permanently saved and can be queried, filtered, or displayed in a future web interface.

**Where it appears:**
`storage.py` — all three functions (`init_db`, `save_email`, `get_all_emails`) and `emails.db` on disk.

---

### Concept Levels At A Glance

| Concept | Level | Most Important File |
|---|---|---|
| APIs | Beginner | `analyzer.py`, `replier.py` |
| Authentication / API Keys | Beginner | `.env`, `main.py` |
| Environment Variables | Beginner | `.env`, `main.py` |
| JSON | Beginner | `analyzer.py`, `sample_emails.json` |
| Error Handling | Beginner | `analyzer.py`, `reader.py` |
| Data Parsing | Beginner | `analyzer.py`, `reader.py` |
| Workflow Logic / Pipeline | Beginner | `main.py` |
| Database Persistence | Beginner | `storage.py` |
| Classification | Intermediate | `analyzer.py` |
| Summarization | Intermediate | `analyzer.py` |
| Prompt Engineering | Intermediate | `analyzer.py`, `replier.py` |
| Separation of Concerns | Intermediate | Entire project structure |
| Email Parsing | Beginner | `analyzer.py` |
| Database Persistence | Beginner | `storage.py` |

---

### 11. Email Parsing
**Level:** Beginner

**What it is:** Reading an email's raw data and pulling out the specific parts you care about — sender, subject, body, date.

**Why it matters here:** You don't want to send GPT a messy blob of data. You extract the relevant fields and format them cleanly before sending. In a real project with Gmail this step becomes much more complex — emails contain HTML, attachments, encoding issues. That is why `reader.py` exists as a separate file — so that complexity stays isolated.

**Where it appears:**
`analyzer.py` — this block:
```python
email_text = (
    f"From: {email['from']}\n"
    f"Subject: {email['subject']}\n"
    f"Date: {email['date']}\n\n"
    f"{email['body']}"
)
```

---

### 12. Separation of Concerns
**Level:** Intermediate

**What it is:** Each file or function should do exactly one job. Don't mix reading, processing, and saving in the same place.

**Why it matters here:** Because of this you can swap any single piece without breaking the rest. Want Gmail instead of JSON? Change only `reader.py`. Want to swap the AI model? Change only `analyzer.py` and `replier.py`. Nothing else needs to touch.

**Where it appears:** The entire folder structure. One file per job.

---

### Quick Reference Table

| Concept | Level | Key File |
|---|---|---|
| APIs | Beginner | `analyzer.py`, `replier.py` |
| Authentication | Beginner | `.env`, `main.py` |
| Environment Variables | Beginner | `.env`, `main.py` |
| JSON | Beginner | `analyzer.py`, `sample_emails.json` |
| Error Handling | Beginner | `analyzer.py`, `reader.py` |
| Data Parsing | Beginner | `analyzer.py`, `reader.py` |
| Email Parsing | Beginner | `analyzer.py` |
| Workflow / Pipeline | Beginner | `main.py` |
| Classification | Intermediate | `analyzer.py` |
| Summarization | Intermediate | `analyzer.py` |
| Prompt Engineering | Intermediate | `analyzer.py`, `replier.py` |
| Separation of Concerns | Intermediate | Entire project |

---

## Concept → Code Map

---

### APIs
**File:** `analyzer.py` line 40, `replier.py` line 38
**Function:** `analyze_email()`, `draft_reply()`
**What it's doing here:** Sending a POST request to OpenAI's servers with your email text and receiving a response back
**Pay attention to:**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)
```
This one line is the entire API call. Everything before it is preparation. Everything after it is handling the response.

---

### Authentication
**File:** `.env`, `main.py` lines 1-2
**Function:** `load_dotenv()`
**What it's doing here:** Reading `OPENAI_API_KEY` from `.env` into memory so the `openai` library can find it automatically without you passing it anywhere manually
**Pay attention to:** The order — `load_dotenv()` must run before anything else. If it runs after the OpenAI client is created, the key is never loaded.

---

### Environment Variables
**File:** `.env`
**Function:** `load_dotenv()` in `main.py`
**What it's doing here:** Hiding your secret key outside the code so it never accidentally gets shared
**Pay attention to:** `.env` is in your folder but should never be uploaded to GitHub. `.env.example` is the safe version you share.

---

### JSON
**File:** `analyzer.py`, `reader.py`, `sample_emails.json`
**Functions:** `load_emails()`, `analyze_email()`
**What it's doing here:** Two different jobs —
1. `reader.py` reads the JSON file and converts it to a Python list
2. `analyzer.py` takes GPT's text response and converts it back to a Python dictionary

**Pay attention to:**
```python
json.load(f)      # reader.py  — reads JSON from a FILE
json.loads(raw)   # analyzer.py — reads JSON from a STRING
```
`json.load` reads from a file. `json.loads` reads from a string. Easy to mix up.

---

### Prompt Engineering
**File:** `analyzer.py`, `replier.py`
**What:** `SYSTEM_PROMPT` constant at the top of each file
**What it's doing here:** Giving GPT its rules before it sees any email. The system prompt in `analyzer.py` tells GPT to act as a classifier and return only JSON. The one in `replier.py` tells it to act as a professional email writer.
**Pay attention to:**
```python
{"role": "system", "content": SYSTEM_PROMPT}  # rules for GPT
{"role": "user",   "content": email_text}      # the actual email
```
The system message shapes every response. Changing it is the fastest way to change the project's behaviour.

---

### Classification
**File:** `analyzer.py`
**Function:** `analyze_email()`
**What it's doing here:** Sending the email to GPT and getting back a label — `type` and `priority`. The `SYSTEM_PROMPT` defines the allowed categories and the rules for choosing between them.
**Pay attention to:** The fallback when classification fails:
```python
except json.JSONDecodeError:
    result = {"type": "unknown", "priority": "low"}
```
This is why you saw `unknown / low` — GPT returned something that wasn't clean JSON and the fallback kicked in.

---

### Summarization
**File:** `analyzer.py`
**Function:** `analyze_email()`
**What it's doing here:** As part of the same API call that classifies, GPT also writes a 1-2 sentence summary. Both happen in one request — GPT returns all three fields (`summary`, `type`, `priority`) together in one JSON response.
**Pay attention to:** Summarization and classification are not separate API calls. They share one call and one prompt. That is more efficient but means if the prompt breaks, both break together.

---

### Workflow / Pipeline
**File:** `main.py`
**Function:** `main()`
**What it's doing here:** Running every step in the right order. The `for` loop ensures each email is fully processed before moving to the next.
**Pay attention to:**
```python
for email in emails:
    analysis = analyze_email(email)        # step 1 output
    draft = draft_reply(email, analysis)   # step 2 uses step 1's output
    save_email(email, analysis, draft)     # step 3 uses both
```
`analysis` flows from step 1 into step 2. The output of one step is the input of the next. That is the pipeline.

---

### Error Handling
**File:** `analyzer.py`, `reader.py`
**Functions:** `analyze_email()`, `load_emails()`
**What it's doing here:** Two types —
1. `reader.py` raises a clear error if the file does not exist instead of letting Python give a confusing message
2. `analyzer.py` catches bad JSON from GPT and uses a safe fallback instead of crashing

**Pay attention to:**
```python
try:
    result = json.loads(raw)    # attempt the risky operation
except json.JSONDecodeError:    # catch the specific error type
    result = {...fallback...}   # use safe default instead
```
Always catch a specific error type, not a generic `except`. It makes debugging much easier.

---

### Email Parsing
**File:** `analyzer.py`
**Function:** `analyze_email()`
**What it's doing here:** Taking the email dictionary and formatting its fields into a clean readable block of text before sending to GPT
**Pay attention to:**
```python
email_text = (
    f"From: {email['from']}\n"
    f"Subject: {email['subject']}\n"
    f"Date: {email['date']}\n\n"
    f"{email['body']}"
)
```
This is simple for now because emails are clean JSON. With real Gmail emails this would be far more complex — stripping HTML, decoding attachments, handling character encoding.

---

### Database Persistence
**File:** `storage.py`
**Functions:** `init_db()`, `save_email()`, `get_all_emails()`
**What it's doing here:** Three jobs in one file —
1. `init_db()` — creates the table structure once
2. `save_email()` — writes one row per email
3. `get_all_emails()` — reads all rows back sorted by priority

**Pay attention to:**
```python
# Never creates duplicates — overwrites if same ID exists
INSERT OR REPLACE INTO processed_emails ...

# Sorts by urgency not alphabetically
CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
```

---

### Separation of Concerns
**Appears across:** The entire folder structure
**What it's doing here:** Every file has exactly one job. `reader.py` only reads. `analyzer.py` only analyzes. `replier.py` only drafts. `storage.py` only stores. `main.py` only orchestrates.
**Pay attention to:** `main.py` never touches the database directly. `storage.py` never calls OpenAI. `analyzer.py` never reads files. Each file is completely unaware of what the others do internally — they just pass data back and forth through function calls.

---

## Complete Data Flow — Start To Finish

---

### STAGE 0 — Program Starts

```
You type: py -3.12 main.py
```

Python opens `main.py` and runs it top to bottom. The very first thing that happens:

```python
from dotenv import load_dotenv
load_dotenv()
```

Python opens `.env`, reads `OPENAI_API_KEY=sk-...` and loads it silently into memory. From this point forward every OpenAI call will automatically find the key. No key = everything that follows fails.

---

### STAGE 1 — Database Prepared

```
main.py → calls init_db() → storage.py
```

`storage.py` checks if `emails.db` exists on disk.
- If it does not exist → creates it and builds the table structure
- If it already exists → skips creation, does nothing

```
┌────┬────────┬─────────┬──────┬──────┬─────────┬──────┬──────────┬────────────┐
│ id │ sender │ subject │ date │ body │ summary │ type │ priority │ draft_reply│
└────┴────────┴─────────┴──────┴──────┴─────────┴──────┴──────────┴────────────┘
```

**Data at this point:** Empty table waiting to receive rows.

---

### STAGE 2 — Emails Enter The System

```
main.py → calls load_emails_gmail() → reader.py → gmail_auth.py → Gmail API
```

`gmail_auth.py` loads `token.json` silently (no browser). `reader.py` calls the Gmail API asking for unread emails in the inbox. Each email's headers (From, Subject, Date) and body are extracted and decoded from base64.

Raw data coming back from Gmail:
```python
{
    "id": "18e4a2b9c...",
    "sender": "sarah.chen@company.com",
    "subject": "Q3 Budget Review - Action Required by Friday",
    "date": "Thu, 19 Mar 2026 09:15:00 +0000",
    "body": "Hi,\n\nI need you to review the attached Q3 budget..."
}
```

`reader.py` returns this list to `main.py`. All data lives in memory.

**Data at this point:** Unread email dictionaries in a Python list in memory.

---

### STAGE 3 — The Loop Begins

```
main.py → for email in emails
```

`main.py` picks up the first email. Stages 4 through 6 repeat for every single email before moving to the next.

---

### STAGE 4 — Email Is Parsed And Sent For Analysis

```
main.py → calls analyze_email(email) → analyzer.py
```

**Step 4a — Email fields are extracted and formatted**

The raw dictionary becomes formatted plain text:
```python
email_text = (
    f"From: sarah.chen@company.com\n"
    f"Subject: Q3 Budget Review - Action Required by Friday\n"
    f"Date: 2026-03-19T09:15:00\n\n"
    f"Hi,\n\nI need you to review the attached Q3 budget..."
)
```

**Step 4b — Message is built**

Two messages assembled — one instruction, one email:
```python
messages = [
    {"role": "system", "content": "You are an intelligent email assistant. Return JSON..."},
    {"role": "user",   "content": "From: sarah.chen@company.com\nSubject: Q3 Budget..."}
]
```

**Step 4c — Request leaves your computer**

```python
response = client.chat.completions.create(model="gpt-4o", messages=messages)
```

Your computer sends an HTTPS request to `api.openai.com`. The email text travels over the internet. GPT-4o reads both messages.

**Step 4d — Response arrives back**

```
response.choices[0].message.content =
'{"summary": "Sarah needs budget numbers by Friday.", "type": "work", "priority": "high"}'
```

This is a raw string. It looks like JSON but Python treats it as plain text at this point.

**Step 4e — Response is parsed**

```python
raw = response.choices[0].message.content.strip()
result = json.loads(raw)
# result is now a real Python dictionary
# {"summary": "Sarah needs budget numbers...", "type": "work", "priority": "high"}
```

If GPT returned something malformed, `json.loads()` raises an error. The `try/except` catches it and returns a safe fallback instead of crashing.

**Data at this point:** Original email dict + analysis dict both in memory.

---

### STAGE 5 — Draft Reply Is Generated

```
main.py → calls draft_reply(email, analysis) → replier.py
```

**Step 5a — Context is assembled using the analysis from Stage 4**

```python
context = (
    f"Email type: work\n"
    f"Priority: high\n"
    f"Summary: Sarah needs budget numbers by Friday...\n\n"
    f"---\n"
    f"From: sarah.chen@company.com\n"
    f"Subject: Q3 Budget Review...\n\n"
    f"Hi,\n\nI need you to review..."
)
```

The analysis from Stage 4 feeds directly into Stage 5. GPT knows the context before reading the email body.

**Step 5b — Second request leaves your computer**

Same process as Stage 4 — built with a different system prompt, sent to OpenAI, GPT generates a reply draft.

**Step 5c — Response arrives as plain text**

```
"Hi Sarah,\n\nThank you for the heads up. I'll get you the headcount costs..."
```

No JSON parsing needed this time — it comes back as a plain string.

**Data at this point:** Email + analysis + draft reply all in memory.

---

### STAGE 6 — Everything Is Saved

```
main.py → calls save_email(email, analysis, draft) → storage.py
```

All three pieces written as one row into `emails.db`:

```
┌─────┬──────────────────────┬──────────────────────────┬───────┬──────────┬─────────────┐
│ id  │ sender               │ subject                  │ type  │ priority │ draft_reply │
├─────┼──────────────────────┼──────────────────────────┼───────┼──────────┼─────────────┤
│ 001 │ sarah.chen@company.. │ Q3 Budget Review...      │ work  │ high     │ Hi Sarah... │
└─────┴──────────────────────┴──────────────────────────┴───────┴──────────┴─────────────┘
```

`INSERT OR REPLACE` means if this email ID already exists it overwrites — no duplicates. Data is now permanently on disk.

**Stages 4 → 5 → 6 repeat for all 6 emails.**

---

### STAGE 7 — All Results Are Fetched

```
main.py → calls get_all_emails() → storage.py
```

After all 6 emails are processed, `storage.py` reads every row from `emails.db` and sorts by priority:

```sql
CASE priority
    WHEN 'high'   THEN 1
    WHEN 'medium' THEN 2
    ELSE               3
END
```

Returns a sorted list of 6 dictionaries to `main.py`.

**Data at this point:** Sorted list of all 6 processed emails read back from the database.

---

### STAGE 8 — Report Is Printed To The User

```
main.py → calls print_report(processed)
```

`print_report()` loops through the sorted list and formats each email:

```
🔴 [HIGH] WORK
   From:    sarah.chen@company.com
   Subject: Q3 Budget Review - Action Required by Friday
   Summary: Sarah needs budget numbers by Friday for a Monday board presentation.
   Draft reply:

     Hi Sarah,
     Thank you for the heads up. I'll get you the headcount costs...
```

This is the only thing the user ever sees. Everything before this was invisible background processing. Program ends. Memory cleared. `emails.db` keeps the results permanently.

---

### Full Pipeline In One View

```
.env
 │
 └── OPENAI_API_KEY loaded into memory
          │
          ▼
   emails.db created (if not exists)
          │
          ▼
   sample_emails.json opened
   json.load() → list of 6 email dicts
          │
          ▼
   ┌─── FOR EACH EMAIL ────────────────────────────────┐
   │                                                    │
   │  email dict                                        │
   │    │                                               │
   │    ▼                                               │
   │  fields extracted → formatted as plain text        │
   │    │                                               │
   │    ▼                                               │
   │  system prompt + email text → sent to OpenAI       │
   │                    │                               │
   │                    ▼                               │
   │            GPT reads, returns JSON string          │
   │                    │                               │
   │                    ▼                               │
   │            json.loads() → analysis dict            │
   │            {summary, type, priority}               │
   │                    │                               │
   │    ▼               ▼                               │
   │  email + analysis → sent to OpenAI                 │
   │                    │                               │
   │                    ▼                               │
   │            GPT reads, returns plain text draft     │
   │                    │                               │
   │    ▼               ▼                               │
   │  email + analysis + draft → saved to emails.db     │
   │                                                    │
   └─── NEXT EMAIL ─────────────────────────────────────┘
          │
          ▼
   all rows fetched from emails.db
   sorted: high → medium → low
          │
          ▼
   coloured report printed to terminal
          │
          ▼
        DONE
```

---

## Module and Component Breakdown

---

### The 6 Modules

```
┌─────────────────────────────────────────────────────┐
│                   EMAIL ASSISTANT                   │
├──────────────┬──────────────┬───────────────────────┤
│    INPUT     │     AI       │       OUTPUT          │
│   HANDLING   │  PROCESSING  │                       │
├──────────────┼──────────────┼───────────────────────┤
│ Config       │ Summarizer   │ Storage               │
│ Loader       │ Classifier   │ UI / Reporter         │
│ Email Parser │ Reply        │                       │
│              │ Generator    │                       │
└──────────────┴──────────────┴───────────────────────┘
```

---

### Module 1 — Config Loader

**What it is:** The setup module. Runs before everything else.

**File:** `main.py` lines 1-2

**Responsibility:**
- Read the `.env` file
- Load the API key into memory
- Make it available to all other modules without them having to ask for it

```python
from dotenv import load_dotenv
load_dotenv()
```

**Inputs it receives:** Nothing — finds `.env` automatically in the current folder

**Outputs it produces:** Nothing visible — silently sets `OPENAI_API_KEY` as a system environment variable in memory

**What it owns:** The API key

**What breaks without it:** Every module that touches OpenAI fails immediately

**Talks to:** Indirectly feeds into Summarizer, Classifier, and Reply Generator — they all use the key it loaded

---

### Module 2 — Email Parser (Input Handler)

**What it is:** The data entry point. The only module that touches the raw email source.

**File:** `reader.py`

**Responsibility:**
- Open the email source file
- Read raw JSON
- Convert it into Python dictionaries
- Hand a clean structured list to the rest of the system

```python
def load_emails(path):
    with open(file, encoding="utf-8") as f:
        emails = json.load(f)
    return emails
```

**Inputs it receives:** A file path pointing to `sample_emails.json`

**Outputs it produces:** A Python list of email dictionaries:
```python
[
    {"id": "001", "from": "...", "subject": "...", "body": "..."},
    {"id": "002", ...},
]
```

**What it owns:** The connection to the email source. Every other module just receives clean dictionaries — they have no idea whether emails came from a JSON file, Gmail, or Outlook.

**What breaks without it:** Nothing enters the system. The pipeline has no data to process.

**Talks to:** Sends the email list up to the Orchestrator (`main.py`)

---

### Module 3 — Summarizer + Classifier

**What it is:** The analysis brain. Where the first AI thinking happens.

**File:** `analyzer.py`

**Responsibility:**
- Take one raw email
- Format it into clean text for GPT
- Send it to OpenAI with instructions to return JSON
- Parse the response
- Return a structured analysis

**This module does two jobs in one API call:**

**Job A — Summarization:** Condenses the email body into 1-2 sentences.

**Job B — Classification:** Assigns two labels:
- `type` — what kind of email? (`work`, `personal`, `newsletter`, etc.)
- `priority` — how urgent? (`high`, `medium`, `low`)

Why combined: Both jobs require reading the full email and both return structured data. One API call instead of two saves time and cost.

```python
def analyze_email(email: dict) -> dict:
```

**Inputs it receives:** One email dictionary from the Orchestrator

**Outputs it produces:**
```python
{
    "summary": "Sarah needs Q3 budget numbers by Friday for a board presentation.",
    "type": "work",
    "priority": "high"
}
```

**What it owns:** The `SYSTEM_PROMPT` that defines classification rules. The logic for how emails get labelled lives entirely here.

**What breaks without it:** No summaries. No type labels. No priority sorting. The report is useless.

**Talks to:** Receives email from Orchestrator → sends HTTP request to OpenAI → returns analysis dict to Orchestrator

---

### Module 4 — Reply Generator

**What it is:** The writing brain. The second AI module.

**File:** `replier.py`

**Responsibility:**
- Take the original email AND its analysis
- Send both to OpenAI with instructions to write a reply
- Return the draft text

**Why it needs the analysis too:** The analysis tells GPT the tone and urgency before it starts writing. A high priority work email gets a formal reply. A personal email from mum gets a warm casual reply. Without the analysis GPT writes generic replies.

```python
def draft_reply(email: dict, analysis: dict) -> str:
```

**Inputs it receives:**
- One email dictionary
- One analysis dictionary (output of Module 3)

**Outputs it produces:** A plain string — the draft reply:
```python
"Hi Sarah,\n\nThank you for the heads up. I'll get you the headcount costs..."
```

**What it owns:** The reply-writing `SYSTEM_PROMPT`. Rules for tone, length, and style of draft replies live here.

**What breaks without it:** No draft replies generated.

**Talks to:** Receives email + analysis from Orchestrator → sends HTTP request to OpenAI → returns draft string to Orchestrator

---

### Module 5 — Storage

**What it is:** The memory of the system. Everything that needs to survive after the program stops goes here.

**File:** `storage.py`

**Responsibility:**
- Create and maintain the database structure
- Write processed emails to disk
- Read them back when needed
- Sort them by priority for the report

**Three functions, three jobs:**

`init_db()` — Setup: Creates `emails.db` and defines table columns. Safe to run multiple times — never overwrites existing data.

`save_email()` — Write: Takes email + analysis + draft and writes one row. Uses `INSERT OR REPLACE` so running the program twice never duplicates rows.

`get_all_emails()` — Read: Fetches all rows sorted by priority (high first). Returns them as a list of dictionaries ready for the UI module.

**Inputs it receives:**
- `init_db()` — nothing
- `save_email()` — email dict + analysis dict + draft string
- `get_all_emails()` — nothing

**Outputs it produces:**
- `init_db()` — `emails.db` file on disk
- `save_email()` — nothing returned, writes to disk
- `get_all_emails()` — sorted list of all processed email dicts

**What it owns:** The database schema. The sort logic. The only module that ever touches `emails.db`.

**What breaks without it:** Results disappear when the program ends. Nothing is persisted. Report module has nothing to display.

**Talks to:** Receives data from Orchestrator → reads and writes `emails.db` → returns sorted results to Orchestrator

---

### Module 6 — UI / Reporter

**What it is:** The display layer. The only module the user ever actually sees.

**File:** `main.py` — `print_report()` function

**Responsibility:**
- Take the sorted list of processed emails
- Format each one clearly
- Print a colour-coded report to the terminal

```python
def print_report(emails: list[dict]):
```

**Inputs it receives:** Sorted list of processed email dictionaries from Storage

**Outputs it produces:** Printed terminal output — nothing returned, nothing saved

**What it owns:** The display format. How results look to the user lives entirely here.

**What breaks without it:** Nothing crashes. Results still saved to `emails.db`. You just see nothing in the terminal.

**Talks to:** Only receives data from the Orchestrator. Does not talk to any other module.

---

### The Orchestrator

**What it is:** The conductor that connects all modules. Not really a module itself — it does no real work, it just coordinates.

**File:** `main.py` — `main()` function

```python
def main():
    load_dotenv()            # Config Loader
    init_db()                # Storage — setup
    emails = load_emails()   # Email Parser

    for email in emails:
        analysis = analyze_email(email)        # Summarizer + Classifier
        draft = draft_reply(email, analysis)   # Reply Generator
        save_email(email, analysis, draft)     # Storage — write

    processed = get_all_emails()   # Storage — read
    print_report(processed)        # UI / Reporter
```

---

### How The Modules Talk To Each Other

Modules do not call each other directly. They all talk through the Orchestrator. The Orchestrator passes data between them like a relay race.

```
Config Loader
      │
      │  (API key silently available to all AI modules)
      │
      ▼
Email Parser ──→ [email list] ──→ Orchestrator
                                       │
                              ┌────────┴────────┐
                              ▼                 │
                   Summarizer+Classifier        │
                   [receives: email]            │
                   [returns: analysis]          │
                              │                 │
                              ▼                 │
                       Reply Generator          │
                       [receives: email         │
                                + analysis]     │
                       [returns: draft]         │
                              │                 │
                              ▼                 │
                           Storage              │
                    [receives: email            │
                             + analysis         │
                             + draft]           │
                    [writes to disk]            │
                    [returns: sorted list] ──→  ▼
                                          UI / Reporter
                                          [prints report]
```

**The key rule:** No module imports from another module. Only `main.py` imports from all of them.

- `analyzer.py` has no idea `storage.py` exists
- `replier.py` has no idea `reader.py` exists
- `storage.py` has no idea `analyzer.py` exists

They are completely independent. They only know about the data they receive and the data they return.

---

### Module Responsibility Summary

| Module | File | Receives | Returns | Touches Outside World |
|---|---|---|---|---|
| Config Loader | `main.py` | nothing | nothing (sets memory) | `.env` file |
| Email Parser | `reader.py` | file path | list of email dicts | `sample_emails.json` |
| Summarizer + Classifier | `analyzer.py` | one email dict | analysis dict | OpenAI API |
| Reply Generator | `replier.py` | email + analysis | draft string | OpenAI API |
| Storage | `storage.py` | email + analysis + draft | sorted list | `emails.db` |
| UI / Reporter | `main.py` | sorted list | nothing | terminal |
| Orchestrator | `main.py` | nothing | nothing | coordinates all |

**Only two modules touch the outside world with network calls:** Summarizer+Classifier and Reply Generator. Everything else stays on your computer.

---

## What To Upgrade Next

| Upgrade | What to change |
|---|---|
| ~~Use a real inbox~~ ✅ Done | Gmail API + OAuth added in `gmail_auth.py` and `reader.py` |
| Deduplicate processed emails | Add `is_already_processed()` to `storage.py`, check in `main.py` loop |
| Approve before sending | Add review prompt in `main.py` after `draft_reply()` |
| Add a web interface | Add Flask or Gradio on top of `main.py` |
| Fix classification | Update the `SYSTEM_PROMPT` in `analyzer.py` |
| Schedule automatic runs | Add polling loop to `main.py`, run with `py -3.12 main.py loop` |
