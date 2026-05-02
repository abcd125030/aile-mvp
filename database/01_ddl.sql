-- ============================================================
-- 艾乐学伴 MVP — DDL 建表脚本
-- 文件: database/01_ddl.sql
-- 说明: 创建扩展、9 张业务表、索引、触发器、视图
-- ============================================================

-- 1. 启用扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 2. 创建业务表（按外键依赖顺序）
-- ============================================================

-- 2.1 knowledge_points（无外键依赖）
CREATE TABLE IF NOT EXISTS knowledge_points (
    id              VARCHAR(50)     PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL,
    description     TEXT,
    prerequisite_ids JSONB          NOT NULL DEFAULT '[]',
    difficulty      NUMERIC(3,2)    NOT NULL DEFAULT 0.5,
    subject         VARCHAR(20)     NOT NULL DEFAULT 'math',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.2 exercise_items（无外键依赖）
CREATE TABLE IF NOT EXISTS exercise_items (
    id                  VARCHAR(50)     PRIMARY KEY,
    stem                TEXT            NOT NULL,
    options             JSONB,
    correct_answer      VARCHAR(500)    NOT NULL,
    solution            TEXT,
    knowledge_point_ids JSONB           NOT NULL DEFAULT '[]',
    difficulty          NUMERIC(3,2)    NOT NULL DEFAULT 0.5,
    metadata            JSONB           NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.3 users（current_plan_id 外键延迟添加）
CREATE TABLE IF NOT EXISTS users (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    phone               VARCHAR(20)     UNIQUE,
    avatar_url          TEXT,
    nickname            VARCHAR(50)     NOT NULL DEFAULT '',
    grade               VARCHAR(10)     NOT NULL,
    textbook_version    VARCHAR(50)     NOT NULL DEFAULT '人教版A版',
    settings            JSONB           NOT NULL DEFAULT '{}',
    current_plan_id     UUID,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.4 learning_plans（依赖 users）
CREATE TABLE IF NOT EXISTS learning_plans (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200)    NOT NULL,
    status      VARCHAR(20)     NOT NULL DEFAULT 'active',
    version     INTEGER         NOT NULL DEFAULT 1,
    snapshot    JSONB,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.5 daily_problems（依赖 users；resolution_task_id 延迟添加）
CREATE TABLE IF NOT EXISTS daily_problems (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID            NOT NULL REFERENCES users(id),
    session_id          UUID            NOT NULL,
    original_utterance  TEXT            NOT NULL,
    clarified_question  TEXT,
    intent              VARCHAR(100)    NOT NULL,
    slots               JSONB           NOT NULL DEFAULT '{}',
    resolution_type     VARCHAR(50),
    resolution_task_id  UUID,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.6 content_packages（延迟外键：associated_task_id, associated_problem_id）
CREATE TABLE IF NOT EXISTS content_packages (
    id                      UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    production_job_id       VARCHAR(100),
    status                  VARCHAR(20)     NOT NULL DEFAULT 'generating',
    manifest                JSONB           NOT NULL,
    associated_task_id      UUID,
    associated_problem_id   UUID,
    created_at              TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.7 learning_tasks（依赖 learning_plans, daily_problems, content_packages）
CREATE TABLE IF NOT EXISTS learning_tasks (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id             UUID            NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    title               VARCHAR(200)    NOT NULL,
    type                VARCHAR(50)     NOT NULL,
    status              VARCHAR(20)     NOT NULL DEFAULT 'pending',
    source              VARCHAR(50)     NOT NULL DEFAULT 'scheduled',
    source_problem_id   UUID            REFERENCES daily_problems(id) ON DELETE SET NULL,
    knowledge_point_ids JSONB           NOT NULL DEFAULT '[]',
    content_package_id  UUID            REFERENCES content_packages(id) ON DELETE SET NULL,
    metadata            JSONB           NOT NULL DEFAULT '{}',
    due_at              TIMESTAMPTZ,
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.8 diagnosis_reports（依赖 users, learning_plans）
CREATE TABLE IF NOT EXISTS diagnosis_reports (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID            NOT NULL REFERENCES users(id),
    title               VARCHAR(200)    NOT NULL,
    original_file_url   TEXT,
    summary             JSONB           NOT NULL,
    detailed_analysis   JSONB           NOT NULL,
    generated_plan_id   UUID            REFERENCES learning_plans(id),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.9 user_behavior_events（依赖 users）
CREATE TABLE IF NOT EXISTS user_behavior_events (
    id          BIGSERIAL       PRIMARY KEY,
    user_id     UUID            NOT NULL REFERENCES users(id),
    session_id  VARCHAR(100)    NOT NULL,
    event_type  VARCHAR(50)     NOT NULL,
    event_data  JSONB           NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. 添加延迟外键
-- ============================================================

-- users.current_plan_id → learning_plans(id)
ALTER TABLE users
    ADD CONSTRAINT fk_users_current_plan
    FOREIGN KEY (current_plan_id) REFERENCES learning_plans(id)
    ON DELETE SET NULL;

-- content_packages.associated_task_id → learning_tasks(id)
ALTER TABLE content_packages
    ADD CONSTRAINT fk_content_packages_task
    FOREIGN KEY (associated_task_id) REFERENCES learning_tasks(id);

-- content_packages.associated_problem_id → daily_problems(id)
ALTER TABLE content_packages
    ADD CONSTRAINT fk_content_packages_problem
    FOREIGN KEY (associated_problem_id) REFERENCES daily_problems(id);

-- daily_problems.resolution_task_id → learning_tasks(id)
ALTER TABLE daily_problems
    ADD CONSTRAINT fk_daily_problems_resolution_task
    FOREIGN KEY (resolution_task_id) REFERENCES learning_tasks(id);

-- ============================================================
-- 4. 创建索引
-- ============================================================

-- users 索引
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_phone
    ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_grade
    ON users(grade);

-- learning_plans 复合索引
CREATE INDEX IF NOT EXISTS idx_learning_plans_user_status
    ON learning_plans(user_id, status);

-- learning_tasks 索引
CREATE INDEX IF NOT EXISTS idx_learning_tasks_status
    ON learning_tasks(status);
CREATE INDEX IF NOT EXISTS idx_learning_tasks_due_at
    ON learning_tasks(due_at);

-- daily_problems 索引
CREATE INDEX IF NOT EXISTS idx_daily_problems_session_id
    ON daily_problems(session_id);
CREATE INDEX IF NOT EXISTS idx_daily_problems_intent
    ON daily_problems(intent);

-- user_behavior_events 索引
CREATE INDEX IF NOT EXISTS idx_user_behavior_events_session_id
    ON user_behavior_events(session_id);
CREATE INDEX IF NOT EXISTS idx_user_behavior_events_event_type
    ON user_behavior_events(event_type);

-- ============================================================
-- 5. 创建触发器函数和触发器
-- ============================================================

-- 通用触发器函数：自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 为 users 表挂载触发器
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- 为 learning_plans 表挂载触发器
DROP TRIGGER IF EXISTS trg_learning_plans_updated_at ON learning_plans;
CREATE TRIGGER trg_learning_plans_updated_at
    BEFORE UPDATE ON learning_plans
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- 为 content_packages 表挂载触发器
DROP TRIGGER IF EXISTS trg_content_packages_updated_at ON content_packages;
CREATE TRIGGER trg_content_packages_updated_at
    BEFORE UPDATE ON content_packages
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();

-- ============================================================
-- 6. 创建视图
-- ============================================================

-- 视图: v_user_current_learning_context
-- 展示用户当前学习上下文（用户信息、当前计划、待办任务数、进行中任务数、最近3个活跃任务）
CREATE OR REPLACE VIEW v_user_current_learning_context AS
SELECT
    u.id AS user_id,
    u.nickname,
    u.grade,
    u.textbook_version,
    lp.id AS current_plan_id,
    lp.title AS current_plan_title,
    lp.status AS current_plan_status,
    COALESCE(pending_counts.pending_count, 0) AS pending_task_count,
    COALESCE(progress_counts.in_progress_count, 0) AS in_progress_task_count,
    recent_tasks.recent_active_tasks
FROM users u
LEFT JOIN learning_plans lp ON u.current_plan_id = lp.id
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS pending_count
    FROM learning_tasks lt
    WHERE lt.plan_id = lp.id AND lt.status = 'pending'
) pending_counts ON TRUE
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS in_progress_count
    FROM learning_tasks lt
    WHERE lt.plan_id = lp.id AND lt.status = 'in_progress'
) progress_counts ON TRUE
LEFT JOIN LATERAL (
    SELECT COALESCE(
        json_agg(
            json_build_object(
                'id', lt.id,
                'title', lt.title,
                'type', lt.type,
                'status', lt.status,
                'due_at', lt.due_at
            ) ORDER BY lt.created_at DESC
        ) FILTER (WHERE lt.id IS NOT NULL),
        '[]'::json
    ) AS recent_active_tasks
    FROM (
        SELECT lt2.*
        FROM learning_tasks lt2
        WHERE lt2.plan_id = lp.id
          AND lt2.status IN ('pending', 'in_progress')
        ORDER BY lt2.created_at DESC
        LIMIT 3
    ) lt
) recent_tasks ON TRUE;

-- 视图: v_daily_problems_with_resolution
-- 展示日清问题及其关联的解决任务信息
CREATE OR REPLACE VIEW v_daily_problems_with_resolution AS
SELECT
    dp.id AS problem_id,
    dp.user_id,
    dp.session_id,
    dp.original_utterance,
    dp.clarified_question,
    dp.intent,
    dp.slots,
    dp.resolution_type,
    dp.resolution_task_id,
    dp.created_at AS problem_created_at,
    lt.id AS task_id,
    lt.title AS task_title,
    lt.type AS task_type,
    lt.status AS task_status,
    lt.completed_at AS task_completed_at
FROM daily_problems dp
LEFT JOIN learning_tasks lt ON dp.resolution_task_id = lt.id;
