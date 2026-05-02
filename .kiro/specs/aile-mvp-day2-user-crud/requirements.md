# 需求文档：艾乐学伴 MVP Day 2 — 用户系统与后端核心 CRUD

## 简介

本文档定义 Day 2 的交付需求，目标是在 Day 1 项目初始化完成后，为前端与后续 AI 旅程提供第一批可用业务接口。范围包含用户认证、用户画像、学习计划 CRUD、学习任务 CRUD、题目提交判定以及知识点/题库查询。

交付标准：Swagger 或 Postman 能跑通全部 Day 2 接口，JWT 鉴权生效，数据返回与数据库设计一致。

## 术语表

- **Access_Token**：登录后签发的 JWT 令牌，用于访问受保护接口
- **Current_User**：由 Bearer Token 解析出的当前登录用户
- **User_Profile**：用户画像信息，包括昵称、年级、教材版本、目标院校与设置项
- **Learning_Plan**：用户的学习计划，是学习任务的容器
- **Learning_Task**：计划下的具体任务，包含类型、状态、知识点与扩展元数据
- **Task_Metadata**：任务的 JSON 扩展信息，至少支持 `estimated_minutes`、`difficulty`、`exercise_ids`
- **Current_Plan**：`users.current_plan_id` 指向的当前活跃计划
- **Knowledge_Point**：知识点定义，包含先修关系
- **Exercise_Item**：练习题实体，支持选择题与填空题

## 需求

### 需求 1：API 路由与鉴权基础设施

**用户故事：** 作为后端开发者，我希望 Day 2 的业务接口统一挂载在 `/api/v1` 下，并且除登录外都受 JWT 鉴权保护，以便前端能直接复用 Day 1 的 API 客户端访问约定。

#### 验收标准

1. THE FastAPI_App SHALL 在 `main.py` 中注册统一的 `/api/v1` 业务路由分组
2. THE FastAPI_App SHALL 提供 JWT 工具，用于令牌生成、解码、过期校验
3. THE FastAPI_App SHALL 提供 `Current_User` 依赖，从 Bearer Token 中解析用户身份
4. IF 请求缺失 `Authorization` 请求头，THEN 受保护接口 SHALL 返回 `401 Unauthorized`
5. IF JWT 无效、过期或用户不存在，THEN 受保护接口 SHALL 返回 `401 Unauthorized`
6. THE Swagger_Docs SHALL 能展示 Day 2 全部接口并支持 Bearer Token 调试

### 需求 2：手机号登录

**用户故事：** 作为演示用户，我希望通过手机号和固定验证码快速登录，以便在 MVP 阶段无需真实短信服务也能完成演示闭环。

#### 验收标准

1. THE Auth_API SHALL 提供 `POST /api/v1/auth/login` 接口
2. THE Auth_API SHALL 接收 `phone` 和 `sms_code` 两个字段
3. THE Auth_API SHALL 校验手机号为 11 位大陆手机号格式
4. THE Auth_API SHALL 将固定验证码 `8888` 视为唯一合法验证码
5. IF `sms_code` 不等于 `8888`，THEN THE Auth_API SHALL 返回 `400 Bad Request`
6. WHEN 使用已存在手机号登录时，THE Auth_API SHALL 返回该用户信息、JWT 和 `is_new_user=false`
7. WHEN 使用未注册手机号登录时，THE Auth_API SHALL 自动创建用户，并返回 `is_new_user=true`
8. THE 新用户默认信息 SHALL 至少包含：`nickname=""`、`grade="高一"`、`textbook_version="人教版A版"`、`settings={}`
9. THE 登录响应 SHALL 包含字段：`user`、`token`、`is_new_user`
10. THE `token` SHALL 使用 `HS256` 生成，并包含用户 ID 作为 `sub`

### 需求 3：当前用户信息读取与画像更新

**用户故事：** 作为登录用户，我希望查看并更新自己的画像信息，以便后续生成更贴合我的学习计划与任务。

#### 验收标准

1. THE User_API SHALL 提供 `GET /api/v1/users/me` 接口
2. WHEN 调用 `GET /api/v1/users/me` 成功时，THE User_API SHALL 返回：`id`、`phone`、`nickname`、`grade`、`textbook_version`、`target_university`、`settings`、`current_plan_id`、`current_plan_snapshot`
3. THE `current_plan_snapshot` SHALL 在存在当前计划时返回 `{ title, status }`，否则返回 `null`
4. THE User_API SHALL 提供 `PUT /api/v1/users/me` 接口
5. THE `PUT /api/v1/users/me` 请求体 SHALL 仅允许更新：`nickname`、`grade`、`textbook_version`、`target_university`、`settings`
6. THE User_API SHALL 禁止通过该接口修改 `phone`
7. THE User_API SHALL 将 `target_university` 持久化到 `users.settings.target_university`
8. IF 请求同时包含顶层 `target_university` 和 `settings.target_university`，THEN THE User_API SHALL 以顶层字段为准
9. WHEN 用户画像更新成功时，THE User_API SHALL 返回更新后的完整用户信息，其结构与 `GET /api/v1/users/me` 一致
10. IF 请求未携带合法 JWT，THEN `GET /api/v1/users/me` 与 `PUT /api/v1/users/me` SHALL 返回 `401 Unauthorized`

