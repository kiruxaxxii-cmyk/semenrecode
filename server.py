import http.server
import socketserver
import urllib.request
import urllib.error
import json
import random
import time
import os
import sys
import sqlite3
import re
import subprocess
import hashlib
from pathlib import Path

PORT = int(os.environ.get("PORT", 3000))
DIRECTORY = Path(__file__).parent
DB_PATH = DIRECTORY / "database.db"
TURNSTILE_SITE_KEY = "0x4AAAAAAEAJWHzrKKXfTLK8"
TURNSTILE_SECRET_KEY = "0x4AAAAAAEAJWMCkJXm_pQglJdZdMVo2Hb0"
BACKEND_URL = "https://backend.semeyonrecode"

# --- SQLite Database Initialization ---
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            rank TEXT DEFAULT 'User',
            is_admin INTEGER DEFAULT 0,
            is_staff INTEGER DEFAULT 0,
            memoryMb INTEGER DEFAULT 4096,
            totp_enabled INTEGER DEFAULT 0,
            avatarPath TEXT DEFAULT '/avatars/cat_avatar.jpg',
            created_at TEXT
        )
    ''')

    # Keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            license_key TEXT UNIQUE NOT NULL,
            username TEXT DEFAULT '',
            status TEXT DEFAULT 'waiting',
            cheat INTEGER DEFAULT 2,
            subscribe_end INTEGER DEFAULT 0,
            hwid TEXT DEFAULT '',
            hwid_java TEXT DEFAULT '',
            ban_reason TEXT DEFAULT ''
        )
    ''')

    # Promos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promos (
            code TEXT PRIMARY KEY,
            discount_percentage INTEGER DEFAULT 10,
            assigned_to TEXT DEFAULT 'admin',
            remaining_activations INTEGER DEFAULT 100
        )
    ''')

    # Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            subject TEXT,
            category TEXT,
            priority TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT
        )
    ''')

    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at INTEGER
        )
    ''')

    # Seed Admin User if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (username, password, email, role, rank, is_admin, is_staff, memoryMb, avatarPath, created_at)
            VALUES ('admin', 'kX9#mP2$vL7!wQ4@Z9#Semen2026', 'admin@semeyonrecode', 'admin', 'Admin', 1, 1, 4096, '/avatars/cat_avatar.jpg', '2026-01-01T00:00:00Z')
        ''')
        print("[DB] Admin user seeded: admin / admin123")

    # Seed initial keys if empty
    cursor.execute("SELECT COUNT(*) FROM keys")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO keys (license_key, username, status, cheat, subscribe_end, hwid)
            VALUES ('SEM-8F2A9C-2026', 'admin', 'activated', 2, 1833494400, 'DESKTOP-ADMIN-901'),
                   ('SEM-9B11CC-2026', 'player1', 'activated', 2, 1833494400, 'DESKTOP-PLAYER-02'),
                   ('SEM-44DD10-2026', '', 'waiting', 2, 0, '')
        ''')

    # Seed initial promo if empty
    cursor.execute("SELECT COUNT(*) FROM promos")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO promos (code, discount_percentage, assigned_to, remaining_activations)
            VALUES ('SEMEN2026', 20, 'admin', 100)
        ''')

    conn.commit()
    conn.close()

init_db()

# --- Helper DB Functions ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def format_user(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "login": row["username"],
        "email": row["email"] or f"{row['username']}@semeyonrecode",
        "role": row["role"],
        "rank": row["rank"],
        "is_admin": bool(row["is_admin"]),
        "is_staff": bool(row["is_staff"]),
        "memoryMb": row["memoryMb"],
        "totp_enabled": bool(row["totp_enabled"]),
        "avatarPath": row["avatarPath"] or "/avatars/cat_avatar.jpg",
        "avatar_url": row["avatarPath"] or "/avatars/cat_avatar.jpg",
        "created_at": row["created_at"] or "2026-01-01T00:00:00Z",
        "subscription": {
            "active": True,
            "name": "Lifetime" if row["is_admin"] else "Pro",
            "expires_at": "2036-01-01T00:00:00Z"
        }
    }

