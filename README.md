# Email Assistant

An AI-powered email assistant that reads your real Gmail inbox, summarizes and prioritizes each email, and drafts a reply — all from the terminal.

Built with Python, OpenAI GPT-4o, Gmail API, and SQLite.

---

## What it does

- Connects to your real Gmail inbox via the Gmail API (OAuth 2.0)
- Fetches only unread emails — never re-processes what it has already seen
- Uses GPT-4o to summarize each email, categorize it, and assign a priority (high / medium / low)
- Drafts a professional reply suggestion for every email
- Saves everything to a local SQLite database
- Prints a clean, colour-coded terminal report sorted by priority

---

## Setup

1. Clone the repo
2. Install dependencies
   ```
   py -3.12 -m pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key
   ```
   OPENAI_API_KEY=your-key-here
   ```
4. Set up Gmail API credentials
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a project, enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop app) and download as `credentials.json`
   - Place `credentials.json` in the project root
5. Run — browser will open once for Gmail login, then closes
   ```
   py -3.12 main.py
   ```

---

## Project structure

```
email-assistant/
├── main.py                  # Entry point
├── assistant/
│   ├── gmail_auth.py        # Gmail OAuth login and token management
│   ├── reader.py            # Loads emails from Gmail (or JSON for testing)
│   ├── analyzer.py          # Summarizes and classifies emails via Claude
│   ├── replier.py           # Drafts reply suggestions via Claude
│   └── storage.py           # Saves and retrieves emails from SQLite
├── data/
│   └── sample_emails.json   # Sample inbox (mock/testing mode)
├── credentials.json         # Gmail OAuth credentials (never commit — add to .gitignore)
├── token.json               # Auto-created after first login (never commit — add to .gitignore)
├── .env.example             # API key template
└── requirements.txt
```

---

## Tech stack

- Python 3.12
- OpenAI GPT-4o API
- Gmail API (google-auth, google-auth-oauthlib, google-api-python-client)
- SQLite (built into Python)
- python-dotenv

---

Built by Cerin
