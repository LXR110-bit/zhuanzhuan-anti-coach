# 反卷伙伴 周日 21:00 周规划

输出渠道：coze_only
预计时长：60-90 分钟

执行步骤：
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`。
2. 只运行：`python3 scripts/coze_schedule_runner.py weekly_21:00`。
3. 按返回的 `coach_message` 和 `prompts/weekly_planner.md` 走 6 阶段周规划。
4. 周规划完成后，调用 `python3 scripts/weekly_plan_manager.py create_json '<weekly_plan_json>'` 写入 `data/weekly_plans/`。

禁止事项：
- 不要手写 heartbeat 命令。
- 不要在工作日 21:00 触发周规划。
- 不要发送到任何外部群聊。
- 不要携带任何机器人地址、外部推送地址或群聊配置。
