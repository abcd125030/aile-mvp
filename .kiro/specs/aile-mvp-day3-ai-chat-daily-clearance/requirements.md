# 需求文档：艾乐学伴 MVP Day 3 — AI 对话引擎与日清旅程后端

## 简介

本文档定义 Day 3 的交付需求，目标是在 Day 2 核心 CRUD 能力之上，实现可演示的 AI 对话引擎与日清旅程后端能力，支持意图识别、问题落库、任务自动生成、会话回放与 AI 内容生成。

交付标准：通过 API 能完成“发送日清消息 -> 流式获得 AI 回复 -> 自动创建学习任务 -> 查询会话历史”的完整链路。

## 术语表

- **LLM_Service**：统一大模型调用服务，封装 provider 差异
- **Qwen_Provider**：千问 `qwen-plus` 的 OpenAI-compatible 接入实现
- **Chat_Session**：一次日清/自由聊对话会话，由 `session_id` 标识
- **Chat_Message**：会话中的单条消息（用户或助手）
- **Intent_Result**：意图识别结构化输出，包含主意图与槽位
- **Daily_Problem_Record**：`daily_problems` 表中的问题记录
- **Auto_Generated_Task**：由日清识别结果自动创建的 `learning_tasks` 记录
- **Content_Package**：`content_packages` 表中的 AI 讲解内容包

## 需求

### 需求 1：统一 LLM 调用层与 Qwen 接入

**用户故事：** 作为后端开发者，我希望有统一的 LLM 调用抽象并默认接入千问 `qwen-plus`，以便 Day 3 快速上线并为后续模型切换预留扩展点。

#### 验收标准

