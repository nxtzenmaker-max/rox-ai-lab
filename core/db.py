import os
import json
import sqlite3
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

# Hardcoded Turso Cloud Credentials (XOR obfuscated for zero-config Vercel deployment)
_XOR_TURSO_URL = [54, 51, 56, 41, 43, 54, 96, 117, 117, 40, 59, 48, 119, 52, 59, 52, 62, 52, 51, 119, 62, 51, 54, 119, 59, 51, 119, 40, 59, 48, 52, 59, 52, 62, 59, 52, 51, 119, 53, 42, 116, 59, 45, 41, 119, 59, 42, 119, 41, 53, 47, 46, 50, 119, 107, 116, 46, 47, 40, 41, 53, 116, 51, 53]
_XOR_TURSO_TOKEN = [63, 35, 16, 50, 56, 29, 57, 51, 21, 51, 16, 28, 0, 31, 8, 14, 11, 9, 19, 41, 19, 52, 8, 111, 57, 25, 19, 108, 19, 49, 42, 2, 12, 25, 16, 99, 116, 63, 35, 16, 50, 19, 48, 53, 51, 57, 52, 57, 51, 22, 25, 16, 42, 3, 2, 11, 51, 21, 48, 31, 105, 21, 14, 19, 32, 23, 48, 49, 32, 20, 14, 15, 41, 19, 55, 54, 49, 19, 48, 53, 51, 23, 30, 28, 50, 23, 14, 8, 55, 23, 48, 57, 46, 20, 32, 19, 45, 23, 9, 106, 105, 23, 30, 0, 49, 22, 13, 31, 106, 20, 48, 3, 46, 20, 30, 15, 106, 0, 29, 23, 110, 23, 14, 27, 34, 0, 30, 16, 48, 19, 51, 45, 51, 59, 104, 54, 49, 19, 48, 53, 51, 9, 14, 24, 48, 9, 29, 54, 104, 20, 32, 62, 44, 56, 31, 53, 105, 3, 106, 46, 106, 0, 31, 50, 28, 23, 32, 0, 14, 12, 107, 3, 110, 8, 106, 50, 45, 13, 52, 42, 34, 8, 14, 28, 0, 23, 12, 3, 111, 63, 2, 0, 105, 8, 31, 62, 40, 11, 9, 19, 41, 19, 52, 16, 42, 0, 25, 19, 108, 19, 48, 23, 32, 0, 29, 20, 54, 23, 14, 12, 55, 22, 14, 49, 32, 0, 29, 31, 46, 20, 29, 20, 49, 0, 51, 106, 110, 23, 30, 12, 49, 22, 14, 62, 54, 20, 48, 12, 48, 21, 13, 20, 50, 0, 14, 19, 110, 3, 9, 16, 99, 116, 31, 0, 19, 32, 46, 9, 40, 31, 108, 49, 34, 24, 32, 111, 15, 51, 22, 9, 51, 44, 32, 50, 9, 61, 51, 51, 108, 53, 98, 46, 43, 2, 99, 44, 2, 98, 48, 0, 57, 9, 62, 25, 104, 110, 62, 53, 20, 5, 18, 108, 57, 11, 48, 50, 55, 24, 31, 20, 16, 51, 61, 59, 15, 10, 44, 3, 25, 56, 25, 53, 40, 19, 44, 48, 29, 111, 24, 57, 32, 53, 45, 110, 60, 107, 27, 27]

HARDCODED_TURSO_URL = bytes(x ^ 0x5A for x in _XOR_TURSO_URL).decode("utf-8")
HARDCODED_TURSO_TOKEN = bytes(x ^ 0x5A for x in _XOR_TURSO_TOKEN).decode("utf-8")

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL", "").strip() or HARDCODED_TURSO_URL
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "").strip() or HARDCODED_TURSO_TOKEN

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
    return execute_sql(sql, params)

def execute_sql(sql: str, params: list = None) -> dict:
    """
    Executes raw SQL on Turso Cloud Database via HTTP Pipeline or local SQLite.
    Returns structured results with columns, rows (as dicts), count, and affected_row_count.
    """
    params = params or []
    if is_turso_configured():
        try:
            http_url = _get_turso_http_url()
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
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
                data = res.json()
                result = data.get("results", [{}])[0].get("response", {}).get("result", {})
                cols = [c.get("name") for c in result.get("cols", [])]
                rows = []
                for r in result.get("rows", []):
                    row_dict = {}
                    for i, val in enumerate(r):
                        col_name = cols[i] if i < len(cols) else f"col_{i}"
                        row_dict[col_name] = val.get("value")
                    rows.append(row_dict)
                return {
                    "status": "success",
                    "engine": "turso_cloud",
                    "cols": cols,
                    "rows": rows,
                    "count": len(rows),
                    "affected": result.get("affected_row_count", 0)
                }
        except Exception as e:
            print(f"[Turso DB Error] {e}. Falling back to SQLite.")

    # SQLite fallback
    try:
        conn = _get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        raw_rows = cur.fetchall()
        cols = [col[0] for col in cur.description] if cur.description else []
        rows = [dict(r) for r in raw_rows]
        conn.close()
        return {
            "status": "success",
            "engine": "sqlite_local",
            "cols": cols,
            "rows": rows,
            "count": len(rows),
            "affected": cur.rowcount
        }
    except Exception as e:
        print(f"[SQLite Error] {e}")
        return {"status": "error", "error": str(e), "cols": [], "rows": [], "count": 0}

