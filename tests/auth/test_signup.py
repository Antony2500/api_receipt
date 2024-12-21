import pytest
import sys
import os
from pathlib import Path
from sqlalchemy import select

from app.models.user import User as DB_User
from app.models.auth import AuthToken


# Тест для регистрации пользователя
async def test_signup(client, test_session):
    signup_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "username": "testuser"
    }

    # Отправляем запрос на регистрацию
    response = client.post("/auth/registration", json=signup_data)
    assert response.status_code == 200, f"Response: {response.json()}"

    # Проверяем созданного пользователя в базе данных
    user = await test_session.scalar(
        select(DB_User).filter(DB_User.email == "testuser@example.com")
    )
    refresh_token = await test_session.scalar(
        select(AuthToken).filter(AuthToken.user_id == user.id)
    )

    assert user.email is not None
    assert refresh_token is not None


async def test_signup_unavailable_username(client):
    signup_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "username": "xxx"
    }

    response = client.post("/auth/registration", json=signup_data)

    assert response.status_code == 422


async def test_signup_existed_username(client, register_user):
    signup_data = {
        "email": "testuser2@example.com",
        "password": "testpassword",
        "username": "testuser"
    }

    response = client.post("/auth/registration", json=signup_data)

    assert response.status_code == 400

    json_response = response.json()
    assert "Username already exists" in json_response["detail"]


async def test_signup_existed_email(client, register_user):
    signup_data = {
        "email": "testuser@example.com",
        "password": "testpassword",
        "username": "testuser2"
    }

    response = client.post("/auth/registration", json=signup_data)

    assert response.status_code == 400

    json_response = response.json()
    assert "Email already exists" in json_response["detail"]
