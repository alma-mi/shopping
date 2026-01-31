import sqlite3
import os
from datetime import datetime
from passlib.hash import bcrypt
from constants import MIN_INDEX, MAX_INDEX

MIN = MIN_INDEX
MAX = MAX_INDEX
# Database path (uses existing databaselog.db in project root by default)
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "databaselog.db")


def get_conn():
    """Open and return a sqlite3 connection."""
    # timeout small to avoid locking issues; row factory left default
    return sqlite3.connect(DB_PATH, timeout=5)


def create_tables():
    """Create users table if it doesn't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    finally:
        conn.close()


def add_user(username: str, password: str) -> bool:
    """Add a new user with a hashed password.

    Returns True on success, False if username already exists.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    finally:
        conn.close()


def verify_user(username: str, password: str):
    """Verify username and password.

    Returns a user dict (id, username) on success, or None on failure.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            return False
        return row[0] == password
    finally:
        conn.close()


def get_user(username: str):
    """Return basic user info (no password hash)."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT username, password FROM users WHERE username = ?",
            (username,))
        row = cur.fetchone()
        if row:
            return {"username": row[MIN], "password": row[MAX]}
        return None
    finally:
        conn.close()


def change_password(username: str, new_password: str) -> bool:
    """Change a user's password (hashes new password).
    Returns True if updated."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (new_password, username))
        conn.commit()
        return cur.rowcount > MIN
    finally:
        conn.close()


if __name__ == "__main__":
    # simple CLI to create tables and add an admin if desired
    import argparse

    parser = argparse.ArgumentParser(
        description="Simple DB helper for users table")
    parser.add_argument("--init", action="store_true", help="Create tables")
    parser.add_argument(
        "--add",
        nargs=2,
        metavar=(
            "USERNAME",
            "PASSWORD"),
        help="Add a user")
    args = parser.parse_args()

    if args.init:
        create_tables()
        print("Tables created (or already existed)")
    if args.add:
        u, p = args.add
        ok = add_user(u, p)
        print("User added:", ok)
