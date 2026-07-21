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


def _public_user(user: dict[str, Any]) -> dict[str, Any]:
    registered = user.get("registeredAt")
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "USER"),
        "hasSubscription": bool(user.get("hasSubscription", False)),
        "subscriptionUntil": user.get("subscriptionUntil"),
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

    api_path = path[4:]
    payload: dict[str, Any] = {}
    if body:
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}

    if api_path == "/auth/login" and method == "POST":
        return _login(payload)

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

    if api_path.startswith("/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/") or api_path.startswith("/media/") or api_path.startswith("/settings/"):
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

    if api_path == "/user/checkHwid" and method == "POST":
        return _check_hwid(token, payload)

    if api_path.startswith("/user/eventGetter") and method == "POST":
        return 200, []

    return None


def _login(payload: dict[str, Any]) -> tuple[int, dict[str, Any] | str]:
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    if not username or not password:
        return 400, {"message": "Username and password are required."}

    with _LOCK:
        data = _load()
        user = _find_user(data, username=username)
        if not user or user["password"] != _hash_password(password, user["salt"]):
            return 401, {"message": "Invalid username or password."}

        token = secrets.token_urlsafe(32)
        data.setdefault("sessions", {})[token] = user["id"]
        _save(data)
        
        # Полный ответ, который ожидает чит (AuthResponse)
        return 200, {
            "token": token, 
            "message": "Login successful.",
            "authorized": True,
            "uid": user["id"],
            "discord_username": user["username"],
            "expires_at": 9999999999999,
            "hwid_resets_left": 99,
            "client_version": "1.0.0",
            "reason": "OK",
            "allowed_versions": ["1.21.4"]
        }


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
        return 200, _public_user(user)


def _sub(token: str | None) -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"error": "Not authenticated"}
        sub = user.get("subscriptionUntil") if user.get("hasSubscription") else None
        if sub:
            return 200, {"sub": {"outDate": sub}}
        return 200, {"sub": None}


def _hwid(token: str | None) -> tuple[int, dict[str, Any] | str]:
    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"error": "Not authenticated"}
        return 200, {"hwid": user.get("hwid", "-")}


def _check_hwid(token: str | None, payload: dict[str, Any]) -> tuple[int, dict[str, Any] | str]:
    hwid = str(payload.get("hwid", "")).strip()
    if not hwid:
        return 400, {"message": "HWID is required"}

    with _LOCK:
        data = _load()
        user = _user_from_token(data, token)
        if not user:
            return 401, {"message": "Not authenticated"}

        current_hwid = user.get("hwid", "-")
        
        # Полный ответ, который ожидает чит (AuthResponse)
        auth_response = {
            "authorized": True,
            "uid": user["id"],
            "discord_username": user["username"],
            "token": token,
            "expires_at": 9999999999999,
            "hwid_resets_left": 99,
            "client_version": "1.0.0",
            "reason": "OK",
            "allowed_versions": ["1.21.4"]
        }
        
        if current_hwid == "-":
            user["hwid"] = hwid
            _save(data)
            auth_response["message"] = "HWID привязан"
            auth_response["bound"] = True
            return 200, auth_response
        
        if current_hwid == hwid:
            auth_response["message"] = "HWID verified"
            auth_response["bound"] = False
            return 200, auth_response
        
        auth_response["authorized"] = False
        auth_response["message"] = "Ошибка HWID: Аккаунт привязан к другому ПК."
        return 403, auth_response


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
            days = int(key_item.get("days") or 30)
            until = datetime.now(timezone.utc) + timedelta(days=days)
            user["hasSubscription"] = True
            user["subscriptionUntil"] = until.isoformat()
            message = f"Subscription activated for {days} days."
        else:
            user["hwid"] = "-"
            message = "HWID reset key activated."

        _save(data)
        return 200, {"message": message}
