from datetime import datetime, timezone

from app.api import chat as chat_api
from app.api import content as content_api
from app.schemas.chat import ChatHistoryMessageResponse, ChatSessionResponse
from app.schemas.content import ContentGenerateResponse, ContentSection


def test_chat_message_requires_auth(client):
    response = client.post("/api/v1/chat/message", json={"message": "我不懂三角函数"})
    assert response.status_code == 401


def test_chat_message_sse_stream(client, authorized_user, monkeypatch):
    class FakeChatService:
        async def stream_message(self, *, current_user, message: str, session_id: str | None):
            assert str(current_user.id) == str(authorized_user.id)
            assert message == "我不懂三角函数"
            assert session_id is None
            yield {"event": "token", "data": {"text": "我"}}
            yield {
                "event": "metadata",
                "data": {
                    "session_id": "11111111-1111-1111-1111-111111111111",
                    "intent": "CLARIFY_CONCEPT",
                    "knowledge_point_ids": ["kp_trig_def"],
                    "task_created": True,
                    "task_id": "22222222-2222-2222-2222-222222222222",
                },
            }
            yield {
                "event": "done",
                "data": {
                    "session_id": "11111111-1111-1111-1111-111111111111",
                    "assistant_message": "我来陪你过一遍三角函数定义。",
                },
            }

    monkeypatch.setattr(chat_api, "get_chat_service", lambda _db: FakeChatService())
    response = client.post("/api/v1/chat/message", json={"message": "我不懂三角函数"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event: token" in body
    assert "event: metadata" in body
    assert "event: done" in body
    assert "CLARIFY_CONCEPT" in body
    assert "kp_trig_def" in body


def test_chat_sessions_list(client, authorized_user, monkeypatch):
    now = datetime.now(timezone.utc)

    class FakeChatService:
        async def list_sessions(self, *, current_user):
            assert str(current_user.id) == str(authorized_user.id)
            return [
                ChatSessionResponse(
                    session_id="11111111-1111-1111-1111-111111111111",
                    last_message="我来帮你拆解一下",
                    last_active_at=now,
                    message_count=2,
                )
            ]

    monkeypatch.setattr(chat_api, "get_chat_service", lambda _db: FakeChatService())
    response = client.get("/api/v1/chat/sessions")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["session_id"] == "11111111-1111-1111-1111-111111111111"
    assert payload[0]["message_count"] == 2


def test_chat_session_messages_list(client, authorized_user, monkeypatch):
    now = datetime.now(timezone.utc)

    class FakeChatService:
        async def list_messages(self, *, current_user, session_id: str):
            assert str(current_user.id) == str(authorized_user.id)
            assert session_id == "11111111-1111-1111-1111-111111111111"
            return [
                ChatHistoryMessageResponse(
                    role="user",
                    content="我不懂三角函数",
                    created_at=now,
                    intent="CLARIFY_CONCEPT",
                    knowledge_point_ids=["kp_trig_def"],
                ),
                ChatHistoryMessageResponse(
                    role="assistant",
                    content="我们先看定义和单位圆。",
                    created_at=now,
                    intent=None,
                    knowledge_point_ids=[],
                ),
            ]

    monkeypatch.setattr(chat_api, "get_chat_service", lambda _db: FakeChatService())
    response = client.get("/api/v1/chat/sessions/11111111-1111-1111-1111-111111111111/messages")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["role"] == "user"
    assert payload[0]["intent"] == "CLARIFY_CONCEPT"
    assert payload[1]["role"] == "assistant"


def test_content_generate_requires_auth(client):
    response = client.post(
        "/api/v1/content/generate",
        json={"knowledge_point_ids": ["kp_trig_def"]},
    )
    assert response.status_code == 401


def test_content_generate_success(client, authorized_user, monkeypatch):
    class FakeContentService:
        async def generate(self, *, payload):
            assert payload.knowledge_point_ids == ["kp_trig_def"]
            return ContentGenerateResponse(
                content_package_id="33333333-3333-3333-3333-333333333333",
                status="ready",
                sections=[
                    ContentSection(type="text", content="先理解三角函数定义与单位圆。"),
                    ContentSection(type="example", content="例题：求 sin(5π/6) 的值。"),
                ],
            )

    monkeypatch.setattr(
        content_api,
        "get_content_generation_service",
        lambda _db: FakeContentService(),
    )
    response = client.post(
        "/api/v1/content/generate",
        json={
            "knowledge_point_ids": ["kp_trig_def"],
            "style": "encouraging",
            "target_minutes": 8,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["content_package_id"] == "33333333-3333-3333-3333-333333333333"
    assert len(payload["sections"]) == 2
    assert payload["sections"][0]["type"] == "text"
