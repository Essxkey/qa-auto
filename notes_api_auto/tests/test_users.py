# -*- coding: utf-8 -*-
"""用户模块：注册 / 登录 / 资料（含数据驱动校验用例）。"""

import json
from pathlib import Path

import pytest

from api_client.notes_client import random_email, random_name
from config import VALID_PASSWORD

DATA = json.loads((Path(__file__).resolve().parents[1] / "data" / "test_data.json").read_text(encoding="utf-8"))


class TestRegister:
    def test_register_success(self, client):
        resp = client.register(random_name(), random_email(), VALID_PASSWORD)
        assert resp.status_code == 201
        assert resp.success is True
        assert resp.json["message"] == "User account created successfully"
        # 返回体应包含 id / name / email，且与请求一致
        assert resp.data["id"]
        assert resp.data["name"].startswith("ApiTester")
        assert "@" in resp.data["email"]

    def test_register_duplicate_email(self, client, new_user):
        """同一邮箱重复注册应被拒绝（409）。"""
        resp = client.register(new_user["name"], new_user["email"], VALID_PASSWORD)
        assert resp.status_code == 409
        assert resp.success is False
        assert resp.message == "An account already exists with the same email address"

    @pytest.mark.parametrize("case", DATA["register_validation"], ids=lambda c: c["id"])
    def test_register_validation(self, client, case):
        """数据驱动：非法邮箱 / 名字越界 / 密码越界。"""
        resp = client.register(case["name"], case["email"], case["password"])
        assert resp.status_code == case["expected_status"]
        assert resp.success is False
        assert case["expected_message"] in resp.message


class TestLogin:
    def test_login_success(self, client, new_user):
        resp = client.login(new_user["email"], VALID_PASSWORD)
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.json["message"] == "Login successful"
        assert resp.data["token"]                     # token 非空
        assert resp.data["email"] == new_user["email"]

    def test_login_wrong_password(self, client, new_user):
        resp = client.login(new_user["email"], "WrongPass1")
        assert resp.status_code == 401
        assert resp.success is False
        assert resp.message == "Incorrect email address or password"

    def test_login_nonexistent_email(self, client):
        resp = client.login(random_email(prefix="ghost"), VALID_PASSWORD)
        assert resp.status_code == 401
        assert resp.message == "Incorrect email address or password"

    @pytest.mark.parametrize("case", DATA["login_validation"], ids=lambda c: c["id"])
    def test_login_validation(self, client, case):
        resp = client.login(case["email"], case["password"])
        assert resp.status_code == case["expected_status"]
        assert resp.success is False
        if "expected_message" in case:
            assert case["expected_message"] in resp.message


class TestProfile:
    def test_get_profile_matches_registered(self, client, new_user):
        resp = client.get_profile(new_user["token"])
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.data["name"] == new_user["name"]
        assert resp.data["email"] == new_user["email"]

    def test_patch_profile_name(self, client, new_user):
        new_name = "Renamed" + random_name()
        resp = client.patch_profile(new_user["token"], new_name)
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.json["message"] == "Profile updated successful"
        assert resp.data["name"] == new_name

        # 修改后查询应反映新名字
        profile = client.get_profile(new_user["token"])
        assert profile.data["name"] == new_name

    def test_patch_profile_name_too_short(self, client, new_user):
        resp = client.patch_profile(new_user["token"], "ab")
        assert resp.status_code == 400
        assert resp.message == "User name must be between 4 and 30 characters"
