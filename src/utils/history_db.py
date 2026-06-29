"""
history_db.py — SQLite persistence layer for ESG report history.

Stores every generated report with:
    company_name, date_generated, e_score, s_score, g_score, report_text

All functions are thread-safe: each call opens, uses, and closes its own
connection so concurrent Streamlit sessions don't conflict.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Store the DB next to the project root (same folder as app.py)
DB_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "esg_history.db"
)
DB_PATH = os.path.abspath(DB_PATH)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the report_history table if it does not already exist."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS report_history (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name    TEXT    NOT NULL,
                date_generated  TEXT    NOT NULL,
                e_score         TEXT    NOT NULL,
                s_score         TEXT    NOT NULL,
                g_score         TEXT    NOT NULL,
                report_text     TEXT
            )
            """
        )
        conn.commit()


def save_report(
    company_name: str,
    e_score: str,
    s_score: str,
    g_score: str,
    report_text: str,
) -> int:
    """Insert a new report row and return its auto-assigned id."""
    date_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO report_history
                (company_name, date_generated, e_score, s_score, g_score, report_text)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (company_name, date_generated, e_score, s_score, g_score, report_text),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_history() -> List[Dict[str, Any]]:
    """Return all rows newest-first (report_text excluded for performance)."""
    with _connect() as conn:
        cursor = conn.execute(
            """
            SELECT id, company_name, date_generated, e_score, s_score, g_score
            FROM report_history
            ORDER BY date_generated DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]


def get_report_by_id(report_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a single complete row (including report_text) by primary key."""
    with _connect() as conn:
        cursor = conn.execute(
            "SELECT * FROM report_history WHERE id = ?", (report_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_company_history(company_name: str) -> List[Dict[str, Any]]:
    """
    Return all rows for a company sorted oldest-first.
    Used to build the E/S/G trend chart.
    Case-insensitive match on company_name.
    """
    with _connect() as conn:
        cursor = conn.execute(
            """
            SELECT id, company_name, date_generated, e_score, s_score, g_score
            FROM report_history
            WHERE LOWER(company_name) = LOWER(?)
            ORDER BY date_generated ASC
            """,
            (company_name,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_distinct_companies() -> List[str]:
    """Return all unique company names that have been analyzed."""
    with _connect() as conn:
        cursor = conn.execute(
            "SELECT DISTINCT company_name FROM report_history ORDER BY company_name"
        )
        return [row[0] for row in cursor.fetchall()]


def delete_report(report_id: int) -> None:
    """Remove a single report by id."""
    with _connect() as conn:
        conn.execute("DELETE FROM report_history WHERE id = ?", (report_id,))
        conn.commit()
