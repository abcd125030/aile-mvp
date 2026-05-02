## 第一部分：用户、会话与计划任务接口

### 1. 引言

#### 1.1 文档概述

**本文档是艾乐学伴MVP 1.0的权威接口规范，使用OpenAPI 3.0格式定义。它为前端、后端及AI服务间的通信提供了精确、可执行的技术契约。所有接口请求与响应的数据结构均与《数据库详细设计书 (DDL)》中定义的表字段严格对齐，确保数据在系统内流转的一致性。**

#### 1.2 基础约定
- **Base URL**: **https://api.ailestudy.com/v1**
- **认证**: 除登录接口外，所有请求需在Header中包含 **Authorization: Bearer <jwt_token>**。
- **数据格式**: 请求与响应主体均使用 **application/json**。
- **时间格式**: 所有时间字段均使用ISO 8601格式的UTC时间字符串，例如：**2023-10-26T10:30:00Z**。

#### 1.3 全局响应结构

**所有接口均返回标准HTTP状态码。对于错误响应，使用统一的错误体格式：**

```json
{
  "code": "ERROR_CODE",
  "message": "可读的错误描述，可供前端直接显示给用户",
  "details": {} // 可选，用于调试的额外信息
}
```

**常见错误码：**
- **401 UNAUTHORIZED**: Token无效或缺失。
- **403 FORBIDDEN**: 权限不足。
- **404 NOT_FOUND**: 资源不存在。
- **422 UNPROCESSABLE_ENTITY**: 请求参数验证失败。
- **500 INTERNAL_SERVER_ERROR**: 服务器内部错误。

---

### 2. 用户与认证接口

#### 2.1 手机号登录/注册
- **描述**: 通过手机验证码登录。如果手机号未注册，则自动注册。
- **路径**: **POST** **/auth/login**
- **请求体**:

```json
{
  "phone": "13800138000",
  "sms_code": "123456" // 6位数字验证码
}
```
- **响应体 (200 OK)**:

```json
{
  "user": {
    "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    "phone": "13800138000",
    "nickname": "",
    "grade": "高一",
    "textbook_version": "人教版A版",
    "settings": {}
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", // JWT，有效期7天
  "is_new_user": false // 标识此次是否为首次注册
}
```
- **业务规则**:
- **验证码需由独立的短信服务发送，本接口仅负责校验。**
- **is_new_user**为 **true** **时，前端应引导用户完善个人信息（年级、教材）。**

#### 2.2 获取当前用户信息
- **描述**: 获取已登录用户的详细信息及当前学习上下文。
- **路径**: **GET** **/users/me**
- **响应体 (200 OK)**:

```json
{
  "id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
  "phone": "13800138000",
  "nickname": "艾学同学",
  "grade": "高一",
  "textbook_version": "人教版A版",
  "settings": {
    "notification": true,
    "theme": "light"
  },
  "current_plan_id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12",
  "current_plan_snapshot": { // 来自learning_plans.snapshot的简化视图
    "title": "函数模块巩固计划",
    "status": "active"
  }
}
```

#### 2.3 更新用户信息
- **描述**: 更新用户昵称、年级、教材、设置等。手机号不可通过此接口修改。
- **路径**: **PATCH** **/users/me**
- **请求体 (所有字段均为可选)**:

```json
{
  "nickname": "新昵称",
  "grade": "高二",
  "textbook_version": "北师大版",
  "settings": {
    "notification": false
  }
}
```
- **响应体 (200 OK)**: 返回更新后的完整用户信息，同 **GET /users/me**。

---

### 3. 会话与上下文接口

#### 3.1 获取会话上下文 (PIOPPE决策入口)
- **描述**: 核心接口。应用启动时调用，触发PIOPPE引擎决策，返回用户当前应进入的旅程、问候语及可能的干预建议。
- **路径**: **GET** **/session/context**
- **响应体 (200 OK)**:

