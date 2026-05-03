-- ============================================================
-- 艾乐学伴 MVP — 按用户检查任务与内容包绑定脚本
-- 文件: database/05_check_task_content_binding_by_user.sql
-- 说明: 通过 user_id 查看该用户最近任务是否已绑定 content_package
-- ============================================================

SET search_path TO public;

-- 用你要排查的用户 ID 替换这里
-- 示例: 'a0000000-0000-0000-0000-000000000001'
WITH target_user AS (
  SELECT CAST('a0000000-0000-0000-0000-000000000001' AS uuid) AS user_id
)

-- 1) 该用户最近 50 条任务绑定明细
SELECT
  lt.id AS task_id,
  lt.title AS task_title,
  lt.type AS task_type,
  lt.status AS task_status,
  lt.source AS task_source,
  lt.created_at AS task_created_at,
  lt.content_package_id,
  cp.status AS content_package_status,
  cp.associated_task_id,
  cp.associated_problem_id,
  cp.created_at AS package_created_at,
  CASE
    WHEN lt.content_package_id IS NULL THEN 'missing'
    WHEN cp.id IS NULL THEN 'dangling_fk'
    WHEN cp.status = 'ready' THEN 'ok_ready'
    WHEN cp.status = 'generating' THEN 'pending_generation'
    WHEN cp.status = 'failed' THEN 'generation_failed'
    ELSE 'unknown'
  END AS binding_health
FROM learning_tasks lt
JOIN learning_plans lp
  ON lp.id = lt.plan_id
LEFT JOIN content_packages cp
  ON cp.id = lt.content_package_id
JOIN target_user tu
  ON lp.user_id = tu.user_id
ORDER BY lt.created_at DESC
LIMIT 50;

-- 2) 该用户汇总统计
WITH target_user AS (
  SELECT CAST('a0000000-0000-0000-0000-000000000001' AS uuid) AS user_id
)
SELECT
  COUNT(*) AS total_tasks,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NOT NULL) AS tasks_with_content_package_id,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NULL) AS tasks_without_content_package_id,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NOT NULL AND cp.id IS NULL) AS dangling_fk_count,
  COUNT(*) FILTER (WHERE cp.status = 'ready') AS package_ready_count,
  COUNT(*) FILTER (WHERE cp.status = 'generating') AS package_generating_count,
  COUNT(*) FILTER (WHERE cp.status = 'failed') AS package_failed_count
FROM learning_tasks lt
JOIN learning_plans lp
  ON lp.id = lt.plan_id
LEFT JOIN content_packages cp
  ON cp.id = lt.content_package_id
JOIN target_user tu
  ON lp.user_id = tu.user_id;
