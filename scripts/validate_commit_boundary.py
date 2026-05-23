#!/usr/bin/env python3
"""Validate staged files stay inside anti-coach repository boundaries."""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

CODE_PREFIXES = (
    "scripts/",
    "config/",
    "policy/",
    "templates/",
    "docs/",
)
CODE_FILES = (
    "README.md",
    "SKILL.md",
    ".gitignore",
)
RAW_LOG_PREFIXES = (
    "data/logs/",
    "logs/",
)
ANTI_RUNTIME_PREFIXES = (
    "data/goal_cards/",
)
MARKET_RUNTIME_PREFIXES = (
    "data/report_cards/",
    "data/trend_history/",
    "data/daily_price_records/",
)
MARKET_RUNTIME_FILES = {
    "data/action_archive.json",
    "data/anomaly_votes.json",
    "data/daily_report_payload.json",
    "data/news_signal_dedupe_history.json",
    "data/news_signals.json",
    "data/news_signals_filtered.json",
    "data/price_cache.json",
    "data/push_status.json",
    "data/validation_report.json",
}
MARKET_CODE_PREFIXES = (
    "行情追踪AI助手/",
    "market-tracker/",
    "zhuanzhuan-AI/",
)
OLD_MONOREPO_PREFIXES = (
    "skills/anti-involution-coach/",
    "skills/anti-pretend-effort/",
)


def staged_files():
    completed = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        return [], completed.stderr.strip() or "git diff --cached failed"
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()], None


def startswith_any(path, prefixes):
    return any(path.startswith(prefix) for prefix in prefixes)


def is_code(path):
    return startswith_any(path, CODE_PREFIXES) or path in CODE_FILES


def is_anti_runtime(path):
    return startswith_any(path, ANTI_RUNTIME_PREFIXES)


def main():
    files, error = staged_files()
    if error:
        print(json.dumps({"ok": False, "error": error}, ensure_ascii=False, indent=2))
        return 2

    violations = []
    raw_logs = [path for path in files if startswith_any(path, RAW_LOG_PREFIXES)]
    market_runtime = [
        path for path in files
        if startswith_any(path, MARKET_RUNTIME_PREFIXES) or path in MARKET_RUNTIME_FILES
    ]
    market_code = [path for path in files if startswith_any(path, MARKET_CODE_PREFIXES)]
    old_monorepo = [path for path in files if startswith_any(path, OLD_MONOREPO_PREFIXES)]
    code_files = [path for path in files if is_code(path)]
    anti_runtime = [path for path in files if is_anti_runtime(path)]

    if raw_logs:
        violations.append({
            "rule": "raw_logs_forbidden",
            "message": "不要提交原始 runtime log；日志只留在 data/logs/ 本地诊断。",
            "files": raw_logs,
        })
    if market_runtime:
        violations.append({
            "rule": "market_runtime_forbidden",
            "message": "反卷教练仓不得提交行情运行数据、日报 payload、news signals、report cards 或 trend history。",
            "files": market_runtime,
        })
    if market_code:
        violations.append({
            "rule": "market_code_forbidden",
            "message": "反卷教练仓不得提交行情代码或行情仓目录。",
            "files": market_code,
        })
    if old_monorepo:
        violations.append({
            "rule": "old_monorepo_skill_path_forbidden",
            "message": "反卷教练独立仓不得再使用旧 mono-repo skills/anti-involution-coach 路径。",
            "files": old_monorepo,
        })
    if code_files and anti_runtime:
        violations.append({
            "rule": "code_runtime_mixed_commit",
            "message": "反卷教练代码/模板变更不得和 goal_cards 运行态混在同一个 commit。",
            "code_files": code_files,
            "runtime_files": anti_runtime,
        })

    result = {
        "ok": not violations,
        "repo": "zhuanzhuan-anti-coach",
        "checked": "staged_files",
        "staged_count": len(files),
        "violations": violations,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
