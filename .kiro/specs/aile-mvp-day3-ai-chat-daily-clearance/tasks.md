# 实施计划：艾乐学伴 MVP Day 3 — AI 对话引擎与日清旅程后端

## 概述

将 Day 3 设计方案拆解为可执行任务，遵循“LLM 基础设施 -> 对话接口 -> 意图与日清落库 -> 自动任务生成 -> 内容生成 -> 验证”的增量路径。  
本文件用于实现前确认，当前全部任务保持未开始状态。

## 任务

- [x] 1. 搭建 Day 3 公共基础设施
  - [x] 1.1 扩展配置项与环境变量
    - 在 `backend/app/config.py` 增加 `LLM_PROVIDER`、`LLM_MODEL`、`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_TIMEOUT_SECONDS`
    - 默认 provider 设为 `qwen`，默认模型设为 `qwen-plus`
    - 补充 `.env.example` 或 README 的 Day 3 配置说明（禁止将真实 key 提交入仓库）
    - _需求: 1.5, 1.7_

  - [x] 1.2 新增 LLM 抽象与 Qwen Provider
    - 创建 `services/llm/base.py` 定义统一接口（chat + stream）
    - 创建 `services/llm/qwen_provider.py` 实现 DashScope compatible-mode 调用
    - 创建 `services/llm/service.py` 负责 provider 选择、超时控制、错误包装
    - _需求: 1.1, 1.2, 1.3, 1.4, 1.6_

- [x] 2. 新增 Day 3 数据访问层
  - [x] 2.1 创建日清问题与内容包 Repository
    - 新建 `daily_problem_repository.py`，实现创建问题、回填解决任务 ID
    - 新建 `content_package_repository.py`，实现内容包创建与查询
    - _需求: 5.1, 5.2, 5.9, 6.7_

  - [x] 2.2 创建会话消息 Repository（复用 user_behavior_events）
    - 新建 `user_behavior_event_repository.py`，实现写入消息事件
    - 实现按用户聚合会话列表、按会话查询消息明细
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.7, 3.8, 7.1, 7.2, 7.3, 7.4, 7.6_

- [x] 3. 实现意图识别与槽位提取服务
  - [x] 3.1 新增 `intent_service.py`
    - 基于 LLM 输出 `primary_intent` 与 `slots`
    - 规范化主意图枚举并过滤非法知识点 ID
    - 增加模型失败时的规则兜底策略
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [x] 4. 实现日清编排与自动任务生成
  - [x] 4.1 新增 `daily_clearance_service.py`
    - 创建 `daily_problems` 记录
    - 根据意图与知识点决定是否自动创建任务
    - 处理“无当前计划时自动创建 active 计划”的归属逻辑
    - _需求: 5.1, 5.2, 5.3, 5.7, 5.8_

  - [x] 4.2 集成任务创建与问题回填
    - 调用现有计划/任务服务或仓储创建 `learning_tasks`
    - 设置任务字段：`source=daily_clearance`、`source_problem_id`、`pending`
    - 回填 `daily_problems.resolution_task_id`
    - _需求: 5.4, 5.5, 5.6, 5.9, 5.10_

- [x] 5. 实现对话服务与 SSE 输出
  - [x] 5.1 新增 `chat_service.py`
    - 编排用户消息持久化 -> 意图识别 -> 日清落库/任务生成 -> LLM 回复
    - 将用户与助手消息分别写入 `user_behavior_events`
    - _需求: 2.3, 2.4, 4.1, 5.1, 7.2, 7.3, 7.4_

  - [x] 5.2 新增 `api/chat.py` 与 `schemas/chat.py`
    - 实现 `POST /api/v1/chat/message`（SSE）
    - 实现 `GET /api/v1/chat/sessions`
    - 实现 `GET /api/v1/chat/sessions/{session_id}/messages`
    - 保证接口鉴权、响应结构与错误码一致
    - _需求: 2.1, 2.2, 2.5, 2.6, 2.7, 2.8, 3.1, 3.2, 3.5, 3.6, 3.9, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 6. 实现 AI 内容生成接口
  - [x] 6.1 新增 `content_generation_service.py`
    - 基于 `knowledge_point_ids` 调用 LLM 生成 `sections`
    - 归一化输出类型为 `text`/`example`
    - _需求: 6.3, 6.4, 6.5, 6.6_

  - [x] 6.2 新增 `api/content.py` 与 `schemas/content.py`
    - 实现 `POST /api/v1/content/generate`
    - 写入 `content_packages` 并返回 `content_package_id`、`status`、`sections`
    - _需求: 6.1, 6.2, 6.7, 6.8, 6.9_

- [x] 7. 路由注册与文档补充
  - [x] 7.1 注册 Day 3 新路由
    - 在 `backend/app/api/__init__.py` 挂载 `chat` 与 `content` router
    - _需求: 2.1, 3.1, 6.1_

  - [x] 7.2 补充开发文档
    - 更新 README 或后端说明，新增 Day 3 环境变量与调试步骤
    - 明确本地演示使用 qwen-plus 与配置方式
    - _需求: 1.5, 1.7, 9.1_

- [ ] 8. 验证与质量检查
  - [ ] 8.1 最小链路联调验证
    - 验证 chat SSE、日清落库、自动任务生成、会话历史查询、内容生成接口
    - _需求: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [x] 8.2 运行诊断与修复
    - 使用 `GetDiagnostics` 检查 Day 3 新增/修改文件
    - 修复可快速定位的语法与类型错误
    - _需求: 8.1, 8.2, 8.3, 8.4, 8.5_

## 备注

- 按你的要求，`tasks.md` 确认后再进入代码实现阶段
- Day 3 首版以“稳定演示闭环”为优先，不引入 WebSocket 与多模型路由复杂度
- `8.1` 中“代码与测试验证”已完成；“本机端到端联调”受当前执行环境缺少 Docker 命令限制，需在具备 Docker 的机器上按 README 步骤执行 smoke 验证。
