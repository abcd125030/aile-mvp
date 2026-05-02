import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401 - ensure metadata is loaded
from app.db.base import Base
from app.models.exercise_item import ExerciseItem
from app.models.learning_plan import LearningPlan
from app.models.learning_task import LearningTask
from app.models.user import User
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.plans import UpdatePlanStatusRequest
from app.schemas.tasks import SubmitAnswerRequest, TaskStatus, UpdateTaskStatusRequest
from app.services.plan_service import PlanService
from app.services.task_service import TaskService


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/aile_mvp",
)


@pytest.fixture(scope="session")
def test_schema() -> str:
    return f"test_day2_{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="session")
async def db_engine(test_schema: str):
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"server_settings": {"search_path": test_schema}},
    )
    try:
        async with engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{test_schema}"'))
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # pragma: no cover - environment dependent
        await engine.dispose()
        pytest.skip(
            f"无法连接测试数据库({TEST_DATABASE_URL})，请设置可用的 TEST_DATABASE_URL。错误: {exc}"
        )
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{test_schema}" CASCADE'))
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


async def _seed_user_plan_task_exercise(session: AsyncSession):
    user = User(
        phone="13800000001",
        nickname="艾学同学",
        grade="高二",
        textbook_version="人教版A版",
        settings={},
    )
    session.add(user)
    await session.flush()

    plan = LearningPlan(
        user_id=user.id,
        title="函数与导数综合提升计划",
        status="active",
        version=1,
    )
    session.add(plan)
    await session.flush()
    user.current_plan_id = plan.id

    task = LearningTask(
        plan_id=plan.id,
        title="复合函数单调性专项练习",
        type="practice",
        status="pending",
        source="scheduled",
        knowledge_point_ids=["kp_comp_func_mono"],
        metadata_={"exercise_ids": ["ex_func_001"], "type": "choice"},
    )
    session.add(task)

    exercise = ExerciseItem(
        id="ex_func_001",
        stem="示例题目",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        solution="解析",
        knowledge_point_ids=["kp_comp_func_mono"],
        metadata_={"type": "choice"},
    )
    session.add(exercise)
    await session.commit()
    await session.refresh(user)
    await session.refresh(plan)
    await session.refresh(task)
    return user, plan, task, exercise


@pytest.mark.asyncio
async def test_plan_service_archive_current_plan_clears_current_plan(db_session: AsyncSession):
    user, plan, _, _ = await _seed_user_plan_task_exercise(db_session)
    service = PlanService(
        plan_repository=PlanRepository(db_session),
        user_repository=UserRepository(db_session),
    )

    await service.update_plan_status(
        plan_id=str(plan.id),
        current_user=user,
        payload=UpdatePlanStatusRequest(status="archived"),
    )
    await db_session.refresh(user)
    assert user.current_plan_id is None


@pytest.mark.asyncio
async def test_task_service_status_transition_pending_to_completed(db_session: AsyncSession):
    user, _, task, _ = await _seed_user_plan_task_exercise(db_session)
    service = TaskService(
        task_repository=TaskRepository(db_session),
        plan_repository=PlanRepository(db_session),
        knowledge_point_repository=KnowledgePointRepository(db_session),
        exercise_repository=ExerciseRepository(db_session),
    )

    in_progress = await service.update_task_status(
        current_user=user,
        task_id=str(task.id),
        payload=UpdateTaskStatusRequest(status=TaskStatus.in_progress),
    )
    assert in_progress.status == TaskStatus.in_progress
    assert in_progress.started_at is not None

    completed = await service.update_task_status(
        current_user=user,
        task_id=str(task.id),
        payload=UpdateTaskStatusRequest(status=TaskStatus.completed),
    )
    assert completed.status == TaskStatus.completed
    assert completed.completed_at is not None


@pytest.mark.asyncio
async def test_task_service_submit_answer_marks_completed_from_pending(db_session: AsyncSession):
    user, _, task, _ = await _seed_user_plan_task_exercise(db_session)
    service = TaskService(
        task_repository=TaskRepository(db_session),
        plan_repository=PlanRepository(db_session),
        knowledge_point_repository=KnowledgePointRepository(db_session),
        exercise_repository=ExerciseRepository(db_session),
    )

    result = await service.submit_answer(
        current_user=user,
        task_id=str(task.id),
        payload=SubmitAnswerRequest(exercise_id="ex_func_001", answer="A"),
    )
    assert result.is_correct is True
    assert result.task_status == TaskStatus.completed

    refreshed_task = await TaskRepository(db_session).get_by_id(task.id)
    assert refreshed_task is not None
    assert refreshed_task.status == "completed"
    assert refreshed_task.started_at is not None
    assert refreshed_task.completed_at is not None


@pytest.mark.asyncio
async def test_task_service_invalid_transition_pending_to_completed_returns_400(
    db_session: AsyncSession,
):
    user, _, task, _ = await _seed_user_plan_task_exercise(db_session)
    service = TaskService(
        task_repository=TaskRepository(db_session),
        plan_repository=PlanRepository(db_session),
        knowledge_point_repository=KnowledgePointRepository(db_session),
        exercise_repository=ExerciseRepository(db_session),
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.update_task_status(
            current_user=user,
            task_id=str(task.id),
            payload=UpdateTaskStatusRequest(status=TaskStatus.completed),
        )

    assert exc_info.value.status_code == 400
    assert "只有进行中任务可完成" in exc_info.value.detail
