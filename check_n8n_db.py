import sqlite3
import os

db_path = os.path.expanduser('~/.n8n/database.sqlite')
print('DB exists:', os.path.exists(db_path))
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cur.fetchall()]
    print('Tables:', tables)
    if 'user' in tables:
        cur.execute("SELECT id, email, firstName, lastName, password FROM user;")
        print('Users:', cur.fetchall())
    if 'workflow_entity' in tables:
        cur.execute("SELECT id, name, active FROM workflow_entity;")
        rows = cur.fetchall()
        print(f'Workflows count: {len(rows)}')
        for r in rows:
            print('  ID:', r[0], '| Active:', r[2], '| Name:', r[1])
