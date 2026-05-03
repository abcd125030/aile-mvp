-- ============================================================
-- 艾乐学伴 MVP Day 6 — 演示场景补充种子数据
-- 文件: database/03_day6_demo_seed.sql
-- 说明: 场景 A/B/C 的演示数据，支持可重复执行
-- ============================================================

-- 场景 A：新用户首次使用（画像 + 计划）
UPDATE users
SET
  grade = '高二',
  textbook_version = '人教版A版',
  nickname = COALESCE(NULLIF(nickname, ''), '艾学同学'),
  settings = COALESCE(settings, '{}'::jsonb) || '{"target_score_gap": 28, "exam_countdown_days": 210}'::jsonb
WHERE id = 'a0000000-0000-0000-0000-000000000001';

-- 场景 B：日清核心卖点（固定话语 -> 任务）
INSERT INTO daily_problems (
  id,
  user_id,
  session_id,
  original_utterance,
  clarified_question,
  intent,
  slots,
  resolution_type,
  resolution_task_id
) VALUES (
  'd0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  '00000000-0000-0000-0000-00000000d601',
  '今天数学课讲了三角函数，有个地方没听懂',
  '我不清楚正弦函数定义中角与函数值的对应关系',
  'CLARIFY_CONCEPT',
  '{"knowledge_point_ids": ["kp_sin_func"], "subject": "math"}'::jsonb,
  'task_created',
  'c0000000-0000-0000-0000-000000000003'
)
ON CONFLICT (id) DO NOTHING;

UPDATE learning_tasks
SET
  source = 'daily_clearance',
  source_problem_id = 'd0000000-0000-0000-0000-000000000001',
  metadata = COALESCE(metadata, '{}'::jsonb) || '{"estimated_minutes": 18, "demo_scene": "B"}'::jsonb
WHERE id = 'c0000000-0000-0000-0000-000000000003';

-- 场景 C：诊断报告（薄弱点 + 计划关联）
INSERT INTO diagnosis_reports (
  id,
  user_id,
  title,
  original_file_url,
  summary,
  detailed_analysis,
  generated_plan_id
) VALUES (
  'e0000000-0000-0000-0000-000000000001',
  'a0000000-0000-0000-0000-000000000001',
  '高二数学阶段诊断报告（演示）',
  'demo://day6/exam-paper',
  '{"total_score": 78, "total_points": 100, "knowledge_weaknesses": ["kp_sin_func", "kp_derivative_basic", "kp_func_mono"]}'::jsonb,
  '{"items": [{"item_index": 3, "is_correct": false, "knowledge_point_ids": ["kp_sin_func"], "error_type": "concept_confusion"}], "knowledge_summary": {"kp_sin_func": {"mastery": 0.35, "recommendation": "优先回顾定义域与图像周期"}, "kp_derivative_basic": {"mastery": 0.42, "recommendation": "强化乘除与链式法则"}, "kp_func_mono": {"mastery": 0.48, "recommendation": "结合导数符号做区间判定"}}}'::jsonb,
  'b0000000-0000-0000-0000-000000000001'
)
ON CONFLICT (id) DO NOTHING;
