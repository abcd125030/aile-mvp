# 实施计划：艾乐学伴 MVP Day 2 — 用户系统与后端核心 CRUD

## 概述

将 Day 2 设计方案拆解为可执行的后端开发任务，按“基础设施 -> 用户认证 -> 计划 CRUD -> 任务 CRUD -> 学习资源查询 -> 验证”顺序推进。所有任务均以当前单体 FastAPI 工程为落点，并与 Day 1 已完成结构保持一致。

## 任务

- [x] 1. 搭建 Day 2 公共基础设施
  - [x] 1.1 统一注册 `/api/v1` 业务路由
    - 在 `backend/app/main.py` 中创建并挂载 API v1 路由分组
    - 将健康检查保留为现有入口，同时新增 Day 2 各业务 router 的集中注册点
    - 确保 Swagger 中能展示全部 Day 2 接口
    - _需求: 1.1, 1.6, 8.1_

  - [x] 1.2 新增 JWT 工具与当前用户依赖
    - 创建 JWT 编解码工具，统一处理 `sub`、`phone`、`exp`
    - 创建 Bearer Token 解析依赖，返回当前登录用户
    - 统一鉴权失败时的 `401 Unauthorized` 行为
    - _需求: 1.2, 1.3, 1.4, 1.5_

  - [x] 1.3 补充通用异常与枚举定义
    - 为计划状态、任务状态定义可复用枚举
    - 为资源不存在、权限不足、状态流转非法提供统一异常出口
    - _需求: 4.13, 5.12, 8.2_

- [x] 2. 补充 ORM 关系与 Schema 基础模型
  - [x] 2.1 为现有 ORM 模型增加关键关系
    - 为 `User` 增加 `plans`、`current_plan`
    - 为 `LearningPlan` 增加 `user`、`tasks`
    - 为 `LearningTask` 增加 `plan`、`content_package`
    - 保持与当前 DDL 一致，不新增数据库字段
    - _需求: 4.9, 5.7, 8.6_

  - [x] 2.2 新增 Day 2 的 Pydantic 模型
    - 创建认证、用户、计划、任务、知识点、练习题等请求/响应 Schema
    - 在用户 Schema 中暴露顶层 `target_university`
    - 在任务详情 Schema 中区分 `task`、`knowledge_points`、`content_package`、`exercises`
    - _需求: 3.2, 4.7, 5.8, 6.3, 7.5, 8.1, 8.3, 8.4, 8.5_

- [x] 3. 实现用户认证与用户画像模块
  - [x] 3.1 创建用户与认证 Repository
    - 新增按手机号查询用户、按 ID 查询用户、创建默认用户、更新用户的方法
    - 为 `GET /users/me` 准备带当前计划摘要的查询支持
    - _需求: 2.6, 2.7, 3.2, 3.3_

  - [x] 3.2 实现 `AuthService.login`
    - 校验手机号格式与固定验证码 `8888`
    - 已存在用户直接登录；不存在则创建默认用户
    - 生成 7 天有效期 JWT 并返回 `is_new_user`
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10_

  - [x] 3.3 实现 `UserService.get_me` 与 `UserService.update_me`
    - 返回用户基本信息、`current_plan_id` 与 `current_plan_snapshot`
    - 支持更新 `nickname`、`grade`、`textbook_version`、`target_university`、`settings`
    - 将 `target_university` 映射写入 `users.settings.target_university`
    - 阻止手机号修改
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

  - [x] 3.4 暴露认证与用户路由
    - 新建 `auth.py` 与 `users.py` 路由文件
    - 实现 `POST /api/v1/auth/login`
    - 实现 `GET /api/v1/users/me` 与 `PUT /api/v1/users/me`
    - _需求: 2.1, 3.1, 3.4, 8.1_

- [x] 4. 实现学习计划 CRUD
  - [x] 4.1 创建学习计划 Repository
    - 新增查询当前用户全部计划、按 ID 查询计划详情、创建计划、更新计划状态的方法
    - 详情查询需预加载任务列表
    - _需求: 4.1, 4.2, 4.5, 4.9, 4.12_

  - [x] 4.2 实现 `PlanService`
    - 列表按 `active -> completed -> archived`、`updated_at DESC` 排序
    - 创建计划时支持 `set_as_current`
    - 更新状态时同步维护 `users.current_plan_id`
    - 校验用户只能访问自己的计划
    - _需求: 4.3, 4.4, 4.6, 4.7, 4.8, 4.10, 4.11, 4.13, 4.14, 4.15, 4.16, 4.17_

  - [x] 4.3 暴露学习计划路由
    - 实现 `GET /api/v1/plans`
    - 实现 `POST /api/v1/plans`
    - 实现 `GET /api/v1/plans/{plan_id}`
    - 实现 `PUT /api/v1/plans/{plan_id}/status`
    - _需求: 4.1, 4.5, 4.9, 4.12_