```json
{
  "journey": "DAILY_CLEARANCE", // PIOPPE决策的旅程。枚举：DAILY_CLEARANCE, TASK_EXECUTION, DIAGNOSIS, FREE_CHAT
  "greeting": {
    "text": "晚上好，艾学同学！今天函数学得怎么样？有什么新问题想聊聊吗？",
    "audio_url": "https://cdn.ailestudy.com/audio/greeting_123.wav" // 可选，AI生成的问候语音
  },
  "suggestions": [ // 可选的旅程建议卡片，用于启动页
    {
      "type": "journey_card",
      "title": "继续未完成任务",
      "description": "你还有一个‘复合函数单调性’任务正在进行中。",
      "journey": "TASK_EXECUTION",
      "action_params": { "task_id": "task_xxx" } // 跳转参数
    }
  ],
  "urgent_intervention": null // 若非空，表示有强打断干预，前端必须立即处理
}
```
- **业务规则**:
- **PIOPPE引擎综合用户最后学习时间、未完成任务、历史完成率等因素进行决策。**
- **若** **journey** **为** **DAILY_CLEARANCE**，前端应直接导航至日清界面。

#### 3.2 上报用户行为事件
- **描述**: 前端上报用户的关键交互事件，用于动机状态分析和数据收集。
- **路径**: **POST** **/events**
- **请求体**:

```json
{
  "session_id": "sess_abcdef", // 前端生成的会话ID
  "event_type": "task_start", // 枚举: task_start, task_submit, help_request, content_play, utterance_sent...
  "event_data": { // 自由格式，但鼓励结构化
    "task_id": "task_xxx",
    "timestamp_client": 1620000000000
  }
}
```
- **响应体 (202 Accepted)**: 空。本接口为异步处理，保证接收即可。

---

### 4. 学习计划与任务接口

#### 4.1 获取当前学习计划
- **描述**: 获取用户当前活跃的学习计划及其下的所有任务。
- **路径**: **GET** **/plans/current**
- **响应体 (200 OK)**:

```json
{
  "plan": {
    "id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12",
    "title": "函数模块巩固计划",
    "status": "active",
    "version": 2,
    "created_at": "2023-10-25T14:30:00Z"
  },
  "tasks": [
    {
      "id": "c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a13",
      "title": "掌握复合函数单调性判断",
      "type": "practice",
      "status": "pending",
      "source": "daily_clearance",
      "source_problem_id": "prob_xxx", // 关联的“日清”问题ID
      "estimated_minutes": 15,
      "knowledge_point_ids": ["kp_101", "kp_102"],
      "metadata": {
        "difficulty": 0.6,
        "exercise_ids": ["ex_1", "ex_2"]
      },
      "due_at": null,
      "started_at": null,
      "completed_at": null
    }
    // ... 其他任务
  ]
}
```
- **业务规则**:
- **返回的任务按** **status** **和** **due_at** **排序：**in_progress **->** **pending** **->** **completed**。
- **如果用户没有活跃计划，**plan **字段为** **null**，**tasks** **为空数组。**

#### 4.2 创建学习任务
- **描述**: 由“日清”或“诊断”旅程调用，将规划引擎生成的任务草稿正式加入当前计划。
- **路径**: **POST** **/tasks**
- **请求体**:

```json
{
  "plan_id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a12", // 必须属于当前用户
  "title": "掌握复合函数单调性判断",
  "type": "practice",
  "source": "daily_clearance",
  "source_problem_id": "prob_xxx", // 可选
  "estimated_minutes": 15,
  "knowledge_point_ids": ["kp_101", "kp_102"],
  "metadata": {
    "difficulty": 0.6,
    "exercise_ids": ["ex_1", "ex_2"],
    "pedagogical_strategy": "worked_example"
  }
}
```
- **响应体 (201 Created)**:

```json
{
  "id": "c2eebc99-9c0b-4ef8-bb6d-6bb9bd380a13",
  "created_at": "2023-10-26T10:30:00Z"
}
```

