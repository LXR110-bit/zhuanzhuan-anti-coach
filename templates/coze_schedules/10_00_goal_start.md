# 反卷伙伴 10:00 日校准

输出渠道：coze_only
预计时长：5-10 分钟

执行步骤：
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`。
2. 只运行：`python3 scripts/coze_schedule_runner.py 10:00`。
3. 按返回的 `coach_message` 在扣子主对话输出。
4. 如果返回 `next_step=ask_daily_morning_calibration`，按 `prompts/daily_morning.md` 走 3 问翻账本流程。
5. 3 问完成后，调用 `python3 scripts/goal_card_manager.py create ...` 写入今日目标卡。

禁止事项：
- 不要手写 heartbeat 命令。
- 不要触发 v1 五题澄清。
- 不要重新做战略决策。
- 不要发送到任何外部群聊。
- 不要携带任何机器人地址、外部推送地址或群聊配置。
