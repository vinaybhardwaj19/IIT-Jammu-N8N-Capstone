import sqlite3

db = r'C:\Users\HP\.n8n\.n8n\database.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT * FROM user_api_keys;")
print('API Keys:', cur.fetchall())

cur.execute("PRAGMA table_info(settings);")
print('Settings cols:', [r[1] for r in cur.fetchall()])
cur.execute("SELECT * FROM settings;")
print('Settings:', cur.fetchall())
