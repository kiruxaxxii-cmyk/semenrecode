#!/usr/bin/env python3
"""Local mirror server for skycoreclient.xyz with local auth."""

from __future__ import annotations

import http.server
import json
import secrets
import socketserver
import urllib.error
import urllib.request
from http.cookies import SimpleCookie
from pathlib import Path

import local_auth

ROOT = Path(__file__).resolve().parent
HOST = "0.0.0.0"
PORT = 8080
REMOTE = "https://skycoreclient.xyz"
REMOTE_API = f"{REMOTE}/api"
SPA_ROUTES = {
    "/",
    "/privacy",
    "/terms",
    "/products",
    "/media",
    "/cabinet",
    "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret",
    "/register",
    "/login",
    "/checkout",
    "/addons",
    "/reset-password",
    "/confirm-deploy",
    "/launcher/cabinet",
}

_CHALLENGE_TOKENS: set[str] = set()
_CHALLENGE_COOKIE = "cf_chl_rc_m"


def _challenge_html(target: str, token: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Проверка</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box}}
  body{{min-height:100vh;display:flex;align-items:center;justify-content:center;background:#0d0d11;font-family:system-ui,-apple-system,sans-serif;color:#fff}}
  .card{{background:#1a1a24;border:1px solid #ffffff14;border-radius:16px;padding:48px;text-align:center;max-width:420px;width:90%}}
  .logo{{font-size:48px;margin-bottom:16px}}
  h1{{font-size:22px;font-weight:700;margin-bottom:8px;background:linear-gradient(135deg,#f7a11a,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  p{{font-size:14px;color:#999;margin-bottom:24px}}
  .btn{{display:inline-flex;align-items:center;gap:10px;padding:12px 32px;border:none;border-radius:10px;background:linear-gradient(135deg,#f7a11a,#ff6b6b);color:#fff;font-size:16px;font-weight:500;cursor:pointer;transition:opacity .2s}}
  .btn:hover{{opacity:.85}}
  .footer{{margin-top:20px;font-size:12px;color:#555;line-height:1.6}}
</style>
</head>
<body>
<div class="card">
  <div class="logo">🔒</div>
  <h1>Проверка безопасности</h1>
  <p>Нажмите кнопку, чтобы подтвердить, что вы не робот</p>
  <form method="POST" action="/api/challenge/verify">
    <input type="hidden" name="token" value="{token}">
    <input type="hidden" name="redirect" value="{target}">
    <button class="btn" type="submit">Я не робот</button>
  </form>
  <div class="footer">protected for @AntiSk3d and SVITIK and @cabbitguard and @AntiSk3dGuard and dima moriarti</div>
</div>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")

    def _path(self) -> str:
        return self.path.split("?", 1)[0]

    def do_HEAD(self):
        if self._dispatch("HEAD"):
            return
        return super().do_HEAD()

    def do_GET(self):
        if self._dispatch("GET"):
            return
        return super().do_GET()

    def _challenge_passed(self) -> bool:
        raw = self.headers.get("Cookie", "")
        if not raw:
            return False
        for part in raw.split(";"):
            part = part.strip()
            if part.startswith(_CHALLENGE_COOKIE + "="):
                val = part[len(_CHALLENGE_COOKIE) + 1:]
                ok = val in _CHALLENGE_TOKENS
                return ok
        return False

    def _dispatch(self, method: str) -> bool:
        path = self._path()
        if path.startswith("/api/"):
            body = self._read_body() if method not in ("GET", "HEAD") else None
            if self._handle_local_api(method, body):
                return True
            self._proxy(method, body)
            return True
        if path in ("/files/launcher.exe", "/files/launcher.jar"):
            self.send_error(404)
            return True
        if path.startswith("/files/"):
            local = ROOT / path.lstrip("/")
            if local.is_file():
                if method == "HEAD":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Length", str(local.stat().st_size))
                    self.end_headers()
                else:
                    super().do_GET()
            else:
                self._proxy_remote(method, f"{REMOTE}{path}")
            return True
        if path == "/admin-logs":
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
            return True
        if path in SPA_ROUTES or (
            not path.startswith("/assets/")
            and "." not in Path(path).name
        ):
            if not self._challenge_passed():
                token = secrets.token_urlsafe(24)
                _CHALLENGE_TOKENS.add(token)
                html = _challenge_html(path, token)
                data = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return True
            if method == "HEAD":
                data = self._index_html().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
            else:
                self._serve_index()
            return True
        return False

    def do_POST(self):
        path = self._path()
        if path == "/api/challenge/verify":
            body = self._read_body()
            if body:
                import urllib.parse
                params = urllib.parse.parse_qs(body.decode("utf-8", errors="replace"))
                token = (params.get("token") or [""])[0]
                redirect = (params.get("redirect") or [""])[0]
                if token in _CHALLENGE_TOKENS:
                    import http.cookies
                    cookie = http.cookies.SimpleCookie()
                    cookie[_CHALLENGE_COOKIE] = token
                    cookie[_CHALLENGE_COOKIE]["path"] = "/"
                    cookie[_CHALLENGE_COOKIE]["max-age"] = 3600
                    cookie[_CHALLENGE_COOKIE]["samesite"] = "strict"
                    self.send_response(302)
                    self.send_header("Location", redirect or "/")
                    self.send_header("Set-Cookie", cookie[_CHALLENGE_COOKIE].OutputString())
                    self.end_headers()
                else:
                    self.send_response(302)
                    self.send_header("Location", "/")
                    self.end_headers()
            else:
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
            return
        if self._path().startswith("/api/"):
            body = self._read_body()
            if self._handle_local_api("POST", body):
                return
            return self._proxy("POST", body)
        self.send_error(404)

    def do_PUT(self):
        if self._path().startswith("/api/"):
            body = self._read_body()
            if self._handle_local_api("PUT", body):
                return
            return self._proxy("PUT", body)
        self.send_error(404)

    def do_PATCH(self):
        if self._path().startswith("/api/"):
            body = self._read_body()
            if self._handle_local_api("PATCH", body):
                return
            return self._proxy("PATCH", body)
        self.send_error(404)

    def do_DELETE(self):
        if self._path().startswith("/api/"):
            body = self._read_body()
            if self._handle_local_api("DELETE", body):
                return
            return self._proxy("DELETE", body)
        self.send_error(404)

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Authorization, Content-Type, X-Requested-With, CF-Turnstile-Token",
            )
            self.end_headers()
            return
        self.send_error(404)

    def _request_headers(self) -> dict[str, str]:
        headers = {k: v for k, v in self.headers.items()}
        headers["X-Real-IP"] = self.client_address[0]
        return headers

    def _read_body(self) -> bytes | None:
        if hasattr(self, "_cached_body"):
            return self._cached_body
        length = int(self.headers.get("Content-Length", "0") or 0)
        self._cached_body = self.rfile.read(length) if length else None
        return self._cached_body

    def _handle_local_api(self, method: str, body: bytes | None = None) -> bool:
        if body is None:
            body = self._read_body()
        result = local_auth.handle(self.path, method, body, self._request_headers())
        if result is None:
            return False
        status, payload = result
        self._send_response(status, payload)
        return True

    def _send_response(self, status: int, payload: dict | list | str):
        if isinstance(payload, str):
            data = payload.encode("utf-8")
            content_type = "text/plain; charset=utf-8"
        else:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            content_type = "application/json"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status: int, payload: dict | list | str):
        self._send_response(status, payload)

    def end_headers(self):
        if self.path.startswith("/api/") or self.path.endswith((".js", ".html")) or self._path() in SPA_ROUTES:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def _index_html(self) -> str:
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        index = index.replace("/assets/index-BgNmguIY.js", "/assets/local.bundle.js")
        index = index.replace("/assets/index-BgNmguIY.patched.js", "/assets/local.bundle.js")
        if "/assets/local.bundle.js" not in index:
            index = index.replace(
                "/assets/index-BgNmguIY.js",
                "/assets/local.bundle.js",
            )
        return index

    def _serve_index(self):
        html = self._index_html()
        
        # Log visit
        try:
            import local_auth
            with local_auth._LOCK:
                data = local_auth._load()
                data.setdefault("logs", [])
                ip = self.client_address[0]
                # Avoid logging the same IP rapidly
                recent = False
                for log in data["logs"][:10]:
                    if log.get("ip") == ip and log.get("action") == "visit":
                        recent = True
                        break
                if not recent:
                    data["logs"].insert(0, {"user": "Guest", "ip": ip, "time": local_auth._now(), "action": "visit"})
                    if len(data["logs"]) > 2000:
                        data["logs"] = data["logs"][:2000]
                    local_auth._save(data)
        except Exception:
            pass

        if self.path.startswith("/svitikadmin"):
            inject = '''
            <script>
            (async function() {
                const token = localStorage.getItem("token") || localStorage.getItem("auth_token");
                if (!token) {
                    document.documentElement.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%;font-family:sans-serif'>Access Denied: Admin Rights Required</h1>";
                    return;
                }
                try {
                    const res = await fetch("/api/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/check-admin-panel", {
                        method: "POST",
                        headers: { "Authorization": "Bearer " + token }
                    });
                    if (!res.ok) {
                        document.documentElement.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%;font-family:sans-serif'>Access Denied: Admin Rights Required</h1>";
                    }
                } catch(e) {
                    document.documentElement.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%;font-family:sans-serif'>Access Denied: Admin Rights Required</h1>";
                }
            })();
            </script>
            '''
            html = html.replace("<head>", "<head>" + inject)
            
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _proxy_remote(self, method: str, target: str):
        length = int(self.headers.get("Content-Length", "0") or 0)
        body = self.rfile.read(length) if length and method != "GET" else None

        headers = {}
        for key in ("Authorization", "Content-Type", "Accept", "User-Agent", "Range"):
            if key in self.headers:
                headers[key] = self.headers[key]
        headers.setdefault("User-Agent", "SemenRecodeLocalMirror/1.0")

        req = urllib.request.Request(target, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = resp.read() if method != "HEAD" else b""
                if b"SKY" in payload:
                    payload = payload.replace(b"SKY", b"SEMEN")
                self.send_response(resp.status)
                for key, value in resp.headers.items():
                    lk = key.lower()
                    if lk in {"transfer-encoding", "connection", "content-encoding"}:
                        continue
                    self.send_header(key, value)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                if method != "HEAD":
                    self.wfile.write(payload)
        except urllib.error.HTTPError as e:
            payload = e.read() if method != "HEAD" else b""
            if b"SKY" in payload:
                payload = payload.replace(b"SKY", b"SEMEN")
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if method != "HEAD":
                self.wfile.write(payload)
        except Exception as e:
            msg = f"Proxy error: {e}".encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            if method != "HEAD":
                self.wfile.write(msg)

    def _proxy(self, method: str, body: bytes | None = None):
        target = f"{REMOTE_API}{self.path[4:]}"
        # Reverse prefix for outgoing requests (server stores SKY, display shows SEMEN)
        if "SEMEN" in target:
            target = target.replace("SEMEN", "SKY")
        if body and b"SEMEN" in body:
            body = body.replace(b"SEMEN", b"SKY")
        if body is None and method not in ("GET", "HEAD"):
            body = self._read_body()

        headers = {}
        for key in ("Authorization", "Content-Type", "Accept", "User-Agent"):
            if key in self.headers:
                headers[key] = self.headers[key]
        headers.setdefault("User-Agent", "SemenRecodeLocalMirror/1.0")

        req = urllib.request.Request(target, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
                # Replace key prefix
                if b"SKY" in payload:
                    payload = payload.replace(b"SKY", b"SEMEN")
                self.send_response(resp.status)
                for key, value in resp.headers.items():
                    lk = key.lower()
                    if lk in {"transfer-encoding", "connection", "content-encoding"}:
                        continue
                    self.send_header(key, value)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)
        except urllib.error.HTTPError as e:
            payload = e.read()
            if b"SKY" in payload:
                payload = payload.replace(b"SKY", b"SEMEN")
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        except Exception as e:
            msg = f"Proxy error: {e}".encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(msg)


def main():
    local_auth.ensure_default_user()
    with socketserver.ThreadingTCPServer((HOST, PORT), Handler) as httpd:
        print(f"Serving {ROOT}")
        print(f"Open http://{HOST}:{PORT}")
        print("Local auth enabled (data/local_auth.json)")
        print("Default account: admin / admin")
        print(f"Other API proxied to {REMOTE_API}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
