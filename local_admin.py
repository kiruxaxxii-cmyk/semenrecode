"""Local admin/media API for the mirrored SemenRecode site."""

from __future__ import annotations

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import parse_qs

import local_auth

ADMIN_ROLES = {"admin", "owner", "moder", "administrator", "moderator"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_query(query: str) -> dict[str, str]:
    return {k: v[0] for k, v in parse_qs(query).items()}


def _is_admin(user: dict[str, Any] | None) -> bool:
    if not user:
        return False
    return str(user.get("role", "")).lower() in ADMIN_ROLES


def _admin_user_or_403(token: str | None) -> tuple[dict[str, Any] | None, tuple[int, dict[str, str]] | None]:
    with local_auth._LOCK:
        data = local_auth._load()
        user = local_auth._user_from_token(data, token)
    if not user:
        return None, (401, {"message": "Not authenticated"})
    return user, None


def _ensure_store(data: dict[str, Any]) -> None:
    data.setdefault("keys", {"regular": [], "hwid": []})
    data.setdefault("promos", [])
    data.setdefault("payments", {"balances": {}, "transactions": []})
    data.setdefault("next_key_id", 1)
    data.setdefault("next_promo_id", 1)


def _user_row(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "USER"),
        "regDate": user.get("registeredAt"),
        "hasSubscription": bool(user.get("hasSubscription", False)),
    }


def _gen_key() -> str:
    part = lambda n: "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(n))
    return f"SKY-{part(4)}-{part(4)}"


def _make_key(data: dict[str, Any], *, days: int | None, kind: str) -> dict[str, Any]:
    _ensure_store(data)
    key_id = int(data.get("next_key_id", 1))
    item = {
        "id": key_id,
        "value": _gen_key(),
        "days": days,
        "used": 0,
        "entDate": _now(),
        "activationId": None,
    }
    data["keys"][kind].append(item)
    data["next_key_id"] = key_id + 1
    return item


