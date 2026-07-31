import sqlite3
import random
import string

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Generate a complex 16-character password
chars = string.ascii_letters + string.digits + "!@#$%^&*"
new_password = ''.join(random.choice(chars) for _ in range(16))

cursor.execute("UPDATE users SET password = ? WHERE username = 'XdSvitik'", (new_password,))
conn.commit()
conn.close()

print(f"Password updated to: {new_password}")