1. THE Backend SHALL 提供统一的 `LLM_Service` 接口，支持非流式与流式调用模式
2. THE Backend SHALL 实现 `Qwen_Provider`，通过 `https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions` 调用模型
3. THE `Qwen_Provider` SHALL 使用 OpenAI-compatible 请求体结构：`model`、`messages`、`temperature`、`stream`
4. THE `Qwen_Provider` SHALL 从配置读取 `LLM_API_KEY`，并通过 `Authorization: Bearer <key>` 发送鉴权头
5. THE Backend SHALL 支持配置项：`LLM_PROVIDER`、`LLM_MODEL`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_TIMEOUT_SECONDS`
6. IF LLM 请求超时或失败，THEN THE `LLM_Service` SHALL 返回可处理的错误对象而非未捕获异常
7. THE Day 3 默认模型配置 SHALL 指向 `qwen-plus`

### 需求 2：日清对话消息接口（SSE）

**用户故事：** 作为前端与用户，我希望发送一条日清消息后能实时看到 AI 回复流式输出，以获得自然对话体验。

#### 验收标准

1. THE Chat_API SHALL 提供 `POST /api/v1/chat/message` 接口
2. THE `POST /api/v1/chat/message` SHALL 要求登录态（JWT 鉴权）
3. THE `POST /api/v1/chat/message` 请求体 SHALL 至少包含：`message`，并支持可选 `session_id` 与 `journey`
4. WHEN 请求未提供 `session_id` 时，THEN THE Chat_API SHALL 自动创建新会话 ID
5. THE `POST /api/v1/chat/message` 响应 SHALL 使用 `text/event-stream`（SSE）
6. THE SSE 输出 SHALL 至少包含 `token` 事件和 `done` 事件
7. THE SSE `done` 事件 SHALL 包含 `session_id` 与 `assistant_message` 汇总文本
8. IF LLM 流式过程中发生错误，THEN THE SSE SHALL 输出错误事件并正常结束连接

### 需求 3：会话与消息历史查询

**用户故事：** 作为前端，我希望能拉取用户会话列表和会话消息历史，以支持 Day 4 对话页回放。

#### 验收标准

1. THE Chat_API SHALL 提供 `GET /api/v1/chat/sessions` 接口
2. THE `GET /api/v1/chat/sessions` SHALL 仅返回当前登录用户的会话
3. THE `GET /api/v1/chat/sessions` 结果 SHALL 包含：`session_id`、`last_message`、`last_active_at`、`message_count`
4. THE `GET /api/v1/chat/sessions` 结果 SHALL 按 `last_active_at` 倒序
5. THE Chat_API SHALL 提供 `GET /api/v1/chat/sessions/{session_id}/messages` 接口
6. THE `GET /api/v1/chat/sessions/{session_id}/messages` SHALL 仅返回当前用户可访问会话的消息
7. THE 消息结构 SHALL 包含：`role`、`content`、`created_at`，并可选返回 `intent`、`knowledge_point_ids`
8. THE 消息列表 SHALL 按创建时间升序
9. IF 会话不存在或不属于当前用户，THEN 接口 SHALL 返回 `404 Not Found` 或 `403 Forbidden`

### 需求 4：意图识别与槽位提取

**用户故事：** 作为系统，我希望把用户自然语言转成结构化意图与槽位，以驱动日清问题管理和任务生成。

#### 验收标准

1. THE Backend SHALL 在对话处理链路中执行意图识别
2. THE 主意图枚举 SHALL 至少支持：`CLARIFY_CONCEPT`、`SOLVE_PROBLEM`、`PLAN_REQUEST`
3. THE 意图结果 SHALL 包含 `primary_intent` 与 `slots`
4. THE `slots` SHALL 支持 `knowledge_point_ids` 字段，类型为数组
5. IF LLM 返回非法主意图，THEN 系统 SHALL 回退为 `CLARIFY_CONCEPT`
6. IF `knowledge_point_ids` 包含不存在的知识点 ID，THEN 系统 SHALL 过滤无效 ID
7. THE 对话链路 SHALL 在响应元数据中返回意图识别结果摘要

### 需求 5：日清问题落库与任务自动生成

**用户故事：** 作为产品负责人，我希望用户表达学习困难后系统自动记录问题并生成可执行任务，以实现 Day 3 的核心价值。

#### 验收标准

1. THE Chat_Service SHALL 在处理用户消息后创建 `daily_problems` 记录
2. THE `daily_problems` 记录 SHALL 写入：`user_id`、`session_id`、`original_utterance`、`intent`、`slots`
3. IF 主意图为 `CLARIFY_CONCEPT` 或 `SOLVE_PROBLEM` 且存在 `knowledge_point_ids`，THEN 系统 SHALL 自动创建学习任务
4. THE 自动创建任务 SHALL 写入 `learning_tasks.source='daily_clearance'`
5. THE 自动创建任务 SHALL 写入 `learning_tasks.source_problem_id = daily_problems.id`
6. THE 自动创建任务状态 SHALL 初始化为 `pending`
7. IF 用户存在 `current_plan_id`，THEN 自动任务 SHALL 归属当前计划
8. IF 用户无当前计划，THEN 系统 SHALL 创建一个新的 `active` 计划并将任务归属该计划
9. WHEN 自动任务创建成功时，THE `daily_problems.resolution_task_id` SHALL 回填该任务 ID
10. THE 对话返回元数据 SHALL 指示是否创建了任务与任务 ID

### 需求 6：AI 内容生成接口

**用户故事：** 作为前端与学习流程，我希望根据知识点快速生成讲解内容包，以支撑“听讲解”环节。

#### 验收标准

1. THE Content_API SHALL 提供 `POST /api/v1/content/generate` 接口
2. THE `POST /api/v1/content/generate` SHALL 要求登录态（JWT 鉴权）
3. THE 请求体 SHALL 至少包含 `knowledge_point_ids`，并支持可选 `style`、`target_minutes`
4. THE 接口 SHALL 调用 `LLM_Service` 生成结构化讲解内容
5. THE 生成结果 SHALL 归一化为 `sections` 数组，元素包含 `type` 与 `content`
6. THE `sections.type` SHALL 至少支持 `text` 与 `example`
7. THE 接口 SHALL 持久化 `content_packages` 记录并返回 `content_package_id`
8. THE 接口成功响应 SHALL 返回：`content_package_id`、`status`、`sections`
9. IF 生成失败，THEN 接口 SHALL 返回可读错误信息并保证数据库状态可追踪

### 需求 7：会话消息持久化

**用户故事：** 作为后端开发者，我希望在不新增数据库表的前提下保存会话消息，满足 MVP 历史回放能力。

#### 验收标准

1. THE Backend SHALL 使用 `user_behavior_events` 持久化会话消息
2. THE 用户消息事件 `event_type` SHALL 使用 `utterance_sent`
3. THE 助手消息事件 `event_type` SHALL 使用 `assistant_replied`
4. THE `event_data` SHALL 至少存储 `role` 与 `content`
5. THE `event_data` MAY 存储 `intent`、`knowledge_point_ids` 等扩展字段
6. THE `session_id` 字段 SHALL 统一使用对话会话 ID 字符串

### 需求 8：鉴权与异常处理一致性

**用户故事：** 作为前后端协作者，我希望 Day 3 新接口在鉴权、错误码、响应结构上与 Day 2 保持一致，降低联调成本。

#### 验收标准

1. THE Day 3 全部业务接口 SHALL 复用 Day 2 的 `Current_User` 鉴权依赖
2. IF 请求缺失或携带无效 Token，THEN 接口 SHALL 返回 `401 Unauthorized`
3. IF 请求参数非法，THEN 接口 SHALL 返回 `422 Unprocessable Entity` 或 `400 Bad Request`
4. IF 资源不存在，THEN 接口 SHALL 返回 `404 Not Found`
5. THE 业务异常响应体 SHALL 维持 `{ "detail": "..." }` 结构

### 需求 9：Day 3 交付验证

**用户故事：** 作为项目负责人，我希望有清晰可执行的验证路径，确认 Day 3 达到冲刺计划交付标准。

#### 验收标准

1. WHEN 调用 `POST /api/v1/chat/message` 并发送“我不懂三角函数”时，THE 接口 SHALL 流式返回 AI 回复文本
2. WHEN 上述请求完成后，THE 数据库 SHALL 新增一条 `daily_problems` 记录
3. WHEN 上述请求识别到有效知识点时，THE 数据库 SHALL 自动新增一条 `learning_tasks` 记录
4. WHEN 调用 `GET /api/v1/chat/sessions` 时，THE 接口 SHALL 返回包含该会话的列表项
5. WHEN 调用 `GET /api/v1/chat/sessions/{session_id}/messages` 时，THE 接口 SHALL 返回至少 1 条用户消息和 1 条助手消息
6. WHEN 调用 `POST /api/v1/content/generate` 并提供知识点 ID 时，THE 接口 SHALL 返回 `content_package_id` 与非空 `sections`
