# 反卷教练 21:00 下班总结

输出渠道：coze_only

执行步骤：
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`。
2. 只运行：`python3 scripts/coze_schedule_runner.py 21:00`。
3. 如果返回 `coach_message` 为空，沉默退出。
4. 如果返回 `next_step=ask_phase3_questions_then_call_goal_card_manager_summary`，按返回的 `coach_message` 追问，并在主人回答后调用 `python3 scripts/goal_card_manager.py summary ...` 写入每日总结。
5. 如果返回“今天没有目标卡，无法做有效总结”，只在扣子主对话输出该句，不补造总结。

禁止事项：
- 不要手写 heartbeat 命令。
- 不要发送到任何外部群聊。
- 不要携带任何机器人地址、外部推送地址或群聊配置。
