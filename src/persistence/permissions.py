import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parents[2] / "permissions.db"

def _init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS granted (
            uid TEXT,
            action TEXT,
            target TEXT,
            granted_at TEXT
        )
    """)
    con.commit()
    con.close()

_init_db()

def is_granted(uid: str, action: str, target: str) -> bool:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "SELECT 1 FROM granted WHERE uid=? AND action=? AND target=?",
        (uid, action, target),
    )
    result = cur.fetchone() is not None
    con.close()
    return result

def grant(uid: str, action: str, target: str, timestamp: str = None):
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat()
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO granted (uid, action, target, granted_at) VALUES (?,?,?,?)",
        (uid, action, target, timestamp),
    )
    con.commit()
    con.close()
