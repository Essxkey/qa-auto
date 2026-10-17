# -*- coding: utf-8 -*-
"""笔记模块主流程（CRUD 正向用例）。"""

import pytest

pytestmark = pytest.mark.smoke


class TestNoteCreate:
    def test_create_note_success(self, client, new_user):
        resp = client.create_note(new_user["token"], "Buy Coffee Beans", "order 1kg from local roastery", "Work")
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.json["message"] == "Note successfully created"
        assert resp.data["title"] == "Buy Coffee Beans"
        assert resp.data["description"] == "order 1kg from local roastery"
        assert resp.data["category"] == "Work"
        assert resp.data["completed"] is False            # 默认未完成
        assert resp.data["id"]
        assert resp.data["user_id"] == new_user["user_id"]

    def test_create_note_minimal_fields(self, client, new_user):
        resp = client.create_note(new_user["token"], "Minimal Note", "some description", "Personal")
        assert resp.status_code == 200
        assert resp.data["category"] == "Personal"


class TestNoteRead:
    def test_get_all_notes_contains_created(self, client, new_user):
        created = client.create_note(new_user["token"], "List Check", "note used for list assertion", "Home")
        assert created.status_code == 200

        resp = client.get_notes(new_user["token"])
        assert resp.status_code == 200
        assert resp.success is True
        ids = [n["id"] for n in resp.data]
        assert created.data["id"] in ids

    def test_get_single_note(self, client, new_user):
        created = client.create_note(new_user["token"], "Single Note", "fetch me by id", "Work")
        resp = client.get_note(new_user["token"], created.data["id"])
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.data["id"] == created.data["id"]
        assert resp.data["title"] == "Single Note"


class TestNoteUpdate:
    def test_put_updates_all_fields(self, client, new_user):
        created = client.create_note(new_user["token"], "Old Title", "old description", "Work")
        resp = client.update_note(
            new_user["token"], created.data["id"],
            "New Title", "new description", "Home", True,
        )
        assert resp.status_code == 200
        assert resp.json["message"] == "Note successfully Updated"
        assert resp.data["title"] == "New Title"
        assert resp.data["description"] == "new description"
        assert resp.data["category"] == "Home"
        assert resp.data["completed"] is True

    def test_put_toggle_completed(self, client, new_user):
        created = client.create_note(new_user["token"], "Toggle Me", "toggle completed", "Personal")
        resp = client.update_note(
            new_user["token"], created.data["id"],
            "Toggle Me", "toggle completed", "Personal", True,
        )
        assert resp.data["completed"] is True
        # 再次查询确认持久化
        fetched = client.get_note(new_user["token"], created.data["id"])
        assert fetched.data["completed"] is True

    def test_patch_ignores_title_change(self, client, new_user):
        """实测行为：PATCH 只生效 completed，title 修改被静默忽略（疑似缺陷）。"""
        created = client.create_note(new_user["token"], "Patch Base", "original description", "Work")
        resp = client.patch_note(new_user["token"], created.data["id"], {"title": "Patched Title", "completed": False})
        assert resp.status_code == 200
        assert resp.data["title"] == "Patch Base"        # 标题未被修改
        assert resp.data["description"] == "original description"
        assert resp.data["category"] == "Work"
        assert resp.data["completed"] is False           # completed 生效

    def test_patch_toggle_completed(self, client, new_user):
        created = client.create_note(new_user["token"], "Complete It", "mark as done", "Work")
        resp = client.patch_note(new_user["token"], created.data["id"], {"completed": True})
        assert resp.status_code == 200
        assert resp.data["completed"] is True


class TestNoteDelete:
    def test_delete_note_success(self, client, new_user):
        created = client.create_note(new_user["token"], "Delete Me", "will be removed", "Work")
        resp = client.delete_note(new_user["token"], created.data["id"])
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.json["message"] == "Note successfully deleted"

    def test_get_deleted_note_returns_404(self, client, new_user):
        created = client.create_note(new_user["token"], "Gone Soon", "deleted afterwards", "Work")
        client.delete_note(new_user["token"], created.data["id"])
        resp = client.get_note(new_user["token"], created.data["id"])
        assert resp.status_code == 404
        assert resp.success is False
        assert resp.message == "No note was found with the provided ID, Maybe it was deleted"

    def test_get_nonexistent_note_returns_404(self, client, new_user):
        resp = client.get_note(new_user["token"], "deadbeefdeadbeefdeadbeef")
        assert resp.status_code == 404
        assert resp.success is False

    def test_delete_nonexistent_note_returns_404(self, client, new_user):
        resp = client.delete_note(new_user["token"], "deadbeefdeadbeefdeadbeef")
        assert resp.status_code == 404
