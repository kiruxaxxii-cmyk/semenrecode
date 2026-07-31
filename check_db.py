import sqlite3

def check_db():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
    row = cursor.fetchone()
    if row:
        print("Schema:", row[0])
        cursor.execute("SELECT id, username, is_admin FROM users")
        print("Users:", cursor.fetchall())
    else:
        print("No users table found in database.sqlite")
    conn.close()

check_db()
