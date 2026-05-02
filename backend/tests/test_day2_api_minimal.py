from datetime import datetime, timezone
from types import SimpleNamespace

from app.api import auth as auth_api
from app.api import plans as plans_api
from app.api import tasks as tasks_api
from app.schemas.plans import LearningPlanResponse
from app.schemas.tasks import LearningTaskResponse, SubmitAnswerResponse, TaskStatus


def test_login_success_returns_token(client, monkeypatch):
    fake_user = SimpleNamespace(
        id="a0000000-0000-0000-0000-000000000001",
        phone="13800000001",
        nickname="艾学同学",
        grade="高二",
        textbook_version="人教版A版",
        settings={},
        current_plan_id=None,
        current_plan=None,
    )

    class FakeAuthService:
        def __init__(self, _repo):
            pass

        async def login(self, *, phone: str, sms_code: str):
            assert phone == "13800000001"
            assert sms_code == "8888"
            return fake_user, "fake-jwt-token", False

    monkeypatch.setattr(auth_api, "AuthService", FakeAuthService)
    response = client.post(
        "/api/v1/auth/login",
        json={"phone": "13800000001", "sms_code": "8888"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token"] == "fake-jwt-token"
    assert payload["is_new_user"] is False
    assert payload["user"]["phone"] == "13800000001"


def test_users_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_list_plans_authorized(client, authorized_user, monkeypatch):
    now = datetime.now(timezone.utc)

    class FakePlanService:
        async def list_plans(self, *, current_user):
            assert str(current_user.id) == str(authorized_user.id)
            return [
                LearningPlanResponse(
                    id="b0000000-0000-0000-0000-000000000001",
                    user_id=str(authorized_user.id),
                    title="函数与导数综合提升计划",
                    status="active",
                    version=1,
                    snapshot=None,
                    created_at=now,
                    updated_at=now,
                )
            ]

    monkeypatch.setattr(plans_api, "get_plan_service", lambda _db: FakePlanService())
    response = client.get("/api/v1/plans")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "函数与导数综合提升计划"
    assert payload[0]["status"] == "active"


def test_update_task_status(client, authorized_user, monkeypatch):
    now = datetime.now(timezone.utc)

    class FakeTaskService:
        async def update_task_status(self, *, current_user, task_id: str, payload):
            assert str(current_user.id) == str(authorized_user.id)
            assert task_id == "c0000000-0000-0000-0000-000000000003"
            assert payload.status == TaskStatus.in_progress
            return LearningTaskResponse(
                id=task_id,
                plan_id="b0000000-0000-0000-0000-000000000001",
                title="复合函数单调性专项练习",
                type="practice",
                status=TaskStatus.in_progress,
                source="scheduled",
                source_problem_id=None,
                knowledge_point_ids=["kp_comp_func_mono"],
                metadata={},
                due_at=None,
                started_at=now,
                completed_at=None,
                created_at=now,
            )

    monkeypatch.setattr(tasks_api, "get_task_service", lambda _db: FakeTaskService())
    response = client.put(
        "/api/v1/tasks/c0000000-0000-0000-0000-000000000003/status",
        json={"status": "in_progress"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "in_progress"
    assert payload["id"] == "c0000000-0000-0000-0000-000000000003"


def test_submit_answer(client, authorized_user, monkeypatch):
    class FakeTaskService:
        async def submit_answer(self, *, current_user, task_id: str, payload):
            assert str(current_user.id) == str(authorized_user.id)
            assert task_id == "c0000000-0000-0000-0000-000000000003"
            assert payload.exercise_id == "ex_func_001"
            return SubmitAnswerResponse(
                task_id=task_id,
                exercise_id=payload.exercise_id,
                is_correct=True,
                correct_answer="A",
                solution="解析",
                task_status=TaskStatus.completed,
            )

    monkeypatch.setattr(tasks_api, "get_task_service", lambda _db: FakeTaskService())
    response = client.post(
        "/api/v1/tasks/c0000000-0000-0000-0000-000000000003/submit-answer",
        json={"exercise_id": "ex_func_001", "answer": "A"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["is_correct"] is True
    assert payload["task_status"] == "completed"
