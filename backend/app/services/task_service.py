"""Learning task service."""

import uuid

from app.core.exceptions import bad_request, forbidden, not_found
from app.models.exercise_item import ExerciseItem
from app.models.user import User
from app.repositories.exercise_repository import ExerciseRepository
from app.repositories.knowledge_point_repository import KnowledgePointRepository
from app.repositories.plan_repository import PlanRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.tasks import (
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TaskDetailResponse,
    UpdateTaskStatusRequest,
)
from app.services.presenters import (
    build_content_package_response,
    build_exercise_response,
    build_knowledge_point_response,
    build_task_response,
)

TASK_STATUS_ORDER = {"in_progress": 0, "pending": 1, "completed": 2}


class TaskService:
    """Task list, detail, transitions, and answer submission."""

    def __init__(
        self,
        *,
        task_repository: TaskRepository,
        plan_repository: PlanRepository,
        knowledge_point_repository: KnowledgePointRepository,
        exercise_repository: ExerciseRepository,
    ) -> None:
        self.task_repository = task_repository
        self.plan_repository = plan_repository
        self.knowledge_point_repository = knowledge_point_repository
        self.exercise_repository = exercise_repository
        self.session = task_repository.session

    async def list_tasks(
        self,
        *,
        current_user: User,
        plan_id: str | None,
        status_filter: str | None,
    ):
        resolved_plan_id = await self._resolve_plan_id(current_user=current_user, plan_id=plan_id)
        if resolved_plan_id is None:
            return []

        tasks = await self.task_repository.list_by_plan_id(resolved_plan_id, status=status_filter)
        tasks.sort(key=lambda task: (TASK_STATUS_ORDER.get(task.status, 99), task.created_at))
        return [build_task_response(task) for task in tasks]

    async def get_task_detail(self, *, current_user: User, task_id: str) -> TaskDetailResponse:
        task = await self._get_owned_task(task_id, current_user=current_user)
        knowledge_points = await self.knowledge_point_repository.get_by_ids(
            list(task.knowledge_point_ids or [])
        )
        exercises = await self._resolve_task_exercises(task)
        return TaskDetailResponse(
            task=build_task_response(task),
            knowledge_points=[build_knowledge_point_response(item) for item in knowledge_points],
            content_package=(
                build_content_package_response(task.content_package) if task.content_package else None
            ),
            exercises=[build_exercise_response(item) for item in exercises],
        )

    async def update_task_status(
        self,
        *,
        current_user: User,
        task_id: str,
        payload: UpdateTaskStatusRequest,
    ):
        task = await self._get_owned_task(task_id, current_user=current_user)
        next_status = payload.status.value

        if next_status == "in_progress":
            if task.status != "pending":
                raise bad_request("只有待开始任务可开始")
            task.started_at = task.started_at or self._utcnow()
        elif next_status == "completed":
            if task.status != "in_progress":
                raise bad_request("只有进行中任务可完成")
            task.completed_at = self._utcnow()
        else:
            raise bad_request("不支持的任务状态")

        task.status = next_status
        await self.task_repository.save(task)
        await self.session.commit()
        refreshed_task = await self.task_repository.get_by_id(task.id)
        return build_task_response(refreshed_task or task)

    async def submit_answer(
        self,
        *,
        current_user: User,
        task_id: str,
        payload: SubmitAnswerRequest,
    ) -> SubmitAnswerResponse:
        task = await self._get_owned_task(task_id, current_user=current_user)
        exercise = await self.exercise_repository.get_by_id(payload.exercise_id)
        if exercise is None:
            raise not_found("题目不存在")

        available_exercises = await self._resolve_task_exercises(task)
        available_ids = {item.id for item in available_exercises}
        if exercise.id not in available_ids:
            raise bad_request("题目不属于该任务")

        is_correct = self._is_correct_answer(exercise, payload.answer)
        if is_correct and task.status != "completed":
            if task.status == "pending":
                task.started_at = task.started_at or self._utcnow()
            task.status = "completed"
            task.completed_at = self._utcnow()
            await self.task_repository.save(task)
            await self.session.commit()

        return SubmitAnswerResponse(
            task_id=str(task.id),
            exercise_id=exercise.id,
            is_correct=is_correct,
            correct_answer=exercise.correct_answer,
            solution=exercise.solution,
            task_status=task.status,
        )

    async def _resolve_plan_id(self, *, current_user: User, plan_id: str | None) -> uuid.UUID | None:
        if plan_id is None:
            return current_user.current_plan_id

        try:
            parsed_plan_id = uuid.UUID(plan_id)
        except ValueError as exc:
            raise not_found("学习计划不存在") from exc

        plan = await self.plan_repository.get_by_id(parsed_plan_id)
        if plan is None:
            raise not_found("学习计划不存在")
        if plan.user_id != current_user.id:
            raise forbidden("无权访问该学习计划")
        return parsed_plan_id

    async def _get_owned_task(self, task_id: str, *, current_user: User):
        try:
            parsed_task_id = uuid.UUID(task_id)
        except ValueError as exc:
            raise not_found("学习任务不存在") from exc

        task = await self.task_repository.get_by_id(parsed_task_id)
        if task is None:
            raise not_found("学习任务不存在")
        if task.plan.user_id != current_user.id:
            raise forbidden("无权访问该学习任务")
        return task

    async def _resolve_task_exercises(self, task) -> list[ExerciseItem]:
        exercise_ids = list((task.metadata_ or {}).get("exercise_ids") or [])
        if exercise_ids:
            return await self.exercise_repository.get_by_ids([str(item) for item in exercise_ids])
        return await self.exercise_repository.list_for_knowledge_points(
            [str(item) for item in list(task.knowledge_point_ids or [])],
            limit=10,
        )

    @staticmethod
    def _is_correct_answer(exercise: ExerciseItem, answer: str) -> bool:
        expected = (exercise.correct_answer or "").strip()
        actual = (answer or "").strip()
        exercise_type = (exercise.metadata_ or {}).get("type")
        if exercise.options is None or exercise_type == "fill_blank":
            return actual.lower() == expected.lower()
        return actual == expected

    @staticmethod
    def _utcnow():
        from datetime import datetime, timezone

        return datetime.now(timezone.utc)
