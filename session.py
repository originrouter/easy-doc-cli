import json
import os

CACHE_FILE = ".session_cache.json"


class SessionError(Exception):
    pass


def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        raise SessionError("未找到 session 缓存，请先运行: python cli.py session create --doc-id <id>")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cache(data: dict):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_session_id() -> str:
    cache = load_cache()
    sid = cache.get("sessionId")
    if not sid:
        raise SessionError("缓存存在但缺少 sessionId")
    return sid


def get_cache() -> dict:
    return load_cache()