#### 4.3 更新任务状态
- **描述**: 更新任务的 **status**、**started_at**、**completed_at**。这是驱动任务状态机的核心接口。
- **路径**: **PATCH** **/tasks/{task_id}**
- **请求体 (支持部分更新)**:

```json
{
  "status": "in_progress" // 或 "completed", "skipped"
}
```
- **业务规则 (必须在后端强制实现)**:
- **当** **status** **从** **pending** **变为** **in_progress** **时，自动将** **started_at** **设置为当前时间。**
- **当** **status** **变为** **completed** **时，自动将** **completed_at** **设置为当前时间，并触发内容生成（异步）。**
- **状态流转必须合法：**pending **->** **in_progress** **->** **completed**。**skipped** **可从** **pending** **或** **in_progress** **直接跳转。**

#### 4.4 为任务请求帮助 (触发内容生成)
- **描述**: 用户在任务执行中点击“求助”，触发AI生成讲解。这是一个异步接口，调用后应通过WebSocket监听生成结果。
- **路径**: **POST** **/tasks/{task_id}/help**
- **请求体 (可选，可提供更详细的卡点信息)**:

```json
{
  "diagnosis": "卡在求导后的符号判断上。"
}
```
- **响应体 (202 Accepted)**:

```json
{
  "help_session_id": "help_sess_xyz",
  "message": "已收到求助，正在准备讲解..."
}
```
- **后续流程**:
- **后端触发内容生成服务。**
- **通过WebSocket向该用户连接推送** **CONTENT_GENERATION_UPDATE** **消息。**
- **生成完成后，推送** **CONTENT_PACKAGE_READY** **消息，其中包含** **content_package_id**。
- **前端使用** **content_package_id** **调用** **GET /content/packages/{package_id}** **获取内容并播放。**

---

### 5. 下一步：API接口规范第二部分

**以上接口涵盖了用户、会话、计划与任务的核心生命周期。它们与已完成的数据库设计（users, learning_plans, learning_tasks表）完全对应，为MVP的核心学习闭环（启动->日清->计划->执行）提供了完整的后端支持。**

**基于此，下一个需要撰写的文档是第二部分：日清、诊断与内容接口。该部分将定义：**
- **日清旅程**：提交问题、多轮对话、获取解决方案的接口。
- **诊断旅程**：上传试卷、获取诊断报告的接口。
- **内容服务**：获取AI生成内容包的接口。
- **WebSocket**：实时消息的详细协议。

**这将是前后端与AI服务集成的最关键部分。**

---
## 第二部分：日清、诊断与内容接口

### 1. 引言

**本部分是API接口规范的第二卷，聚焦于定义“日清”、“诊断”两大核心旅程的交互接口，以及“内容”的获取与实时通信协议。这些接口是实现智能体“感知-决策-创造”能力的关键通信枢纽，与《数据库详细设计书 (DDL)》中定义的** **daily_problems**，**diagnosis_reports**，**content_packages** **等表紧密对应。**

### 2. 日清旅程接口

#### 2.1 提交用户话语（核心感知接口）
- **描述**: 核心接口。用户在“日清”或“自由聊”旅程中，每说一句话（或输入一段文本），前端调用此接口。它将用户原始输入提交给感知与理解服务，获得意图、情感、实体等结构化理解结果，并触发对话引擎生成学伴的下一句回复。
- **路径**: **POST** **/conversation/utterance**
- **请求体**:

