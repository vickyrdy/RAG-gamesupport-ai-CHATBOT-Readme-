import re
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def ask(client, thread_id, message):
    response = client.post("/chat", json={
        "user_id": "evaluation-user",
        "thread_id": thread_id,
        "message": message,
    })
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["blocked"] is False
    print("\nANSWER:", data["answer"])
    return data


def test_refund_policy(client):
    data = ask(
        client,
        str(uuid4()),
        "State the refund time limit and playtime limit.",
    )

    answer = data["answer"].lower()

    assert re.search(r"\b(14|fourteen)\b", answer)
    assert re.search(r"\b(2|two)\b", answer)
    assert "refund-policy.md" in data["sources"]


def test_conversation_memory(client):
    thread = str(uuid4())

    ask(
        client,
        thread,
        "I played for 73 minutes. Can I request a refund?",
    )

    data = ask(
        client,
        thread,
        "How many minutes did I say I played?",
    )

    assert re.search(
        r"\b73\b|seventy[\s-]+three",
        data["answer"].lower(),
    )