- [x] 5. 实现学习任务 CRUD 与状态机
  - [x] 5.1 创建学习任务 Repository
    - 新增按计划查询任务列表、按 ID 查询任务详情、更新任务状态的方法
    - 为详情接口准备任务、计划、内容包的联合装载
    - _需求: 5.1, 5.2, 5.7, 5.8, 5.11_

  - [x] 5.2 实现 `TaskService.list_tasks` 与 `TaskService.get_task_detail`
    - 支持 `plan_id` 和 `status` 筛选
    - 默认读取 `Current_Plan`
    - 详情聚合知识点、内容包、题目数据
    - 优先使用 `metadata.exercise_ids`，缺省时按 `knowledge_point_ids` 回查推荐题
    - _需求: 5.3, 5.4, 5.5, 5.6, 5.8, 5.9, 5.10_

  - [x] 5.3 实现 `TaskService.update_task_status`
    - 仅允许 `pending`、`in_progress`、`completed`
    - 强制执行 `pending -> in_progress -> completed`
    - 自动写入 `started_at`、`completed_at`
    - _需求: 5.11, 5.12, 5.13, 5.14, 5.15, 5.16, 5.17_

  - [x] 5.4 实现 `TaskService.submit_answer`
    - 校验任务访问权限与题目归属
    - 区分选择题与填空题判题规则
    - 正确作答时自动补齐任务开始/完成状态
    - 返回判题结果、标准答案与解析
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 6.10, 6.11, 6.12_

  - [x] 5.5 暴露学习任务路由
    - 实现 `GET /api/v1/tasks`
    - 实现 `GET /api/v1/tasks/{task_id}`
    - 实现 `PUT /api/v1/tasks/{task_id}/status`
    - 实现 `POST /api/v1/tasks/{task_id}/submit-answer`
    - _需求: 5.1, 5.7, 5.11, 6.1_

- [x] 6. 实现知识点与题库查询
  - [x] 6.1 创建知识点与练习题 Repository
    - 支持按 ID、按 `subject`、按知识点、按难度区间查询
    - 支持批量读取先修知识点
    - _需求: 7.1, 7.2, 7.4, 7.6, 7.7, 7.8, 7.9_

  - [x] 6.2 实现学习资源 Service
    - 知识点列表按 `id` 升序返回
    - 知识点详情带先修知识点对象
    - 题目列表按 `difficulty ASC, id ASC` 返回并支持 `limit`
    - _需求: 7.3, 7.5, 7.6, 7.10, 7.11, 7.12_

  - [x] 6.3 暴露知识点与题库路由
    - 实现 `GET /api/v1/knowledge-points`
    - 实现 `GET /api/v1/knowledge-points/{knowledge_point_id}`
    - 实现 `GET /api/v1/exercises`
    - _需求: 7.1, 7.4, 7.7_

- [x] 7. 做接口联调与质量验证
  - [x] 7.1 补充最小可行验证
    - 使用 Swagger 或 Postman 验证登录、鉴权、计划、任务、知识点、题库接口
    - 覆盖至少一次正确判题与自动完成任务路径
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

  - [x] 7.2 运行静态检查与诊断
    - 对最近编辑的 Python 文件执行诊断检查
    - 修复新增的语法或类型错误
    - _需求: 8.1, 9.1_

  - [x] 7.3 更新必要的开发说明
    - 若实现中引入新的环境变量约定或接口说明，补充到 README 或相关模块注释
    - 保持 Day 2 交付可被后续 Day 3/Day 4 直接承接
    - _需求: 1.6, 8.6, 9.1_

## 备注

- Day 2 严格不进入 AI 内容生成与实时通信实现
- 若实现过程中发现 OpenAPI 与冲刺计划存在新的冲突，以本规格文档为准并在提交说明中标注
- `tasks.md` 确认后，再开始实际业务代码开发