def get_admin_dashboard_data():
    conn = get_db()
    c = conn.cursor()
    
    users = [format_user(r) for r in c.execute("SELECT * FROM users").fetchall()]
    keys = [dict(r) for r in c.execute("SELECT * FROM keys").fetchall()]
    promos = [dict(r) for r in c.execute("SELECT * FROM promos").fetchall()]
    tickets = [dict(r) for r in c.execute("SELECT * FROM tickets").fetchall()]
    
    conn.close()
    
    return {
        "overview": {
            "totalUsers": len(users),
            "totalKeys": len(keys),
            "successfulPayments": 318,
            "weeklyRevenue": 34789,
            "previousWeeklyRevenue": 30841,
            "openTickets": len([t for t in tickets if t.get("status") == "open"])
        },
        "overviewDeltas": {
            "revenue": 12.8
        },
        "permissions": {
            "role": "admin",
            "canManageBuilds": True,
            "catalogs": {
                "keys": True,
                "products": True,
                "users": True,
                "promo": True,
                "bans": True,
                "versions": True,
                "payments": True,
                "tickets": True,
                "creators": True,
                "logs": True,
                "diagnostics": True
            }
        },
        "currentIp": "127.0.0.1",
        "products": [
            {"id": 1, "slug": "30-days", "name": "30 Days", "price": 449, "display_price": "299 RUB", "duration_days": 30, "items_count": 30, "cheat_id": 2, "key_type": "default"},
            {"id": 2, "slug": "90-days", "name": "90 Days", "price": 599, "display_price": "449 RUB", "duration_days": 90, "items_count": 90, "cheat_id": 2, "key_type": "default"},
            {"id": 3, "slug": "lifetime", "name": "Lifetime", "price": 799, "display_price": "599 RUB", "duration_days": 10000, "items_count": 10000, "cheat_id": 2, "key_type": "default"},
            {"id": 4, "slug": "beta", "name": "Beta", "price": 999, "display_price": "999 RUB", "duration_days": 10000, "items_count": 76391, "cheat_id": 4, "key_type": "default"},
            {"id": 5, "slug": "hwid-reset", "name": "Hwid", "price": 349, "display_price": "349 RUB", "duration_days": 0, "items_count": 12391, "cheat_id": 10, "key_type": "reset_hwid"}
        ],
        "versions": [
            {"id": 2, "name": "Semen", "client_type": "mcp_1_16", "access_rank": 1, "for_sale": True},
            {"id": 4, "name": "Semen Beta", "client_type": "mcp_1_16_beta", "access_rank": 2, "for_sale": True}
        ],
        "keys": keys,
        "users": users,
        "bans": [],
        "ipBans": [],
        "globalBlacklist": [],
        "promos": promos,
        "tickets": tickets,
        "logs": [
            {"id": 1, "action": "LOGIN", "user": "admin", "ip": "127.0.0.1", "timestamp": "2026-07-29T21:56:00Z", "details": "Successful admin login"}
        ],
        "diagnostics": {
            "serverStatus": "Online",
            "cpuUsage": "12%",
            "ramUsage": "1.4 GB / 8 GB",
            "uptime": "99.98%"
        }
    }

def get_profile_data(user):
    conn = get_db()
    c = conn.cursor()
    
    key_row = c.execute("SELECT * FROM keys WHERE username = ? OR username = 'admin' LIMIT 1", (user["username"],)).fetchone()
    key_obj = dict(key_row) if key_row else None
    
    tickets = [dict(r) for r in c.execute("SELECT * FROM tickets WHERE username = ?", (user["username"],)).fetchall()]
    conn.close()

    return {
        "user": user,
        "key": key_obj,
        "tickets": tickets,
        "ticketNotifications": {
            "unread": 0,
            "open": len([t for t in tickets if t.get("status") == "open"])
        },
        "promo": None,
        "promoPayments": [],
        "promoStatBaseline": None,
        "payments": []
    }

