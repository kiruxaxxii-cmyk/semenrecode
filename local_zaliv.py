"""Local jar upload (zaliv) API."""

from __future__ import annotations

import json
import re
import secrets
import shutil
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import local_auth

ROOT = Path(__file__).resolve().parent
ZALIV_DIR = ROOT / "data" / "zaliv"
UPLOADS_DIR = ZALIV_DIR / "uploads"
FILES_DIR = ROOT / "files"
STATE_PATH = ZALIV_DIR / "state.json"


def _load_state() -> dict[str, Any]:
    _ensure_dirs()
    if not STATE_PATH.exists():
        return {"status": "idle", "message": "", "uploaded_at": 0, "filename": ""}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, Any]) -> None:
    ZALIV_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _auth_user(token: str | None) -> dict[str, Any] | None:
    with local_auth._LOCK:
        data = local_auth._load()
        return local_auth._user_from_token(data, token)


def _is_admin(user: dict[str, Any]) -> bool:
    return str(user.get("role", "")).lower() in {"admin", "owner", "moder", "administrator", "moderator"}


def handle(
    api_path: str,
    method: str,
    query: str,
    body: bytes | None,
    headers: dict[str, str],
    token: str | None,
) -> tuple[int, str | dict[str, Any]] | None:
    if not api_path.startswith("/zaliv/"):
        return None

    # GET launcher-url is public (no auth needed)
    if api_path == "/zaliv/launcher-url" and method == "GET":
        with local_auth._LOCK:
            data = local_auth._load()
            url = data.get("launcher_url", "")
        return 200, {"url": url}

    user = _auth_user(token)
    if not user:
        return 401, {"message": "Not authenticated"}

    params = {k: v[0] for k, v in parse_qs(query).items()}

    if api_path == "/zaliv/jar" and method == "POST":
        return _upload_jar(body or b"", headers)

    if api_path == "/zaliv/jar/status" and method == "GET":
        return _jar_status()

    if api_path == "/zaliv/jar/confirm" and method == "POST":
        return _jar_confirm(params.get("token", ""))

    if api_path == "/zaliv/launcher-url" and method == "POST":
        if not _is_admin(user):
            return 403, {"message": "Admin only"}
        payload = {}
        if body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}
        url = (payload.get("url") or params.get("url") or "").strip()
        with local_auth._LOCK:
            data = local_auth._load()
            data["launcher_url"] = url
            local_auth._save(data)
        return 200, {"message": "Launcher URL updated", "url": url}

    return 200, {"message": "OK"}


def _parse_multipart(body: bytes, content_type: str) -> dict[str, dict[str, Any]]:
    match = re.search(r'boundary=(?:"([^"]+)"|([^;]+))', content_type)
    if not match:
        raise ValueError("Missing multipart boundary")
    boundary = (match.group(1) or match.group(2) or "").strip()
    delimiter = f"--{boundary}".encode()
    fields: dict[str, dict[str, Any]] = {}

    for raw_part in body.split(delimiter)[1:]:
        part = raw_part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        header_end = part.find(b"\r\n\r\n")
        if header_end < 0:
            continue
        headers = part[:header_end].decode("utf-8", errors="ignore")
        content = part[header_end + 4 :]
        if content.endswith(b"\r\n"):
            content = content[:-2]

        name_match = re.search(r'name="([^"]+)"', headers)
        if not name_match:
            continue
        name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]*)"', headers)
        fields[name] = {
            "content": content,
            "filename": filename_match.group(1) if filename_match else None,
        }
    return fields


def _ensure_dirs() -> None:
    ZALIV_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    FILES_DIR.mkdir(parents=True, exist_ok=True)


def _header(headers: dict[str, str], name: str) -> str:
    name_l = name.lower()
    for key, value in headers.items():
        if key.lower() == name_l:
            return value
    return ""


def _upload_jar(body: bytes, headers: dict[str, str]) -> tuple[int, str]:
    content_type = _header(headers, "Content-Type")
    if "multipart/form-data" not in content_type:
        return 400, "Expected multipart upload"

    try:
        _ensure_dirs()
        fields = _parse_multipart(body, content_type)
        file_field = fields.get("file")
        if not file_field or not file_field["content"]:
            return 400, "File is required"

        filename = Path(file_field.get("filename") or "upload.jar").name
        dest = UPLOADS_DIR / filename
        dest.write_bytes(file_field["content"])

        state = {
            "status": "building",
            "message": "Upload accepted",
            "uploaded_at": time.time(),
            "filename": filename,
            "confirm_token": secrets.token_urlsafe(16),
        }
        _save_state(state)
        return 202, "Jar upload accepted. Waiting for confirmation."
    except Exception as exc:
        return 500, f"Upload failed: {exc}"


def _jar_status() -> tuple[int, str]:
    state = _load_state()
    if state.get("status") != "building":
        return 200, "No active build"

    uploaded_at = float(state.get("uploaded_at", 0))
    if time.time() - uploaded_at < 2.0:
        return 202, "Building jar..."

    src = UPLOADS_DIR / state.get("filename", "")
    if not src.is_file():
        return 500, "Uploaded file not found"

    out_name = "launcher.jar" if src.suffix.lower() == ".jar" else src.name
    dest = FILES_DIR / out_name
    shutil.copy2(src, dest)

    state["status"] = "ready"
    state["message"] = f"Jar ready at /files/{out_name}"
    _save_state(state)
    return 200, state["message"]


def _jar_confirm(token: str) -> tuple[int, str]:
    state = _load_state()
    if not token:
        return 400, "Token is required"

    saved = state.get("confirm_token", "")
    if saved and token != saved:
        return 409, "Deploy token mismatch"

    if state.get("status") == "ready":
        return 200, "Deploy confirmed"

    # Allow confirm even if status polling was skipped
    src_name = state.get("filename", "")
    src = UPLOADS_DIR / src_name if src_name else None
    if src and src.is_file():
        out_name = "launcher.jar" if src.suffix.lower() == ".jar" else src.name
        shutil.copy2(src, FILES_DIR / out_name)
        state["status"] = "ready"
        _save_state(state)
        return 200, "Deploy confirmed"

    return 409, "No uploaded jar to confirm"