### 需求 4：学习计划查询、创建与状态更新

**用户故事：** 作为登录用户，我希望查看自己的所有学习计划、创建新计划并更新计划状态，以便管理不同阶段的学习安排。

#### 验收标准

1. THE Plan_API SHALL 提供 `GET /api/v1/plans` 接口，返回当前用户的全部学习计划列表
2. THE `GET /api/v1/plans` 结果 SHALL 仅包含当前用户的数据，不得泄露其他用户计划
3. THE `GET /api/v1/plans` 结果 SHALL 按状态优先级排序：`active` → `completed` → `archived`
4. THE `GET /api/v1/plans` 同状态结果 SHALL 按 `updated_at` 倒序排列
5. THE Plan_API SHALL 提供 `POST /api/v1/plans` 接口，用于创建计划
6. THE `POST /api/v1/plans` 请求体 SHALL 至少支持：`title`、`status`、`snapshot`、`set_as_current`
7. WHEN 创建计划成功时，THE Plan_API SHALL 返回新计划完整信息
8. IF `set_as_current=true`，THEN THE Plan_API SHALL 将该计划写入 `users.current_plan_id`
9. THE Plan_API SHALL 提供 `GET /api/v1/plans/{plan_id}` 接口，返回计划详情及任务列表
10. THE `GET /api/v1/plans/{plan_id}` 任务列表 SHALL 按状态优先级排序：`in_progress` → `pending` → `completed`
11. THE `GET /api/v1/plans/{plan_id}` 同状态任务 SHALL 优先按 `due_at` 升序，再按 `created_at` 升序
12. THE Plan_API SHALL 提供 `PUT /api/v1/plans/{plan_id}/status` 接口
13. THE 计划状态更新 SHALL 仅允许值：`active`、`completed`、`archived`
14. WHEN 计划状态被更新为 `active` 时，THE Plan_API SHALL 将该计划设置为 `Current_Plan`
15. WHEN 当前计划被更新为非 `active` 且用户不存在其他 `active` 计划时，THE Plan_API SHALL 将 `users.current_plan_id` 置空
16. IF 用户访问或修改不属于自己的计划，THEN THE Plan_API SHALL 返回 `403 Forbidden`
17. IF `plan_id` 不存在，THEN THE Plan_API SHALL 返回 `404 Not Found`

### 需求 5：学习任务列表、详情与状态机

**用户故事：** 作为登录用户，我希望查看任务列表、打开任务详情并推进任务状态，以便完成我的学习过程。

#### 验收标准

1. THE Task_API SHALL 提供 `GET /api/v1/tasks` 接口
2. THE `GET /api/v1/tasks` SHALL 支持可选查询参数：`plan_id`、`status`
3. IF `plan_id` 未提供且用户存在 `Current_Plan`，THEN THE Task_API SHALL 默认查询当前计划任务
4. IF `plan_id` 未提供且用户不存在 `Current_Plan`，THEN THE Task_API SHALL 返回空数组
5. THE `GET /api/v1/tasks` 结果 SHALL 仅包含当前用户可访问任务
6. THE `GET /api/v1/tasks` 结果 SHALL 按状态优先级排序：`in_progress` → `pending` → `completed`
7. THE Task_API SHALL 提供 `GET /api/v1/tasks/{task_id}` 接口
8. THE `GET /api/v1/tasks/{task_id}` 响应 SHALL 包含：`task`、`knowledge_points`、`content_package`、`exercises`
9. THE `GET /api/v1/tasks/{task_id}` SHALL 优先根据 `Task_Metadata.exercise_ids` 加载题目
10. IF `Task_Metadata.exercise_ids` 为空，THEN THE `GET /api/v1/tasks/{task_id}` SHALL 根据任务的 `knowledge_point_ids` 回查推荐题目
11. THE Task_API SHALL 提供 `PUT /api/v1/tasks/{task_id}/status` 接口
12. THE 任务状态更新 SHALL 仅允许值：`pending`、`in_progress`、`completed`
13. WHEN 任务状态从 `pending` 变为 `in_progress` 时，THE Task_API SHALL 自动写入 `started_at`
14. WHEN 任务状态从 `in_progress` 变为 `completed` 时，THE Task_API SHALL 自动写入 `completed_at`
15. IF 任务状态流转不满足 `pending -> in_progress -> completed`，THEN THE Task_API SHALL 返回 `400 Bad Request`
16. IF 用户访问或修改不属于自己的任务，THEN THE Task_API SHALL 返回 `403 Forbidden`
17. IF `task_id` 不存在，THEN THE Task_API SHALL 返回 `404 Not Found`

### 需求 6：提交答案与任务完成联动

**用户故事：** 作为登录用户，我希望提交练习题答案并立即得到判定结果，以便知道自己是否掌握该任务。

#### 验收标准

