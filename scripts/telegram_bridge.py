#!/usr/bin/env python3
"""Telegram -> GitHub Lobster 橋接器。"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = PROJECT_ROOT / "runtime"
STATE_PATH = STATE_DIR / "telegram-bridge-state.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALLOWED_CHAT_IDS = {
    item.strip() for item in os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "").split(",") if item.strip()
}
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "bangdoll/github-lobster")
GITHUB_WORKFLOW = os.environ.get("GITHUB_WORKFLOW", "Lobster Task Router")
DEFAULT_MODE = os.environ.get("LOBSTER_TELEGRAM_DEFAULT_MODE", "dry-run")

LANE_MAP = {
    "/research": "research",
    "/knowledge": "knowledge",
    "/publish": "publish",
    "/ops": "ops",
}


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> Dict[str, Any]:
    if not STATE_PATH.exists():
        return {"offset": 0}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: Dict[str, Any]) -> None:
    ensure_state_dir()
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def api_request(url: str, method: str = "GET", data: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None) -> Dict[str, Any]:
    payload = None
    request_headers = headers or {}
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=payload, headers=request_headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def telegram_api(method: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    return api_request(url, method="POST" if payload is not None else "GET", data=payload)


def send_message(chat_id: str, text: str) -> None:
    telegram_api(
        "sendMessage",
        {
            "chat_id": chat_id,
            "text": text,
        },
    )


def workflow_dispatch(mission: str, details: str, lane: str, mode: str, source: str) -> None:
    owner, repo = GITHUB_REPO.split("/", 1)
    encoded_workflow = urllib.parse.quote(GITHUB_WORKFLOW, safe="")
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{encoded_workflow}/dispatches"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "ref": "main",
        "inputs": {
            "mission": mission,
            "details": details,
            "lane": lane,
            "mode": mode,
        },
    }
    api_request(url, method="POST", data=payload, headers=headers)


def github_api(path: str) -> Dict[str, Any]:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    return api_request(url, method="GET", headers=headers)


def fetch_recent_run() -> Dict[str, Any]:
    owner, repo = GITHUB_REPO.split("/", 1)
    data = github_api(f"/repos/{owner}/{repo}/actions/runs?per_page=1")
    runs = data.get("workflow_runs", [])
    return runs[0] if runs else {}


def parse_command(text: str) -> Dict[str, str]:
    stripped = text.strip()
    if not stripped:
        return {"action": "empty"}

    parts = stripped.split(maxsplit=1)
    command = parts[0]
    content = parts[1].strip() if len(parts) > 1 else ""

    if command == "/help":
        return {"action": "help"}
    if command == "/status":
        return {"action": "status"}
    if command in LANE_MAP:
        return {
            "action": "dispatch",
            "lane": LANE_MAP[command],
            "mission": content or "未命名龍蝦任務",
        }
    return {"action": "unknown"}


def build_details(lane: str, mission: str) -> str:
    if lane == "research":
        return "\n".join(
            [
                "請整理重點摘要、風險與下一步。",
                "內容來源之一請包含：",
                "1. https://ai-digest.liziran.com",
                "2. https://ai-brief.liziran.com/zh/",
            ]
        )
    if lane == "knowledge":
        return "\n".join(
            [
                "### 目標資料夾",
                "Inbox",
                "",
                "### 預期輸出",
                f"請整理任務：{mission}",
                "",
                "### 風險邊界",
                "不要覆寫原始內容",
            ]
        )
    if lane == "publish":
        return "請輸出發布前檢查清單、風險與待補項目。"
    return "請輸出巡檢摘要、風險與下一步。"


def format_help() -> str:
    return "\n".join(
        [
            "GitHub Lobster Telegram 指令：",
            "/research <任務內容>",
            "/knowledge <任務內容>",
            "/publish <任務內容>",
            "/ops <任務內容>",
            "/status",
            "/help",
        ]
    )


def format_status(run: Dict[str, Any]) -> str:
    if not run:
        return "目前查不到最近的 GitHub Actions run。"
    return "\n".join(
        [
            "最近一次龍蝦任務：",
            f"- 名稱：{run.get('name', '未知')}",
            f"- 狀態：{run.get('status', '未知')}",
            f"- 結果：{run.get('conclusion', '未知')}",
            f"- 連結：{run.get('html_url', '無')}",
        ]
    )


def is_allowed_chat(chat_id: str) -> bool:
    return not TELEGRAM_ALLOWED_CHAT_IDS or chat_id in TELEGRAM_ALLOWED_CHAT_IDS


def validate_env() -> None:
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if missing:
        raise SystemExit(f"缺少必要環境變數：{', '.join(missing)}")


def handle_message(message: Dict[str, Any]) -> None:
    chat = message.get("chat", {})
    chat_id = str(chat.get("id", ""))
    text = message.get("text", "")

    if not chat_id or not text:
        return

    if not is_allowed_chat(chat_id):
        send_message(chat_id, "此聊天未在白名單中，拒絕執行。")
        return

    parsed = parse_command(text)
    action = parsed["action"]

    if action == "help":
        send_message(chat_id, format_help())
        return
    if action == "status":
        send_message(chat_id, format_status(fetch_recent_run()))
        return
    if action == "unknown":
        send_message(chat_id, "無法辨識指令，請輸入 /help 查看用法。")
        return
    if action == "empty":
        return

    lane = parsed["lane"]
    mission = parsed["mission"]
    details = build_details(lane, mission)
    workflow_dispatch(
        mission=mission,
        details=details,
        lane=lane,
        mode=DEFAULT_MODE,
        source="telegram_bridge",
    )
    send_message(
        chat_id,
        "\n".join(
            [
                "已派工給 GitHub Lobster。",
                f"- 工作線：{lane}",
                f"- 任務：{mission}",
                f"- 模式：{DEFAULT_MODE}",
            ]
        ),
    )


def poll_updates() -> Iterable[Dict[str, Any]]:
    state = load_state()
    offset = int(state.get("offset", 0))
    response = telegram_api("getUpdates", {"timeout": 20, "offset": offset})
    for item in response.get("result", []):
        yield item
        state["offset"] = item["update_id"] + 1
        save_state(state)


def main() -> int:
    validate_env()
    ensure_state_dir()
    print("Telegram bridge 已啟動，開始輪詢更新。")
    while True:
        try:
            for update in poll_updates():
                message = update.get("message", {})
                handle_message(message)
        except urllib.error.HTTPError as exc:
            print(f"HTTP 錯誤：{exc}")
            time.sleep(5)
        except urllib.error.URLError as exc:
            print(f"網路錯誤：{exc}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("已手動停止 Telegram bridge。")
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"未預期錯誤：{exc}")
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
