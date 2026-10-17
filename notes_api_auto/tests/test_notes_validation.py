# -*- coding: utf-8 -*-
"""笔记模块字段校验（边界值 / 非法值 / 数据驱动）。"""

import json
from pathlib import Path

import pytest

from api_client.notes_client import random_text
from config import DESCRIPTION_MAX, TITLE_MAX

DATA = json.loads((Path(__file__).resolve().parents[1] / "data" / "test_data.json").read_text(encoding="utf-8"))


class TestCreateValidation:
    def test_title_too_short(self, client, new_user):
        resp = client.create_note(new_user["token"], "ab", "valid description here", "Work")
        assert resp.status_code == 400
        assert resp.message == "Title must be between 4 and 100 characters"

    def test_title_too_long(self, client, new_user):
        resp = client.create_note(new_user["token"], random_text("T", TITLE_MAX + 1), "valid description here", "Work")
        assert resp.status_code == 400
        assert resp.message == "Title must be between 4 and 100 characters"

    def test_description_too_short(self, client, new_user):
        resp = client.create_note(new_user["token"], "Valid Title", "abc", "Work")
        assert resp.status_code == 400
        assert resp.message == "Description must be between 4 and 1000 characters"

    def test_description_too_long(self, client, new_user):
        resp = client.create_note(new_user["token"], "Valid Title", random_text("D", DESCRIPTION_MAX + 1), "Work")
        assert resp.status_code == 400
        assert resp.message == "Description must be between 4 and 1000 characters"

    @pytest.mark.parametrize("case", DATA["note_category_invalid"], ids=lambda c: c["id"])
    def test_invalid_category(self, client, new_user, case):
        resp = client.create_note(new_user["token"], "Valid Title", "valid description", case["category"])
        assert resp.status_code == 400
        assert resp.message == "Category must be one of the categories: Home, Work, Personal"


class TestUpdateValidation:
    def test_put_title_too_short(self, client, created_note):
        note = created_note
        resp = client.update_note(
            note["user"]["token"], note["note_id"], "ab", "valid description", "Work", False
        )
        assert resp.status_code == 400
        assert resp.message == "Title must be between 4 and 100 characters"

    def test_put_missing_category(self, client, created_note):
        note = created_note
        # 直接发送缺 category 的请求体（客户端方法不强制，这里模拟漏传）
        resp = client.patch_note(note["user"]["token"], note["note_id"],
                                 {"title": "New Title", "description": "desc", "completed": False})
        # PATCH 与 PUT 行为不同，单独验证 PUT 语义：用底层请求构造缺 category 的 PUT
        from api_client.notes_client import ApiResponse
        raw = client.session.request(
            "PUT",
            f"{client.base_url}/notes/{note['note_id']}",
            json={"title": "New Title", "description": "valid desc", "completed": False},
            headers={"X-Auth-Token": note["user"]["token"]},
            timeout=client.timeout,
        )
        resp = ApiResponse(raw.status_code, raw.json() if raw.text else None, raw.text)
        assert resp.status_code == 400
        assert resp.message == "Category must be one of the categories: Home, Work, Personal"

    @pytest.mark.parametrize("case", DATA["note_completed_not_boolean"], ids=lambda c: c["id"])
    def test_patch_completed_must_be_boolean(self, client, created_note, case):
        note = created_note
        resp = client.patch_note(note["user"]["token"], note["note_id"], {"completed": case["completed"]})
        assert resp.status_code == 400
        assert resp.message == "Note completed status must be boolean"

    @pytest.mark.parametrize("value,expected", [(1, True), (0, False)], ids=["int_one_true", "int_zero_false"])
    def test_patch_completed_accepts_int(self, client, created_note, value, expected):
        """实测行为：completed 接受整数 0/1（宽松布尔），按真值处理。"""
        note = created_note
        resp = client.patch_note(note["user"]["token"], note["note_id"], {"completed": value})
        assert resp.status_code == 200
        assert resp.data["completed"] is expected

    def test_patch_missing_completed(self, client, created_note):
        note = created_note
        resp = client.patch_note(note["user"]["token"], note["note_id"], {"title": "Only Title"})
        assert resp.status_code == 400
        assert resp.message == "Note completed status must be boolean"
