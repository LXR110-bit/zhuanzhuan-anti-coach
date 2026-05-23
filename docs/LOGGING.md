# 反卷伙伴 v2 日志说明

## 日志分层

反卷伙伴 v2 默认写 3 份 JSONL 日志，全部位于 `data/logs/`，用于诊断，不随代码提交。

| 文件 | 用途 | 主要看什么 |
|------|------|------------|
| `anti_coach_runtime.jsonl` | 脚本运行细节 | 命令、cwd、参数数量、异常堆栈 |
| `anti_coach_stability.jsonl` | 代码和调度稳定性 | `ok=false`、路径错误、渠道拒绝、命令失败 |
| `anti_coach_usage.jsonl` | 日常使用情况 | 节点是否触发、目标卡/周计划/日复盘是否写入 |

## 常用判断

- 扣子没有提醒：先看 `anti_coach_stability.jsonl` 是否有 `path_check_failed` 或命令失败。
- 提醒了但没有进入流程：看 `anti_coach_usage.jsonl` 的 `active_card_found`、`push_status`、`next_step`。
- 用户没跟上：看 `anti_coach_usage.jsonl` 是否只有 `node_triggered`，没有后续 `goal_card_created`、`daily_review_created` 或 `weekly_plan_created`。
- 代码异常：看 `anti_coach_runtime.jsonl` 和 `anti_coach_stability.jsonl` 的 `ok=false`、`error_type`、`traceback`。

## 环境变量

验证或测试时建议把日志写到 `/tmp`，避免污染仓内日志：

```bash
ANTI_COACH_LOG_FILE=/tmp/anti-coach-runtime.jsonl
ANTI_COACH_STABILITY_LOG_FILE=/tmp/anti-coach-stability.jsonl
ANTI_COACH_USAGE_LOG_FILE=/tmp/anti-coach-usage.jsonl
```

## 提交规则

- 代码、模板、文档可以正常提交。
- `data/logs/` 不和代码混在同一个 commit。
- 需要让我诊断日志时，单独打包或单独提交日志。
