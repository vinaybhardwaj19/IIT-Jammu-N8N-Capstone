import sqlite3

db = r'C:\Users\HP\.n8n\.n8n\database.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("PRAGMA table_info(user);")
print('User columns:', [r[1] for r in cur.fetchall()])

cur.execute("SELECT * FROM user;")
print('User rows:', cur.fetchall())

cur.execute("SELECT * FROM project;")
print('Projects:', cur.fetchall())

cur.execute("PRAGMA table_info(shared_workflow);")
print('shared_workflow columns:', [r[1] for r in cur.fetchall()])
cur.execute("SELECT * FROM shared_workflow;")
print('shared_workflow rows:', cur.fetchall())
