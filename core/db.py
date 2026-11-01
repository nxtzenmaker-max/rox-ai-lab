import os
import json
import sqlite3
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "").strip()
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "").strip()

def is_turso_configured() -> bool:
    """Returns True if Turso cloud URL and token are configured."""
    return bool(TURSO_DATABASE_URL and TURSO_DATABASE_URL.startswith(("libsql://", "https://")))

def _get_turso_http_url() -> str:
    """Converts libsql://<db>.turso.io to https://<db>.turso.io/v2/pipeline."""
    url = TURSO_DATABASE_URL
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    url = url.rstrip("/")
    if not url.endswith("/v2/pipeline"):
        url = f"{url}/v2/pipeline"
    return url

def _get_sqlite_conn():
    """Returns a local SQLite connection (uses /tmp on Vercel or local directory)."""
    db_file = "/tmp/rox_local.db" if os.path.exists("/tmp") else "local.db"
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(sql: str, params: list = None):
    """
    Executes a query either on Turso Cloud via HTTP pipeline or on local SQLite.
    Zero-config and 100% resilient on Vercel Serverless.
    """
    params = params or []
    if is_turso_configured():
        try:
            http_url = _get_turso_http_url()
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            # Turso Pipeline format
            body = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": sql,
                            "args": [{"type": "text", "value": str(p)} for p in params]
                        }
                    },
                    {"type": "close"}
                ]
            }
            res = requests.post(http_url, headers=headers, json=body, timeout=5)
            if res.status_code == 200:
                return {"status": "success", "engine": "turso_cloud"}
        except Exception as e:
            print(f"[Turso DB Error] {e}. Falling back to SQLite.")

    # SQLite fallback
    try:
        conn = _get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        rows = cur.fetchall()
        conn.close()
        return {"status": "success", "engine": "sqlite_local", "rows": rows}
    except Exception as e:
        print(f"[SQLite Error] {e}")
        return {"status": "error", "error": str(e)}

def init_db():
    """Initializes tables for conversation history and photo logging."""
    execute_query("""
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    execute_query("""
    CREATE TABLE IF NOT EXISTS captured_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facing TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

def save_message(role: str, message: str):
    """Saves a conversation turn to Turso / SQLite database."""
    try:
        execute_query(
            "INSERT INTO conversation_history (role, message) VALUES (?, ?);",
            [role, message]
        )
    except Exception as e:
        print(f"[DB Save Error] {e}")

def log_photo(facing: str):
    """Logs photo capture action (front or back)."""
    try:
        execute_query(
            "INSERT INTO captured_photos (facing) VALUES (?);",
            [facing]
        )
    except Exception as e:
        print(f"[DB Photo Log Error] {e}")

# Initialize on module load
try:
    init_db()
except Exception as e:
    pass
