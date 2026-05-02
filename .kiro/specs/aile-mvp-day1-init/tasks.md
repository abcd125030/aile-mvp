# 实施计划：艾乐学伴 MVP Day 1 — 项目初始化与基础设施落地

## 概述

将 Day 1 设计方案转化为可执行的编码任务，按增量方式逐步搭建 Monorepo 项目骨架、数据库脚本、后端 FastAPI 框架、前端 React 框架和 Docker Compose 编排，最终实现端到端一键启动。

## 任务

- [x] 1. 创建 Monorepo 项目结构与根目录文件
  - [x] 1.1 创建顶层目录结构和根目录配置文件
    - 创建 `frontend/`、`backend/`、`database/` 目录
    - 创建 `.gitignore` 文件，排除 `node_modules/`、`__pycache__/`、`.env`、`venv/`、`*.pyc`、`.vscode/`、`.idea/` 等
    - 创建 `README.md`，包含项目概述、技术栈说明、启动方式（`docker-compose up --build`）和演示账号信息（13800000001 / 13800000002）
    - _需求: 1.1, 1.2, 1.3_

- [x] 2. 编写数据库 DDL 建表脚本
  - [x] 2.1 创建 `database/01_ddl.sql` — 扩展、9 张业务表、索引、触发器、视图
    - 启用 `uuid-ossp` 扩展
    - 按外键依赖顺序创建 9 张表：`knowledge_points` → `exercise_items` → `users`（延迟 `current_plan_id` 外键）→ `learning_plans` → `daily_problems` → `content_packages`（延迟外键）→ `learning_tasks` → `diagnosis_reports` → `user_behavior_events`
    - 添加延迟外键：`users.current_plan_id → learning_plans(id)`、`content_packages.associated_task_id → learning_tasks(id)`、`content_packages.associated_problem_id → daily_problems(id)`
    - 创建全部索引（`users.phone` 唯一索引、`users.grade`、`learning_plans(user_id, status)` 复合索引、`learning_tasks.status`、`learning_tasks.due_at`、`daily_problems.session_id`、`daily_problems.intent`、`user_behavior_events.session_id`、`user_behavior_events.event_type`）
    - 创建触发器函数 `update_modified_column()` 并为 `users`、`learning_plans`、`content_packages` 挂载触发器
    - 创建视图 `v_user_current_learning_context` 和 `v_daily_problems_with_resolution`
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14, 3.15, 3.16_

- [x] 3. 编写种子数据脚本
  - [x] 3.1 创建 `database/02_seed.sql` — 知识点、练习题、演示用户、学习计划与任务
    - 插入 ≥20 个数学知识点（函数模块 ≥8、三角函数模块 ≥6、导数模块 ≥6），正确设置 `prerequisite_ids` 先修依赖
    - 插入 ≥15 道练习题（选择题 ≥10 道含 `options` JSONB、填空题 ≥5 道 `options` 为 NULL），关联有效的 `knowledge_point_ids`
    - 插入 2 个演示用户（13800000001 艾学同学 高二、13800000002 小明同学 高三）
    - 为用户 1 创建 1 个 active 学习计划"函数与导数综合提升计划"和 5 个学习任务（覆盖 concept_learning/practice 类型和 completed/in_progress/pending 状态）
    - 更新用户 1 的 `current_plan_id` 为该计划 ID
    - 全部使用 `ON CONFLICT DO NOTHING` 确保可重复执行
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_

- [x] 4. 检查点 — 确认数据库脚本完整性
  - 确保 DDL 和种子数据脚本语法正确，所有外键引用有效，ask the user if questions arise.

- [x] 5. 初始化后端 FastAPI 项目
  - [x] 5.1 创建后端项目结构和配置文件
    - 创建 `backend/app/` 目录结构：`db/`、`models/`、`schemas/`、`repositories/`、`services/`、`api/`、`middlewares/`，每个目录包含 `__init__.py`
    - 创建 `backend/requirements.txt`，列出所有依赖及版本号：`fastapi`、`uvicorn[standard]`、`sqlalchemy[asyncio]`、`asyncpg`、`redis[hiredis]`、`pydantic`、`pydantic-settings`、`python-jose[cryptography]`、`passlib[bcrypt]`
    - 创建 `backend/app/config.py`，使用 `pydantic-settings` 的 `BaseSettings` 读取 `DATABASE_URL`、`REDIS_URL`、`JWT_SECRET` 环境变量
    - _需求: 5.1, 5.2, 5.8_

  - [x] 5.2 实现数据库连接层
    - 创建 `backend/app/db/base.py`，定义 SQLAlchemy `DeclarativeBase`
    - 创建 `backend/app/db/session.py`，配置 `create_async_engine` + `async_sessionmaker`，提供 `get_db` 异步生成器依赖
    - _需求: 5.3_

  - [x] 5.3 定义 9 个 SQLAlchemy ORM 模型
    - 在 `backend/app/models/` 下创建 9 个模型文件：`user.py`、`learning_plan.py`、`learning_task.py`、`daily_problem.py`、`content_package.py`、`knowledge_point.py`、`exercise_item.py`、`diagnosis_report.py`、`user_behavior_event.py`
    - 每个模型使用 `mapped_column` 声明字段，类型和约束与 DDL 脚本保持一致
    - 在 `backend/app/models/__init__.py` 中统一导出所有模型
    - _需求: 5.4_

  - [x] 5.4 实现 FastAPI 入口和健康检查接口
    - 创建 `backend/app/api/health.py`，实现 `GET /health` 接口：执行 `SELECT 1` 检查 PostgreSQL、执行 `PING` 检查 Redis，全部成功返回 200，任一失败返回 503
    - 创建 `backend/app/main.py`，配置 CORS 中间件（允许 `localhost:3000` 和 `localhost:5173`）、注册健康检查路由
    - _需求: 5.5, 5.6, 5.7_

  - [x] 5.5 创建后端 Dockerfile
    - 基于 `python:3.11-slim` 镜像，安装依赖，以 `uvicorn app.main:app --host 0.0.0.0 --port 8000` 启动
    - _需求: 5.9_

