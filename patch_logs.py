import os

folder = r"c:\Users\tyert\OneDrive\Desktop\anongrief.fun"
secret = "svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret"

# 1. Update local_auth.py to save logs to db
auth_path = os.path.join(folder, "local_auth.py")
with open(auth_path, "r", encoding="utf-8") as f:
    auth_content = f.read()

old_login = """    if api_path == "/auth/login" and method == "POST":
        res = _login(payload)
        if res and res[0] == 200:
            ip = headers.get("X-Real-IP", "Unknown")
            print(f"[LOG] User {payload.get('username')} logged in from IP: {ip}")
        return res"""

new_login = """    if api_path == "/auth/login" and method == "POST":
        res = _login(payload)
        if res and res[0] == 200:
            ip = headers.get("X-Real-IP", "Unknown")
            print(f"[LOG] User {payload.get('username')} logged in from IP: {ip}")
            with _LOCK:
                data = _load()
                data.setdefault("logs", [])
                data["logs"].insert(0, {"user": payload.get("username"), "ip": ip, "time": _now(), "action": "login"})
                _save(data)
        return res"""

if old_login in auth_content:
    with open(auth_path, "w", encoding="utf-8") as f:
        f.write(auth_content.replace(old_login, new_login))
    print("Patched local_auth.py")
else:
    print("Could not patch local_auth.py - maybe already patched?")

# 2. Update local_admin.py to expose the logs endpoint
admin_path = os.path.join(folder, "local_admin.py")
with open(admin_path, "r", encoding="utf-8") as f:
    admin_content = f.read()

logs_endpoint = f"""
    if api_path == "/{secret}/logs" and method == "GET":
        with local_auth._LOCK:
            data = local_auth._load()
            return 200, data.get("logs", [])
"""

if "logs" not in admin_content:
    # insert before the generic handler or at the top of the api handlers
    target = f'    if api_path == "/{secret}/give/check-admin-panel" and method == "POST":'
    if target in admin_content:
        new_admin = admin_content.replace(target, logs_endpoint + "\n" + target)
        with open(admin_path, "w", encoding="utf-8") as f:
            f.write(new_admin)
        print("Patched local_admin.py")
    else:
        print("Could not find target in local_admin.py")
else:
    print("local_admin.py already has logs endpoint")

# 3. Update server.py to serve the logs.html
server_path = os.path.join(folder, "server.py")
with open(server_path, "r", encoding="utf-8") as f:
    server_content = f.read()

logs_route = """        if path == "/admin-logs":
            local = ROOT / "logs.html"
            if local.is_file():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                data = local.read_text(encoding="utf-8").encode("utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404)
            return True"""

if "/admin-logs" not in server_content:
    target_server = "if path in SPA_ROUTES or ("
    if target_server in server_content:
        new_server = server_content.replace(target_server, logs_route + "\n        " + target_server)
        with open(server_path, "w", encoding="utf-8") as f:
            f.write(new_server)
        print("Patched server.py")
    else:
        print("Could not find target in server.py")
else:
    print("server.py already has /admin-logs route")
