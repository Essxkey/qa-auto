# -*- coding: utf-8 -*-
"""pytest fixtures：API 客户端、独立随机用户、第二个用户、已建笔记。"""

import pytest

from api_client.notes_client import NotesApiClient, random_email, random_name
from config import VALID_PASSWORD


@pytest.fixture(scope="session")
def client() -> NotesApiClient:
    """会话级 API 客户端（自动重试瞬时网络故障）。"""
    return NotesApiClient()


@pytest.fixture
def new_user(client):
    """注册并登录一个全新随机用户，返回 {name, email, password, token, user_id}。"""
    name = random_name()
    email = random_email()
    reg = client.register(name, email, VALID_PASSWORD)
    assert reg.status_code == 201, f"fixture 注册失败: {reg.text}"

    login = client.login(email, VALID_PASSWORD)
    assert login.status_code == 200, f"fixture 登录失败: {login.text}"

    user = {
        "name": name,
        "email": email,
        "password": VALID_PASSWORD,
        "token": login.data["token"],
        "user_id": login.data["id"],
    }
    return user


@pytest.fixture
def second_user(client):
    """另一个独立随机用户，用于跨用户隔离测试。"""
    name = random_name(prefix="Second")
    email = random_email(prefix="sec")
    client.register(name, email, VALID_PASSWORD)
    login = client.login(email, VALID_PASSWORD)
    return {
        "name": name,
        "email": email,
        "password": VALID_PASSWORD,
        "token": login.data["token"],
        "user_id": login.data["id"],
    }


@pytest.fixture
def created_note(client, new_user):
    """为 new_user 创建一条 Work 分类笔记，返回 (user, note) 与辅助字典。"""
    title = f"Auto Note {random_name(prefix='N')}"
    description = "created by api automation framework"
    note = client.create_note(new_user["token"], title, description, "Work")
    assert note.status_code == 200, f"fixture 创建笔记失败: {note.text}"
    return {
        "user": new_user,
        "note_id": note.data["id"],
        "title": title,
        "description": description,
        "category": "Work",
    }
