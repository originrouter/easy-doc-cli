import os
import requests
from dotenv import load_dotenv

load_dotenv()

_BASE_URL = os.getenv("BASE_URL")
_API_KEY = os.getenv("API_KEY")


class APIError(Exception):
    pass


def post(endpoint: str, payload: dict) -> dict:
    if not _BASE_URL or not _API_KEY:
        raise APIError("缺少 BASE_URL 或 API_KEY，请检查 .env 文件")
    url = f"{_BASE_URL}{endpoint}"
    headers = {"x-api-key": _API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            msg += f"\n服务器回复: {e.response.text}"
        raise APIError(msg)
    data = resp.json()
    if data.get("code") != 1:
        raise APIError(f"API 错误 code={data.get('code')}: {data.get('message', '')}")
    return data.get("data", {})
