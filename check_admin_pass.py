import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()
row = c.execute("SELECT username, password FROM users WHERE username = 'admin'").fetchone()
print("Stored admin password in DB:", repr(row[1]))
conn.close()
