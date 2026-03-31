# ============================================
# DATABASE.PY — handles all database work
# ============================================

import sqlite3   # built into Python, no pip needed!
import bcrypt 
# ── Connect to database ───────────────────────────
# This creates a file called "app.db" automatically
# if it doesn't exist yet
def get_connection():
    conn = sqlite3.connect("app.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()

    # Tasks table (same as before)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            text  TEXT    NOT NULL,
            done  INTEGER DEFAULT 0
        )
    """)

    # Messages table (same as before)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            email   TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    # ── NEW: Users table ──────────────────────────
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database tables ready!")


# ── NEW: Hash a password ──────────────────────────
def hash_password(plain_password):
    # Convert password to bytes, then hash it
    password_bytes = plain_password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")   # store as string


# ── NEW: Check if password matches hash ───────────
def check_password(plain_password, hashed_password):
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes   = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)