```json
{
  "session_id": "sess_abc123", // 本次“日清”会话的唯一ID，由前端在进入旅程时生成
  "journey": "DAILY_CLEARANCE", // 当前旅程。枚举：DAILY_CLEARANCE, FREE_CHAT
  "utterance": "复合函数单调性不太懂。", // 用户输入的文本
  "audio_url": "https://cdn.ailestudy.com/audio/user_123.wav", // 可选，用户语音文件的URL
  "context": { // 当前对话上下文，对多轮理解至关重要
    "current_problems": ["prob_001", "prob_002"], // 本次会话中已澄清的问题ID列表
    "conversation_history": [ // 近期的对话历史，用于LLM理解上下文
      {"role": "user", "content": "第一个问题..."},
      {"role": "assistant", "content": "具体是哪里不懂？"}
    ]
  }
}
```
- **响应体 (200 OK)**:

```json
{
  "request_id": "req_789xyz",
  "understanding": { // 来自“感知与理解服务”的结构化输出
    "primary_intent": "CLARIFY_CONCEPT",
    "intents": [ // 可能识别出多个意图，按置信度排序
      {"intent": "CLARIFY_CONCEPT", "confidence": 0.92, "slots": {"concept": "composite_function_monotonicity", "aspect": "同增异减法则"}},
      {"intent": "REQUEST_EXAMPLE", "confidence": 0.45, "slots": {}}
    ],
    "extracted_entities": [
      {"type": "KNOWLEDGE_POINT", "id": "kp_comp_func_mono", "name": "复合函数的单调性", "confidence": 0.98}
    ],
    "inferred_state": {
      "cognitive_confusion": 0.8,
      "emotional_sentiment": "confused"
    },
    "suggested_actions": ["REQUEST_CLARIFICATION"] // 建议后端对话引擎执行的动作
  },
  "ai_response": { // 来自“对话引擎”的回复
    "text": "具体是判断单调性的‘同增异减’法则不清楚，还是不知道如何分解复合函数？",
    "audio_url": "https://cdn.ailestudy.com/audio/ai_resp_456.wav" // 可选，AI合成语音
  },
  "problem_summary": { // 如果此轮对话澄清了一个问题，返回其摘要
    "problem_id": "prob_003", // 系统为此问题生成的唯一ID，用于前端追踪
    "description": "不理解复合函数单调性判断中的‘同增异减’法则",
    "is_clarified": false // 是否已澄清完毕。为false时，学伴会继续追问。
  }
}
```
- **业务规则**:
- **多轮对话管理**：若 **problem_summary.is_clarified** **为** **false**，前端应将 **problem_summary.problem_id** **加入请求体** **context.current_problems**，并继续对话。当其为 **true** **时，表示该问题已澄清完毕，可加入“已澄清问题列表”。**
- **问题去重**：后端需在会话 (**session_id**) 内，对相似意图的问题进行去重和归并。

#### 2.2 获取解决方案建议
- **描述**: 用户点击“我讲完了”后，前端提交所有已澄清的问题列表，请求决策与规划服务生成解决方案建议（快速讲解或练习任务）。
- **路径**: **POST** **/daily-clearance/resolutions**
- **请求体**:

```json
{
  "session_id": "sess_abc123",
  "clarified_problems": [ // 来自前端的、已澄清的问题列表
    {
      "problem_id": "prob_001",
      "intent": "CLARIFY_CONCEPT",
      "slots": {"concept": "composite_function_monotonicity"}
    }
  ]
}
```
- **响应体 (200 OK)**:

```json
{
  "session_id": "sess_abc123",
  "resolutions": [
    {
      "type": "QUICK_EXPLAIN",
      "target_problem_id": "prob_001",
      "summary": "复合函数‘同增异减’法则的核心是...",
      "content_preview": "如果内外层函数单调性相同，则复合函数为增函数；否则为减函数。", // 文本摘要
      "estimated_duration_seconds": 60
    },
    {
      "type": "PRACTICE_TASK",
      "target_problem_id": "prob_001",
      "task_draft": { // 这是一个“任务草稿”，用户确认后需调用 POST /tasks 创建正式任务
        "title": "掌握复合函数单调性判断",
        "type": "practice",
        "source": "daily_clearance",
        "source_problem_id": "prob_001",
        "estimated_minutes": 15,
        "knowledge_point_ids": ["kp_comp_func_mono"],
        "metadata": {
          "difficulty": 0.6,
          "exercise_ids": ["ex_comp_mono_1", "ex_comp_mono_2"]
        }
      }
    }
  ]
}
```

