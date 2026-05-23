#!/usr/bin/env python3
"""Structured runtime logging for anti-coach Coze schedules."""

import json
import os
import sys
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path


CST = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_FILE = ROOT / "data" / "logs" / "anti_coach_runtime.jsonl"
DEFAULT_STABILITY_LOG_FILE = ROOT / "data" / "logs" / "anti_coach_stability.jsonl"
DEFAULT_USAGE_LOG_FILE = ROOT / "data" / "logs" / "anti_coach_usage.jsonl"


def now_iso():
    return datetime.now(CST).isoformat()


def runtime_log_file():
    override = os.environ.get("ANTI_COACH_LOG_FILE")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_LOG_FILE


def stability_log_file():
    override = os.environ.get("ANTI_COACH_STABILITY_LOG_FILE")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_STABILITY_LOG_FILE


def usage_log_file():
    override = os.environ.get("ANTI_COACH_USAGE_LOG_FILE")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_USAGE_LOG_FILE


def _json_safe(value):
    try:
        json.dumps(value, ensure_ascii=False)
        return value
    except TypeError:
        return str(value)


def safe_argv():
    if os.environ.get("ANTI_COACH_LOG_RAW_ARGS") == "1":
        return sys.argv
    if len(sys.argv) <= 2:
        return sys.argv
    return sys.argv[:2] + [f"<{len(sys.argv) - 2} args redacted>"]


def base_record(event, log_type, **fields):
    record = {
        "ts": now_iso(),
        "log_type": log_type,
        "event": event,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
        "argv": safe_argv(),
        "arg_count": max(len(sys.argv) - 2, 0),
    }
    for key, value in fields.items():
        record[key] = _json_safe(value)
    return record


def write_jsonl(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def log_event(event, **fields):
    write_jsonl(runtime_log_file(), base_record(event, "runtime", **fields))


def log_stability(event, **fields):
    write_jsonl(stability_log_file(), base_record(event, "stability", **fields))


def log_usage(event, **fields):
    write_jsonl(usage_log_file(), base_record(event, "usage", **fields))


def log_exception(event, exc):
    fields = {
        "ok": False,
        "error": str(exc),
        "error_type": exc.__class__.__name__,
        "traceback": traceback.format_exc(limit=8),
    }
    log_event(event, **fields)
    log_stability(event, **fields)
