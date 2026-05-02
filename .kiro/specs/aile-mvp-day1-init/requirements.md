# 需求文档：艾乐学伴 MVP Day 1 — 项目初始化与基础设施落地

## 简介

本文档定义艾乐学伴 MVP Demo 7天冲刺计划中 Day 1 的全部交付需求。Day 1 的核心目标是完成项目骨架搭建、数据库建表与种子数据填充、后端 FastAPI 基础框架初始化、前端 React 基础框架初始化，以及 Docker Compose 一键编排，使整个技术栈可端到端启动运行。

交付标准：Docker Compose 一键启动后，前端页面可访问，后端健康检查接口返回正常，数据库中包含完整的种子数据。

## 术语表

- **Monorepo**：单一代码仓库，包含前端、后端、数据库脚本等所有子项目
- **Docker_Compose**：Docker 容器编排工具，通过 YAML 文件定义多容器应用
- **FastAPI_App**：基于 Python FastAPI 框架的后端应用服务
- **React_App**：基于 React 18 + TypeScript + Vite 的前端应用
- **PostgreSQL_DB**：PostgreSQL 15 关系型数据库实例
- **Redis_Cache**：Redis 缓存服务实例
- **SQLAlchemy_ORM**：Python SQLAlchemy 2.x 对象关系映射层
- **Health_Check_Endpoint**：后端健康检查 HTTP 接口 `GET /health`
- **Seed_Data_Script**：数据库种子数据 SQL 脚本
- **DDL_Script**：数据库建表 SQL 脚本（含表、索引、外键、视图、触发器）
- **API_Client**：前端封装的 axios HTTP 请求客户端
- **Layout_Component**：前端基础布局组件，包含页面公共结构

## 需求

### 需求 1：Monorepo 项目结构创建

**用户故事：** 作为开发者，我希望有一个清晰的 monorepo 项目结构，以便前端、后端、数据库脚本各自独立管理且统一版本控制。

#### 验收标准

1. THE Monorepo SHALL 包含以下顶层目录结构：`frontend/`（React 应用）、`backend/`（FastAPI 应用）、`database/`（SQL 脚本）、`docker-compose.yml`、`README.md`
2. THE Monorepo SHALL 在根目录包含 `README.md` 文件，其中说明项目概述、技术栈、启动方式和演示账号信息
3. THE Monorepo SHALL 在根目录包含 `.gitignore` 文件，排除 `node_modules/`、`__pycache__/`、`.env`、`venv/` 等常见临时文件

### 需求 2：Docker Compose 容器编排

**用户故事：** 作为开发者，我希望通过一条 `docker-compose up` 命令启动全部服务（数据库、缓存、后端、前端），以便快速搭建本地开发环境。

#### 验收标准

1. THE Docker_Compose SHALL 定义四个服务：`postgres`（PostgreSQL 15）、`redis`（Redis）、`backend`（FastAPI_App）、`frontend`（React_App）
2. THE Docker_Compose SHALL 为 PostgreSQL_DB 配置持久化数据卷，防止容器重启后数据丢失
3. THE Docker_Compose SHALL 为 PostgreSQL_DB 配置环境变量：数据库名称 `aile_mvp`、用户名 `postgres`、密码通过环境变量传入
4. THE Docker_Compose SHALL 为 Redis_Cache 暴露默认端口 6379
5. THE Docker_Compose SHALL 配置 `backend` 服务依赖 `postgres` 和 `redis`，确保数据库和缓存先于后端启动
6. THE Docker_Compose SHALL 配置 `frontend` 服务依赖 `backend`，确保后端先于前端启动
7. WHEN `docker-compose up` 命令执行完成后，THE Docker_Compose SHALL 使所有四个服务处于运行状态
8. THE Docker_Compose SHALL 将 PostgreSQL_DB 的 `database/` 目录下的初始化 SQL 脚本挂载到容器的 `/docker-entrypoint-initdb.d/` 目录，实现首次启动时自动执行建表和种子数据脚本

### 需求 3：数据库 DDL 建表脚本

**用户故事：** 作为开发者，我希望有完整的建表 SQL 脚本，以便一次性创建所有业务表、索引、外键、视图和触发器。

#### 验收标准