---

### 3. 诊断旅程接口

#### 3.1 上传试卷文件（启动诊断）
- **描述**: 用户拍照、选择图片或上传PDF后，将文件提交至服务器，启动异步诊断流程。
- **路径**: **POST** **/diagnosis/upload**
- **Content-Type**: **multipart/form-data**
- **请求参数**:
- **file** **(File): 试卷文件，支持 `jpg`、`png`、`pdf`。大小限制5MB。**
- **title** **(String, Optional): 用户为此次诊断命名的标题，如“期中试卷”。**
- **响应体 (202 Accepted)**:

```json
{
  "diagnosis_job_id": "job_diag_xyz",
  "message": "试卷已上传，正在识别与分析中，请稍候..."
}
```
- **后续流程**:
- **前端应通过WebSocket监听** **DIAGNOSIS_UPDATE** **和** **DIAGNOSIS_READY** **消息，或轮询** **GET /diagnosis/reports/{id}/status**。
- **诊断完成后，后端会创建一个** **diagnosis_reports** **记录。**

#### 3.2 获取诊断报告详情
- **描述**: 根据诊断报告ID，获取完整的诊断报告详情。
- **路径**: **GET** **/diagnosis/reports/{report_id}**
- **响应体 (200 OK)**:

```json
{
  "id": "report_123",
  "user_id": "user_xxx",
  "title": "高一函数单元测试诊断报告",
  "created_at": "2023-10-26T11:00:00Z",
  "summary": {
    "total_score": 85,
    "total_points": 100,
    "correct_count": 17,
    "knowledge_weaknesses": ["kp_comp_func_mono"]
  },
  "detailed_analysis": {
    "items": [
      {
        "item_index": 1,
        "user_answer": "A",
        "correct_answer": "B",
        "is_correct": false,
        "knowledge_point_ids": ["kp_func_def"],
        "error_type": "concept_confusion"
      }
    ],
    "knowledge_summary": {
      "kp_comp_func_mono": {
        "correct_count": 0,
        "total_count": 3,
        "mastery": 0.0,
        "recommendation": "需重点巩固"
      }
    }
  },
  "generated_plan_id": null // 如果已生成计划，这里会有ID
}
```

#### 3.3 基于诊断报告生成学习计划
- **描述**: 用户在查看诊断报告后，请求系统为其薄弱点生成一个专项提升计划。
- **路径**: **POST** **/diagnosis/reports/{report_id}/generate-plan**
- **请求体 (可选)**:

```json
{
  "focus_knowledge_point_ids": ["kp_comp_func_mono"] // 可选，指定要针对的知识点，不传则使用报告推荐的全部薄弱点
}
```
- **响应体 (202 Accepted)**:

```json
{
  "plan_job_id": "job_plan_abc",
  "message": "正在为你生成专项提升计划..."
}
```
- **后续流程**:
- **触发决策与规划服务。**
- **生成完成后，会创建一个新的** **learning_plans** **记录，并将其ID更新到** **diagnosis_reports.generated_plan_id** **字段。**
- **前端可通过WebSocket监听** **DIAGNOSIS_UPDATE** **消息，或轮询报告详情接口，检查** **generated_plan_id** **字段是否被填充。**

---

### 4. 内容服务接口

#### 4.1 获取内容包
- **描述**: 根据内容包ID，获取其清单(manifest)，用于前端渲染和播放。
- **路径**: **GET** **/content/packages/{package_id}**
- **响应体 (200 OK)**:

