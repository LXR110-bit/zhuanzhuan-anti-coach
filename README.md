# 反卷教练

反卷教练是一个只通过扣子主对话运行的 coaching skill。它通过五题澄清、工作段心跳、每日总结和 goal_card JSON 追踪，帮助聚焦可交付产出，避免忙碌式白干。

## 扣子运行方式

扣子仍是单 agent，但执行反卷教练时必须先进入本仓目录：

```bash
cd /Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach
```

6 个扣子日程 description 使用：

- `templates/coze_schedules/10_00_goal_start.md`
- `templates/coze_schedules/12_00_morning_close.md`
- `templates/coze_schedules/13_30_afternoon_start.md`
- `templates/coze_schedules/18_00_dinner_handoff.md`
- `templates/coze_schedules/19_00_evening_start.md`
- `templates/coze_schedules/21_00_daily_close.md`

每个日程模板都只允许调用统一入口：

```bash
python3 scripts/coze_schedule_runner.py <node>
```

不要在扣子日程里手写 `goal_card_manager.py heartbeat` 参数；runner 会自动完成 `status -> heartbeat -> coach_message`，避免参数错位。

## 渠道规则

- coaching 消息只允许输出到扣子主对话，渠道名固定为 `coze`。
- 日程 description 不得包含外部群聊、机器人地址或 webhook 配置。
- 发布或修改日程前必须运行：

```bash
python3 scripts/validate_channels.py
```

## 验证命令

```bash
python3 -m py_compile scripts/goal_card_manager.py scripts/validate_channels.py scripts/runtime_logger.py scripts/coze_schedule_runner.py
python3 scripts/validate_channels.py
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/coze_schedule_runner.py 10:00
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 19:00 heartbeat true evening_start success ok coze
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 19:00 heartbeat true evening_start success ok wecom
```

最后一条应该失败，用于确认非 `coze` 渠道被拒绝。

## 运行日志

脚本会写结构化 JSONL 运行日志，用于排查扣子日程冷启动和渠道污染：

- 默认路径：`data/logs/anti_coach_runtime.jsonl`
- 可用环境变量覆盖：`ANTI_COACH_LOG_FILE=/tmp/anti-coach-runtime.jsonl`
- 每行包含 `ts/event/pid/cwd/argv`，以及命令结果、数据文件路径、渠道拒绝原因或校验结果。
- 默认会脱敏五题答案等命令参数，只保留命令名和参数数量；如需临时排查原始参数，可设置 `ANTI_COACH_LOG_RAW_ARGS=1`。
- `data/logs/` 默认不提交 Git，只用于本地和扣子运行诊断。

常用查看：

```bash
tail -50 data/logs/anti_coach_runtime.jsonl
```

如果日志里出现旧目录名 `anti-pretend-effort`，说明扣子没有切到新仓路径，必须先修正日程 description 或工作目录。

## 提交前防串台

扣子提交前必须执行：

```bash
python3 scripts/validate_channels.py
python3 scripts/validate_commit_boundary.py
```

详细规则见 `docs/扣子防串台提交规范.md`。
