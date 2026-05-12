import sqlite3
import datetime
import json
from pathlib import Path

DB_PATH = Path("src/persistence/jarvis_logs.db")

def init_db():
    """Initialize the logging database."""
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for all interactions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_id TEXT,
            query TEXT,
            response TEXT,
            intent TEXT,
            tool_output TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_interaction(user_id, query, response, intent=None, tool_output=None):
    """Log a complete interaction to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.datetime.now().isoformat()
    intent_json = json.dumps(intent) if intent else None
    tool_json = json.dumps(tool_output) if tool_output else None
    
    cursor.execute('''
        INSERT INTO interactions (timestamp, user_id, query, response, intent, tool_output)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, user_id, query, response, intent_json, tool_json))
    
    conn.commit()
    conn.close()

def get_recent_logs(limit=10):
    """Retrieve recent logs for context or dashboard."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interactions ORDER BY id DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
