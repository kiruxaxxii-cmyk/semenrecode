"""Local user database and auth for the mirrored SemenRecode site."""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs

import local_db

_LOCK = threading.Lock()
_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
_LOGIN_LOCK = threading.Lock()


def _check_rate_limit(ip: str) -> tuple[bool, int]:
    now = datetime.now(timezone.utc).timestamp()
    with _LOGIN_LOCK:
        attempts = _LOGIN_ATTEMPTS.get(ip, [])
        attempts = [t for t in attempts if now - t < 900]
        if len(attempts) >= 10:
            remaining = int(900 - (now - attempts[0]))
            return False, remaining
        attempts.append(now)
        _LOGIN_ATTEMPTS[ip] = attempts
    return True, 0


def _clear_rate_limit(ip: str) -> None:
    with _LOGIN_LOCK:
        _LOGIN_ATTEMPTS.pop(ip, None)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def _load() -> dict[str, Any]:
    return local_db.load()


def _save(data: dict[str, Any]) -> None:
    local_db.save(data)


def _find_user(data: dict[str, Any], *, username: str | None = None, email: str | None = None, user_id: int | None = None):
    for user in data["users"]:
        if user_id is not None and user["id"] == user_id:
            return user
        if username and user["username"].lower() == username.lower():
            return user
        if email and user["email"].lower() == email.lower():
            return user
    return None


def _is_subscription_active(user: dict[str, Any]) -> bool:
    if not user.get("hasSubscription"):
        return False
    until = user.get("subscriptionUntil")
    if not until:
        return False
    try:
        expiry = datetime.fromisoformat(until.replace("Z", "+00:00"))
        return expiry > datetime.now(timezone.utc)
    except (ValueError, TypeError):
        return bool(until)


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    active = _is_subscription_active(user)
    registered = user.get("registeredAt")
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "USER"),
        "hasSubscription": active,
        "subscriptionUntil": user.get("subscriptionUntil") if active else None,
        "regDate": registered,
        "registeredAt": registered,
        "hwid": user.get("hwid", "-"),
    }


def _token_from_headers(headers: dict[str, str]) -> str | None:
    for key, value in headers.items():
        if key.lower() == "authorization" and value.lower().startswith("bearer "):
            return value[7:].strip() or None
    return None


def _user_from_token(data: dict[str, Any], token: str | None) -> dict[str, Any] | None:
    if not token:
        return None
    user_id = data.get("sessions", {}).get(token)
    if user_id is None:
        return None
    # Check session age (7 days max)
    meta = data.get("session_meta", {}).get(token)
    if meta:
        created = meta.get("created", 0)
        if datetime.now(timezone.utc).timestamp() - created > 604800:
            data["sessions"].pop(token, None)
            data["session_meta"].pop(token, None)
            import local_db
            local_db.save(data)
            return None
    return _find_user(data, user_id=int(user_id))


def ensure_default_user() -> None:
    with _LOCK:
        data = _load()
        if data["users"]:
            return
        salt = secrets.token_hex(8)
        data["users"].append(
            {
                "id": 1,
                "username": "admin",
                "email": "admin@local",
                "salt": salt,
                "password": _hash_password("admin", salt),
                "role": "admin",
                "hasSubscription": True,
                "subscriptionUntil": "2099-12-31T00:00:00.000Z",
                "hwid": "-",
                "registeredAt": _now(),
            }
        )
        data["next_id"] = 2
        _save(data)


def handle(path: str, method: str, body: bytes | None, headers: dict[str, str]) -> tuple[int, dict[str, Any] | str] | None:
    """Return (status, payload) for local auth routes, or None to proxy."""
    query = ""
    if "?" in path:
        path, query = path.split("?", 1)

    if not path.startswith("/api/"):
        return None

    remote_addr = headers.pop("__remote_addr", "unknown")

    api_path = path[4:]
    payload: dict[str, Any] = {}
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}

    if api_path == "/auth/login" and method == "POST":
        return _login(payload, remote_addr)

    if api_path == "/auth/register" and method == "POST":
        return _register(payload)

    if api_path == "/auth/forgot-password" and method == "POST":
        return 200, {"message": "If the email exists, a reset link was sent."}

    if api_path == "/auth/reset-password" and method == "POST":
        return 200, {"message": "Password updated."}

    token = _token_from_headers(headers)

    key_paths = {
        "/auth/keyActivate",
        "/auth/keyActivateHwid",
        "/auth/keyHwidActivate",
        "/auth/hwidKeyActivate",
    }
    if api_path in key_paths and method == "POST":
        return _activate_key(token, query, payload, api_path)

    if api_path.startswith("/admin/") or api_path.startswith("/media/") or api_path.startswith("/settings/"):
        import local_admin

        result = local_admin.handle(api_path, method, query, body, headers, token)
        if result is not None:
            return result

    if api_path.startswith("/zaliv/"):
        import local_zaliv

        result = local_zaliv.handle(api_path, method, query, body, headers, token)
        if result is not None:
            return result

    if api_path == "/user/profile" and method == "GET":
        return _profile(token)

    if api_path == "/user/sub" and method == "POST":
        return _sub(token)

    if api_path == "/user/getHwid" and method == "GET":
        return _hwid(token)

    if api_path.startswith("/user/eventGetter") and method == "POST":
        return 200, []

    if api_path == "/maintenance" and method == "GET":
        return _get_maintenance()

    return None


