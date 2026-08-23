import os
import psycopg2
import psycopg2.extras
import psycopg2.pool
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. This app requires a Postgres database - "
        "add a Postgres instance on Render (or run one locally) and set "
        "DATABASE_URL in your .env file, e.g. "
        "postgresql://user:password@host:5432/dbname"
    )

# A small connection pool - reused across requests instead of opening a
# brand new TCP connection to Postgres on every single query, which is
# what the old SQLite version did (cheap for a local file, expensive
# for a networked database).
_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)


def _translate(query):
    """Existing call sites throughout this file use SQLite-style '?'
    placeholders - translate them to psycopg2's '%s' style so none of
    those call sites need to change."""
    return query.replace("?", "%s")


def execute(query, params=()):
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(_translate(query), tuple(params))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def insert_returning_id(query, params=()):
    """Same as execute(), but for INSERT statements where the caller
    needs the newly created row's id back (SQLite's cursor.lastrowid
    equivalent - Postgres needs an explicit RETURNING clause for this)."""
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(_translate(query) + " RETURNING id", tuple(params))
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


def fetch_one(query, params=()):
    conn = _pool.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(_translate(query), tuple(params))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        _pool.putconn(conn)


def fetch_all(query, params=()):
    conn = _pool.getconn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(_translate(query), tuple(params))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        _pool.putconn(conn)


def initialize_database():
    execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            language TEXT DEFAULT 'English',
            voice TEXT DEFAULT 'female',
            theme TEXT DEFAULT 'light',
            wallpaper TEXT DEFAULT 'dawn',
            voice_reply INTEGER DEFAULT 0,
            daily_quotes INTEGER DEFAULT 1,
            scripture INTEGER DEFAULT 1,
            notifications INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS moods(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("""
        CREATE TABLE IF NOT EXISTS journal_entries(
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            entry TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    execute("CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id, topic)")
    execute("CREATE INDEX IF NOT EXISTS idx_moods_user ON moods(user_id)")
    execute("CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id)")


# ==========================================================
# USERS
# ==========================================================

def create_user(username, email, password_hash, full_name=""):
    return insert_returning_id(
        """
        INSERT INTO users(username, email, password_hash, full_name)
        VALUES(?,?,?,?)
        """,
        (username, email, password_hash, full_name),
    )


def get_user_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email=?", (email,))


def get_user_by_username(username):
    return fetch_one("SELECT * FROM users WHERE username=?", (username,))


def get_user(user_id):
    return fetch_one("SELECT * FROM users WHERE id=?", (user_id,))


def update_preferences(user_id, **fields):
    if not fields:
        return
    allowed = {
        "language", "voice", "theme", "wallpaper", "voice_reply",
        "daily_quotes", "scripture", "notifications", "full_name",
    }
    keys = [k for k in fields.keys() if k in allowed]
    if not keys:
        return
    set_clause = ", ".join(f"{k}=?" for k in keys)
    values = [fields[k] for k in keys]
    values.append(user_id)
    execute(f"UPDATE users SET {set_clause} WHERE id=?", values)


def delete_user(user_id):
    execute("DELETE FROM users WHERE id=?", (user_id,))


# ==========================================================
# MESSAGES
# ==========================================================

def save_message(user_id, topic, sender, message):
    execute(
        """
        INSERT INTO messages(user_id, topic, sender, message)
        VALUES(?,?,?,?)
        """,
        (user_id, topic, sender, message),
    )


def load_messages(user_id, topic, limit=50):
    rows = fetch_all(
        """
        SELECT * FROM messages
        WHERE user_id=? AND topic=?
        ORDER BY id ASC
        LIMIT ?
        """,
        (user_id, topic, limit),
    )
    return rows


def delete_all_messages(user_id):
    execute("DELETE FROM messages WHERE user_id=?", (user_id,))


# ==========================================================
# MOODS
# ==========================================================

def save_mood(user_id, mood):
    execute(
        "INSERT INTO moods(user_id, mood) VALUES(?,?)",
        (user_id, mood),
    )


def load_moods(user_id, limit=20):
    return fetch_all(
        """
        SELECT * FROM moods
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )


# ==========================================================
# JOURNAL
# ==========================================================

def save_journal_entry(user_id, entry):
    execute(
        "INSERT INTO journal_entries(user_id, entry) VALUES(?,?)",
        (user_id, entry),
    )


def load_journal_entries(user_id, limit=100):
    return fetch_all(
        """
        SELECT * FROM journal_entries
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )


def delete_journal_entry(entry_id, user_id):
    execute(
        "DELETE FROM journal_entries WHERE id=? AND user_id=?",
        (entry_id, user_id),
    )