```json
{
  "id": "cp_123456",
  "status": "ready",
  "manifest": [
    {
      "type": "text",
      "content": "我们先回顾一下复合函数求导法则...",
      "duration": 0
    },
    {
      "type": "image",
      "url": "https://cdn.ailestudy.com/images/graph_123.svg",
      "caption": "图1：函数f和g的图像",
      "duration": 5
    },
    {
      "type": "audio",
      "url": "https://cdn.ailestudy.com/audio/explain_123.mp3",
      "duration": 30
    }
  ],
  "associated_task_id": "task_xxx",
  "created_at": "2023-10-26T10:35:00Z"
}
```
- **业务规则**:
- **manifest** **中的资源 URL 应已携带鉴权参数或为临时签名 URL，有效期内前端可直接加载。**

---

### 5. WebSocket实时通信协议

#### 5.1 连接建立
- **URL**: **wss://api.ailestudy.com/v1/realtime?token=<jwt_token>**
- **心跳**: 客户端每30秒发送一次 **PING**，服务端回复 **PONG**。

#### 5.2 核心消息类型（服务端 -> 客户端）
- **内容生成进度更新**

```json
{
  "type": "CONTENT_GENERATION_UPDATE",
  "package_id": "cp_123456",
  "status": "generating", // 枚举：generating, ready, failed
  "progress": 0.65, // 0~1
  "eta_seconds": 3
}
```
- **内容包就绪通知**

```json
{
  "type": "CONTENT_PACKAGE_READY",
  "package_id": "cp_123456"
}
```
- **前端动作**：收到此消息后，立即调用 **GET /content/packages/{package_id}** **获取内容并播放。**
- **PIOPPE主动介入**

```json
{
  "type": "PIOPPE_INTERVENTION",
  "intervention_id": "intv_001",
  "level": "SUGGESTION", // 等级：SUGGESTION（建议）, REMINDER（提醒）, INTERRUPTION（强打断）
  "action": "SUGGEST_BREAK",
  "parameters": {"duration_s": 300},
  "narration": "连续学习50分钟了，站起来活动一下？",
  "options": [ // 用户可选的回应
    {"id": "accept", "text": "休息5分钟"},
    {"id": "decline", "text": "继续学习"}
  ],
  "expires_in_s": 30 // 此介入的有效期，超时未选择则自动失效
}
```
- **前端动作**：根据 **level** **渲染相应UI（气泡/卡片/弹窗）。用户选择后，需调用** **POST /interventions/{intervention_id}/respond** **上报选择。**
- **诊断任务更新**

```json
{
  "type": "DIAGNOSIS_UPDATE",
  "job_id": "job_diag_xyz",
  "status": "OCR_PROCESSING", // 或 AI_ANALYZING, REPORT_GENERATING
  "progress": 0.4
}
```
- **诊断报告就绪**

```json
{
  "type": "DIAGNOSIS_READY",
  "report_id": "report_123"
}
```

#### 5.3 核心消息类型（客户端 -> 服务端）
- **响应PIOPPE介入**

```json
{
  "type": "INTERVENTION_RESPONSE",
  "intervention_id": "intv_001",
  "option_id": "accept" // 对应服务端下发options中的id
}
```
- **上报“没听懂”反馈**

```json
{
  "type": "CONTENT_FEEDBACK",
  "package_id": "cp_123456",
  "feedback_type": "NOT_UNDERSTAND"
}
```

### 6. 后续：API接口规范第三部分

**以上接口定义了“日清”、“诊断”、“内容”三大模块以及与前端实时通信的完整契约。结合第一部分，MVP核心业务的功能性接口已基本覆盖。**

**后续内容为第三部分：辅助接口与附录。这部分将收尾剩余的必要接口，并完善整个API体系的全局定义，包括：**
- **知识图谱接口：查询知识点、题目详情。**
- **数据看板接口：用户学习数据统计。**
- **文件上传接口：通用文件上传（用于头像等）。**
- **全局附录：完整的枚举值列表、错误码表、分页与排序规范。**

