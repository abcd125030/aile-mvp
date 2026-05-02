# 《艾乐学伴MVP后端微服务详细设计书（Python统一技术栈版）》

## 统一技术栈约定
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- API风格：RESTful + WebSocket（由 FastAPI 提供）
- 数据访问：SQLAlchemy 2.x（ORM）+ Alembic（迁移）
- 缓存与会话：Redis
- 异步任务：Celery（可选 RQ）
- 测试：pytest、pytest-asyncio、httpx、testcontainers-python

---

# 第一部分：用户服务与计划任务服务

## 1. 概述
本文档提供 user-service 与 plan-task-service 的模块级实现方案，所有设计均以 Python 技术栈为基线，确保接口、数据库与服务边界一致。

## 2. 用户服务（user-service）详细设计

### 2.1 服务概览
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：用户身份生命周期、基础画像、设置管理
- 核心数据表：`users`

### 2.2 项目结构
```text
user-service/
├── app/
│   ├── main.py                    # FastAPI 启动入口
│   ├── config.py                  # 配置管理
│   ├── db/
│   │   ├── session.py             # SQLAlchemy Session 工厂
│   │   └── base.py                # Declarative Base
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   ├── repositories/
│   │   └── user_repository.py
│   ├── services/
│   │   └── user_service.py
│   ├── api/
│   │   ├── auth.py
│   │   └── users.py
│   └── middlewares/
│       ├── auth.py
│       └── logging.py
├── alembic/
├── requirements.txt
└── pyproject.toml
```

### 2.3 核心业务流程：登录/注册（`POST /auth/login`）
```python
from sqlalchemy.exc import NoResultFound

class UserService:
    def __init__(self, repo, redis_client, jwt_util):
        self.repo = repo
        self.redis = redis_client
        self.jwt_util = jwt_util

    async def login(self, phone: str, sms_code: str):
        key = f"sms_code:{phone}"
        cached_code = await self.redis.get(key)
        if not cached_code or cached_code != sms_code:
            raise ValueError("验证码错误或已过期")

        try:
            user = await self.repo.get_by_phone(phone)
            is_new_user = False
        except NoResultFound:
            user = await self.repo.create(
                phone=phone,
                grade="高一",
                textbook_version="人教版A版",
            )
            is_new_user = True

        token = self.jwt_util.generate_token(str(user.id))
        await self.redis.delete(key)
        return user, token, is_new_user
```

### 2.4 ORM 数据模型（`models/user.py`）
```python
import uuid
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(50), default="")
    grade: Mapped[str] = mapped_column(String(10), nullable=False)
    textbook_version: Mapped[str] = mapped_column(String(50), nullable=False, default="人教版A版")
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    current_plan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 2.5 外部依赖
- Redis：短信验证码缓存（`sms_code:{phone}`，TTL=5分钟）与会话黑名单
- 短信服务：抽象 `SmsClient`，MVP 可先固定验证码

## 3. 计划任务服务（plan-task-service）详细设计

### 3.1 服务概览
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：学习计划/任务 CRUD、任务状态机、内容生成触发
- 核心数据表：`learning_plans`、`learning_tasks`、`daily_problems`

### 3.2 项目结构
```text
plan-task-service/
├── app/
│   ├── main.py
│   ├── models/
│   │   ├── plan.py
│   │   ├── task.py
│   │   └── daily_problem.py
│   ├── schemas/
│   ├── repositories/
│   │   ├── plan_repository.py
│   │   ├── task_repository.py
│   │   └── daily_problem_repository.py
│   ├── services/
│   │   ├── plan_service.py
│   │   └── task_service.py
│   ├── api/
│   │   ├── plans.py
│   │   ├── tasks.py
│   │   └── internal_resolution.py
│   └── events/
│       └── publisher.py
└── alembic/
```

### 3.3 核心业务流程：任务状态机
```python
from datetime import datetime

class TaskService:
    async def update_task_status(self, task_id: str, new_status: str, user_id: str):
        task = await self.task_repo.get_with_plan(task_id)
        if str(task.plan.user_id) != user_id:
            raise PermissionError("无权限操作该任务")

        if new_status == "in_progress":
            if task.status != "pending":
                raise ValueError("只有待开始任务可开始")
            task.started_at = datetime.utcnow()

        elif new_status == "completed":
            if task.status != "in_progress":
                raise ValueError("只有进行中任务可完成")
            task.completed_at = datetime.utcnow()
            await self.event_publisher.publish_task_completed(task)

        elif new_status == "skipped":
            if task.status not in {"pending", "in_progress"}:
                raise ValueError("只有待开始或进行中任务可跳过")
        else:
            raise ValueError("无效状态")

        task.status = new_status
        await self.task_repo.save(task)
```

### 3.4 关键查询：当前计划及任务
```python
from sqlalchemy import select, case
from sqlalchemy.orm import selectinload

async def get_current_plan_with_tasks(session, user_id):
    stmt = (
        select(LearningPlan)
        .where(LearningPlan.user_id == user_id, LearningPlan.status == "active")
        .options(selectinload(LearningPlan.tasks))
    )
    plan = (await session.execute(stmt)).scalar_one()

    plan.tasks.sort(
        key=lambda t: (
            {"in_progress": 1, "pending": 2, "completed": 3}.get(t.status, 4),
            t.due_at or "9999-12-31",
        )
    )
    return plan
```

## 4. 测试策略

### 4.1 单元测试
- 目标：service / repository 关键路径
- 工具：`pytest`、`pytest-asyncio`、`unittest.mock`

```python
import pytest