1. THE DDL_Script SHALL 启用 `uuid-ossp` 扩展以支持 UUID 生成
2. THE DDL_Script SHALL 创建以下 9 张业务表：`users`、`learning_plans`、`learning_tasks`、`daily_problems`、`content_packages`、`knowledge_points`、`exercise_items`、`diagnosis_reports`、`user_behavior_events`
3. THE DDL_Script SHALL 为 `users` 表定义以下字段：`id`（UUID 主键，默认 `gen_random_uuid()`）、`phone`（VARCHAR(20) UNIQUE 可空）、`avatar_url`（TEXT 可空）、`nickname`（VARCHAR(50) 非空默认空字符串）、`grade`（VARCHAR(10) 非空）、`textbook_version`（VARCHAR(50) 非空默认 '人教版A版'）、`settings`（JSONB 非空默认 '{}'）、`current_plan_id`（UUID 可空外键引用 `learning_plans(id)` ON DELETE SET NULL）、`created_at`（TIMESTAMPTZ 非空默认 CURRENT_TIMESTAMP）、`updated_at`（TIMESTAMPTZ 非空默认 CURRENT_TIMESTAMP）
4. THE DDL_Script SHALL 为 `learning_plans` 表定义以下字段：`id`（UUID 主键）、`user_id`（UUID 非空外键引用 `users(id)` ON DELETE CASCADE）、`title`（VARCHAR(200) 非空）、`status`（VARCHAR(20) 非空默认 'active'）、`version`（INTEGER 非空默认 1）、`snapshot`（JSONB 可空）、`created_at`、`updated_at`
5. THE DDL_Script SHALL 为 `learning_tasks` 表定义以下字段：`id`（UUID 主键）、`plan_id`（UUID 非空外键引用 `learning_plans(id)` ON DELETE CASCADE）、`title`（VARCHAR(200) 非空）、`type`（VARCHAR(50) 非空）、`status`（VARCHAR(20) 非空默认 'pending'）、`source`（VARCHAR(50) 非空默认 'scheduled'）、`source_problem_id`（UUID 可空外键引用 `daily_problems(id)` ON DELETE SET NULL）、`knowledge_point_ids`（JSONB 非空默认 '[]'）、`content_package_id`（UUID 可空外键引用 `content_packages(id)` ON DELETE SET NULL）、`metadata`（JSONB 非空默认 '{}'）、`due_at`（TIMESTAMPTZ 可空）、`started_at`（TIMESTAMPTZ 可空）、`completed_at`（TIMESTAMPTZ 可空）、`created_at`
6. THE DDL_Script SHALL 为 `daily_problems` 表定义以下字段：`id`（UUID 主键）、`user_id`（UUID 非空外键引用 `users(id)`）、`session_id`（UUID 非空）、`original_utterance`（TEXT 非空）、`clarified_question`（TEXT 可空）、`intent`（VARCHAR(100) 非空）、`slots`（JSONB 非空默认 '{}'）、`resolution_type`（VARCHAR(50) 可空）、`resolution_task_id`（UUID 可空外键引用 `learning_tasks(id)`）、`created_at`
7. THE DDL_Script SHALL 为 `content_packages` 表定义以下字段：`id`（UUID 主键）、`production_job_id`（VARCHAR(100) 可空）、`status`（VARCHAR(20) 非空默认 'generating'）、`manifest`（JSONB 非空）、`associated_task_id`（UUID 可空外键引用 `learning_tasks(id)`）、`associated_problem_id`（UUID 可空外键引用 `daily_problems(id)`）、`created_at`、`updated_at`
8. THE DDL_Script SHALL 为 `knowledge_points` 表定义以下字段：`id`（VARCHAR(50) 主键）、`name`（VARCHAR(200) 非空）、`description`（TEXT 可空）、`prerequisite_ids`（JSONB 非空默认 '[]'）、`difficulty`（NUMERIC(3,2) 非空默认 0.5）、`subject`（VARCHAR(20) 非空默认 'math'）、`created_at`
9. THE DDL_Script SHALL 为 `exercise_items` 表定义以下字段：`id`（VARCHAR(50) 主键）、`stem`（TEXT 非空）、`options`（JSONB 可空）、`correct_answer`（VARCHAR(500) 非空）、`solution`（TEXT 可空）、`knowledge_point_ids`（JSONB 非空默认 '[]'）、`difficulty`（NUMERIC(3,2) 非空默认 0.5）、`metadata`（JSONB 非空默认 '{}'）、`created_at`
10. THE DDL_Script SHALL 为 `diagnosis_reports` 表定义以下字段：`id`（UUID 主键）、`user_id`（UUID 非空外键引用 `users(id)`）、`title`（VARCHAR(200) 非空）、`original_file_url`（TEXT 可空）、`summary`（JSONB 非空）、`detailed_analysis`（JSONB 非空）、`generated_plan_id`（UUID 可空外键引用 `learning_plans(id)`）、`created_at`
11. THE DDL_Script SHALL 为 `user_behavior_events` 表定义以下字段：`id`（BIGSERIAL 主键）、`user_id`（UUID 非空外键引用 `users(id)`）、`session_id`（VARCHAR(100) 非空）、`event_type`（VARCHAR(50) 非空）、`event_data`（JSONB 非空默认 '{}'）、`created_at`
12. THE DDL_Script SHALL 为高频查询字段创建索引，包括：`users.phone`（唯一索引）、`users.grade`、`learning_plans(user_id, status)`（复合索引）、`learning_tasks.status`、`learning_tasks.due_at`、`daily_problems.session_id`、`daily_problems.intent`、`user_behavior_events.session_id`、`user_behavior_events.event_type`
13. THE DDL_Script SHALL 创建通用触发器函数 `update_modified_column()`，在 UPDATE 操作前自动将 `updated_at` 字段设置为 `CURRENT_TIMESTAMP`
14. THE DDL_Script SHALL 为所有包含 `updated_at` 字段的表（`users`、`learning_plans`、`content_packages`）挂载 `update_modified_column` 触发器
15. THE DDL_Script SHALL 创建视图 `v_user_current_learning_context`，展示用户当前学习上下文（用户信息、当前计划、待办任务数、进行中任务数、最近3个活跃任务）
16. THE DDL_Script SHALL 创建视图 `v_daily_problems_with_resolution`，展示日清问题及其关联的解决任务信息

