# 需求文档：艾乐学伴 MVP Day 5 — 学习闭环前端 + 前后端联调

## 简介

本文档定义 Day 5 的前端学习闭环与联调需求。在 Day 4 已完成登录、主界面、对话、任务列表的基础上，Day 5 需要实现“任务学习讲解 + 练习作答 + 状态完成”的执行闭环，并完成关键前后端链路联调。

Day 5 交付标准：可完整跑通“登录 -> 对话提问 -> 任务生成 -> 学习讲解 -> 做题 -> 完成”。

## 术语表

- **Focused_Task**：当前在执行页被选中并进入学习/练习态的任务
- **Task_Detail**：任务详情数据，来源 `GET /api/v1/tasks/{task_id}`
- **Task_Status_Machine**：任务状态流转规则，`pending -> in_progress -> completed`
- **Answer_Submission**：提交练习答案动作，调用 `POST /api/v1/tasks/{task_id}/submit-answer`
- **Execution_Context**：执行页上下文，包含任务、讲解、练习与答题进度
- **Task_Created_Linkage**：对话页创建任务后跳转执行页并定位任务的联动机制

## 需求

### 需求 1：执行页任务聚焦与详情加载

**用户故事：** 作为用户，我希望在执行页选择某个任务后能看到完整学习内容，便于进入学习状态。

#### 验收标准

1. THE `/execution` 页面 SHALL 支持任务卡片点击后进入 `Focused_Task` 状态
2. WHEN 用户进入 `Focused_Task` 状态时，THE Frontend SHALL 调用 `GET /api/v1/tasks/{task_id}` 获取 `Task_Detail`
3. IF `Task_Detail` 拉取失败，THEN THE 页面 SHALL 提供可读错误提示与重试入口
4. IF 未指定 `task_id`，THEN THE 页面 SHALL 默认选择 `in_progress` 优先、`pending` 次优的任务

### 需求 2：任务开始状态自动推进

**用户故事：** 作为用户，我希望开始学习任务后系统自动记录开始状态，无需手工标记。

#### 验收标准

1. WHEN `Focused_Task.status = pending` 且用户进入任务学习区时，THE Frontend SHALL 调用 `PUT /api/v1/tasks/{task_id}/status` 提交 `in_progress`
2. IF 状态更新成功，THEN THE 页面 SHALL 刷新本地任务状态并展示进行中标识
3. IF 状态更新失败，THEN THE 页面 SHALL 阻止后续完成提交并提示重试

### 需求 3：讲解区分段展示

**用户故事：** 作为用户，我希望学习讲解内容按阶段展示，理解更清晰。

#### 验收标准

1. THE 讲解区 SHALL 按“概念 -> 例题 -> 总结”三段结构展示内容
2. IF 后端返回内容不完整，THEN THE Frontend SHALL 使用保底文案或映射策略保证页面可读
3. THE 页面 SHALL 提供“我有疑问”入口并可跳转 `/daily-clearance`，携带当前任务或知识点上下文

### 需求 4：练习题交互（选择/填空）

**用户故事：** 作为用户，我希望在执行页直接完成练习题并获得即时反馈。

#### 验收标准

1. THE 执行页 SHALL 支持选择题单选作答与填空题文本输入
2. THE 页面 SHALL 支持逐题提交或按任务提交（以当前接口能力为准）
3. WHEN 调用 `POST /api/v1/tasks/{task_id}/submit-answer` 后，THE 页面 SHALL 渲染正确/错误结果
4. IF 返回解析内容，THEN THE 页面 SHALL 展示标准解析
5. IF 判定失败或网络异常，THEN THE 页面 SHALL 保留用户输入并允许重试

### 需求 5：任务完成状态推进

**用户故事：** 作为用户，我希望完成练习后任务自动进入完成状态，学习进度可见。

#### 验收标准

1. WHEN 任务满足完成条件时，THE Frontend SHALL 调用 `PUT /api/v1/tasks/{task_id}/status` 提交 `completed`
2. IF 完成更新成功，THEN THE 页面 SHALL 刷新任务分组并将该任务显示在 `completed`
3. IF 完成更新失败，THEN THE 页面 SHALL 保持原状态并提示用户稍后重试

### 需求 6：对话到执行页任务联动

**用户故事：** 作为用户，我希望在对话生成任务后能直接进入该任务执行，减少操作成本。

#### 验收标准

1. IF 对话页出现任务创建提示，THEN THE Frontend SHALL 提供跳转 `/execution` 的入口
2. WHEN 跳转到 `/execution` 时，THE 页面 SHALL 优先加载提示中携带的 `task_id`
3. IF 指定任务不存在或不可访问，THEN THE 页面 SHALL 回退到默认任务选择策略

### 需求 7：诊断页简化版可演示能力

**用户故事：** 作为演示方，我希望 Day 5 提供一个基础可展示的诊断页，支持后续扩展。

#### 验收标准

1. THE `/diagnosis` 页面 SHALL 展示薄弱知识点列表（可来自接口或预置映射）
2. THE 页面 SHALL 提供“生成巩固计划”按钮
3. IF 暂无诊断数据，THEN THE 页面 SHALL 展示空态说明，不出现报错白屏

### 需求 8：前后端联调主链路

**用户故事：** 作为项目负责人，我希望 Day 5 的关键链路都有可复现验证，确保演示闭环稳定。

#### 验收标准

1. WHEN 用户登录成功后，THE 系统 SHALL 正常展示主界面与任务入口
2. WHEN 用户在对话页触发任务创建后，THE 执行页 SHALL 可见新任务
3. WHEN 用户完成练习并提交后，THE 任务状态 SHALL 从 `in_progress` 变为 `completed`
4. THE 联调过程 SHALL 记录并修复关键字段映射与状态同步问题

### 需求 9：鉴权与异常一致性

**用户故事：** 作为系统维护者，我希望 Day 5 新增页面与流程遵循统一鉴权和错误处理策略。

#### 验收标准

1. THE 受保护页面（`/`、`/daily-clearance`、`/execution`、`/diagnosis`） SHALL 仅在登录态访问
2. IF 接口返回 `401`，THEN THE Frontend SHALL 清理 token 并跳转 `/auth/login`
3. THE Day 5 新增页面交互 SHALL 提供 loading/error/empty 三态

### 需求 10：Day 5 闭环验收

**用户故事：** 作为验收人，我希望有明确路径判断 Day 5 是否完成。

#### 验收标准

1. WHEN 按“登录 -> 对话提问 -> 任务生成 -> 学习讲解 -> 做题 -> 完成”执行时，THE 流程 SHALL 可一次走通
2. THE 用户在执行页刷新后 SHALL 能恢复任务上下文或回到可继续执行状态
3. THE Day 5 功能 SHALL 不破坏 Day 4 已完成链路（登录、对话、任务列表）

