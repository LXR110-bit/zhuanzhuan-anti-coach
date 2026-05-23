#!/usr/bin/env python3
"""Stable Coze schedule entrypoint for anti-coach v2 nodes."""

import json
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from io import StringIO
from pathlib import Path

from goal_card_manager import add_heartbeat, load_data, get_active_goal, get_latest_review_for_card, get_today_file
from runtime_logger import log_event, log_exception, log_stability, log_usage


CST = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REPO_NAME = "zhuanzhuan-anti-coach"
LEGACY_REPO_NAME = "anti-pretend-effort"
EXPECTED_REMOTE_FRAGMENT = "zhuanzhuan-anti-coach"

NODE_CONFIG = {
    "10:00": {
        "event_type": "goal_start",
        "action": "morning_calibration",
        "missing_status": "success",
        "missing_reason": "",
    },
    "14:00": {
        "event_type": "mid_check",
        "action": "mid_check",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "18:00": {
        "event_type": "daily_close",
        "action": "evening_review",
        "missing_status": "skipped",
        "missing_reason": "no_active_goal_card",
    },
    "weekly_21:00": {
        "event_type": "weekly_plan",
        "action": "start_weekly_planning",
        "missing_status": "success",
        "missing_reason": "",
    },
}


def now_cst():
    return datetime.now(CST)


def date_str(day):
    return day.strftime("%Y-%m-%d")


def week_start_for(day):
    return day - timedelta(days=day.weekday())


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
        log_stability("coze_schedule_runner.path_check_failed", ok=False, errors=errors, **ctx)
        return False, ctx, errors
    log_event("coze_schedule_runner.path_check_done", ok=True, **ctx)
    log_stability("coze_schedule_runner.path_check_done", ok=True, **ctx)
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


def context_paths():
    today = now_cst()
    monday = week_start_for(today)
    yesterday = today - timedelta(days=1)
    return {
        "week_start": date_str(monday),
        "weekly_plan": str(ROOT / "data" / "weekly_plans" / f"{date_str(monday)}.json"),
        "yesterday_daily_review": str(ROOT / "data" / "daily_reviews" / f"{date_str(yesterday)}.md"),
        "today_daily_review": str(ROOT / "data" / "daily_reviews" / f"{date_str(today)}.md"),
        "business_journal": str(ROOT / "data" / "business_journal" / f"{date_str(today)}.md"),
        "thinking_gap_journal": str(ROOT / "data" / "thinking_gap_journal" / f"{date_str(today)}.md"),
        "my_compass": str(ROOT / "config" / "my_compass.md"),
    }


def message_for_node(node, active_card, latest_review):
    paths = context_paths()
    if node == "weekly_21:00":
        return (
            "周日晚上了。我们做本周作战图，60-90 分钟，只做这一次高耗能决策。"
            f"先读月锚 {paths['my_compass']}，再按 prompts/weekly_planner.md 走 6 阶段。准备好就说“开始”。"
        )

    if node == "10:00":
        if active_card:
            return (
                f"早。今天已经有目标卡：{active_card.get('deliverable')}。"
                "先不重开规划，确认今天 3 件必做和深度时段有没有调整。"
            )
        return (
            "早。今天走日校准，不做 v1 五题。"
            f"先看本周作战图 {paths['weekly_plan']} 和昨日复盘 {paths['yesterday_daily_review']}。"
            "然后只回答 3 件事：今天有无调整、3 件必做、深度时段锁哪件。"
        )

    if not active_card:
        return ""

    deliverable = active_card.get("deliverable", "")
    latest_output = latest_review.get("output", "") if latest_review else "还没有 review"

    if node == "14:00":
        return "中段感知，3 分钟。上午 3 件必做完成了几件？有没有看到 1 个业务异常或新数据？"
    if node == "18:00":
        return (
            f"下班 15 分钟复盘。今天目标是：{deliverable}；上一段记录：{latest_output}。"
            "我们走 5 步：今天结果、业务观察、思维差异、明日大块、一句话总结。"
        )
    return ""


def next_step_for_node(node, active_found):
    if node == "weekly_21:00":
        return "ask_weekly_planning_then_call_weekly_plan_manager_create_json"
    if node == "10:00":
        return "ask_daily_morning_calibration"
    if node == "14:00" and active_found:
        return "ask_mid_check_then_append_business_observation_if_any"
    if node == "18:00" and active_found:
        return "ask_daily_evening_review"
    return "silent_exit_after_logged_skipped_heartbeat"


def run_node(node):
    if node not in NODE_CONFIG:
        print_json({"ok": False, "error": f"unsupported node: {node}", "supported_nodes": sorted(NODE_CONFIG)}, 2)

    ok, ctx, errors = path_check()
    if not ok:
        print_json({
            "ok": False,
            "error": "anti-coach path check failed",
            "errors": errors,
            "repo_context": ctx,
            "action": "stop_before_coaching_output",
        }, 3)

    state = load_status()
    active_card = state["active_card"]
    latest_review = state["latest_review_for_active"]
    active_found = bool(active_card)
    config = NODE_CONFIG[node]
    push_status = "success" if active_found or node in {"10:00", "weekly_21:00"} else config["missing_status"]
    reason = "" if active_found or node in {"10:00", "weekly_21:00"} else config["missing_reason"]

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
        "context_paths": context_paths(),
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
    log_stability(
        "coze_schedule_runner.node_done",
        ok=True,
        node=node,
        active_card_found=active_found,
        push_status=push_status,
        reason=reason,
        output_channel="coze",
        repo_root=ctx.get("root"),
        git_branch=ctx.get("branch"),
        git_remote=ctx.get("remote"),
    )
    log_usage(
        "anti_coach.node_triggered",
        node=node,
        active_card_found=active_found,
        push_status=push_status,
        reason=reason,
        next_step=result["next_step"],
        has_coach_message=bool(message),
        total_cards=state["total_cards"],
        total_reviews=state["total_reviews"],
        total_daily_summaries=state["total_daily_summaries"],
        total_heartbeats_before_run=state["total_heartbeats"],
        week_start=result["context_paths"]["week_start"],
    )
    print_json(result)


def main():
    log_event("coze_schedule_runner.start", root=str(ROOT))
    try:
        if len(sys.argv) != 2:
            print_json({"ok": False, "error": "usage: coze_schedule_runner.py <10:00|14:00|18:00|weekly_21:00>"}, 1)
        run_node(sys.argv[1])
    except SystemExit:
        raise
    except Exception as exc:
        log_exception("coze_schedule_runner.exception", exc)
        raise


if __name__ == "__main__":
    main()
