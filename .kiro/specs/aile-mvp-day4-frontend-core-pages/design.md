# 设计文档：艾乐学伴 MVP Day 4 — 前端核心页面开发

## 概述

Day 4 的目标是完成 Demo 演示链路中的 4 个前端核心页面，并与 Day 2/Day 3 后端能力打通：

- 登录页（手机号 + 验证码 + 首登画像引导）
- 主界面（目标信息 + 当前任务卡片 + 艾乐入口）
- 艾乐对话页（SSE 流式回复 + 任务创建提示）
- 学习计划页（计划信息 + 按状态分组任务列表）

本设计基于以下文档与现状统一落地：

- `艾乐学伴MVP(Demo版)-7天冲刺计划.md` 的 Day 4 范围与交付标准
- `1-艾乐学伴MVP数据库详细设计书.md` 的核心实体关系（`users`、`learning_plans`、`learning_tasks`、`daily_problems`）
- `2-艾乐学伴MVP API接口规范全集 (OpenAPI 3.0).md` 的认证与资源契约
- `3-艾乐学伴MVP后端微服务详细设计书.md` 的登录、计划任务、状态机规则
- `4-艾乐学伴MVP前端应用详细设计书.md` 的路由与状态管理建议
- 现有代码基线（Day 3 已落地 `/api/v1/chat/*`、`/api/v1/plans`、`/api/v1/tasks`、`/api/v1/auth/login`）

## 范围与边界

### 本次实现范围

- 将 Day 1 占位页升级为可交互业务页
- 接入已落地后端接口，不新增后端接口
- 完成登录态持久化、页面导航、基础加载/空态/错误态
- 完成 SSE 文本流式渲染与任务创建提示卡片

### 明确不在 Day 4 范围

- 任务详情学习页与做题闭环（Day 5）
- 诊断报告可视化（Day 5/6）
- 语音输入输出、WebSocket、复杂动画与视觉精修（Day 6）

## 对齐策略（规范与代码差异）

为保证 Day 4 可立即联调，前端优先对齐当前仓库已实现接口：

- 登录：`POST /api/v1/auth/login`
- 当前用户：`GET /api/v1/users/me`，更新画像：`PUT /api/v1/users/me`
- 对话：`POST /api/v1/chat/message`（SSE）、`GET /api/v1/chat/sessions`、`GET /api/v1/chat/sessions/{session_id}/messages`
- 计划与任务：`GET /api/v1/plans`、`GET /api/v1/plans/{plan_id}`、`GET /api/v1/tasks`

说明：OpenAPI 文档中部分接口命名为 `/conversation/*` 与 `/plans/current`；Day 4 前端以仓库现有 `/api/v1/*` 能力为准，减少返工风险。

## 路由与页面信息架构

保留现有路由骨架，完善页面语义：

- `/auth/login` -> `LoginPage`
- `/` -> `HomePage`（主界面）
- `/daily-clearance` -> `DailyClearancePage`（艾乐对话）
- `/execution` -> `ExecutionPage`（学习计划与任务列表）
- `/diagnosis` 保持占位（不在 Day 4 交付范围）

导航策略：

- 未登录访问业务页时跳转 `/auth/login`
- 登录成功后默认跳转 `/`
- 主界面点击“艾乐入口”跳转 `/daily-clearance`
- 主界面点击“当前任务卡片/我的计划”跳转 `/execution`

## 页面级设计

### 1) 登录页（LoginPage）

布局模块：

- 手机号输入框、验证码输入框、登录按钮
- `is_new_user=true` 时弹出首登信息区：年级、教材版本、目标院校（写入 `users.settings.target_college`）

交互流程：

1. 用户输入手机号与验证码
2. 调用 `POST /api/v1/auth/login`
3. 持久化 token，拉取 `GET /api/v1/users/me`
4. 若首登或画像不完整，提交 `PUT /api/v1/users/me`
5. 跳转主界面 `/`

异常处理：

- 表单校验失败：前端即时提示
- 401/400：展示可读错误，不清空手机号
- 网络异常：保留输入并允许重试

