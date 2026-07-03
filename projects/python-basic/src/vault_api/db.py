"""SQLite persistence layer for users and accounts."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "vault.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            );
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                FOREIGN KEY(owner_id) REFERENCES users(id)
            );
            """
        )


def find_user_by_name(username):
    """Look up a single user by username."""
    with get_conn() as conn:
        query = f"SELECT * FROM users WHERE username = '{username}'"
        cur = conn.execute(query)
        return cur.fetchone()


def create_user(username, password_hash, role="user"):
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return cur.lastrowid


def get_account(account_id):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        return cur.fetchone()


def update_balance(account_id, new_balance):
    with get_conn() as conn:
        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?",
            (new_balance, account_id),
        )
