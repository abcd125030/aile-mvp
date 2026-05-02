from __future__ import annotations

import uuid
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.schemas.chat import IntentResult
from app.schemas.content import ContentGenerateRequest
from app.services.chat_service import ChatService
from app.services.content_generation_service import ContentGenerationService


class _FakeSession:
    async def commit(self):
        return None

    def add(self, _obj):
        return None

    async def flush(self):
        return None


class _FakeEventRepo:
    def __init__(self):
        self.created_events: list[dict] = []

    async def create_message_event(self, **kwargs):
        self.created_events.append(kwargs)
        return SimpleNamespace(event_data=kwargs)

    async def list_messages(self, *, user_id, session_id):  # noqa: ARG002
        return []


class _FakeDailyProblemRepo:
    def __init__(self):
        self.last_problem_id = uuid.uuid4()
        self.resolution_updates: list[dict] = []

    async def create(self, **kwargs):
        return SimpleNamespace(id=self.last_problem_id, **kwargs)

    async def set_resolution_task(self, **kwargs):
        self.resolution_updates.append(kwargs)


class _FakeDailyClearanceService:
    def __init__(self, *, task_created: bool):
        self.session = _FakeSession()
        self.task_created = task_created
        self.calls: list[dict] = []
        self.resolution_updates: list[dict] = []

    async def record_problem_and_generate_task(
        self,
        *,
        current_user,
        session_id: str,
        utterance: str,
        intent,
    ):
        self.calls.append(
            {
                "current_user": current_user,
                "session_id": session_id,
                "utterance": utterance,
                "intent": intent,
            }
        )
        daily_problem = SimpleNamespace(id=uuid.uuid4())
        if self.task_created:
            task = SimpleNamespace(id=uuid.uuid4())
            self.resolution_updates.append({"problem_id": daily_problem.id, "task_id": task.id})
            return daily_problem, task
        return daily_problem, None


class _FakePlanRepo:
    def __init__(self, existing_plan_id: str | None):
        self.existing_plan_id = existing_plan_id
        self.created_plan_id = uuid.uuid4()

    async def get_by_id(self, plan_id):
        if self.existing_plan_id and str(plan_id) == self.existing_plan_id:
            return SimpleNamespace(id=uuid.UUID(self.existing_plan_id))
        return None

    async def create(self, **kwargs):
        return SimpleNamespace(id=self.created_plan_id, **kwargs)


class _FakeTaskRepo:
    def __init__(self):
        self.session = _FakeSession()
        self.saved_tasks: list = []

    async def save(self, task):
        task.id = uuid.uuid4()
        self.saved_tasks.append(task)
        return task


class _FakeKnowledgePointRepo:
    async def get_by_ids(self, ids):
        return [SimpleNamespace(id=item, name=f"知识点-{item}") for item in ids]


class _FakeLLMService:
    def __init__(self, chunks: list[str] | None = None, text: str = ""):
        self.chunks = chunks or []
        self.text = text

    async def stream_chat(self, **kwargs):  # noqa: ARG002
        for chunk in self.chunks:
            yield chunk

    async def chat(self, **kwargs):  # noqa: ARG002
        return self.text


class _FakeIntentService:
    def __init__(self, result: IntentResult):
        self.result = result

    async def classify(self, *, message: str):  # noqa: ARG002
        return self.result


@dataclass
class _FakeUser:
    id: uuid.UUID
    current_plan_id: uuid.UUID | None


@pytest.mark.asyncio
async def test_chat_service_creates_task_when_intent_and_kp_match():
    llm_service = _FakeLLMService(chunks=["你好"])
    intent_service = _FakeIntentService(
        IntentResult(
            primary_intent="CLARIFY_CONCEPT",
            slots={"knowledge_point_ids": ["kp_trig_def"]},
        )
    )
    event_repo = _FakeEventRepo()
    daily_clearance_service = _FakeDailyClearanceService(task_created=True)
    service = ChatService(
        llm_service=llm_service,
        intent_service=intent_service,
        event_repository=event_repo,
        daily_clearance_service=daily_clearance_service,
    )
    user = _FakeUser(id=uuid.uuid4(), current_plan_id=None)

    events = []
    async for item in service.stream_message(
        current_user=user,
        message="我不懂三角函数",
        session_id=None,
    ):
        events.append(item)

    metadata_event = next(item for item in events if item["event"] == "metadata")
    assert metadata_event["data"]["task_created"] is True
    assert metadata_event["data"]["task_id"] is not None
    assert daily_clearance_service.resolution_updates, "应回填 daily_problems.resolution_task_id"


@pytest.mark.asyncio
async def test_chat_service_not_create_task_when_no_kp():
    llm_service = _FakeLLMService(chunks=["好的"])
    intent_service = _FakeIntentService(
        IntentResult(primary_intent="CLARIFY_CONCEPT", slots={"knowledge_point_ids": []})
    )
    event_repo = _FakeEventRepo()
    daily_clearance_service = _FakeDailyClearanceService(task_created=False)
    service = ChatService(
        llm_service=llm_service,
        intent_service=intent_service,
        event_repository=event_repo,
        daily_clearance_service=daily_clearance_service,
    )
    user = _FakeUser(id=uuid.uuid4(), current_plan_id=None)

    events = []
    async for item in service.stream_message(
        current_user=user,
        message="有点不懂",
        session_id=None,
    ):
        events.append(item)

    metadata_event = next(item for item in events if item["event"] == "metadata")
    assert metadata_event["data"]["task_created"] is False
    assert metadata_event["data"]["task_id"] is None
    assert len(daily_clearance_service.resolution_updates) == 0


@pytest.mark.asyncio
async def test_content_generation_service_fallback_when_llm_returns_invalid_json():
    class _Repo:
        def __init__(self):
            self.session = _FakeSession()
            self.created_manifest = None

        async def create(self, *, manifest, status="ready", associated_task_id=None, associated_problem_id=None):
            self.created_manifest = manifest
            return SimpleNamespace(
                id=uuid.uuid4(),
                status=status,
                manifest=manifest,
                associated_task_id=associated_task_id,
                associated_problem_id=associated_problem_id,
            )

    class _KPRepo:
        async def get_by_ids(self, ids):
            return [SimpleNamespace(id=item, name="三角函数的定义") for item in ids]

    repository = _Repo()
    service = ContentGenerationService(
        llm_service=_FakeLLMService(text="this is not json"),
        knowledge_point_repository=_KPRepo(),
        content_package_repository=repository,
    )
    payload = ContentGenerateRequest(knowledge_point_ids=["kp_trig_def"])

    result = await service.generate(payload=payload)
    assert result.status == "ready"
    assert len(result.sections) == 2
    assert result.sections[0].type == "text"
    assert repository.created_manifest is not None
    assert repository.created_manifest["sections"][0]["type"] in {"text", "example"}
