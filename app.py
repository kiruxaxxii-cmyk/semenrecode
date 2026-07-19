#!/usr/bin/env python3
"""Flask app that serves the SemenRecode SPA with local auth."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory, render_template

import local_auth
from local_admin import _is_admin

app = Flask(__name__, static_folder="static")
app.secret_key = os.urandom(24)

ROOT = Path(__file__).resolve().parent
SPA_ROUTES = {
    "/",
    "/privacy",
    "/terms",
    "/products",
    "/media",
    "/cabinet",
    "/register",
    "/login",
    "/checkout",
    "/addons",
    "/reset-password",
    "/confirm-deploy",
    "/launcher/cabinet",
    "/adminsvitiksemenrecodekrytoydebeldaunsoft12312dsfksdfskfs",
}

local_auth.ensure_default_user()


def _get_body():
    length = request.content_length or 0
    return request.get_data() if length else None


def _get_headers():
    return dict(request.headers)


@app.route("/assets/<path:filename>")
def serve_asset(filename):
    return send_from_directory(ROOT / "static" / "assets", filename)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
def catch_all(path):
    full_path = f"/{path}" if path else "/"

    # Handle API routes
    if full_path.startswith("/api/"):
        body = _get_body()
        headers = _get_headers()
        headers["__remote_addr"] = request.remote_addr or request.headers.get("X-Forwarded-For", "unknown")
        result = local_auth.handle(full_path, request.method, body, headers)
        if result is not None:
            status, payload = result
            resp = jsonify(payload) if not isinstance(payload, str) else jsonify({"message": payload})
            # Set auth cookie on login
            if full_path == "/api/auth/login" and status == 200 and isinstance(payload, dict):
                tok = payload.get("token", "")
                if tok:
                    resp.set_cookie("mt_token", tok, max_age=86400 * 30, httponly=False, samesite="Lax")
            return resp, status

        # Subscription check for download-related proxy paths
        DOWNLOAD_PATHS = (
            "/api/loader/", "/api/download/", "/api/launcher/download",
            "/api/client/", "/api/files/",
        )
        if full_path.lower().startswith(DOWNLOAD_PATHS):
            from local_auth import _token_from_headers, _load, _user_from_token, _is_subscription_active
            _token = _token_from_headers(dict(request.headers))
            _data = _load()
            _user = _user_from_token(_data, _token)
            if not _user:
                return jsonify({"error": "Not authenticated"}), 401
            if not _is_subscription_active(_user):
                return jsonify({"error": "Subscription expired"}), 403

        # Proxy to remote API if not handled locally
        import urllib.error
        import urllib.request

        REMOTE_API = "https://skycoreclient.xyz/api"
        target = f"{REMOTE_API}{full_path[4:]}"
        if "SEMEN" in target:
            target = target.replace("SEMEN", "SKY")

        headers = {}
        for key in ("Authorization", "Content-Type", "Accept", "User-Agent"):
            if key in request.headers:
                headers[key] = request.headers[key]

        req = urllib.request.Request(
            target,
            data=body if request.method not in ("GET", "HEAD") else None,
            headers=headers,
            method=request.method,
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read()
                if b"SKY" in payload:
                    payload = payload.replace(b"SKY", b"SEMEN")
                return jsonify(json.loads(payload)), resp.status
        except urllib.error.HTTPError as e:
            payload = e.read()
            if b"SKY" in payload:
                payload = payload.replace(b"SKY", b"SEMEN")
            try:
                return jsonify(json.loads(payload)), e.code
            except json.JSONDecodeError:
                return payload, e.code
        except Exception as e:
            return jsonify({"error": str(e)}), 502

    # Check maintenance mode (skip for API, assets, static)
    if full_path not in ("/api/maintenance",) and not full_path.startswith("/assets/") and not full_path.startswith("/static/") and not full_path.startswith("/api/"):
        data = local_auth._load()
        if data.get("maintenance", {}).get("enabled", False):
            # Allow admin users through
            token = None
            auth_header = request.headers.get("Authorization", "")
            if auth_header.lower().startswith("bearer "):
                token = auth_header[7:].strip()
            if not token:
                token = request.cookies.get("mt_token", "")
            if not token:
                token = request.args.get("mt", "")
            if token:
                user = local_auth._user_from_token(data, token)
                if user and _is_admin(user):
                    pass  # admin bypass
                else:
                    return render_template("maintenance.html")
            else:
                return render_template("maintenance.html")

    # Block /admin (only secret path works)
    if full_path == "/admin":
        return "Not found", 404

    # Serve SPA index.html for SPA routes
    if full_path in SPA_ROUTES or (
        not full_path.startswith("/static/") and not full_path.startswith("/assets/")
        and "." not in Path(path).name
    ):
        return send_from_directory(ROOT, "index.html")

    return ("Not Found", 404)


@app.after_request
def add_cors(response):
    if request.path.startswith("/api/") or request.path.endswith((".js", ".html")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
