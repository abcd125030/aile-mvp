# 需求文档：艾乐学伴 MVP Day 4 — 前端核心页面开发

## 简介

本文档定义 Day 4 的前端交付需求。目标是在现有 Day 1-3 基线下，交付可演示的 4 个核心页面：登录、主界面、艾乐对话、学习计划，并完成与后端接口的基础联调。

Day 4 交付标准：前端核心页面可交互，用户可完成“登录 -> 查看主界面 -> 与艾乐对话 -> 查看任务列表”的最小闭环。

## 术语表

- **Auth_Token**：登录成功后返回的 JWT，用于调用受保护接口
- **Current_User_Profile**：当前用户信息，来源 `GET /api/v1/users/me`
- **Current_Plan**：当前活跃学习计划
- **Learning_Task**：计划下的学习任务
- **Chat_Session**：对话会话，由 `session_id` 标识
- **SSE_Stream**：`text/event-stream` 流式返回通道
- **Task_Created_Hint_Card**：对话中“已为你创建学习任务”提示卡片

## 需求

### 需求 1：登录页与认证流程

**用户故事：** 作为学生用户，我希望通过手机号与验证码登录，并在登录后自动进入学习主页。

#### 验收标准

1. THE Frontend SHALL 提供 `/auth/login` 登录页，包含手机号输入、验证码输入与登录按钮
2. THE 登录提交 SHALL 调用 `POST /api/v1/auth/login`
3. IF 登录成功，THEN THE Frontend SHALL 持久化 `Auth_Token` 到 `localStorage`
4. IF 登录成功，THEN THE Frontend SHALL 拉取 `GET /api/v1/users/me` 获取用户详情
5. IF 登录失败（4xx/5xx），THEN THE Frontend SHALL 显示可读错误提示且不丢失用户输入
6. THE 已登录用户刷新页面后 SHALL 保持 `isAuthenticated=true`

### 需求 2：首次登录画像引导

**用户故事：** 作为首次登录用户，我希望在进入系统前补全关键画像信息，以便后续主界面展示目标信息。

#### 验收标准

1. IF `POST /api/v1/auth/login` 返回 `is_new_user=true`，THEN THE Frontend SHALL 展示画像补全引导
2. THE 画像补全表单 SHALL 至少包含：年级、教材版本、目标院校
3. THE Frontend SHALL 使用 `PUT /api/v1/users/me` 提交画像信息
4. IF 更新成功，THEN THE Frontend SHALL 重新拉取 `GET /api/v1/users/me` 以同步最新数据
5. IF 用户非首次登录且画像完整，THEN THE Frontend SHALL 跳过画像引导

### 需求 3：主界面信息展示

**用户故事：** 作为已登录用户，我希望主界面直观看到目标和当前任务，快速进入下一步学习行为。

#### 验收标准

1. THE `/` 主界面 SHALL 展示目标信息区（目标院校、差距分数、倒计时天数）
2. THE 主界面 SHALL 展示当前学习任务卡片（标题、知识点标签、操作按钮）
3. THE 主界面数据 SHALL 来自 `GET /api/v1/users/me` 与计划/任务接口组合查询
4. IF 用户存在进行中任务，THEN 主界面 SHALL 优先显示 `in_progress` 任务
5. IF 无进行中任务但有待完成任务，THEN 主界面 SHALL 显示一个 `pending` 任务
6. IF 无可展示任务，THEN 主界面 SHALL 展示空态引导进入对话页

### 需求 4：主界面导航与入口行为

**用户故事：** 作为用户，我希望通过主界面的入口快速进入对话和任务页面。

#### 验收标准

1. THE 主界面 SHALL 提供“艾乐入口”并导航至 `/daily-clearance`
2. THE 主界面 SHALL 提供“我的计划/任务”入口并导航至 `/execution`
3. THE 当前任务卡片上的动作按钮 SHALL 导航至 `/execution` 并携带任务上下文
4. THE 导航行为 SHALL 在路由切换后保持登录态

