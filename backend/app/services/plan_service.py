"""Learning plan service."""

import uuid
from datetime import datetime, timezone

from app.core.exceptions import forbidden, not_found
from app.models.user import User
from app.repositories.plan_repository import PlanRepository
from app.repositories.user_repository import UserRepository
from app.schemas.plans import (
    CreatePlanRequest,
    LearningPlanResponse,
    PlanDetailResponse,
    UpdatePlanStatusRequest,
)
from app.services.presenters import build_plan_response, build_task_response

PLAN_STATUS_ORDER = {"active": 0, "completed": 1, "archived": 2}
TASK_STATUS_ORDER = {"in_progress": 0, "pending": 1, "completed": 2}


class PlanService:
    """Plan CRUD for the current user."""

    def __init__(
        self,
        *,
        plan_repository: PlanRepository,
        user_repository: UserRepository,
    ) -> None:
        self.plan_repository = plan_repository
        self.user_repository = user_repository
        self.session = plan_repository.session

    async def list_plans(self, *, current_user: User) -> list[LearningPlanResponse]:
        plans = await self.plan_repository.list_by_user_id(current_user.id)
        plans.sort(
            key=lambda plan: (
                PLAN_STATUS_ORDER.get(plan.status, 99),
                -(plan.updated_at or datetime.min.replace(tzinfo=timezone.utc)).timestamp(),
            )
        )
        return [build_plan_response(plan) for plan in plans]

    async def create_plan(
        self,
        *,
        current_user: User,
        payload: CreatePlanRequest,
    ) -> LearningPlanResponse:
        plan = await self.plan_repository.create(
            user_id=current_user.id,
            title=payload.title,
            status=payload.status.value,
            snapshot=payload.snapshot,
        )
        if payload.set_as_current:
            current_user.current_plan_id = plan.id

        await self.session.commit()
        saved_plan = await self.plan_repository.get_by_id(plan.id)
        return build_plan_response(saved_plan or plan)

    async def get_plan_detail(self, *, plan_id: str, current_user: User) -> PlanDetailResponse:
        plan = await self._get_owned_plan(plan_id, current_user=current_user, include_tasks=True)
        tasks = list(plan.tasks)
        tasks.sort(key=self._task_sort_key)
        return PlanDetailResponse(
            plan=build_plan_response(plan),
            tasks=[build_task_response(task) for task in tasks],
        )

    async def update_plan_status(
        self,
        *,
        plan_id: str,
        current_user: User,
        payload: UpdatePlanStatusRequest,
    ) -> LearningPlanResponse:
        plan = await self._get_owned_plan(plan_id, current_user=current_user, include_tasks=False)
        plan.status = payload.status.value

        if payload.status.value == "active":
            current_user.current_plan_id = plan.id
        elif current_user.current_plan_id == plan.id:
            active_plans = await self.plan_repository.list_active_by_user_id(
                current_user.id,
                exclude_plan_id=plan.id,
            )
            current_user.current_plan_id = active_plans[0].id if active_plans else None

        await self.plan_repository.save(plan)
        await self.session.commit()
        refreshed_plan = await self.plan_repository.get_by_id(plan.id)
        return build_plan_response(refreshed_plan or plan)

    async def _get_owned_plan(
        self,
        plan_id: str,
        *,
        current_user: User,
        include_tasks: bool,
    ):
        try:
            parsed_plan_id = uuid.UUID(plan_id)
        except ValueError as exc:
            raise not_found("学习计划不存在") from exc

        plan = await self.plan_repository.get_by_id(parsed_plan_id, include_tasks=include_tasks)
        if plan is None:
            raise not_found("学习计划不存在")
        if plan.user_id != current_user.id:
            raise forbidden("无权访问该学习计划")
        return plan

    @staticmethod
    def _task_sort_key(task) -> tuple:
        due_at = task.due_at or datetime.max.replace(tzinfo=timezone.utc)
        return (
            TASK_STATUS_ORDER.get(task.status, 99),
            due_at,
            task.created_at,
        )
