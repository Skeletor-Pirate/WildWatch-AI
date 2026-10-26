import sqlite3
import json
import threading

class OfflineQueue:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY, data TEXT)")

    def add(self, event):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO queue (data) VALUES (?)", (json.dumps(event),))

    def is_empty(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM queue")
            row = cur.fetchone()
            return row[0] == 0 if row else True

    def get_all(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, data FROM queue")
            return [{"db_id": row[0], "event": json.loads(row[1])} for row in cur.fetchall()]

    def clear(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM queue")
            
    def remove(self, db_id):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM queue WHERE id = ?", (db_id,))