### 2) 主界面（HomePage）

布局模块：

- 顶部目标区：目标院校、差距分数、倒计时天数
- 中央任务卡片：任务标题、科目/知识点标签、听讲解按钮、做练习按钮
- 右上角艾乐入口、右下角“我的计划”入口

数据来源：

- 用户画像：`GET /api/v1/users/me`
- 当前计划：优先取 `users.current_plan_id`，再调用 `GET /api/v1/plans/{id}`
- 当前任务：若有任务，优先显示 `in_progress`，其次 `pending`

按钮行为：

- `听讲解` -> 跳转 `/execution` 并附带任务上下文
- `做练习` -> 跳转 `/execution` 并附带任务上下文
- `艾乐入口` -> 跳转 `/daily-clearance`

### 3) 艾乐对话页（DailyClearancePage）

布局模块：

- 消息列表（左助手右用户）
- 输入区（文本框 + 发送按钮）
- 顶部会话标题（艾乐头像 + 名字）

核心机制（SSE）：

1. 发送消息时调用 `POST /api/v1/chat/message`
2. 解析 `text/event-stream` 中 `token`、`metadata`、`done` 事件
3. `token` 持续拼接为助手消息，实现打字效果
4. `metadata.task_created=true` 时在消息流中插入“已为你创建学习任务”提示卡片
5. `done` 后将最终消息固化到会话列表

历史回放：

- 初次进入优先拉取 `GET /api/v1/chat/sessions`
- 有最近会话时拉取 `GET /api/v1/chat/sessions/{session_id}/messages`

### 4) 学习计划页（ExecutionPage）

布局模块：

- 计划头部：标题、状态、创建时间
- 任务分组：进行中 / 待完成 / 已完成
- 任务卡片字段：标题、类型、知识点标签、预计时长

数据来源与映射：

- 计划源：`GET /api/v1/plans` 选 `active` 计划（或最新计划）
- 任务源：`GET /api/v1/tasks?plan_id=<id>`
- 分组规则：按 `status` 分桶，组内按 `due_at` 或 `created_at`

交互：

- 任务卡片点击：保留到本地 `focusedTaskId`，供 Day 5 详情页承接
- 可选状态更新入口：调用 `PUT /api/v1/tasks/{id}/status`

## 前端服务与状态管理设计

在现有 `apiClient`、`useUserStore` 基础上扩展：

- `services/authService.ts`：登录、拉取用户、更新用户画像
- `services/chatService.ts`：SSE 消息发送、会话列表、历史消息查询
- `services/planService.ts`：计划列表/详情、任务列表

新增状态切片（Zustand）：

- `useChatStore`：`sessionId`、`messages`、`isStreaming`、`taskCreatedHint`
- `usePlanStore`：`currentPlan`、`tasksByStatus`、`focusedTaskId`

共享状态原则：

- 用户身份与 token 仅在 `useUserStore`
- 页面临时状态（输入框、loading）放组件本地状态
- 跨页面可复用业务状态放独立 store

## SSE 解析方案

采用浏览器原生 `fetch` + `ReadableStream` 解析：

- 不使用 EventSource（POST 场景不适配）
- 按 `\n\n` 分帧解析事件块
- 兼容中文内容分片，使用 `TextDecoder` 流式解码
- 连接中断时允许用户手动重试，不自动重发上条消息

## 风险与缓解

- 接口字段与文档差异：以当前后端 schema 为准，建立 TS 类型守卫兜底
- SSE 半包/断流：增加事件缓冲区与 `done` 超时保护
- 无 active 计划：主界面展示空态并引导去对话生成任务
- 首登画像缺字段：登录后立即二次拉取用户信息确认写入成功

## Day 4 交付判定

满足以下条件即视为完成：

- 能登录并持久化 token，刷新后保持登录态
- 主界面可展示目标信息与当前任务卡片
- 对话页可发送消息并看到 AI 流式回复
- 对话中任务创建提示可见，计划页可按状态展示任务列表
