import sqlite3
import os

paths = [
    r'C:\Users\HP\.gemini\antigravity-ide\scratch\database.sqlite',
    r'C:\Users\HP\.gemini\antigravity-ide\scratch\.n8n\database.sqlite',
    r'C:\Users\HP\.n8n\database.sqlite',
    r'C:\Users\HP\.n8n\.n8n\database.sqlite'
]
for p in paths:
    if os.path.exists(p):
        conn = sqlite3.connect(p)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workflow_entity';")
        if cur.fetchone():
            cur.execute("SELECT id, name, active FROM workflow_entity;")
            rows = cur.fetchall()
            print(f'=== {p}: {len(rows)} workflows ===')
            for r in rows:
                clean_name = str(r[1]).encode('ascii', errors='replace').decode('ascii')
                print(f"  ID: {r[0]} | Active: {r[2]} | Name: {clean_name}")