### 需求 5：艾乐对话页基础交互

**用户故事：** 作为用户，我希望在对话页发送消息并实时看到艾乐回复。

#### 验收标准

1. THE `/daily-clearance` 页面 SHALL 提供消息列表、输入框、发送按钮
2. THE 用户消息 SHALL 在发送后立即追加到右侧气泡列表
3. THE 页面 SHALL 调用 `POST /api/v1/chat/message` 发送消息
4. THE 对话页 SHALL 正确消费 `SSE_Stream` 并渲染助手侧流式回复
5. THE 助手流式回复 SHALL 呈现逐步增长的“打字”效果
6. IF SSE 连接失败，THEN THE 页面 SHALL 给出失败提示并允许用户重试

### 需求 6：对话历史与会话恢复

**用户故事：** 作为回访用户，我希望进入对话页时能看到最近会话历史。

#### 验收标准

1. THE 对话页进入时 SHALL 调用 `GET /api/v1/chat/sessions`
2. IF 存在最近会话，THEN THE 页面 SHALL 调用 `GET /api/v1/chat/sessions/{session_id}/messages`
3. THE 历史消息 SHALL 按时间正序渲染
4. THE 历史消息项 SHALL 至少展示 `role`、`content`、`created_at`

### 需求 7：任务创建提示卡片

**用户故事：** 作为用户，我希望在对话生成任务时得到明确反馈并可快速查看任务。

#### 验收标准

1. IF `POST /api/v1/chat/message` 的流式元数据标识 `task_created=true`，THEN THE 页面 SHALL 展示 `Task_Created_Hint_Card`
2. THE `Task_Created_Hint_Card` SHALL 显示“已为你创建学习任务”文案
3. THE 卡片 SHALL 提供跳转 `/execution` 的操作入口
4. IF 本次对话未创建任务，THEN 页面 SHALL 不渲染该卡片

### 需求 8：学习计划页任务分组展示

**用户故事：** 作为用户，我希望在计划页按状态清晰查看任务，了解学习进度。

#### 验收标准

1. THE `/execution` 页面 SHALL 展示当前计划标题与状态
2. THE 页面 SHALL 展示任务列表并按状态分组：`in_progress`、`pending`、`completed`
3. THE 页面 SHALL 调用 `GET /api/v1/plans` 和 `GET /api/v1/tasks` 获取数据
4. THE 任务卡片 SHALL 展示标题、类型、知识点标签、预计时长（无时长则显示占位）
5. IF 无计划或无任务，THEN 页面 SHALL 展示空态引导

### 需求 9：登录保护与全局异常一致性

**用户故事：** 作为系统维护者，我希望 Day 4 页面统一遵循鉴权和错误处理策略，降低联调与演示风险。

#### 验收标准

1. THE 受保护页面（`/`、`/daily-clearance`、`/execution`） SHALL 仅在登录态下可访问
2. IF 接口返回 `401`，THEN THE Frontend SHALL 清理 token 并跳转 `/auth/login`
3. THE 页面级数据请求 SHALL 提供 loading、error、empty 三态
4. THE 错误展示 SHALL 使用统一可读文案，不暴露原始异常栈

### 需求 10：Day 4 验证闭环

**用户故事：** 作为项目负责人，我希望有可复现的验证路径，确认 Day 4 达到冲刺计划交付标准。

#### 验收标准

1. WHEN 用户完成登录后，THE 系统 SHALL 跳转主界面并展示用户目标信息
2. WHEN 用户从主界面进入对话页发送消息时，THE 页面 SHALL 显示 AI 流式回复
3. WHEN 对话产生任务创建事件时，THE 页面 SHALL 显示任务创建提示卡片
4. WHEN 用户进入学习计划页时，THE 页面 SHALL 展示按状态分组的任务列表
5. WHEN 用户刷新浏览器时，THE 登录态与核心页面访问能力 SHALL 保持正常
