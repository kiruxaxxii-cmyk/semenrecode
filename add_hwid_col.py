import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check if hwid column exists, add it if not
columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
print("Columns:", columns)

if 'hwid' not in columns:
    cursor.execute("ALTER TABLE users ADD COLUMN hwid TEXT DEFAULT NULL")
    conn.commit()
    print("Added hwid column!")
else:
    print("hwid column already exists.")

conn.close()