def handle(
    api_path: str,
    method: str,
    query: str,
    body: bytes | None,
    headers: dict[str, str],
    token: str | None,
) -> tuple[int, dict[str, Any] | list | str] | None:
    if not (api_path.startswith("/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/") or api_path.startswith("/media/") or api_path.startswith("/settings/")):
        return None

    if api_path.startswith("/media/"):
        return _media(api_path, method, token)

    if api_path.startswith("/settings/"):
        return _settings(api_path, method, token)

    user, denied = _admin_user_or_403(token)
    if denied:
        return denied

    params = _parse_query(query)
    payload: dict[str, Any] = {}
    if body:
        try:
            import json

            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/check-admin-panel" and method == "POST":
        return 200, {"ok": True, "allowed": True}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/user" and method == "POST":
        with local_auth._LOCK:
            data = local_auth._load()
            return 200, [_user_row(u) for u in data.get("users", [])]

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/userProfile" and method == "POST":
        user_id = int(params.get("id", "0"))
        with local_auth._LOCK:
            data = local_auth._load()
            target = local_auth._find_user(data, user_id=user_id)
            if not target:
                return 404, {"message": "User not found"}
            return 200, _user_row(target)

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/keys" and method == "POST":
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            return 200, list(data["keys"]["regular"])

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/hwidKeysGet" and method == "POST":
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            return 200, {"keys": list(data["keys"]["hwid"])}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/give/promocode" and method == "POST":
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            return 200, {"Success": list(data["promos"])}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/payment/balances" and method == "GET":
        return 200, {"balances": [], "total": 0}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/payment/transactions" and method == "POST":
        return 200, {"transactions": [], "items": []}

    if api_path in {"/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/keys", "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/keysHwid", "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/keysHwid"} and method == "POST":
        quantity = int(params.get("quantity", "1"))
        days = int(params["days"]) if "days" in params and api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/keys" else None
        kind = "regular" if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/keys" else "hwid"
        created = []
        with local_auth._LOCK:
            data = local_auth._load()
            for _ in range(max(1, quantity)):
                created.append(_make_key(data, days=days, kind=kind))
            local_auth._save(data)
        return 200, {"keys": created, "message": "Keys created"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/promo" and method == "POST":
        value = params.get("value", "").strip()
        if not value:
            return 400, {"message": "Promo code is required"}
        days = int(params.get("days", "30"))
        promo = {
            "id": 0,
            "value": value,
            "discount": int(float(params.get("discount", "10"))),
            "outActive": int(params.get("outActived", params.get("outActive", "100"))),
            "entActive": 0,
            "outDate": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
            "balance": 0,
        }
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            promo_id = int(data.get("next_promo_id", 1))
            promo["id"] = promo_id
            data["promos"].append(promo)
            data["next_promo_id"] = promo_id + 1
            local_auth._save(data)
        return 200, {"message": "Promo created", "promo": promo}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/user" and method in ("PUT", "POST", "PATCH"):
        combined = {**params}
        for k, v in payload.items():
            combined[k] = str(v)
        return _update_user(combined)

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/deleteKeys" and method == "POST":
        return _delete_item("regular", int(params.get("id", "0")))

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/deleteHwidKeys" and method == "POST":
        return _delete_item("hwid", int(params.get("id", "0")))

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/deletePromocode" and method == "POST":
        promo_id = int(params.get("id", "0"))
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            data["promos"] = [p for p in data["promos"] if int(p.get("id", 0)) != promo_id]
            local_auth._save(data)
        return 200, {"message": "Deleted"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/deleteSub" and method == "POST":
        username = params.get("username", "")
        with local_auth._LOCK:
            data = local_auth._load()
            target = local_auth._find_user(data, username=username)
            if target:
                target["hasSubscription"] = False
                target["subscriptionUntil"] = None
                local_auth._save(data)
        return 200, {"message": "Subscription removed"}

    if api_path in {"/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/bannedHwidForId", "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/bannedHwidForId"} and method == "POST":
        return 200, {"message": "HWID banned"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/unbanHwid" and method == "POST":
        return 200, {"message": "HWID unbanned"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/create/grantAccessPromo" and method == "POST":
        return 200, {"message": "Access granted"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/resetBalancePromo" and method == "POST":
        promo = params.get("promo", "")
        with local_auth._LOCK:
            data = local_auth._load()
            _ensure_store(data)
            for p in data["promos"]:
                if p.get("value") == promo:
                    p["balance"] = 0
            local_auth._save(data)
        return 200, {"message": "Balance reset"}

    if api_path == "/svitikadminproruerweriweirweirikdskfdsfsf1230120310230123ksfdkfdsfskfslldsfjeiriwerwerjwejrdkfksdfkdsfsdkfdkfkdsfkdsfkdsfssecret/read/deleteGrant" and method == "POST":
        return 200, {"message": "Grant deleted"}

    return 200, {"message": "OK", "local": True}


def _delete_item(kind: str, item_id: int) -> tuple[int, dict[str, str]]:
    with local_auth._LOCK:
        data = local_auth._load()
        _ensure_store(data)
        data["keys"][kind] = [k for k in data["keys"][kind] if int(k.get("id", 0)) != item_id]
        local_auth._save(data)
    return 200, {"message": "Deleted"}


def _update_user(params: dict[str, str]) -> tuple[int, dict[str, Any] | str]:
    username = params.get("username", "").strip()
    user_id = params.get("id", "").strip()
    if not username and not user_id:
        return 400, {"message": "Username is required"}
    with local_auth._LOCK:
        data = local_auth._load()
        target = None
        if user_id.isdigit():
            target = local_auth._find_user(data, user_id=int(user_id))
        if not target and username:
            target = local_auth._find_user(data, username=username)
        if not target:
            return 404, {"message": "User not found"}
        if params.get("email"):
            target["email"] = params["email"].strip()
        if params.get("role"):
            target["role"] = params["role"].strip()
        if params.get("subs"):
            days = int(params["subs"])
            if days > 0:
                target["hasSubscription"] = True
                target["subscriptionUntil"] = (
                    datetime.now(timezone.utc) + timedelta(days=days)
                ).isoformat()
            else:
                target["hasSubscription"] = False
                target["subscriptionUntil"] = None
        if params.get("passwordReset", "").lower() == "true":
            salt = secrets.token_hex(8)
            new_password = secrets.token_urlsafe(8)
            target["salt"] = salt
            target["password"] = local_auth._hash_password(new_password, salt)
            local_auth._save(data)
            return 200, f"Saved. New password: {new_password}"
        if params.get("hwidReset", "").lower() == "true":
            target["hwid"] = "-"
        local_auth._save(data)
    return 200, {"message": "Saved"}


def _media(api_path: str, method: str, token: str | None) -> tuple[int, dict[str, Any]]:
    if api_path == "/media/getPromoInfoForMedia" and method == "POST":
        return 200, {"promos": [], "Success": []}
    return 200, {}


def _settings(api_path: str, method: str, token: str | None) -> tuple[int, dict[str, Any]]:
    if api_path == "/settings/ram" and method == "POST":
        return 200, {"message": "Saved"}
    return 200, {"message": "OK"}
