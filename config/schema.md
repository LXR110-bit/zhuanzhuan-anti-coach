# Schema

## goal_cards

One day can contain multiple goal cards, but the manager enforces that only one can be active at a time.

Required fields:
- `card_date`: Local date in Asia/Shanghai, formatted as `YYYY-MM-DD`.
- `card_index`: 1-based index within the day.
- `boss_want`: What the boss/user actually wants (Q1).
- `deliverable`: The most important deliverable today (Q2).
- `min_version`: The minimum viable shape of the deliverable (Q3).
- `deadline`: Deadline or expected handoff time.
- `trap_forecast`: What would make today wasted (Q4).
- `first_cut`: The first concrete cut to start with (Q5).
- `status`: One of `active`, `completed`, `abandoned`.

Recommended future fields:
- `deliverable_acceptance`: What counts as done.
- `next_30min_action`: The next concrete action.

## reviews

Each review must belong to an existing goal card. The manager rejects orphan reviews.

Required fields:
- `card_date`: Local date in Asia/Shanghai.
- `card_index`: Related goal card index.
- `review_index`: 1-based index for this card.
- `did_what`: Actual concrete action in the last block.
- `output`: Usable output or evidence.
- `verdict`: One of `在轨`, `跑偏`, `伪装忙碌`.
- `reason`: Why this verdict was chosen.
- `next_action`: Next concrete action.

Recommended future field:
- `output_evidence`: Link, file, message, table, draft, or other proof that output exists.

## daily_summaries

Daily summary is created at 21:00 or when the user explicitly asks to close the day.

Required fields:
- `summary_date`: Local date in Asia/Shanghai.
- `summary_index`: 1-based index within the day.
- `final_output`: What was finally delivered.
- `goal_delta`: Gap between morning goal and actual result.
- `pretend_effort`: Most obvious fake-effort segment.
- `effective_action`: Action that truly moved output forward.
- `verdict`: One of `有效推进`, `部分推进`, `假装努力`.
- `tomorrow_first_cut`: First concrete action for tomorrow.
- `coach_note`: Short coach summary, under 200 Chinese characters when possible.

## weekly_plans

Weekly plan is created on Sunday 21:00 or Monday morning before work. It is stored as `data/weekly_plans/{week_start}.json` and becomes the source of truth for daily calibration.

Required fields:
- `week_start`: Monday date in Asia/Shanghai, formatted as `YYYY-MM-DD`.
- `key_results`: Up to 3 weekly outcomes with role, minimum version, and deadline.
- `task_buckets`: Major work blocks with estimated hours.
- `cuts`: What is killed, simplified, or delegated this week.
- `protected_slots`: Important-but-not-urgent time blocks.
- `daily_blocks`: Planned deep/collaboration/execution blocks by weekday.
- `growth_focus_this_week`: How the monthly compass becomes action this week.

## daily_reviews

Daily review is created at 18:00 and stored as markdown in `data/daily_reviews/{YYYY-MM-DD}.md`.

Required fields:
- `results_completed`: Completion of the morning top 3.
- `business_observation`: One concrete data/user/business observation.
- `thinking_gap`: One gap between current working style and boss/higher-level perspective.
- `tomorrow_top_3`: Tomorrow's top 3 blocks.
- `one_line_summary`: One sentence worth remembering.

The same run also appends:
- `data/business_journal/{YYYY-MM-DD}.md`
- `data/thinking_gap_journal/{YYYY-MM-DD}.md`

## heartbeat_logs

Diagnostic layer for external scheduler (e.g. Coze) heartbeats. Every heartbeat MUST write a log entry, even if it skips action. The manager validates `event_type`, `active_card_found`, and `push_status`.

Required fields:
- `heartbeat_time`: Local timestamp.
- `node`: Schedule node, such as `10:00`, `14:00`, `18:00`, `weekly_21:00`.
- `event_type`: One of `goal_start`, `heartbeat`, `segment_close`, `daily_close`, `mid_check`, `weekly_plan`.
- `goal_card_path`: JSON file path used by the run.
- `active_card_found`: Boolean.
- `action_taken`: What the run attempted.
- `push_status`: One of `success`, `failed`, `skipped`, `unknown`.
- `reason`: Why it succeeded, failed, or skipped.
- `output_channel`: Must be `coze`. Coaching messages reject every other output channel.

## runtime logs

Runtime logs are JSONL files under `data/logs/`. They are diagnostic artifacts and must not be committed with code.

- `anti_coach_runtime.jsonl`: low-level script execution, command args, cwd, file paths, exceptions.
- `anti_coach_stability.jsonl`: code and scheduler stability, including command success/failure, path checks, channel rejection, runner completion.
- `anti_coach_usage.jsonl`: user/product usage, including node triggers, goal cards created, weekly plans created, daily reviews written, summaries created.

Environment overrides:
- `ANTI_COACH_LOG_FILE`
- `ANTI_COACH_STABILITY_LOG_FILE`
- `ANTI_COACH_USAGE_LOG_FILE`
