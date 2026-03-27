#!/usr/bin/env python3
"""GitHub 龍蝦任務路由器。"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from lobster_lanes import build_packet, render_knowledge_note, slugify_folder_name

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = PROJECT_ROOT / "lobster" / "registry.json"
RUNS_DIR = PROJECT_ROOT / "lobster" / "runs"
KNOWLEDGE_VAULT_DIR = PROJECT_ROOT / "knowledge-vault"


def load_registry() -> Dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def extract_issue_field(details: str, field_name: str) -> str:
    pattern = rf"###\s*{re.escape(field_name)}\s*\n(.*?)(?:\n###\s|\Z)"
    match = re.search(pattern, details, flags=re.DOTALL)
    if not match:
        return ""
    return normalize_text(match.group(1))


def infer_lane(mission: str, details: str, requested_lane: str, registry: Dict[str, Any]) -> str:
    if requested_lane in registry["lanes"]:
        return requested_lane

    issue_lane = extract_issue_field(details, "工作線").lower()
    if issue_lane in registry["lanes"]:
        return issue_lane

    combined_text = f"{mission} {details}".lower()
    if any(keyword in combined_text for keyword in ("研究", "趨勢", "新聞", "news", "research")):
        return "research"
    if any(keyword in combined_text for keyword in ("知識", "筆記", "同步", "knowledge", "sync")):
        return "knowledge"
    if any(keyword in combined_text for keyword in ("發布", "發文", "publish", "wordpress", "pub")):
        return "publish"
    return "ops"


def build_run_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%dT%H%M%S%fZ")


def ensure_within_project(path: Path) -> None:
    resolved = path.resolve()
    project_resolved = PROJECT_ROOT.resolve()
    if not str(resolved).startswith(str(project_resolved)):
        raise ValueError(f"偵測到不安全路徑：{path}")


def write_knowledge_note(packet: Dict[str, Any], run_id: str) -> Path:
    safe_folder = slugify_folder_name(packet.get("target_folder", "Inbox"))
    target_dir = KNOWLEDGE_VAULT_DIR / safe_folder
    ensure_within_project(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    note_name = f"{run_id}-{slugify_folder_name(packet['mission']) or 'knowledge-note'}.md"
    note_path = target_dir / note_name
    ensure_within_project(note_path)
    note_path.write_text(render_knowledge_note(packet, run_id), encoding="utf-8")
    return note_path


def write_outputs(run_dir: Path, summary: Dict[str, Any], packet: Dict[str, Any]) -> None:
    summary_json = run_dir / "summary.json"
    summary_md = run_dir / "summary.md"
    packet_json = run_dir / "packet.json"
    packet_md = run_dir / "packet.md"

    summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    packet_json.write_text(
        json.dumps({k: v for k, v in packet.items() if k != "markdown"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    packet_md.write_text(packet["markdown"], encoding="utf-8")

    lines = [
        f"# 龍蝦任務摘要 {summary['run_id']}",
        "",
        f"- 任務：{summary['mission']}",
        f"- 工作線：{summary['lane']}",
        f"- 工作線標籤：{summary['lane_label']}",
        f"- 模式：{summary['mode']}",
        f"- 狀態：{summary['status']}",
        f"- 來源：{summary['source']}",
        f"- 交付類型：{summary['deliverable_type']}",
        "",
        "## 任務說明",
        "",
        summary["details"] or "未提供補充說明。",
        "",
        "## 驗證 Log",
    ]

    for item in summary["verification_log"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## 執行結果",
            "",
            f"```text\n{summary['execution']}\n```",
            "",
            "## 交付檔案",
            "",
            f"- packet.json: {packet_json.name}",
            f"- packet.md: {packet_md.name}",
        ]
    )

    if summary.get("knowledge_output_path"):
        lines.append(f"- knowledge note: {summary['knowledge_output_path']}")

    summary_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_github_output(run_dir: Path, lane: str, status: str) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return

    with open(github_output, "a", encoding="utf-8") as handle:
        handle.write(f"summary_path={run_dir / 'summary.json'}\n")
        handle.write(f"markdown_path={run_dir / 'summary.md'}\n")
        handle.write(f"lane={lane}\n")
        handle.write(f"status={status}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub 龍蝦任務路由器")
    parser.add_argument("--mission", required=True, help="任務名稱")
    parser.add_argument("--details", default="", help="補充說明")
    parser.add_argument("--lane", default="auto", help="指定工作線")
    parser.add_argument("--mode", default="dry-run", choices=["dry-run", "safe-run"], help="執行模式")
    parser.add_argument("--source", default="workflow_dispatch", help="觸發來源")
    args = parser.parse_args()

    registry = load_registry()
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    mission = normalize_text(args.mission)
    details = args.details.strip()
    lane = infer_lane(mission, details, args.lane, registry)
    lane_info = registry["lanes"][lane]
    run_id = build_run_id()
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    verification_log = [
        "[VERIFIED_SRC] 已載入 lobster/registry.json",
        f"[VERIFIED_SRC] 已完成工作線判斷：{lane}",
        f"[VERIFIED_SRC] 已載入工作線處理器：{lane_info['handler']}",
    ]

    execution = "dry-run 模式，未執行任何外部腳本。"
    status = "completed"
    knowledge_output_path = ""

    packet = build_packet(
        lane_info["handler"],
        lane_info["label"],
        mission,
        details,
        run_id,
    )

    if args.mode == "safe-run":
        if os.environ.get("LOBSTER_ALLOW_LOCAL_EXECUTION") == "1":
            if lane == "knowledge":
                note_path = write_knowledge_note(packet, run_id)
                knowledge_output_path = str(note_path.relative_to(PROJECT_ROOT))
                execution = f"已安全寫入知識筆記：{knowledge_output_path}"
            else:
                execution = "safe-run 已開啟，但目前只有 knowledge 線支援安全寫入。"
        else:
            execution = "safe-run 已要求執行，但環境未開啟 LOBSTER_ALLOW_LOCAL_EXECUTION=1。"

    summary: Dict[str, Any] = {
        "run_id": run_id,
        "mission": mission,
        "details": details,
        "lane": lane,
        "lane_label": lane_info["label"],
        "mode": args.mode,
        "source": args.source,
        "status": status,
        "deliverable_type": lane_info["deliverable_type"],
        "verification_log": verification_log,
        "execution": execution,
        "knowledge_output_path": knowledge_output_path,
    }

    write_outputs(run_dir, summary, packet)
    export_github_output(run_dir, lane, status)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
