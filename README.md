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

## 渠道规则

- coaching 消息只允许输出到扣子主对话，渠道名固定为 `coze`。
- 日程 description 不得包含外部群聊、机器人地址或 webhook 配置。
- 发布或修改日程前必须运行：

```bash
python3 scripts/validate_channels.py
```

## 验证命令

```bash
python3 -m py_compile scripts/goal_card_manager.py scripts/validate_channels.py
python3 scripts/validate_channels.py
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 19:00 heartbeat true evening_start success ok coze
GOAL_CARD_DIR=/tmp/anti-coach-test python3 scripts/goal_card_manager.py heartbeat 19:00 heartbeat true evening_start success ok wecom
```

最后一条应该失败，用于确认非 `coze` 渠道被拒绝。
