import pytest
from aiohttp import web
from src.main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_chat_page1():
    response = client.get("http://localhost:8000/chat1")
    assert response.status_code == 200


async def test_websocket_endpoint():
    with client.websocket_connect("ws://localhost:8000/chat/ws/1") as ws_conn:
        assert ws_conn.closed is False

        await ws_conn.send_text("456:Test message")
        response = await ws_conn.receive_text()

        assert response == "Echoed text: Test message"
