#!/usr/bin/env python3
"""Validate anti-involution coach schedule descriptions are Coze-only."""

import json
import sys
from pathlib import Path

from runtime_logger import log_event, log_exception

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT
POLICY_FILE = SKILL_DIR / "policy" / "channel_policy.json"
DEFAULT_SCAN_TARGETS = [
    SKILL_DIR / "templates" / "coze_schedules",
    SKILL_DIR / "config" / "schedule.md",
    SKILL_DIR / "config" / "schema.md",
]
SCHEDULE_TEMPLATE_DIR = SKILL_DIR / "templates" / "coze_schedules"
EXPECTED_SCHEDULE_RUNNER = "python3 scripts/coze_schedule_runner.py"
FORBIDDEN_TEMPLATE_COMMANDS = [
    "scripts/goal_card_manager.py heartbeat",
    "goal_card_manager.py heartbeat",
]
SKIP_FILES = {
    SKILL_DIR / "SKILL.md",
    POLICY_FILE,
}


def load_policy():
    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def expand_targets(args):
    targets = [Path(arg).expanduser() for arg in args] if args else DEFAULT_SCAN_TARGETS
    files = []
    for target in targets:
        path = target if target.is_absolute() else ROOT / target
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.is_file() and p not in SKIP_FILES))
        elif path.is_file():
            if path not in SKIP_FILES:
                files.append(path)
        else:
            print(json.dumps({"ok": False, "error": f"target not found: {target}"}, ensure_ascii=False))
            sys.exit(2)
    return files


def find_violations(files, forbidden_terms):
    violations = []
    lowered_terms = []
    seen_terms = set()
    for term in forbidden_terms:
        lowered = term.lower()
        if lowered in seen_terms:
            continue
        seen_terms.add(lowered)
        lowered_terms.append((term, lowered))
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        lowered_text = text.lower()
        for original, lowered in lowered_terms:
            if lowered in lowered_text:
                violations.append({
                    "file": display_path(file_path),
                    "term": original,
                })
    return violations


def validate_schedule_templates():
    violations = []
    for file_path in sorted(SCHEDULE_TEMPLATE_DIR.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        if EXPECTED_SCHEDULE_RUNNER not in text:
            violations.append({
                "file": display_path(file_path),
                "error": "missing_coze_schedule_runner_command",
            })
        for command in FORBIDDEN_TEMPLATE_COMMANDS:
            if command in text:
                violations.append({
                    "file": display_path(file_path),
                    "error": "template_must_not_call_heartbeat_directly",
                    "term": command,
                })
    return violations


def display_path(file_path):
    try:
        return str(file_path.relative_to(ROOT))
    except ValueError:
        return str(file_path)


def main():
    log_event("validate_channels.start", targets=sys.argv[1:] or [display_path(path) for path in DEFAULT_SCAN_TARGETS])
    try:
        policy = load_policy()
        files = expand_targets(sys.argv[1:])
        violations = find_violations(files, policy["forbidden_terms"] + policy["forbidden_output_channels"])
        template_violations = validate_schedule_templates() if not sys.argv[1:] else []
        violations.extend(template_violations)
        if violations:
            log_event("validate_channels.failed", ok=False, checked_files=[display_path(path) for path in files], violations=violations)
            print(json.dumps({
                "ok": False,
                "error": "anti-involution coach channel pollution detected",
                "violations": violations,
            }, ensure_ascii=False, indent=2))
            sys.exit(1)
        result = {
            "ok": True,
            "checked_files": [display_path(path) for path in files],
            "allowed_output_channels": policy["allowed_output_channels"],
        }
        log_event("validate_channels.done", **result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except SystemExit:
        raise
    except Exception as exc:
        log_exception("validate_channels.exception", exc)
        raise


if __name__ == "__main__":
    main()
