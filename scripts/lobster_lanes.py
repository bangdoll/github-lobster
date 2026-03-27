#!/usr/bin/env python3
"""各工作線的任務包產生器。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def extract_issue_field(details: str, field_name: str) -> str:
    marker = f"### {field_name}\n"
    if marker not in details:
        return ""
    after = details.split(marker, 1)[1]
    next_marker = after.split("\n### ", 1)
    value = next_marker[0].strip()
    return value


def build_common_sections(mission: str, details: str) -> Dict[str, str]:
    return {
        "mission": mission,
        "details": details.strip() or "未提供補充說明。",
        "output_expectation": extract_issue_field(details, "預期輸出") or "未指定預期輸出。",
        "guardrail": extract_issue_field(details, "風險邊界") or "未指定額外風險邊界。",
    }


def build_research_packet(mission: str, details: str) -> Dict[str, Any]:
    common = build_common_sections(mission, details)
    checklist = [
        "確認研究問題與決策目標",
        "列出至少 3 個檢索關鍵字或資料源",
        "整理觀察重點、風險與待驗證假設",
        "輸出可直接貼到 Issue 或文件的摘要",
    ]
    next_actions = [
        "先列來源清單，再開始蒐集資料",
        "區分已驗證事實與待確認推測",
        "優先輸出 5 點摘要與 3 條後續建議",
    ]
    return {
        "lane_summary": "此任務適合走研究線，目標是把零散問題壓成可決策摘要。",
        "checklist": checklist,
        "next_actions": next_actions,
        "deliverable_title": "研究任務包",
        **common,
    }


def build_knowledge_packet(mission: str, details: str) -> Dict[str, Any]:
    common = build_common_sections(mission, details)
    checklist = [
        "辨識要整理的知識來源與目標資料夾",
        "統一命名規則、日期格式與標籤",
        "拆出摘要、重點、待辦與關聯文件",
        "輸出可直接歸檔的整理建議",
    ]
    next_actions = [
        "先判斷這批內容要進資料庫、筆記或歸檔區",
        "若遇重複內容，先標記合併策略，不直接覆寫",
        "保留原始來源與整理後版本的對照關係",
    ]
    return {
        "lane_summary": "此任務適合走知識線，目標是把內容整理成可持續維護的知識資產。",
        "checklist": checklist,
        "next_actions": next_actions,
        "deliverable_title": "知識整理包",
        **common,
    }


def build_publish_packet(mission: str, details: str) -> Dict[str, Any]:
    common = build_common_sections(mission, details)
    checklist = [
        "確認發布目標、平台與預計時間",
        "檢查標題、摘要、CTA 與連結完整性",
        "執行去標籤檢查，排除 Draft 與內部編號",
        "輸出發布前檢查清單與待補項目",
    ]
    next_actions = [
        "先產出發布準備清單，不直接正式發布",
        "把文案、素材、連結與封面圖分開驗證",
        "完成核對後再切換到真正發布流程",
    ]
    return {
        "lane_summary": "此任務適合走發布線，目標是把發布前風險降到最低。",
        "checklist": checklist,
        "next_actions": next_actions,
        "deliverable_title": "發布準備包",
        **common,
    }


def build_ops_packet(mission: str, details: str) -> Dict[str, Any]:
    common = build_common_sections(mission, details)
    checklist = [
        "確認要巡檢的服務、腳本或排程",
        "列出健康檢查指標與異常門檻",
        "整理當前狀態、風險與建議處置",
        "輸出一份可交班的巡檢摘要",
    ]
    next_actions = [
        "先做盤點，不直接重啟或修改設定",
        "把異常分成立即處理與觀察中兩類",
        "補上下一次巡檢的建議時間點",
    ]
    return {
        "lane_summary": "此任務適合走運維線，目標是讓日常運作可視化、可交班。",
        "checklist": checklist,
        "next_actions": next_actions,
        "deliverable_title": "運維巡檢包",
        **common,
    }


HANDLERS = {
    "build_research_packet": build_research_packet,
    "build_knowledge_packet": build_knowledge_packet,
    "build_publish_packet": build_publish_packet,
    "build_ops_packet": build_ops_packet,
}


def render_markdown(packet: Dict[str, Any], lane_label: str, run_id: str) -> str:
    lines: List[str] = [
        f"# {packet['deliverable_title']} {run_id}",
        "",
        f"- 工作線：{lane_label}",
        f"- 任務：{packet['mission']}",
        f"- 生成時間：{utc_now_text()}",
        "",
        "## 任務定位",
        "",
        packet["lane_summary"],
        "",
        "## 補充說明",
        "",
        packet["details"],
        "",
        "## 預期輸出",
        "",
        packet["output_expectation"],
        "",
        "## 風險邊界",
        "",
        packet["guardrail"],
        "",
        "## 執行清單",
    ]
    for item in packet["checklist"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 建議下一步"])
    for item in packet["next_actions"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def build_packet(handler_name: str, lane_label: str, mission: str, details: str, run_id: str) -> Dict[str, Any]:
    handler = HANDLERS[handler_name]
    packet = handler(mission, details)
    packet["markdown"] = render_markdown(packet, lane_label, run_id)
    return packet
