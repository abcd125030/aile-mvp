-- ============================================================
-- 艾乐学伴 MVP — 任务与内容包绑定检查脚本
-- 文件: database/04_check_task_content_binding.sql
-- 说明: 快速检查最近任务是否已绑定 content_package，以及包状态
-- ============================================================

-- 可选: 先切换到目标 schema（默认 public）
SET search_path TO public;

-- 1) 最近 50 条任务的绑定情况
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
LEFT JOIN content_packages cp
  ON cp.id = lt.content_package_id
ORDER BY lt.created_at DESC
LIMIT 50;

-- 2) 汇总统计（可用于看整体健康度）
SELECT
  COUNT(*) AS total_tasks,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NOT NULL) AS tasks_with_content_package_id,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NULL) AS tasks_without_content_package_id,
  COUNT(*) FILTER (WHERE lt.content_package_id IS NOT NULL AND cp.id IS NULL) AS dangling_fk_count,
  COUNT(*) FILTER (WHERE cp.status = 'ready') AS package_ready_count,
  COUNT(*) FILTER (WHERE cp.status = 'generating') AS package_generating_count,
  COUNT(*) FILTER (WHERE cp.status = 'failed') AS package_failed_count
FROM learning_tasks lt
LEFT JOIN content_packages cp
  ON cp.id = lt.content_package_id;

-- 3) 最近 20 条“缺少内容包”的任务（便于排查）
SELECT
  lt.id,
  lt.title,
  lt.type,
  lt.status,
  lt.source,
  lt.source_problem_id,
  lt.knowledge_point_ids,
  lt.created_at
FROM learning_tasks lt
WHERE lt.content_package_id IS NULL
ORDER BY lt.created_at DESC
LIMIT 20;
