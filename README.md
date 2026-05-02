# 艾乐学伴 MVP (Demo 版)

## 项目概述

艾乐学伴是一款面向高中生的 AI 智能学习伴侣，通过个性化学习计划、日清问题解答和智能诊断，帮助学生高效提升学业水平。本项目为 MVP Demo 版本，采用 7 天冲刺开发模式，实现核心功能闭环演示。

## 技术栈

| 层级        | 技术                   | 版本   |
| ----------- | ---------------------- | ------ |
| 前端框架    | React + TypeScript     | 18.x   |
| 前端构建    | Vite                   | 5.x    |
| CSS 方案    | Tailwind CSS           | 3.x    |
| 状态管理    | Zustand                | 4.x    |
| 路由        | react-router-dom       | 6.x    |
| HTTP 客户端 | axios                  | 1.x    |
| 后端框架    | FastAPI (Python)       | 0.110+ |
| ORM         | SQLAlchemy 2.x (async) | 2.x    |
| 数据库      | PostgreSQL             | 15     |
| 缓存        | Redis                  | 7      |
| 容器编排    | Docker Compose         | v2     |

## 项目结构

```
├── frontend/       # React 前端应用
├── backend/        # FastAPI 后端服务
├── database/       # SQL 脚本（DDL + 种子数据）
├── docker-compose.yml
└── README.md
```

## 快速启动

### 前置要求

- Docker & Docker Compose v2

### 一键启动

```bash
docker-compose up --build
```

启动完成后：

- 前端页面：http://localhost:3000
- 后端健康检查：http://localhost:8000/health
- PostgreSQL：localhost:5432
- Redis：localhost:6379

### 停止服务

```bash
docker-compose down
```

如需清除数据卷（重置数据库）：

```bash
docker-compose down -v
```

## 演示账号

| 手机号      | 昵称     | 年级 | 教材版本  |
| ----------- | -------- | ---- | --------- |
| 13800000001 | 艾学同学 | 高二 | 人教版A版 |
| 13800000002 | 小明同学 | 高三 | 人教版A版 |

## 开发说明

### 本地开发（不使用 Docker）

**后端：**

```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Day 3 模型配置（Qwen）

本项目 Day 3 默认接入 `qwen-plus`。本地开发建议在 `backend/.env` 中配置：

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/aile_mvp
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=dev-secret-key-change-in-production

LLM_PROVIDER=qwen
LLM_MODEL=qwen-plus
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=你的DashScopeKey
LLM_TIMEOUT_SECONDS=30
```

注意：`LLM_API_KEY` 不要提交到仓库。

### Day 3 接口联调示例

先登录拿到 token：

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"phone\":\"13800000001\",\"sms_code\":\"8888\"}"
```

从响应中复制 `token`，再调用以下接口。

**1) Chat SSE（`POST /api/v1/chat/message`）**

```bash
curl -N -X POST "http://localhost:8000/api/v1/chat/message" \
  -H "Authorization: Bearer <你的token>" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"我不懂三角函数\"}"
```

预期会收到 `event: token`、`event: metadata`、`event: done` 三类事件。

**2) 会话列表（`GET /api/v1/chat/sessions`）**

```bash
curl "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer <你的token>"
```

**3) 会话消息（`GET /api/v1/chat/sessions/{session_id}/messages`）**

```bash
curl "http://localhost:8000/api/v1/chat/sessions/<session_id>/messages" \
  -H "Authorization: Bearer <你的token>"
```

**4) 内容生成（`POST /api/v1/content/generate`）**

```bash
curl -X POST "http://localhost:8000/api/v1/content/generate" \
  -H "Authorization: Bearer <你的token>" \
  -H "Content-Type: application/json" \
  -d "{\"knowledge_point_ids\":[\"kp_trig_def\"],\"style\":\"encouraging\",\"target_minutes\":8}"
```

### 后端测试

**最小接口测试（无真实数据库依赖）：**

```bash
cd backend
pytest -q tests/test_day2_api_minimal.py
pytest -q tests/test_day3_api_minimal.py
pytest -q tests/test_day3_services_minimal.py
```

**半集成测试（连接真实测试数据库）：**

```bash
# PowerShell
$env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:<你的密码>@localhost:5432/aile_mvp"
cd backend
pytest -q tests/test_services_db_semi_integration.py
```

说明：
- 半集成测试会在独立测试 schema 中建表与清理，不会污染默认业务表。
- 若 `TEST_DATABASE_URL` 不可用，半集成测试会自动 `skip` 并提示配置。

**前端：**

```bash
cd frontend
npm install
npm run dev
```

## License

Private - All Rights Reserved
