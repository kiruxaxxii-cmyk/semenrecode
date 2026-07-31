import sqlite3
import time

conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Take away admin rights from 'admin'
cursor.execute("UPDATE users SET is_admin = 0, role = 'user' WHERE username = 'admin'")
print(f"Updated admin rights for 'admin': {cursor.rowcount} rows affected.")

# 2. Check if XdSvitik exists
cursor.execute("SELECT id FROM users WHERE username = 'XdSvitik'")
row = cursor.fetchone()

if row:
    # Update existing
    cursor.execute("UPDATE users SET is_admin = 1, role = 'admin', password = 'password123' WHERE username = 'XdSvitik'")
    print("Updated existing XdSvitik account.")
else:
    # Insert new
    cursor.execute('''
        INSERT INTO users (username, password, email, role, rank, is_admin, is_staff, memoryMb, avatarPath, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('XdSvitik', 'password123', 'xdsvitik@semeyonrecode', 'admin', 1, 1, 1, 1024, '/avatars/default.png', time.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("Created new XdSvitik account.")

conn.commit()
conn.close()
