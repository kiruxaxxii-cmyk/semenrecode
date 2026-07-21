"""Persistence layer: JSON file (default) or PostgreSQL (when DATABASE_URL is set)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "local_auth.json"

_use_pg: bool | None = None
_pg_conn = None


def _init_pg():
    global _pg_conn
    try:
        import psycopg2
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            return False
        _pg_conn = psycopg2.connect(database_url, sslmode="require")
        _pg_conn.autocommit = True
        with _pg_conn.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
            )
        return True
    except Exception:
        _pg_conn = None
        return False


def _get_use_pg() -> bool:
    global _use_pg
    if _use_pg is None:
        _use_pg = _init_pg()
    return _use_pg


def load() -> dict[str, Any]:
    if _get_use_pg():
        return _pg_load()
    return _file_load()


def save(data: dict[str, Any]) -> None:
    if _get_use_pg():
        _pg_save(data)
    else:
        _file_save(data)


def _file_load() -> dict[str, Any]:
    if not DB_PATH.exists():
        return {"users": [], "sessions": {}, "next_id": 1}
    return json.loads(DB_PATH.read_text(encoding="utf-8"))


def _file_save(data: dict[str, Any]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _pg_reconnect():
    global _pg_conn
    try:
        import psycopg2
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            _pg_conn = psycopg2.connect(database_url, sslmode="require")
            _pg_conn.autocommit = True
    except Exception:
        _pg_conn = None


def _pg_load() -> dict[str, Any]:
    try:
        with _pg_conn.cursor() as cur:
            cur.execute("SELECT value FROM app_state WHERE key = 'state'")
            row = cur.fetchone()
            if row is None:
                return {"users": [], "sessions": {}, "next_id": 1}
            return json.loads(row[0])
    except Exception:
        _pg_reconnect()
        if _pg_conn is None:
            return _file_load()
        with _pg_conn.cursor() as cur:
            cur.execute("SELECT value FROM app_state WHERE key = 'state'")
            row = cur.fetchone()
            if row is None:
                return {"users": [], "sessions": {}, "next_id": 1}
            return json.loads(row[0])


def _pg_save(data: dict[str, Any]) -> None:
    raw = json.dumps(data, ensure_ascii=False)
    try:
        with _pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app_state (key, value) VALUES ('state', %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (raw,),
            )
    except Exception:
        _pg_reconnect()
        if _pg_conn is None:
            _file_save(data)
            return
        with _pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app_state (key, value) VALUES ('state', %s) "
                "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                (raw,),
            )
