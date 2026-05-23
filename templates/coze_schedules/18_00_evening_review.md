# 反卷伙伴 18:00 下班复盘

输出渠道：coze_only
预计时长：15 分钟

执行步骤：
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`。
2. 只运行：`python3 scripts/coze_schedule_runner.py 18:00`。
3. 如果返回 `coach_message` 为空，沉默退出。
4. 如果返回 `next_step=ask_daily_evening_review`，按返回的 `coach_message` 和 `prompts/daily_evening.md` 走 5 模块复盘。
5. 复盘完成后，调用 `python3 scripts/goal_card_manager.py daily_review ...` 写入今日复盘。

禁止事项：
- 不要手写 heartbeat 命令。
- 不要训斥语气。
- 不要发送到任何外部群聊。
- 不要携带任何机器人地址、外部推送地址或群聊配置。
