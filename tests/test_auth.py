import asyncio

from fastapi.testclient import TestClient

from src.database.database import delete_user_by_username
from src.main import app
from src.secure.secure import create_jwt_token

client = TestClient(app)


def generate_test_token(username):
    return create_jwt_token({"sub": username})


def test_create_user_success():
    user_data = {
        "username": "test_name",
        "password": "test"
    }
    response = client.post("http://127.0.0.1:8000/users/create_user/", json=user_data)
    assert response.status_code == 200
    assert "user_id" in response.json()


def test_create_user_already_exists():
    user_data = {
        "username": "test_name",
        "password": "test"
    }
    response = client.post("http://127.0.0.1:8000/users/create_user/", json=user_data)
    assert response.status_code == 400
    assert "Пользователь с таким username'ом уже зарегестрирован" in response.json()["detail"]


def test_authenticate_user_success():
    user_data = {
        "username": "test_name",
        "password": "test"
    }
    response = client.post("http://127.0.0.1:8000/users/auth/", json=user_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_authenticate_user_invalid_credentials():
    user_data = {
        "username": "non_existing_user",
        "password": "incorrect_password"
    }
    response = client.post("http://127.0.0.1:8000/users/auth/", json=user_data)
    assert response.status_code == 400
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_user_me():
    test_username = "test_name"
    test_token = generate_test_token(test_username)

    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("http://127.0.0.1:8000/users/me/", headers=headers)
    asyncio.run(delete_user_by_username(test_username))
    assert response.status_code == 200