---
## 第三部分：辅助接口与附录

### 1. 知识图谱与资源接口

#### 1.1 查询知识点详情
- **描述**: 根据知识点ID，查询其详细信息及关联的题目。
- **路径**: **GET** **/knowledge-points/{kp_id}**
- **响应体 (200 OK)**:

```json
{
  "id": "kp_comp_func_mono",
  "name": "复合函数的单调性",
  "description": "复合函数y=f[g(x)]的单调性遵循‘同增异减’法则...",
  "prerequisite_ids": ["kp_func_mono", "kp_comp_func"],
  "difficulty": 0.7,
  "related_exercises": [ // 关联的题目（可分页）
    {
      "id": "ex_comp_mono_1",
      "stem": "已知函数f(x)在区间[0, +∞)上单调递增，g(x)=x^2，则复合函数h(x)=f(g(x))在区间________上单调递减。",
      "difficulty": 0.6
    }
  ]
}
```

#### 1.2 搜索题目
- **描述**: 根据知识点、难度等条件筛选题目。
- **路径**: **GET** **/exercises**
- **查询参数**:
- **knowledge_point_id** **(String, Optional): 按知识点筛选。**
- **difficulty_min** **(Number, Optional): 最低难度。**
- **difficulty_max** **(Number, Optional): 最高难度。**
- **limit** **(Integer, Optional): 返回数量，默认10。**
- **响应体 (200 OK)**:

```json
{
  "exercises": [
    {
      "id": "ex_comp_mono_1",
      "stem": "已知函数f(x)...",
      "options": null,
      "correct_answer": "(-∞, 0]",
      "knowledge_point_ids": ["kp_comp_func_mono"],
      "difficulty": 0.6
    }
  ],
  "total_count": 25
}
```

---

### 2. 学习数据与统计接口

#### 2.1 获取用户学习概览（数据看板）
- **描述**: 用于“学习看板”或“个人主页”，展示用户近期学习成果的统计摘要。
- **路径**: **GET** **/users/me/learning-overview**
- **查询参数**:
- **days** **(Integer, Optional): 统计最近多少天的数据，默认7天。**
- **响应体 (200 OK)**:

```json
{
  "time_range": "last_7_days",
  "stats": {
    "total_focused_minutes": 325, // 总专注学习时长
    "tasks_completed": 12, // 完成任务数
    "problems_clarified": 8, // 澄清问题数
    "current_streak_days": 3 // 当前连续学习天数
  },
  "knowledge_heatmap": { // 知识点掌握热力图（简化）
    "kp_comp_func_mono": 0.4,
    "kp_func_def": 0.9
  }
}
```

#### 2.2 获取任务完成历史
- **描述**: 以时间线形式返回用户已完成的任务记录。
- **路径**: **GET** **/users/me/completed-tasks**
- **查询参数**:
- **start_date** **(String, Optional): ISO日期，如** **2023-10-01**。
- **end_date** **(String, Optional): ISO日期。**
- **limit** **(Integer, Optional): 默认20。**
- **响应体 (200 OK)**:

```json
{
  "tasks": [
    {
      "id": "task_123",
      "title": "掌握复合函数单调性判断",
      "completed_at": "2023-10-26T10:30:00Z",
      "type": "practice",
      "knowledge_point_ids": ["kp_comp_func_mono"]
    }
  ]
}
```

---

### 3. 文件上传接口

#### 3.1 通用文件上传
- **描述**: 用于上传用户头像、聊天图片等通用文件。返回可用于访问的URL。
- **路径**: **POST** **/files/upload**
- **Content-Type**: **multipart/form-data**
- **请求参数**:
- **file** **(File): 要上传的文件。**
- **purpose** **(String): 上传用途。枚举：** **avatar**（头像）、**chat_image**（聊天图片）、**other**。
- **响应体 (201 Created)**:

```json
{
  "id": "file_xyz",
  "url": "https://cdn.ailestudy.com/files/avatar_user_123.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 204800
}
```

