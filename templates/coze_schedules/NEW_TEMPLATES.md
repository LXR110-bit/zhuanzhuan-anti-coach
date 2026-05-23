# 反卷伙伴 v2 - 4 个 Coze 节点模板

## 模板 1:10:00 日校准

```markdown
# 反卷伙伴 10:00 日校准

输出渠道:coze_only
预计时长:5-10 分钟

执行步骤:
1. 进入 `/Users/lilixiaoran/工作/转转/zhuanzhuan-anti-coach`
2. 只运行 `python3 scripts/coze_schedule_runner.py 10:00`
3. 按返回的 `coach_message` 和 `prompts/daily_morning.md` 走 3 问翻账本流程
4. 完成后调用 `goal_card_manager.py create` 写入今日 goal_card

禁止事项:
- 不要发送到任何外部群聊
- 不要携带任何机器人地址、外部推送地址或群聊配置
- **不要重新做战略决策**——只翻账本,5-10 分钟必须结束
- **不要触发 Phase1 五题**——v1 流程已废弃
```

## 模板 2:14:00 中段感知(可选)

```markdown
# 反卷伙伴 14:00 中段感知

输出渠道:coze_only
预计时长:3 分钟,可跳过

执行步骤:
1. 进入工作目录
2. 只运行 `python3 scripts/coze_schedule_runner.py 14:00`
3. 如返回 `coach_message` 为空 → 沉默退出
4. 如返回 `coach_message` 不为空,只问 2 个问题:
   - "上午 3 件必做完成了几件?"
   - "今天有没有看到什么业务异常或新数据?(1 个就够)"
6. 把业务观察追加到 `data/business_journal/[今天日期].md`

禁止事项:
- 不要追问、不要"刚才半小时干了什么"那种 v1 心跳
- 用户 5 分钟没回应 → 沉默退出,不重复打扰
- 3 分钟必须结束
```

## 模板 3:18:00 下班复盘(核心)

```markdown
# 反卷伙伴 18:00 下班复盘

输出渠道:coze_only
预计时长:15 分钟(必须完成)

执行步骤:
1. 进入工作目录
2. 只运行 `python3 scripts/coze_schedule_runner.py 18:00`
3. 按 `prompts/daily_evening.md` 走 5 模块流程:
   - 模块 1:今日结果(2 分钟)
   - 模块 2:业务观察(3 分钟,必填)
   - 模块 3:思维差异(3 分钟,必填)
   - 模块 4:明日大块(3 分钟)
   - 模块 5:一句话总结(1 分钟)
4. 写入:
   - `goal_card_manager.py daily_review` 写主结构
   - 追加 `data/business_journal/[date].md`
   - 追加 `data/thinking_gap_journal/[date].md`
   - 创建 `data/goal_cards/[明天日期].json` 预录入(明早直接复用)

异常处理:
- 用户说"今天太累了" → 简化版:只走模块 1 + 4(结果 + 明日)
- 用户开始自我攻击 → 打断泛化,逼回具体事件
- 用户开始大段重排全周计划 → 拦住,标记"下周重做规划"

禁止事项:
- 不要"加油""明天会更好"这类鼓励性废话
- 不要训斥语气
- 必须捕捉 1 个业务观察 + 1 个思维差异(这是长线复利)
```

## 模板 4:周日 21:00 周规划

```markdown
# 反卷伙伴 周日 21:00 周规划

输出渠道:coze_only
预计时长:60-90 分钟(本周唯一允许的高耗能时段)

执行步骤:
1. 进入工作目录
2. 只运行 `python3 scripts/coze_schedule_runner.py weekly_21:00`
3. 按 `prompts/weekly_planner.md` 走 6 阶段流程:
   - 阶段 1:上周回看(10 分钟)
   - 阶段 2:本周关键结果(15 分钟)
   - 阶段 3:任务清单(20 分钟)
   - 阶段 4:取舍(10 分钟,强制)
   - 阶段 5:保护时段(10 分钟,强制)
   - 阶段 6:每日大块(15 分钟)
4. 调用 `python3 scripts/weekly_plan_manager.py create_json '<weekly_plan_json>'` 写入 `data/weekly_plans/[本周周一日期].json`,成为下周日 Agent 的依据

异常处理:
- 用户说"今天太累简化点" → 允许跳过阶段 1/3/6,但**必须完成阶段 2/4/5**(关键结果、取舍、保护时段)
- 用户说"先不想了改天" → 提醒一句:"没有 weekly_plan,下周日 Agent 又会让你每天从零。你确定?"
- 用户反复绕过阶段 4 取舍 → **必须顶住**——这是整个系统的杠杆点

禁止事项:
- 不要在这一节点之外触发周规划
- 不要让日 Agent 染指任何战略决策
```

## 被废弃的 v1 模板(需删除)

以下 6 个 v1 模板**全部废弃**:
- ❌ `templates/coze_schedules/10_00_goal_start.md`(逻辑保留但 prompt 重写)
- ❌ `templates/coze_schedules/12_00_morning_close.md`(完全删除)
- ❌ `templates/coze_schedules/13_30_afternoon_start.md`(完全删除)
- ❌ `templates/coze_schedules/18_00_dinner_handoff.md`(逻辑重写为 18:00 下班复盘)
- ❌ `templates/coze_schedules/19_00_evening_start.md`(完全删除)
- ❌ `templates/coze_schedules/21_00_daily_close.md`(完全删除,周日 21:00 节点取代)

被废弃的还有所有 30 分钟心跳触发(10:30 / 11:00 / 11:30 / 14:00 系列 / 19:30 系列等)。

## Coze 配置变更摘要

| 旧定时器 | 新定时器 | 变更 |
|---------|---------|------|
| 10:00 工作日 | 10:00 工作日 | prompt 更新 |
| 10:30-17:30 30 分钟心跳 | (删除) | 全砍 |
| 12:00 工作日 | (删除) | 砍 |
| 13:30 工作日 | (删除) | 砍 |
| 18:00 工作日 | 14:00 工作日(新增) | 中段感知 |
| 19:00 工作日 | 18:00 工作日(改义) | 下班复盘 |
| 19:30-20:30 30 分钟心跳 | (删除) | 全砍 |
| 21:00 工作日 | (删除) | 砍 |
| (无) | **周日 21:00(新增)** | 周规划 |