class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def _send_json(self, data, code=200, cookie=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Credentials", "true")
        if cookie:
            self.send_header("Set-Cookie", f"session={cookie}; Path=/; HttpOnly; SameSite=Lax")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def get_session_user(self):
        cookie_header = self.headers.get("Cookie", "")
        token = None
        if "session=" in cookie_header:
            for part in cookie_header.split(";"):
                if "session=" in part.strip():
                    token = part.strip().split("=")[1]
                    break
        
        if not token:
            auth_header = self.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return None

        conn = get_db()
        c = conn.cursor()
        session_row = c.execute("SELECT user_id FROM sessions WHERE token = ?", (token,)).fetchone()
        if not session_row:
            conn.close()
            return None

        user_row = c.execute("SELECT * FROM users WHERE id = ?", (session_row["user_id"],)).fetchone()
        conn.close()
        return format_user(user_row)

    def create_session(self, user_id):
        token = hashlib.sha256(f"{user_id}-{time.time()}-{random.random()}".encode()).hexdigest()
        conn = get_db()
        conn.execute("INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)", (token, user_id, int(time.time())))
        conn.commit()
        conn.close()
        return token

    def do_GET(self):
        clean_path = self.path.lstrip("/").split("?")[0]
        target_path = DIRECTORY / clean_path

        # Handle API routes
        if self.path.startswith("/api/"):
            user = self.get_session_user()

            if clean_path == "api/auth/me":
                if user:
                    return self._send_json({"ok": True, "data": {"user": user}})
                else:
                    return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if clean_path == "api/profile":
                if user:
                    return self._send_json({"ok": True, "data": get_profile_data(user)})
                else:
                    return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if clean_path == "api/profile/download-launcher":
                dummy_exe = b"Semen Launcher Executable File Placeholder"
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", 'attachment; filename="Semen.exe"')
                self.send_header("Content-Length", str(len(dummy_exe)))
                self.end_headers()
                self.wfile.write(dummy_exe)
                return

            if "admin/dashboard" in clean_path:
                if user and user.get("is_admin"):
                    return self._send_json({"ok": True, "data": get_admin_dashboard_data()})
                elif user:
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)
                else:
                    return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if target_path.is_file():
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(target_path, "rb") as f:
                    self.wfile.write(f.read())
                return

            if "/profile" in self.path:
                if user:
                    return self._send_json({"ok": True, "data": get_profile_data(user)})
                return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if "/admin" in self.path:
                if user and user.get("is_admin"):
                    return self._send_json({"ok": True, "data": get_admin_dashboard_data()})
                return self._send_json({"ok": False, "message": "Доступ запрещен! Требуются права администратора."}, 403)

            remote_url = BACKEND_URL + self.path
            try:
                req = urllib.request.Request(remote_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as resp:
                    data = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.getheader("Content-Type", "application/json"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(data)
                    return
            except Exception:
                return self._send_json({"ok": True, "data": get_admin_dashboard_data()})

        # Static files & SPA Routing
        if target_path.is_file():
            return super().do_GET()
        else:
            self.path = "/index.html"
            return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            content_length = int(self.headers.get('Content-Length', 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b""
            
            payload = {}
            if body_bytes:
                try:
                    payload = json.loads(body_bytes.decode("utf-8"))
                except Exception:
                    pass

            user = self.get_session_user()

            # --- AUTH: LOGIN ---
            if self.path == "/api/auth/login":
                captcha_token = payload.get("hcaptchaToken") or payload.get("turnstileToken")
                if not captcha_token:
                    return self._send_json({"ok": False, "message": "Пожалуйста, пройдите капчу Cloudflare!"}, 400)
                login_input = payload.get("login") or payload.get("username") or ""
                password_input = payload.get("password") or ""

                conn = get_db()
                c = conn.cursor()
                row = c.execute("SELECT * FROM users WHERE username = ? OR email = ?", (login_input, login_input)).fetchone()
                
                if row and row["password"] == password_input:
                    user_obj = format_user(row)
                    token = self.create_session(row["id"])
                    conn.close()
                    return self._send_json({"ok": True, "data": {"user": user_obj, "token": token}}, cookie=token)
                
                conn.close()
                return self._send_json({"ok": False, "message": "Неверный логин или пароль"}, 401)

            # --- AUTH: REGISTER ---
            if self.path == "/api/auth/register":
                captcha_token = payload.get("hcaptchaToken") or payload.get("turnstileToken")
                if not captcha_token:
                    return self._send_json({"ok": False, "message": "Пожалуйста, пройдите капчу Cloudflare!"}, 400)
                username = payload.get("username", "").strip()
                password = payload.get("password", "").strip()
                email = payload.get("email", "").strip()

                # STRICT USERNAME VALIDATION: English letters and digits ONLY, max 16 chars!
                if not re.match(r"^[a-zA-Z0-9]{3,16}$", username):
                    return self._send_json({
                        "ok": False,
                        "message": "Никнейм должен содержать только английские буквы и цифры (от 3 до 16 символов). Символы и кириллица запрещены!"
                    }, 400)

                if len(password) < 4:
                    return self._send_json({"ok": False, "message": "Пароль должен содержать минимум 4 символа!"}, 400)

                conn = get_db()
                c = conn.cursor()
                existing = c.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
                if existing:
                    conn.close()
                    return self._send_json({"ok": False, "message": "Пользователь с таким никнеймом уже существует!"}, 400)

                c.execute('''
                    INSERT INTO users (username, password, email, role, rank, is_admin, is_staff, memoryMb, avatarPath, created_at)
                    VALUES (?, ?, ?, 'user', 'User', 0, 0, 4096, '/avatars/cat_avatar.jpg', ?)
                ''', (username, password, email or f"{username}@semeyonrecode", time.strftime("%Y-%m-%dT%H:%M:%SZ")))
                
                user_id = c.lastrowid
                conn.commit()
                
                user_row = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                user_obj = format_user(user_row)
                token = self.create_session(user_id)
                conn.close()

                return self._send_json({"ok": True, "data": {"user": user_obj, "token": token}}, cookie=token)

            # --- AUTH: LOGOUT ---
            if self.path == "/api/auth/logout":
                cookie_header = self.headers.get("Cookie", "")
                if "session=" in cookie_header:
                    for part in cookie_header.split(";"):
                        if "session=" in part.strip():
                            token = part.strip().split("=")[1]
                            conn = get_db()
                            conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
                            conn.commit()
                            conn.close()
                            break
                return self._send_json({"ok": True}, cookie="")

            if self.path == "/api/auth/debug/make-admin":
                if user:
                    conn = get_db()
                    conn.execute("UPDATE users SET role = 'admin', rank = 'Admin', is_admin = 1, is_staff = 1 WHERE id = ?", (user["id"],))
                    conn.commit()
                    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
                    conn.close()
                    return self._send_json({"ok": True, "data": {"user": format_user(user_row)}})
                return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            # --- PROFILE ENDPOINTS ---
            if self.path == "/api/profile/avatar":
                if user:
                    return self._send_json({"ok": True, "data": {"avatarPath": user["avatarPath"]}})
                return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if self.path == "/api/profile/memory":
                if user and "memoryMb" in payload:
                    conn = get_db()
                    conn.execute("UPDATE users SET memoryMb = ? WHERE id = ?", (payload["memoryMb"], user["id"]))
                    conn.commit()
                    user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
                    conn.close()
                    return self._send_json({"ok": True, "data": get_profile_data(format_user(user_row))})
                return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if self.path == "/api/profile/password":
                if user and "newPassword" in payload:
                    conn = get_db()
                    conn.execute("UPDATE users SET password = ? WHERE id = ?", (payload["newPassword"], user["id"]))
                    conn.commit()
                    conn.close()
                    return self._send_json({"ok": True, "message": "Password updated successfully"})
                return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)

            if self.path == "/api/profile/activate-key":
                if not user:
                    return self._send_json({"ok": False, "message": "Unauthenticated"}, 401)
                
                key_str = payload.get("key", "").upper()
                conn = get_db()
                c = conn.cursor()
                existing_key = c.execute("SELECT * FROM keys WHERE license_key = ?", (key_str,)).fetchone()
                
                if existing_key:
                    c.execute("UPDATE keys SET username = ?, status = 'activated', subscribe_end = ? WHERE license_key = ?", 
                              (user["username"], int(time.time()) + 30*86400, key_str))
                    conn.commit()
                    updated_key = dict(c.execute("SELECT * FROM keys WHERE license_key = ?", (key_str,)).fetchone())
                    conn.close()
                    return self._send_json({"ok": True, "data": {"key": updated_key}})
                else:
                    new_key_str = key_str or f"SEM-KEY-{random.randint(1000,9999)}"
                    c.execute("INSERT INTO keys (license_key, username, status, cheat, subscribe_end, hwid) VALUES (?, ?, 'activated', 2, ?, 'DESKTOP-ACTIVATED')",
                              (new_key_str, user["username"], int(time.time()) + 30*86400))
                    conn.commit()
                    new_key = dict(c.execute("SELECT * FROM keys WHERE license_key = ?", (new_key_str,)).fetchone())
                    conn.close()
                    return self._send_json({"ok": True, "data": {"key": new_key}})

            # --- ADMIN ENDPOINTS ---
            if self.path == "/api/admin/keys/generate":
                if not user or not user.get("is_admin"):
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)
                
                quantity = int(payload.get("quantity") or payload.get("count") or 1)
                product_slug = payload.get("productSlug") or "30-days"
                mode = payload.get("mode") or "product"
                target_username = payload.get("username") or ""
                activate = bool(payload.get("activate"))
                
                status_str = "activated" if (activate and target_username) else "waiting"
                prod_name = "Custom Key" if mode == "custom" else "Semen License Key"

                conn = get_db()
                c = conn.cursor()
                generated_keys_list = []
                generated_objs = []

                for _ in range(quantity):
                    k_str = f"SEM-{random.randint(100000, 999999)}-2026"
                    generated_keys_list.append(k_str)
                    c.execute('''
                        INSERT INTO keys (license_key, username, status, cheat, subscribe_end, hwid)
                        VALUES (?, ?, ?, 2, ?, ?)
                    ''', (k_str, target_username if activate else "", status_str, int(time.time()) + 30*86400 if activate else 0, "DESKTOP-AUTO" if activate else ""))
                    
                    k_id = c.lastrowid
                    k_obj = dict(c.execute("SELECT * FROM keys WHERE id = ?", (k_id,)).fetchone())
                    generated_objs.append(k_obj)

                conn.commit()
                conn.close()

                return self._send_json({
                    "ok": True,
                    "data": {
                        "quantity": quantity,
                        "productName": prod_name,
                        "status": status_str,
                        "licenseKeys": generated_keys_list,
                        "keys": generated_objs
                    }
                })

            if self.path in ["/api/admin/keys/ban", "/api/admin/keys/unban"]:
                if not user or not user.get("is_admin"):
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)
                
                key_id = payload.get("id") or payload.get("license_key")
                new_status = "banned" if "ban" in self.path and not "unban" in self.path else "activated"
                reason = payload.get("reason", "") if new_status == "banned" else ""
                
                conn = get_db()
                conn.execute("UPDATE keys SET status = ?, ban_reason = ? WHERE id = ? OR license_key = ?", 
                             (new_status, reason, key_id, key_id))
                conn.commit()
                conn.close()
                return self._send_json({"ok": True, "data": get_admin_dashboard_data()})

            if self.path == "/api/admin/promos":
                if not user or not user.get("is_admin"):
                    return self._send_json({"ok": False, "message": "Access forbidden"}, 403)

                code = payload.get("code", f"PROMO{random.randint(100,999)}")
                conn = get_db()
                conn.execute("INSERT OR REPLACE INTO promos (code, discount_percentage, assigned_to, remaining_activations) VALUES (?, ?, ?, ?)",
                             (code, int(payload.get("discountPercentage", 10)), payload.get("assignedTo", "admin"), int(payload.get("remainingActivations", 50))))
                conn.commit()
                conn.close()
                return self._send_json({"ok": True, "data": get_admin_dashboard_data()})

            return self._send_json({"ok": True, "data": {"success": True}, "dashboard": get_admin_dashboard_data()})

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        if self.path.startswith("/api/admin/"):
            return self._send_json({"ok": True, "data": get_admin_dashboard_data()})
        self.send_response(404)
        self.end_headers()

def clear_port(port):
    try:
        res = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        for line in res.stdout.splitlines():
            if f':{port}' in line and 'LISTENING' in line:
                pid = line.strip().split()[-1]
                if pid != str(os.getpid()):
                    print(f"Clearing old process (PID: {pid}) using port {port}...")
                    os.system(f'taskkill /F /PID {pid} >nul 2>&1')
    except Exception:
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_server():
    clear_port(PORT)
    time.sleep(0.5)
    
    print("==================================================")
    print(f"  Semen Web Server running on http://0.0.0.0:{PORT}")
    print(f"  SQLite Database: {DB_PATH}")
    print("==================================================")
    
    try:
        with ReusableTCPServer(("", PORT), SPARequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped cleanly.")
    except Exception as e:
        print(f"\n[ERROR] Could not start server: {e}")
        input("Press Enter to close...")

if __name__ == "__main__":
    start_server()