---

### 4. 附录

#### 4.1 全局枚举值列表

**以下枚举值在整个API体系中通用，后端必须严格校验。**

**任务状态 (`LearningTask.status`)**
- `pending`: 待开始
- `in_progress`: 进行中
- `completed`: 已完成
- `skipped`: 已跳过

**任务来源 (`LearningTask.source`)**
- `scheduled`: 计划生成
- `daily_clearance`: 日清产生
- `diagnosis`: 诊断产生

**内容包状态 (`ContentPackage.status`)**
- `generating`: 生成中
- `ready`: 就绪
- `failed`: 生成失败

**用户旅程 (`journey`)**
- `DAILY_CLEARANCE`: 日清
- `TASK_EXECUTION`: 任务执行
- `DIAGNOSIS`: 诊断
- `FREE_CHAT`: 自由聊

**PIOPPE介入等级 (`PioppeIntervention.level`)**
- `SUGGESTION`: 建议（非模态气泡）
- `REMINDER`: 提醒（模态卡片）
- `INTERRUPTION`: 强打断（必须响应的弹窗）

#### 4.2 全局错误码表

| **HTTP状态码** | **错误码 (code)**         | **描述**                               | **前端建议处理方式**                       |
| -------------------- | ------------------------------- | -------------------------------------------- | ------------------------------------------------ |
| **400**        | **INVALID_PARAMETER**     | **请求参数格式错误**                   | **检查输入，提示用户。**                   |
| **401**        | **UNAUTHORIZED**          | **未提供有效的认证Token**              | **引导用户重新登录。**                     |
| **403**        | **FORBIDDEN**             | **无权访问该资源**                     | **提示用户权限不足。**                     |
| **404**        | **RESOURCE_NOT_FOUND**    | **请求的资源不存在**                   | **检查ID是否正确，提示“内容不存在”。**   |
| **409**        | **RESOURCE_CONFLICT**     | **资源冲突（如重复创建）**             | **提示用户“已存在，无需重复操作”。**     |
| **422**        | **UNPROCESSABLE_ENTITY**  | **业务逻辑校验失败（如状态流转非法）** | **显示后端返回的message。**                |
| **429**        | **RATE_LIMIT_EXCEEDED**   | **请求过于频繁**                       | **提示用户稍后再试。**                     |
| **500**        | **INTERNAL_SERVER_ERROR** | **服务器内部错误**                     | **提示“系统开小差，请稍后重试”。**       |
| **503**        | **SERVICE_UNAVAILABLE**   | **依赖服务不可用（如AI服务超时）**     | **提示“学伴正在思考，请稍候”，可重试。** |

#### 4.3 分页与排序规范
- **支持分页的接口，使用查询参数** **page** **(从1开始) 和** **size** **(默认20，最大100)。**
- **响应体中包含分页信息：**

```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```
- **支持排序的接口，使用查询参数** **sort_by** **(字段名) 和** **sort_order** **(**asc **或** **desc**)。例如: **?sort_by=created_at&sort_order=desc**。

#### 4.4 时间与日期处理
- **所有传入和传出的时间戳字段，均使用ISO 8601格式的UTC时间，并包含时区信息** **Z**。例如：**2023-10-26T10:30:00Z**。
- **日期（不带时间）使用** **YYYY-MM-DD** **格式，例如：**2023-10-26**。**

---

### 5. 总结与交付

**《艾乐学伴MVP API接口规范全集 (OpenAPI 3.0)》共包含三个部分：**
- **第一部分**：用户、会话、计划与任务接口。
- **第二部分**：日清、诊断、内容与实时通信接口。
- **第三部分**：知识图谱、数据统计、文件上传等辅助接口与全局附录。

**此文档与《数据库详细设计书 (DDL)》共同构成了指导前后端及AI服务开发的完整、精确、可执行的工程规格说明书。**



