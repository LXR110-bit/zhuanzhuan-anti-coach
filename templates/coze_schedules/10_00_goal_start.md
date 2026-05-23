# 反卷教练 10:00 目标澄清

输出渠道：coze_only

执行步骤：
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`。
2. 只运行：`python3 scripts/coze_schedule_runner.py 10:00`。
3. 按返回的 `coach_message` 在扣子主对话输出。
4. 如果返回 `next_step=ask_phase1_five_questions_then_call_goal_card_manager_create`，等主人答完五题后，调用 `python3 scripts/goal_card_manager.py create ...` 写入目标卡。

禁止事项：
- 不要手写 heartbeat 命令。
- 不要发送到任何外部群聊。
- 不要携带任何机器人地址、外部推送地址或群聊配置。
