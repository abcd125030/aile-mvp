"""Daily clearance orchestration service."""

from __future__ import annotations

import uuid

from app.models.learning_task import LearningTask
from app.models.user import User
from app.repositories.daily_problem_repository import DailyProblemRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.chat import IntentResult


class DailyClearanceService:
    """Create daily problems and optionally auto-generate learning tasks."""

    def __init__(
        self,
        *,
        daily_problem_repository: DailyProblemRepository,
        knowledge_point_repository: KnowledgePointRepository,
        plan_repository: PlanRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.daily_problem_repository = daily_problem_repository
        self.knowledge_point_repository = knowledge_point_repository
        self.plan_repository = plan_repository
        self.task_repository = task_repository
        self.session = task_repository.session

    async def record_problem_and_generate_task(
        self,
        *,
        current_user: User,
        session_id: str,
        utterance: str,
        intent: IntentResult,
    ):
        daily_problem = await self.daily_problem_repository.create(
            user_id=current_user.id,
            session_id=session_id,
            original_utterance=utterance,
            intent=intent.primary_intent,
            slots=intent.slots,
        )
        task = await self._maybe_create_task(
            current_user=current_user,
            intent=intent,
            source_problem_id=daily_problem.id,
        )
        if task is not None:
            await self.daily_problem_repository.set_resolution_task(
                problem_id=daily_problem.id,
                task_id=task.id,
                resolution_type="practice_task",
            )
        return daily_problem, task

    async def _maybe_create_task(
        self,
        *,
        current_user: User,
        intent: IntentResult,
        source_problem_id: uuid.UUID,
    ) -> LearningTask | None:
        kp_ids = list(intent.slots.get("knowledge_point_ids") or [])
        if not kp_ids:
            return None
        if intent.primary_intent not in {"CLARIFY_CONCEPT", "SOLVE_PROBLEM"}:
            return None

        target_plan = await self._resolve_target_plan(current_user=current_user)
        knowledge_points = await self.knowledge_point_repository.get_by_ids(kp_ids)
        kp_name = knowledge_points[0].name if knowledge_points else "相关知识点"
        task_type = "concept_learning" if intent.primary_intent == "CLARIFY_CONCEPT" else "practice"
        task = LearningTask(
            plan_id=target_plan.id,
            title=f"日清巩固：{kp_name}",
            type=task_type,
            status="pending",
            source="daily_clearance",
            source_problem_id=source_problem_id,
            knowledge_point_ids=kp_ids,
            metadata_={
                "estimated_minutes": 12 if task_type == "concept_learning" else 15,
            },
        )
        return await self.task_repository.save(task)

    async def _resolve_target_plan(self, *, current_user: User):
        if current_user.current_plan_id:
            existing = await self.plan_repository.get_by_id(current_user.current_plan_id)
            if existing is not None:
                return existing

        created = await self.plan_repository.create(
            user_id=current_user.id,
            title="日清巩固计划",
            status="active",
            snapshot={"source": "daily_clearance"},
        )
        current_user.current_plan_id = created.id
        self.session.add(current_user)
        await self.session.flush()
        return created
