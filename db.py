import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_name TEXT,
            department TEXT,
            question TEXT,
            status TEXT DEFAULT 'new',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_ticket(user_id, user_name, department, question):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tickets (user_id, user_name, department, question, status)
        VALUES (?, ?, ?, ?, 'new')
    """, (user_id, user_name, department, question))
    conn.commit()
    ticket_id = cur.lastrowid
    conn.close()
    return ticket_id