def _login(payload: dict[str, Any], remote_addr: str = "unknown") -> tuple[int, dict[str, Any] | str]:
    ok, remaining = _check_rate_limit(remote_addr)
    if not ok:
        return 429, {"message": f"Too many attempts. Try again in {remaining} seconds."}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if not username or not password:
        return 400, {"message": "Username and password are required."}

    with _LOCK:
        data = _load()
        user = _find_user(data, username=username)
        if not user or user["password"] != _hash_password(password, user["salt"]):
            return 401, {"message": "Invalid username or password."}

        # Clean expired sessions before creating new one
        now_ts = datetime.now(timezone.utc).timestamp()
        data.setdefault("session_meta", {})
        expired_sessions = [t for t, meta in data["session_meta"].items()
                           if now_ts - meta.get("created", 0) > 604800]
        for t in expired_sessions:
            data["sessions"].pop(t, None)
            data["session_meta"].pop(t, None)
        _clear_rate_limit(remote_addr)
        token = secrets.token_urlsafe(32)
        data.setdefault("sessions", {})[token] = user["id"]
        data["session_meta"][token] = {"created": now_ts, "ip": remote_addr}
        _save(data)
        return 200, {"token": token, "message": "Login successful."}


def _register(payload: dict[str, Any]) -> tuple[int, dict[str, Any] | str]:
    username = str(payload.get("username", "")).strip()
    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", ""))
    if not username or not email or not password:
        return 400, {"message": "Fill in all fields."}
    if len(password) < 6:
        return 400, {"message": "Password must be at least 6 characters."}
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return 400, {"message": "Latin letters, numbers and underscore only."}

    with _LOCK:
        data = _load()
        if _find_user(data, username=username):
            return 409, {"message": "Username already taken."}
        if _find_user(data, email=email):
            return 409, {"message": "Email already registered."}

        user_id = int(data.get("next_id", 1))
        salt = secrets.token_hex(8)
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "salt": salt,
            "password": _hash_password(password, salt),
            "role": str(payload.get("role", "USER")),
            "hasSubscription": False,
            "subscriptionUntil": None,
            "hwid": "-",
            "registeredAt": payload.get("regDate") or _now(),
        }
        data["users"].append(user)
        data["next_id"] = user_id + 1
        _save(data)
        token = secrets.token_urlsafe(32)
        data.setdefault("sessions", {})[token] = user_id
        _save(data)
        return 200, {
            "message": "Account created. You can log in now.",
            "token": token,
        }


def _profile(token: str | None) -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"error": "Not authenticated"}
        if not _is_subscription_active(user) and user.get("hasSubscription"):
            user["hasSubscription"] = False
            user["subscriptionUntil"] = None
            _save(data)
        return 200, _public_user(user)


def _sub(token: str | None) -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"error": "Not authenticated"}
        active = _is_subscription_active(user)
        if not active and user.get("hasSubscription"):
            user["hasSubscription"] = False
            user["subscriptionUntil"] = None
            _save(data)
        if active and user.get("subscriptionUntil"):
            return 200, {"sub": {"outDate": user["subscriptionUntil"]}}
        return 200, {"sub": None}


def _hwid(token: str | None) -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"error": "Not authenticated"}
        return 200, {"hwid": user.get("hwid", "-")}


def _activate_key(
    token: str | None,
    query: str,
    payload: dict[str, Any] | None = None,
    api_path: str = "",
) -> tuple[int, dict[str, Any] | str]:
    params = {k: v[0] for k, v in parse_qs(query).items()}
    key_value = params.get("key", "") or (payload or {}).get("key", "")
    key_value = str(key_value).strip().upper().replace("SEMEN", "SKY")
    if not key_value:
        return 400, {"message": "Key is required"}

    kind = "hwid" if "hwid" in api_path.lower() else "regular"

    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"message": "Not authenticated"}

        data.setdefault("keys", {"regular": [], "hwid": []})
        keys = data["keys"].setdefault(kind, [])

        key_item = next((k for k in keys if str(k.get("value", "")).upper() == key_value), None)
        if not key_item:
            return 404, {"message": "Key not found"}
        if int(key_item.get("used", 0)):
            return 409, {"message": "Key already used"}

        key_item["used"] = 1
        key_item["activationId"] = user["id"]

        if kind == "regular":
            # Clear expired subscription before adding new days
            current_until = None
            if _is_subscription_active(user):
                try:
                    current_until = datetime.fromisoformat(user["subscriptionUntil"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass
            days = int(key_item.get("days") or 30)
            until = (current_until or datetime.now(timezone.utc)) + timedelta(days=days)
            user["hasSubscription"] = True
            user["subscriptionUntil"] = until.isoformat()
            message = f"Subscription activated for {days} days."
        else:
            user["hwid"] = "-"
            message = "HWID reset key activated."

        _save(data)
        return 200, {"message": message}


def _get_maintenance() -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        return 200, {"enabled": data.get("maintenance", {}).get("enabled", False)}
