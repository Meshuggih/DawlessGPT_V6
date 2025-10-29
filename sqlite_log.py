"""SQLite logging for DawlessGPTv6.

This module records session information, auto‑completions, decisions and
artefact metadata to a SQLite database.  Logging helps trace the evolution
of a session and provides auditability.  The default database file is
`/mnt/data/dawlessgptv6.db`.  Basic insertion is implemented; more
comprehensive tables and indices can be added later.

TODOs:
    [X] Implement a simple table creation and insertion logic.
    [ ] Add indices and foreign keys for performance and relational integrity.
    [ ] Expose query functions for summarising sessions and completions.

"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Any


DB_PATH = Path("/mnt/data/dawlessgptv6.db")


def _ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS sessions ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, seed INTEGER, plan TEXT, completions TEXT, wav_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ")"
    )


def log_session(seed: int, plan_json: str, completions_json: str, wav_path: str) -> None:
    """Insert a session record into the database.

    Parameters
    ----------
    seed : int
        Random seed used for this session.
    plan_json : str
        JSON string of the completed plan.
    completions_json : str
        JSON string describing which fields were auto‑completed.
    wav_path : str
        Path to the rendered WAV file.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        _ensure_tables(conn)
        conn.execute(
            "INSERT INTO sessions (seed, plan, completions, wav_path) VALUES (?, ?, ?, ?)",
            (seed, plan_json, completions_json, wav_path)
        )
        conn.commit()
    finally:
        conn.close()