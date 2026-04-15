import json
import os
import time

CACHE_FILE = ".session_cache.json"
SESSION_TTL = 600  # 10 minutes


class SessionError(Exception):
    pass


def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        raise SessionError("未找到 session 缓存，请先运行: python cli.py session create --doc-id <id>")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(data: dict):
    data["createdAt"] = time.time()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def is_expired(cache: dict) -> bool:
    created_at = cache.get("createdAt")
    if created_at is None:
        return True
    return time.time() - created_at > SESSION_TTL


def get_session_id() -> str:
    cache = load_cache()
    sid = cache.get("sessionId")
    if not sid:
        raise SessionError("缓存存在但缺少 sessionId")
    return sid


def get_cache() -> dict:
    return load_cache()