### 需求 4：种子数据脚本

**用户故事：** 作为开发者，我希望数据库首次启动后自动填充演示用种子数据，以便立即验证系统功能和进行前端开发。

#### 验收标准

1. THE Seed_Data_Script SHALL 插入至少 20 个数学知识点记录到 `knowledge_points` 表，覆盖函数（至少 8 个）、三角函数（至少 6 个）、导数（至少 6 个）三个模块
2. THE Seed_Data_Script SHALL 为每个知识点正确设置 `prerequisite_ids` 先修关系，形成有向无环的知识依赖图
3. THE Seed_Data_Script SHALL 插入至少 15 道练习题到 `exercise_items` 表，其中选择题至少 10 道（包含 `options` 字段）、填空题至少 5 道（`options` 为 NULL）
4. THE Seed_Data_Script SHALL 为每道练习题正确关联 `knowledge_point_ids`，且关联的知识点 ID 在 `knowledge_points` 表中存在
5. THE Seed_Data_Script SHALL 插入 2 个演示用户账号到 `users` 表：一个手机号为 `13800000001`（昵称"艾学同学"，高二，人教版A版），一个手机号为 `13800000002`（昵称"小明同学"，高三，人教版A版）
6. THE Seed_Data_Script SHALL 为第一个演示用户创建 1 个状态为 `active` 的学习计划到 `learning_plans` 表，标题为"函数与导数综合提升计划"
7. THE Seed_Data_Script SHALL 为该学习计划创建 5 个学习任务到 `learning_tasks` 表，覆盖不同的 `type`（concept_learning 和 practice）和 `status`（pending、in_progress、completed），且每个任务关联对应的知识点
8. THE Seed_Data_Script SHALL 将第一个演示用户的 `current_plan_id` 更新为所创建学习计划的 ID
9. THE Seed_Data_Script SHALL 使用 `ON CONFLICT DO NOTHING` 或等效机制确保脚本可重复执行而不报错

### 需求 5：后端 FastAPI 项目初始化

**用户故事：** 作为后端开发者，我希望有一个结构清晰的 FastAPI 项目骨架，包含 ORM 模型、数据库连接和健康检查接口，以便后续快速开发业务接口。

#### 验收标准

