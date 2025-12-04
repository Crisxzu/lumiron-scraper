import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv('DATABASE_PATH', 'data/lumironscraper.db')


def init_db():
    db_dir = Path(DB_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_key TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            company TEXT NOT NULL,
            scraped_data TEXT NOT NULL,
            profile_data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            accessed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cache_key
        ON profile_cache(cache_key)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_created_at
        ON profile_cache(created_at)
    """)

    conn.commit()
    conn.close()

    print(f"[Database] ✓ Initialized at {DB_PATH}")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn