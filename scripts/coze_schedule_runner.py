#!/usr/bin/env python3
"""Stable Coze schedule entrypoint for anti-coach nodes."""

import json
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from goal_card_manager import add_heartbeat, load_data, get_active_goal, get_latest_review_for_card, get_today_file
from runtime_logger import log_event, log_exception


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPO_NAME = "zhuanzhuan-anti-coach"
LEGACY_REPO_NAME = "anti-pretend-effort"
EXPECTED_REMOTE_FRAGMENT = "zhuanzhuan-anti-coach"

NODE_CONFIG = {
    "10:00": {
        "event_type": "goal_start",
        "action": "start_phase1",
        "missing_status": "success",
        "missing_reason": "",
    },
    "12:00": {
        "event_type": "segment_close",
        "action": "morning_close",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "13:30": {
        "event_type": "heartbeat",
        "action": "afternoon_start",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "18:00": {
        "event_type": "segment_close",
        "action": "dinner_handoff",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "19:00": {
        "event_type": "heartbeat",
        "action": "evening_start",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "21:00": {
        "event_type": "daily_close",
        "action": "daily_close",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
}


def git_value(args):
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "returncode": result.returncode,
    }


def repo_context():
    remote = git_value(["remote", "get-url", "origin"])
    branch = git_value(["branch", "--show-current"])
    return {
        "root": str(ROOT),
        "root_name": ROOT.name,
        "cwd": str(Path.cwd().resolve()),
        "cwd_name": Path.cwd().resolve().name,
        "remote": remote.get("stdout", ""),
        "branch": branch.get("stdout", ""),
        "remote_ok": remote.get("ok", False),
        "branch_ok": branch.get("ok", False),
    }


def path_check():
    ctx = repo_context()
    errors = []
    if ctx["root_name"] == LEGACY_REPO_NAME or ctx["cwd_name"] == LEGACY_REPO_NAME:
        errors.append("legacy_anti_pretend_effort_path")
    if Path(ctx["cwd"]) != ROOT:
        errors.append("unexpected_working_directory")
    if ctx["root_name"] != EXPECTED_REPO_NAME:
        errors.append("unexpected_script_repo_name")
    if EXPECTED_REMOTE_FRAGMENT not in ctx["remote"]:
        errors.append("unexpected_git_remote")
    if errors:
        log_event("coze_schedule_runner.path_check_failed", ok=False, errors=errors, **ctx)
        return False, ctx, errors
    log_event("coze_schedule_runner.path_check_done", ok=True, **ctx)
    return True, ctx, []


def print_json(payload, exit_code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def load_status():
    data = load_data(get_today_file())
    active = get_active_goal(data)
    latest_review = None
    if active:
        latest_review = get_latest_review_for_card(data, active.get("card_index"))
    return {
        "data": data,
        "active_card": active,
        "latest_review_for_active": latest_review,
        "total_cards": len(data.get("goal_cards", [])),
        "total_reviews": len(data.get("reviews", [])),
        "total_daily_summaries": len(data.get("daily_summaries", [])),
        "total_heartbeats": len(data.get("heartbeat_logs", [])),
    }


def message_for_node(node, active_card, latest_review):
    if node == "10:00":
        if active_card:
            return (
                f"今天已经有目标卡：{active_card.get('deliverable')}。"
                "继续这张卡，还是明确说要换 goal_card？"
            )
        return (
            "今天先别开干，五题过一遍：\n"
            "1. 老板到底想要什么？\n"
            "2. 今天最重要的产出是什么？\n"
            "3. 最小可交付版本长什么样？\n"
            "4. 什么会让你今天白干？\n"
            "5. 第一刀砍哪里？"
        )
    if not active_card:
        if node == "21:00":
            return "今天没有目标卡，无法做有效总结。明天 10:00 先把五题答实。"
        return ""

    deliverable = active_card.get("deliverable", "")
    min_version = active_card.get("min_version", "")
    latest_output = latest_review.get("output", "") if latest_review else "还没有 review"
    next_action = latest_review.get("next_action", active_card.get("first_cut", "")) if latest_review else active_card.get("first_cut", "")

    if node == "12:00":
        return f"上午收尾。今天要交的是 {deliverable}，最小版本是 {min_version}。上午实际交出来什么？没有就直说。"
    if node == "13:30":
        return f"下午开工。上一段到了：{latest_output}。现在第一刀：30 分钟内做完 {next_action}。开始。"
    if node == "18:00":
        return f"晚饭断点。下午到了：{latest_output}。卡在哪？19:00 回来第一个 30 分钟做什么？讲清楚。"
    if node == "19:00":
        return "晚上 2 小时。21:00 前最小能交什么？一句话回我。"
    if node == "21:00":
        return f"21:00 了。今天 deliverable 是 {deliverable}，交出来了吗？按今日交付、目标偏差、白干片段、有效动作、明日第一刀回答。"
    return ""


def run_node(node):
    if node not in NODE_CONFIG:
        print_json({"ok": False, "error": f"unsupported node: {node}", "supported_nodes": sorted(NODE_CONFIG)}, 2)

    ok, ctx, errors = path_check()
    if not ok:
        payload = {
            "ok": False,
            "error": "anti-coach path check failed",
            "errors": errors,
            "repo_context": ctx,
            "action": "stop_before_coaching_output",
        }
        print_json(payload, 3)

    state = load_status()
    active_card = state["active_card"]
    latest_review = state["latest_review_for_active"]
    active_found = bool(active_card)
    config = NODE_CONFIG[node]
    push_status = "success" if active_found or node == "10:00" else config["missing_status"]
    reason = "" if active_found or node == "10:00" else config["missing_reason"]

    heartbeat_stdout = StringIO()
    with redirect_stdout(heartbeat_stdout):
        add_heartbeat(
            node=node,
            event_type=config["event_type"],
            active_card_found="true" if active_found else "false",
            action_taken=config["action"],
            push_status=push_status,
            reason=reason,
            output_channel="coze",
        )

    message = message_for_node(node, active_card, latest_review)
    result = {
        "ok": True,
        "node": node,
        "output_channel": "coze",
        "active_card_found": active_found,
        "push_status": push_status,
        "reason": reason,
        "coach_message": message,
        "next_step": next_step_for_node(node, active_found),
        "repo_context": ctx,
        "status": {
            "total_cards": state["total_cards"],
            "total_reviews": state["total_reviews"],
            "total_daily_summaries": state["total_daily_summaries"],
            "total_heartbeats_before_run": state["total_heartbeats"],
            "active_card": active_card,
            "latest_review_for_active": latest_review,
        },
    }
    log_event("coze_schedule_runner.node_done", node=node, active_card_found=active_found, push_status=push_status, output_channel="coze")
    print_json(result)


def next_step_for_node(node, active_found):
    if node == "10:00" and not active_found:
        return "ask_phase1_five_questions_then_call_goal_card_manager_create"
    if node == "21:00" and active_found:
        return "ask_phase3_questions_then_call_goal_card_manager_summary"
    if active_found:
        return "continue_node_coaching_in_coze_main_chat"
    return "silent_exit_after_logged_skipped_heartbeat"


def main():
    log_event("coze_schedule_runner.start", root=str(ROOT))
    try:
        if len(sys.argv) != 2:
            print_json({"ok": False, "error": "usage: coze_schedule_runner.py <10:00|12:00|13:30|18:00|19:00|21:00>"}, 1)
        run_node(sys.argv[1])
    except SystemExit:
        raise
    except Exception as exc:
        log_exception("coze_schedule_runner.exception", exc)
        raise


if __name__ == "__main__":
    main()