1. THE FastAPI_App SHALL 采用以下项目目录结构：`app/`（`main.py`、`config.py`、`db/`（`session.py`、`base.py`）、`models/`、`schemas/`、`repositories/`、`services/`、`api/`、`middlewares/`）
2. THE FastAPI_App SHALL 在 `config.py` 中通过环境变量读取数据库连接字符串（`DATABASE_URL`）、Redis 地址（`REDIS_URL`）和 JWT 密钥（`JWT_SECRET`）
3. THE FastAPI_App SHALL 在 `db/session.py` 中配置 SQLAlchemy 2.x 异步数据库连接池，使用 `asyncpg` 驱动
4. THE FastAPI_App SHALL 在 `models/` 目录下定义 9 个 SQLAlchemy ORM 模型类，与数据库 9 张表一一对应，字段类型和约束与 DDL_Script 保持一致
5. WHEN 收到 `GET /health` 请求时，THE Health_Check_Endpoint SHALL 检查 PostgreSQL_DB 连接状态和 Redis_Cache 连接状态，返回 JSON 格式的健康状态信息
6. IF PostgreSQL_DB 或 Redis_Cache 连接失败，THEN THE Health_Check_Endpoint SHALL 返回 HTTP 503 状态码，并在响应体中标明失败的服务名称
7. THE FastAPI_App SHALL 在 `main.py` 中配置 CORS 中间件，允许前端开发服务器的跨域请求
8. THE FastAPI_App SHALL 提供 `requirements.txt` 文件，列出所有 Python 依赖包及其版本号，包括：`fastapi`、`uvicorn`、`sqlalchemy`、`asyncpg`、`redis`、`pydantic`、`pydantic-settings`、`python-jose`、`passlib`
9. THE FastAPI_App SHALL 提供 `Dockerfile`，基于 Python 3.11 镜像构建，安装依赖并以 `uvicorn` 启动应用

### 需求 6：前端 React 项目初始化

**用户故事：** 作为前端开发者，我希望有一个配置完善的 React + TypeScript + Tailwind 项目骨架，包含路由、API 封装和基础布局，以便后续快速开发业务页面。

#### 验收标准

1. THE React_App SHALL 使用 Vite 5.x 创建，采用 React 18 + TypeScript 模板
2. THE React_App SHALL 集成 Tailwind CSS 3.x，并在 `tailwind.config.js` 中配置响应式断点：`sm: 640px`、`md: 768px`、`lg: 1024px`、`xl: 1280px`
3. THE React_App SHALL 采用以下 `src/` 目录结构：`assets/`、`components/`（`ui/`、`layout/`）、`containers/`、`hooks/`、`stores/`、`services/`、`types/`、`utils/`、`config/`、`App.tsx`、`main.tsx`、`index.css`
4. THE React_App SHALL 在 `App.tsx` 中使用 `react-router-dom` 6.x 配置基础路由，包含以下路径：`/`（主页）、`/auth/login`（登录页）、`/daily-clearance`（日清页）、`/execution`（任务执行页）、`/diagnosis`（诊断页）
5. THE React_App SHALL 在 `services/apiClient.ts` 中封装 axios 实例，配置 `baseURL` 为 `/api/v1`，并在请求拦截器中自动附加 `Authorization: Bearer <token>` 请求头
6. IF API 请求返回 HTTP 401 状态码，THEN THE API_Client SHALL 自动清除本地存储的 token 并跳转到登录页
7. THE React_App SHALL 在 `components/layout/` 目录下提供 `AppLayout` 基础布局组件，包含顶部导航栏占位和主内容区域
8. THE React_App SHALL 提供 `Dockerfile`，使用多阶段构建：第一阶段基于 Node 18 镜像执行 `npm run build`，第二阶段基于 Nginx 镜像提供静态文件服务
9. THE React_App SHALL 在 `index.css` 中引入 Tailwind CSS 的 `@tailwind base`、`@tailwind components`、`@tailwind utilities` 指令
10. THE React_App SHALL 安装 `zustand` 状态管理库，并在 `stores/` 目录下创建 `useUserStore.ts` 骨架文件，定义用户状态接口（`user`、`token`、`isAuthenticated`）

### 需求 7：端到端启动验证

**用户故事：** 作为开发者，我希望通过一条命令验证整个技术栈正常工作，以确认 Day 1 的交付标准达成。

#### 验收标准

1. WHEN 在项目根目录执行 `docker-compose up --build` 后，THE Docker_Compose SHALL 在 120 秒内使所有服务达到健康运行状态
2. WHEN 所有服务启动完成后，THE PostgreSQL_DB SHALL 包含 9 张业务表、2 个视图和触发器函数，且种子数据已成功插入
3. WHEN 通过浏览器访问 `http://localhost:3000` 时，THE React_App SHALL 返回可渲染的 HTML 页面
4. WHEN 通过 HTTP 客户端访问 `http://localhost:8000/health` 时，THE Health_Check_Endpoint SHALL 返回 HTTP 200 状态码和包含 `postgres: ok`、`redis: ok` 的 JSON 响应
5. WHEN 查询 `knowledge_points` 表时，THE PostgreSQL_DB SHALL 返回至少 20 条知识点记录
6. WHEN 查询 `exercise_items` 表时，THE PostgreSQL_DB SHALL 返回至少 15 条练习题记录
7. WHEN 查询 `users` 表时，THE PostgreSQL_DB SHALL 返回 2 条演示用户记录