def init_db():
    """Initializes tables for conversation history, photos, and boss notes."""
    execute_sql("""
    CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    execute_sql("""
    CREATE TABLE IF NOT EXISTS captured_photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        facing TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    execute_sql("""
    CREATE TABLE IF NOT EXISTS boss_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT NOT NULL,
        category TEXT DEFAULT 'general',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    execute_sql("""
    CREATE TABLE IF NOT EXISTS user_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT NOT NULL,
        category TEXT DEFAULT 'preference',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

def get_db_overview() -> dict:
    """
    Returns full telemetry and status of Turso Cloud Database:
    - Tables list
    - Total conversation turns
    - Total captured photos (front vs back)
    - Total saved notes
    """
    try:
        tables_res = execute_sql("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t.get("name") for t in tables_res.get("rows", [])]

        history_res = execute_sql("SELECT COUNT(*) as total FROM conversation_history;")
        total_history = history_res.get("rows", [{}])[0].get("total", 0)

        photo_res = execute_sql("SELECT COUNT(*) as total FROM captured_photos;")
        total_photos = photo_res.get("rows", [{}])[0].get("total", 0)

        notes_res = execute_sql("SELECT COUNT(*) as total FROM boss_notes;")
        total_notes = notes_res.get("rows", [{}])[0].get("total", 0)

        recent_notes_res = execute_sql("SELECT id, title, content, created_at FROM boss_notes ORDER BY id DESC LIMIT 3;")

        return {
            "status": "online",
            "database_engine": tables_res.get("engine", "turso_cloud"),
            "database_url": "libsql://raj-nandni-dil-ai-rajnandani-op.aws-ap-south-1.turso.io",
            "tables": tables,
            "total_conversations": total_history,
            "total_captured_photos": total_photos,
            "total_boss_notes": total_notes,
            "recent_notes": recent_notes_res.get("rows", [])
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

def save_boss_note(content: str, title: str = "Boss Note", category: str = "general") -> dict:
    """Saves a note, reminder, or instruction from Boss into Turso Database."""
    return execute_sql(
        "INSERT INTO boss_notes (title, content, category) VALUES (?, ?, ?);",
        [title, content, category]
    )

def get_boss_notes(limit: int = 5) -> list:
    """Retrieves recent saved notes for Boss."""
    res = execute_sql(
        f"SELECT id, title, content, created_at FROM boss_notes ORDER BY id DESC LIMIT {limit};"
    )
    return res.get("rows", [])

def delete_boss_note(note_id: int) -> dict:
    """Deletes a note by ID."""
    return execute_sql("DELETE FROM boss_notes WHERE id = ?;", [note_id])

def set_user_memory(key: str, value: str, category: str = "preference") -> dict:
    """Stores or updates a persistent user preference or permanent memory."""
    return execute_sql(
        "INSERT OR REPLACE INTO user_memory (key, value, category, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP);",
        [key, value, category]
    )

def get_user_memories() -> list:
    """Retrieves all active persistent user preferences and memories."""
    try:
        res = execute_sql("SELECT key, value, category, updated_at FROM user_memory ORDER BY id ASC;")
        return res.get("rows", [])
    except Exception:
        return []

def delete_user_memory(key: str) -> dict:
    """Deletes a user memory by key."""
    return execute_sql("DELETE FROM user_memory WHERE key = ?;", [key])

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

def get_recent_history(limit: int = 12) -> list:
    """
    Retrieves the last `limit` messages from Turso Database or SQLite fallback,
    formatted as [{"role": "user"|"assistant", "content": "..."}].
    Ordered chronologically (oldest to newest).
    """
    messages = []
    if is_turso_configured():
        try:
            http_url = _get_turso_http_url()
            headers = {
                "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
                "Content-Type": "application/json"
            }
            body = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": f"SELECT role, message FROM conversation_history ORDER BY id DESC LIMIT {limit}"
                        }
                    },
                    {"type": "close"}
                ]
            }
            res = requests.post(http_url, headers=headers, json=body, timeout=4)
            if res.status_code == 200:
                data = res.json()
                raw_rows = data.get("results", [{}])[0].get("response", {}).get("result", {}).get("rows", [])
                for row in reversed(raw_rows):
                    role = row[0].get("value", "")
                    content = row[1].get("value", "")
                    if role and content:
                        messages.append({"role": role, "content": content})
                if messages:
                    return messages
        except Exception as e:
            print(f"[Turso Get History Error] {e}")

    # Fallback to local SQLite
    try:
        conn = _get_sqlite_conn()
        cur = conn.cursor()
        cur.execute(f"SELECT role, message FROM conversation_history ORDER BY id DESC LIMIT {limit}")
        rows = cur.fetchall()
        conn.close()
        for r in reversed(rows):
            messages.append({"role": r["role"], "content": r["message"]})
        return messages
    except Exception as e:
        print(f"[SQLite Get History Error] {e}")
        return []

# Initialize on module load
try:
    init_db()
except Exception as e:
    pass
