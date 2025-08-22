import sqlite3
import uuid
from typing import Optional, Dict, Any

# Simple SQLite-based user repository. In-memory DB for tests.
# Using shared connection since app is small.
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row


def init_db() -> None:
    conn.execute(
        """
        create table if not exists users (
            id text primary key,
            email text unique not null,
            password_hash text not null,
            display_name text not null,
            created_at timestamp default current_timestamp
        )
        """
    )
    conn.commit()


def create_user(email: str, password_hash: str, display_name: str) -> Dict[str, Any]:
    user_id = str(uuid.uuid4())
    conn.execute(
        "insert into users (id, email, password_hash, display_name) values (?,?,?,?)",
        (user_id, email, password_hash, display_name),
    )
    conn.commit()
    return {
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "display_name": display_name,
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("select * from users where email = ?", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("select * from users where id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def clear_users() -> None:
    conn.execute("delete from users")
    conn.commit()


init_db()