1. THE Task_API SHALL 提供 `POST /api/v1/tasks/{task_id}/submit-answer` 接口
2. THE `submit-answer` 请求体 SHALL 包含：`exercise_id`、`answer`
3. THE `submit-answer` 响应 SHALL 包含：`task_id`、`exercise_id`、`is_correct`、`correct_answer`、`solution`、`task_status`
4. THE `submit-answer` SHALL 仅允许当前用户对自己可访问任务提交答案
5. THE `submit-answer` SHALL 校验 `exercise_id` 必须属于该任务的可用题目集合
6. IF 题目不属于该任务，THEN THE Task_API SHALL 返回 `400 Bad Request`
7. THE 选择题判题 SHALL 以去除首尾空格后的字符串精确匹配为准
8. THE 填空题判题 SHALL 以去除首尾空格且忽略大小写后的字符串匹配为准
9. WHEN 用户首次正确作答且任务状态为 `in_progress` 时，THE Task_API SHALL 自动将任务更新为 `completed`
10. WHEN 用户首次正确作答且任务状态为 `pending` 时，THE Task_API SHALL 自动补写 `started_at` 和 `completed_at`
11. WHEN 用户答案错误时，THE Task_API SHALL 保持任务状态不变
12. IF `exercise_id` 不存在，THEN THE Task_API SHALL 返回 `404 Not Found`

### 需求 7：知识点与题库查询

**用户故事：** 作为登录用户或前端页面，我希望按知识点浏览知识详情和题目列表，以便支撑任务详情页和后续学习旅程。

#### 验收标准

1. THE Learning_Resource_API SHALL 提供 `GET /api/v1/knowledge-points` 接口
2. THE `GET /api/v1/knowledge-points` SHALL 支持可选查询参数 `subject`
3. THE `GET /api/v1/knowledge-points` 结果 SHALL 按 `id` 升序返回
4. THE Learning_Resource_API SHALL 提供 `GET /api/v1/knowledge-points/{knowledge_point_id}` 接口
5. THE `GET /api/v1/knowledge-points/{knowledge_point_id}` 响应 SHALL 返回知识点基础信息和 `prerequisites` 列表
6. THE `prerequisites` SHALL 根据 `prerequisite_ids` 批量查询并返回对象数组
7. THE Learning_Resource_API SHALL 提供 `GET /api/v1/exercises` 接口
8. THE `GET /api/v1/exercises` SHALL 支持可选查询参数：`knowledge_point_id`、`difficulty_min`、`difficulty_max`、`limit`
9. THE `GET /api/v1/exercises` 结果 SHALL 支持按 `knowledge_point_id` 过滤题目
10. THE `GET /api/v1/exercises` 结果 SHALL 按 `difficulty` 升序、`id` 升序返回
11. IF `knowledge_point_id` 不存在，THEN THE Learning_Resource_API MAY 返回空数组而非错误
12. IF 访问的知识点详情不存在，THEN THE Learning_Resource_API SHALL 返回 `404 Not Found`

### 需求 8：Schema 与接口契约清晰化

**用户故事：** 作为前后端协作者，我希望所有 Day 2 接口都有稳定明确的请求/响应 Schema，以便 Swagger 可读、前端联调成本低。

#### 验收标准

1. THE FastAPI_App SHALL 为 Day 2 所有接口提供 Pydantic 请求与响应模型
2. THE Day 2 Schema SHALL 明确表示计划状态和任务状态的可选值
3. THE Day 2 Schema SHALL 统一将时间字段序列化为 ISO 8601 字符串
4. THE Day 2 Schema SHALL 将 `target_university` 暴露为用户画像顶层字段
5. THE Day 2 Schema SHALL 在任务详情响应中显式区分 `task`、`knowledge_points`、`content_package`、`exercises`
6. THE Day 2 Schema SHALL 兼容当前数据库中的 JSONB 字段结构，不要求新增 DDL

### 需求 9：Day 2 验证与交付

**用户故事：** 作为项目负责人，我希望 Day 2 的后端改动可以被快速验证，以确认用户系统和核心 CRUD 已达到冲刺计划要求。

#### 验收标准

1. WHEN 使用 Swagger 或 Postman 调用 `POST /api/v1/auth/login` 且验证码为 `8888` 时，THE 系统 SHALL 返回 200 与有效 JWT
2. WHEN 使用登录返回的 JWT 调用 `GET /api/v1/users/me` 时，THE 系统 SHALL 返回 200 与用户画像
3. WHEN 调用 `GET /api/v1/plans` 时，THE 系统 SHALL 返回当前用户计划列表
4. WHEN 调用 `GET /api/v1/plans/{plan_id}` 时，THE 系统 SHALL 返回计划详情及排序后的任务列表
5. WHEN 调用 `PUT /api/v1/tasks/{task_id}/status` 按合法顺序推进时，THE 系统 SHALL 正确更新状态与时间字段
6. WHEN 调用 `POST /api/v1/tasks/{task_id}/submit-answer` 且答案正确时，THE 系统 SHALL 返回正确判定结果并自动完成任务
7. WHEN 调用 `GET /api/v1/knowledge-points/{knowledge_point_id}` 时，THE 系统 SHALL 返回知识点详情及先修知识点
8. WHEN 不携带 JWT 调用任一受保护接口时，THE 系统 SHALL 返回 401
