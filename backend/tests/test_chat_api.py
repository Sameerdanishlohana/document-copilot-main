import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.auth.dependencies import get_current_user

client = TestClient(app)

mock_user = MagicMock()
mock_user.id = "user-123"
mock_user.email = "analyst@driftwood.com"


@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()


@patch("app.api.chat.get_service_role_client")
def test_create_and_list_threads(mock_get_client):
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Mock list_threads
    mock_supabase.table().select().eq().order().execute.return_value.data = [
        {"id": 1, "owner_id": "user-123", "title": "Test Chat", "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z"}
    ]

    res = client.get("/chats")
    assert res.status_code == 200
    threads = res.json()
    assert len(threads) == 1
    assert threads[0]["title"] == "Test Chat"


@patch("app.api.chat.get_service_role_client")
def test_thread_forbidden_for_different_user(mock_get_client):
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Mock get_thread returning someone else's thread
    mock_supabase.table().select().eq().maybe_single().execute.return_value.data = {
        "id": 99,
        "owner_id": "other-user-456",
        "title": "Private Chat",
    }

    res = client.get("/chats/99/messages")
    assert res.status_code == 403
    assert "permission" in res.json()["detail"]


@patch("app.api.chat.run_turn")
@patch("app.api.chat.get_service_role_client")
def test_chat_stream_endpoint(mock_get_client, mock_run_turn):
    mock_supabase = MagicMock()
    mock_get_client.return_value = mock_supabase

    # Mock get_thread returning user's thread
    mock_supabase.table().select().eq().maybe_single().execute.return_value.data = {
        "id": 1,
        "owner_id": "user-123",
        "title": "My Chat",
    }
    mock_supabase.table().insert().execute.return_value.data = [{"id": 10}]
    mock_supabase.table().update().eq().execute.return_value.data = [{}]

    async def dummy_generator(*args, **kwargs):
        yield '0:"Grounded response"\n'
        yield 'd:{"finishReason": "stop"}\n'

    mock_run_turn.return_value = dummy_generator()

    payload = {
        "threadId": 1,
        "messages": [
            {"role": "user", "content": "revenue"}
        ]
    }
    res = client.post("/chat/stream", json=payload)
    assert res.status_code == 200
    assert '0:"Grounded response"' in res.text