@pytest.mark.asyncio
async def test_update_task_status_pending_to_in_progress(task_service, fake_task):
    fake_task.status = "pending"
    await task_service.update_task_status(str(fake_task.id), "in_progress", str(fake_task.plan.user_id))
    assert fake_task.status == "in_progress"
    assert fake_task.started_at is not None
```

### 4.2 集成测试
- 目标：API + DB + Redis 联调
- 方法：`testcontainers-python` 拉起 PostgreSQL/Redis
- 覆盖：`POST /auth/login`、`GET /plans/current`、`PATCH /tasks/{id}`

## 5. 部署与配置
```env
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=aile_mvp
REDIS_ADDR=redis:6379
JWT_SECRET=your-super-secret-jwt-key-change-this
```

- 健康检查：`/health`（DB + Redis），`/ready`

---

# 第二部分：会话服务、内容服务与诊断服务

## 1. 概述
本部分覆盖 `session-service`、`content-service`、`diagnosis-service`，全部采用 Python 统一技术栈。

## 2. 会话服务（session-service）
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：会话上下文、WebSocket 推送、行为事件采集

```python
class SessionService:
    async def get_session_context(self, user_id: str):
        user = await self.user_client.get_user(user_id)
        behavior = await self.behavior_repo.get_recent(user_id)
        decision = self.pioppe_engine.make_decision(user, behavior)

        audio_url = None
        try:
            audio_url = await self.intent_client.generate_speech(decision.greeting_text)
        except Exception:
            pass

        return {
            "journey": decision.journey,
            "greeting": {"text": decision.greeting_text, "audio_url": audio_url},
            "suggestions": decision.suggestions,
            "urgent_intervention": decision.urgent_intervention,
        }
```

## 3. 内容服务（content-service）
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：内容包元数据、预签名 URL、分发状态查询

```python
class ContentService:
    async def get_content_package(self, package_id: str, user_id: str):
        package = await self.repo.get(package_id)
        if package is None:
            return None

        signed_manifest = []
        for item in package.manifest:
            signed_item = dict(item)
            if item.get("url"):
                signed_item["url"] = self.storage_client.generate_presigned_url(item["url"], expires=3600)
            signed_manifest.append(signed_item)

        return {
            "id": package.id,
            "status": package.status,
            "manifest": signed_manifest,
            "created_at": package.created_at,
        }
```

## 4. 诊断服务（diagnosis-service）
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：试卷上传、异步诊断流水线、报告管理

```python
from celery import Celery

celery_app = Celery("diagnosis")

@celery_app.task(bind=True, max_retries=3)
def process_diagnosis_pipeline(self, file_url: str, user_id: str, report_id: str):
    try:
        update_report_status(report_id, "processing")
        ocr_result = ocr_client.analyze(file_url)
        analysis = ai_gateway_client.analyze_exam({"items": ocr_result["items"], "subject": "math"})
        save_diagnosis_report(report_id, {
            "summary": analysis["summary"],
            "detailed_analysis": analysis["detailed_analysis"],
        })
        websocket_manager.send_diagnosis_ready(user_id, report_id)
    except Exception as exc:
        update_report_status(report_id, "failed")
        raise self.retry(exc=exc, countdown=60)
```

---

# 第三部分：AI网关与意图理解服务

## 1. 概述
本部分定义 `ai-gateway` 与 `intent-service`，依然遵循统一 Python 技术栈，并与前述业务服务解耦协作。

## 2. 统一AI网关服务（ai-gateway）
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：模型路由、缓存、限流、容错降级

```python
class ModelRouter:
    async def route_request(self, request):
        deployment = self._select_deployment(request)
        if self.circuit_breaker.is_open(deployment.id):
            raise RuntimeError("deployment unavailable")

        cache_key = self._cache_key(request, deployment.id)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        provider = self._provider(deployment.provider_type)
        response = await provider.create_chat_completion(deployment, request)
        await self.cache.set(cache_key, response, ttl=300)
        return response
```

## 3. 意图理解服务（intent-service）
- 技术栈：Python 3.11+、FastAPI、Redis、ORM（SQLAlchemy）
- 职责：混合意图识别、动机状态预测、知识检索增强

```python
class UnderstandingOrchestrator:
    async def understand(self, request):
        context = self._prepare_context(request)
        llm_future = self.llm_analyzer.analyze_async(context)
        domain_future = self.domain_classifier.classify_async(context.utterance)
        knowledge = await self.entity_linker.retrieve_related_knowledge(context.utterance)

        llm_result = await llm_future
        domain_result = await domain_future
        fused = self._fuse_intents(llm_result, domain_result, knowledge)

        inferred_state = await self.motivation_predictor.predict(request.user_id, request.context)
        return {
            "request_id": self._request_id(),
            "understanding": {
                "primary_intent": fused.intent,
                "entities": llm_result.entities,
                "inferred_state": inferred_state,
                "knowledge": knowledge,
            },
        }
```

## 4. 监控与运维
- 指标：接口延迟、错误率、Redis 命中率、任务成功率
- 日志：请求链路 ID、模型调用日志、任务重试日志
- 告警：熔断打开、队列堆积、数据库慢查询

## 5. 文档总结
本设计书已统一为 Python 技术体系，所有微服务均基于 FastAPI、Redis、SQLAlchemy 进行实现与协作，满足 MVP 快速开发与后续扩展需求。