- [x] 6. 检查点 — 确认后端项目结构完整
  - 确保所有后端文件无语法错误，ORM 模型字段与 DDL 一致，ask the user if questions arise.

- [x] 7. 初始化前端 React 项目
  - [x] 7.1 创建前端项目结构和配置文件
    - 创建 `frontend/package.json`，包含 React 18、TypeScript、Vite 5.x、Tailwind CSS 3.x、react-router-dom 6.x、axios、zustand 依赖
    - 创建 `frontend/tsconfig.json`、`frontend/vite.config.ts`
    - 创建 `frontend/tailwind.config.js`，配置响应式断点（sm:640px、md:768px、lg:1024px、xl:1280px）
    - 创建 `frontend/postcss.config.js`
    - 创建 `frontend/index.html` 入口 HTML
    - _需求: 6.1, 6.2_

  - [x] 7.2 创建前端 src 目录结构和入口文件
    - 创建 `src/` 目录结构：`assets/`、`components/ui/`、`components/layout/`、`containers/`、`hooks/`、`stores/`、`services/`、`types/`、`utils/`、`config/`
    - 创建 `src/index.css`，引入 Tailwind 的 `@tailwind base`、`@tailwind components`、`@tailwind utilities`
    - 创建 `src/main.tsx` 应用入口，挂载 React 根组件
    - _需求: 6.3, 6.9_

  - [x] 7.3 实现路由配置和页面占位组件
    - 创建 5 个占位页面组件：`containers/HomePage.tsx`、`containers/LoginPage.tsx`、`containers/DailyClearancePage.tsx`、`containers/ExecutionPage.tsx`、`containers/DiagnosisPage.tsx`
    - 创建 `src/App.tsx`，使用 `react-router-dom` 配置路由：`/`、`/auth/login`、`/daily-clearance`、`/execution`、`/diagnosis`
    - _需求: 6.4_

  - [x] 7.4 实现 API 客户端和用户状态管理
    - 创建 `src/services/apiClient.ts`，封装 axios 实例（baseURL: `/api/v1`），请求拦截器附加 Bearer token，响应拦截器处理 401 自动清除 token 并跳转登录页
    - 创建 `src/stores/useUserStore.ts`，使用 Zustand 定义用户状态接口（`user`、`token`、`isAuthenticated`、`setUser`、`setToken`、`logout`）
    - _需求: 6.5, 6.6, 6.10_

  - [x] 7.5 实现 AppLayout 基础布局组件
    - 创建 `src/components/layout/AppLayout.tsx`，包含顶部导航栏（Logo + 各页面导航链接）和 `<Outlet />` 主内容区域
    - 使用 Tailwind CSS 实现响应式布局
    - _需求: 6.7_

  - [x] 7.6 创建前端 Dockerfile 和 Nginx 配置
    - 创建 `frontend/nginx.conf`，配置 `/` 服务静态文件（SPA history fallback）、`/api/v1/` 反向代理到 `http://backend:8000/api/v1/`
    - 创建 `frontend/Dockerfile`，多阶段构建：Node 18 执行 `npm run build` → Nginx 提供静态文件服务
    - _需求: 6.8_

- [x] 8. 检查点 — 确认前端项目结构完整
  - 确保所有前端文件无语法错误，路由配置正确，ask the user if questions arise.

- [x] 9. 创建 Docker Compose 编排配置
  - [x] 9.1 编写 `docker-compose.yml`
    - 定义 4 个服务：`postgres`（PostgreSQL 15，持久化卷 `pgdata`，挂载 `./database/` 到 `/docker-entrypoint-initdb.d/`，健康检查 `pg_isready`）、`redis`（Redis 7 alpine，端口 6379，健康检查 `redis-cli ping`）、`backend`（构建 `./backend`，端口 8000，环境变量 DATABASE_URL/REDIS_URL/JWT_SECRET，依赖 postgres+redis healthy）、`frontend`（构建 `./frontend`，端口 3000:80，依赖 backend）
    - 配置 PostgreSQL 环境变量：`POSTGRES_DB=aile_mvp`、`POSTGRES_USER=postgres`、`POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}`
    - 定义 `pgdata` 命名卷
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [x] 10. 最终检查点 — 端到端启动验证
  - 确保 `docker-compose.yml` 配置正确，所有 Dockerfile 可构建，数据库脚本可自动执行
  - 验证清单：4 个服务定义完整、PostgreSQL 包含 9 表 + 2 视图 + 种子数据、后端 `/health` 返回 200、前端 `localhost:3000` 可访问
  - Ensure all tests pass, ask the user if questions arise.
  - _需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

## 备注

- 标记 `*` 的任务为可选任务，可跳过以加速 MVP 交付
- 每个任务引用具体需求编号以确保可追溯性
- 检查点任务用于增量验证，确保每个阶段的交付物正确
- 数据库脚本需按文件名排序执行（01_ddl.sql → 02_seed.sql），PostgreSQL 的 `docker-entrypoint-initdb.d` 会按字母序自动执行
