#!/usr/bin/env python3
"""Weekly plan storage for anti-coach v2."""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from runtime_logger import log_event, log_exception


CST = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
WEEKLY_PLAN_DIR = ROOT / "data" / "weekly_plans"


def week_start_for(day):
    return day - timedelta(days=day.weekday())


def default_week_start():
    return week_start_for(datetime.now(CST)).strftime("%Y-%m-%d")


def print_json(payload, exit_code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(exit_code)


def normalize_plan(plan):
    if not isinstance(plan, dict):
        print_json({"ok": False, "error": "weekly_plan must be a JSON object"}, 1)
    plan.setdefault("week_start", default_week_start())
    plan.setdefault("created_at", datetime.now(CST).isoformat())
    return plan


def create_json(raw_json):
    try:
        plan = normalize_plan(json.loads(raw_json))
    except json.JSONDecodeError as exc:
        print_json({"ok": False, "error": f"invalid weekly_plan json: {exc}"}, 1)
    WEEKLY_PLAN_DIR.mkdir(parents=True, exist_ok=True)
    path = WEEKLY_PLAN_DIR / f"{plan['week_start']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
        f.write("\n")
    log_event("weekly_plan_manager.create_done", file=str(path), week_start=plan["week_start"])
    print_json({"ok": True, "weekly_plan_path": str(path), "week_start": plan["week_start"]})


def latest():
    files = sorted(WEEKLY_PLAN_DIR.glob("*.json"))
    if not files:
        print_json({"ok": True, "weekly_plan": None, "weekly_plan_path": None})
    path = files[-1]
    with open(path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    print_json({"ok": True, "weekly_plan_path": str(path), "weekly_plan": plan})


USAGE = """Usage: weekly_plan_manager.py <command> [args]

Commands:
  create_json '<weekly_plan_json>'
      Write a weekly_plan JSON object to data/weekly_plans/{week_start}.json.

  latest
      Print latest weekly plan if one exists.
"""


def main():
    log_event("weekly_plan_manager.command_start", command=sys.argv[1] if len(sys.argv) > 1 else None)
    try:
        if len(sys.argv) < 2:
            print(USAGE)
            sys.exit(1)
        cmd = sys.argv[1]
        if cmd == "create_json":
            if len(sys.argv) < 3:
                print(USAGE)
                sys.exit(1)
            create_json(sys.argv[2])
        elif cmd == "latest":
            latest()
        else:
            print(USAGE)
            sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:
        log_exception("weekly_plan_manager.exception", exc)
        raise


if __name__ == "__main__":
    main()
