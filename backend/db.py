import sqlite3
import json

DB_PATH = 'wildwatch.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            status TEXT
        );
        CREATE TABLE IF NOT EXISTS topology_edges (
            source TEXT,
            target TEXT,
            PRIMARY KEY (source, target)
        );
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            node_id TEXT,
            ts TEXT,
            event_data TEXT
        );
        CREATE TABLE IF NOT EXISTS tracks (
            id TEXT PRIMARY KEY,
            event_id TEXT
        );
        CREATE TABLE IF NOT EXISTS verifications (
            event_id TEXT PRIMARY KEY,
            result_data TEXT
        );
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id TEXT PRIMARY KEY,
            event_id TEXT,
            actions TEXT
        );
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            action TEXT,
            status TEXT DEFAULT 'queued'
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            event_id TEXT,
            feedback_data TEXT
        );
        CREATE TABLE IF NOT EXISTS node_thresholds (
            node_id TEXT PRIMARY KEY,
            thresholds TEXT
        );
    ''')
    conn.commit()
    conn.close()

def store_event(event_id, event_dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO events (id, node_id, ts, event_data) VALUES (?, ?, ?, ?)',
              (event_id, event_dict.get('node_id'), event_dict.get('ts'), json.dumps(event_dict)))
    conn.commit()
    conn.close()

def store_verification(event_id, result_dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO verifications (event_id, result_data) VALUES (?, ?)',
              (event_id, json.dumps(result_dict)))
    conn.commit()
    conn.close()

def queue_command(node_id, action):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT INTO commands (node_id, action, status) VALUES (?, ?, ?)',
              (node_id, json.dumps(action), 'queued'))
    conn.commit()
    conn.close()

def get_queued_commands(node_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, action FROM commands WHERE node_id = ? AND status = ?', (node_id, 'queued'))
    rows = c.fetchall()
    commands = []
    for row in rows:
        commands.append(json.loads(row['action']))
        c.execute('UPDATE commands SET status = ? WHERE id = ?', ('sent', row['id']))
    conn.commit()
    conn.close()
    return commands

def store_agent_decision(event_id, actions):
    conn = get_conn()
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO agent_decisions (id, event_id, actions) VALUES (?, ?, ?)',
              (f"dec_{event_id}", event_id, json.dumps(actions)))
    conn.commit()
    conn.close()

def get_recent_events_from_db(node_id=None, limit=10):
    conn = get_conn()
    c = conn.cursor()
    if node_id:
        c.execute('SELECT id, node_id, ts, event_data FROM events WHERE node_id = ? ORDER BY rowid DESC LIMIT ?', (node_id, limit))
    else:
        c.execute('SELECT id, node_id, ts, event_data FROM events ORDER BY rowid DESC LIMIT ?', (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# Ensure database tables exist on module import
init_db()
