"""SQLite persistence layer for decoyops.

Tables:
    visitors        - who hit a bait path, and when
    tokens          - canary tokens minted, and which bait file they were embedded in
    harvest_events   - a visitor was served a bait file containing a token
    usage_events     - a canary token fired (someone used the leaked credential)
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    user_agent TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT UNIQUE NOT NULL,
    auth_token TEXT NOT NULL,
    token_type TEXT NOT NULL,
    bait_path TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS harvest_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_id INTEGER NOT NULL REFERENCES visitors(id),
    token_id TEXT NOT NULL REFERENCES tokens(token_id),
    bait_path TEXT NOT NULL,
    served_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_id TEXT NOT NULL REFERENCES tokens(token_id),
    source_ip TEXT,
    raw_payload TEXT,
    fired_at TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def upsert_visitor(ip_address: str, user_agent: str) -> int:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM visitors WHERE ip_address = ? AND user_agent = ?",
            (ip_address, user_agent),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE visitors SET last_seen = ? WHERE id = ?", (now(), row["id"])
            )
            return row["id"]
        cur = conn.execute(
            "INSERT INTO visitors (ip_address, user_agent, first_seen, last_seen) VALUES (?, ?, ?, ?)",
            (ip_address, user_agent, now(), now()),
        )
        return cur.lastrowid


def record_token(token_id: str, auth_token: str, token_type: str, bait_path: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO tokens (token_id, auth_token, token_type, bait_path, created_at) VALUES (?, ?, ?, ?, ?)",
            (token_id, auth_token, token_type, bait_path, now()),
        )


def record_harvest_event(visitor_id: int, token_id: str, bait_path: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO harvest_events (visitor_id, token_id, bait_path, served_at) VALUES (?, ?, ?, ?)",
            (visitor_id, token_id, bait_path, now()),
        )


def record_usage_event(token_id: str, source_ip: str, raw_payload: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO usage_events (token_id, source_ip, raw_payload, fired_at) VALUES (?, ?, ?, ?)",
            (token_id, source_ip, raw_payload, now()),
        )
