# 反卷伙伴 v2

反卷伙伴 v2 是一个只通过扣子主对话运行的 coaching skill。它从 v1 的“日内高频心跳”改成“月锚 + 周规划 + 日校准 + 日复盘”：周日把高耗能决策做透，工作日只做轻量翻账本和复盘沉淀。

## 扣子运行方式

执行反卷任务前必须进入本仓目录：

```bash
cd /Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach
```

4 个扣子日程 description 使用：

- `templates/coze_schedules/10_00_goal_start.md`
- `templates/coze_schedules/14_00_mid_check.md`
- `templates/coze_schedules/18_00_evening_review.md`
- `templates/coze_schedules/sunday_21_00_weekly_planner.md`

每个日程模板都只允许调用统一入口：

```bash
python3 scripts/coze_schedule_runner.py <node>
```

支持节点：`10:00`、`14:00`、`18:00`、`weekly_21:00`。不要在扣子日程里手写 `goal_card_manager.py heartbeat` 参数。

## 内容框架

- `config/my_compass.md`：月锚，月初手动维护。
- `prompts/weekly_planner.md`：周日 21:00 周规划，产出 weekly_plan。
- `prompts/daily_morning.md`：工作日 10:00 日校准。
- `prompts/daily_evening.md`：工作日 18:00 下班复盘。
- `REDESIGN.md`：v2 重构诊断和设计说明。
- `docs/MIGRATION_GUIDE.md`：4 周迁移指南。

## 数据沉淀

- `data/weekly_plans/`：周作战图 JSON。
- `data/daily_reviews/`：每日复盘 markdown。
- `data/business_journal/`：业务观察。
- `data/thinking_gap_journal/`：思维差异。
- `data/goal_cards/`：兼容 v1 的目标卡。
- `data/logs/`：扣子运行日志。

## 渠道规则

- coaching 消息只允许输出到扣子主对话，渠道名固定为 `coze`。
- 日程 description 不得包含外部群聊、机器人地址或 webhook 配置。
- 发布或修改日程前必须运行 `python3 scripts/validate_channels.py`。

## 验证命令

```bash
PYTHONPYCACHEPREFIX=/private/tmp/anti-coach-pycache python3 -m py_compile scripts/goal_card_manager.py scripts/validate_channels.py scripts/runtime_logger.py scripts/coze_schedule_runner.py scripts/weekly_plan_manager.py
ANTI_COACH_LOG_FILE=/private/tmp/anti-coach-validate.jsonl python3 scripts/validate_channels.py
GOAL_CARD_DIR=/tmp/anti-coach-test ANTI_COACH_LOG_FILE=/tmp/anti-coach-runtime.jsonl python3 scripts/coze_schedule_runner.py 10:00
GOAL_CARD_DIR=/tmp/anti-coach-test ANTI_COACH_LOG_FILE=/tmp/anti-coach-runtime.jsonl python3 scripts/coze_schedule_runner.py weekly_21:00
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 14:00 mid_check true mid_check success ok coze
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 14:00 mid_check true mid_check success ok wecom
```

最后一条应该失败，用于确认非 `coze` 渠道被拒绝。

## 运行日志

默认日志路径：`data/logs/anti_coach_runtime.jsonl`。如需避免验证写入仓内日志，可设置：

```bash
ANTI_COACH_LOG_FILE=/tmp/anti-coach-runtime.jsonl
```

如果日志里出现旧目录名 `anti-pretend-effort`，说明扣子没有切到新仓路径，必须先修正日程 description 或工作目录。

## 提交前防串台

```bash
python3 scripts/validate_channels.py
python3 scripts/validate_commit_boundary.py
```

详细规则见 `docs/扣子防串台提交规范.md`。
