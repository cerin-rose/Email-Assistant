"""
storage.py — Saves processed emails to a local SQLite database.

SQLite is built into Python — no installation needed.
The database file (emails.db) is created automatically on first run.
"""

import sqlite3
from pathlib import Path

DB_PATH = "emails.db"


def init_db():
    """Create the database and table if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processed_emails (
            id          TEXT PRIMARY KEY,
            sender      TEXT,
            subject     TEXT,
            date        TEXT,
            body        TEXT,
            summary     TEXT,
            type        TEXT,
            priority    TEXT,
            draft_reply TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"[storage] Database ready at '{DB_PATH}'")


def save_email(email: dict, analysis: dict, draft: str):
    """Insert or replace one processed email into the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT OR REPLACE INTO processed_emails
            (id, sender, subject, date, body, summary, type, priority, draft_reply)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            email["id"],
            email["sender"],
            email["subject"],
            email["date"],
            email["body"],
            analysis["summary"],
            analysis["type"],
            analysis["priority"],
            draft,
        ),
    )
    conn.commit()
    conn.close()


def is_already_processed(email_id: str) -> bool:
    """Check if an email ID has already been processed."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM processed_emails WHERE id = ?", (email_id,))
    result = cur.fetchone()
    conn.close()
    return result is not None


def get_all_emails() -> list[dict]:
    """Fetch all processed emails, ordered by priority then date."""
    priority_order = "CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        f"SELECT * FROM processed_emails ORDER BY {priority_order}, date DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
