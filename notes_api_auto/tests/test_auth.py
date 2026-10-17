# -*- coding: utf-8 -*-
"""鉴权与数据隔离：无 token / 非法 token / 跨用户访问。"""

NO_TOKEN_MSG = "No authentication token specified in x-auth-token header"
BAD_TOKEN_MSG = "Access token is not valid or has expired, you will need to login"


class TestAuthRequired:
    def test_get_notes_without_token(self, client):
        resp = client.get_notes("")
        assert resp.status_code == 401
        assert resp.message == NO_TOKEN_MSG

    def test_get_notes_with_invalid_token(self, client):
        resp = client.get_notes("deadbeefdeadbeefdeadbeef")
        assert resp.status_code == 401
        assert resp.message == BAD_TOKEN_MSG

    def test_create_note_without_token(self, client):
        resp = client.create_note("", "No Auth", "should be rejected", "Work")
        assert resp.status_code == 401
        assert resp.message == NO_TOKEN_MSG

    def test_get_profile_without_token(self, client):
        resp = client.get_profile("")
        assert resp.status_code == 401
        assert resp.message == NO_TOKEN_MSG

    def test_patch_profile_without_token(self, client):
        resp = client.patch_profile("", "NewName")
        assert resp.status_code == 401
        assert resp.message == NO_TOKEN_MSG


class TestDataIsolation:
    """用户 B 创建的笔记，用户 A 不应可见 / 可改 / 可删。"""

    def test_cross_user_get_note_returns_404(self, client, new_user, second_user):
        owned = client.create_note(second_user["token"], "Private Note", "only for second user", "Work")
        # 本人可见
        resp = client.get_note(second_user["token"], owned.data["id"])
        assert resp.status_code == 200
        # 他人读取 → 404
        resp = client.get_note(new_user["token"], owned.data["id"])
        assert resp.status_code == 404

    def test_cross_user_update_note_returns_404(self, client, new_user, second_user):
        owned = client.create_note(second_user["token"], "Locked Note", "cannot be touched by others", "Work")
        resp = client.update_note(
            new_user["token"], owned.data["id"], "Hacked", "hacked", "Home", True
        )
        assert resp.status_code == 404

    def test_cross_user_delete_note_returns_404(self, client, new_user, second_user):
        owned = client.create_note(second_user["token"], "Safe Note", "must not be deleted", "Work")
        resp = client.delete_note(new_user["token"], owned.data["id"])
        assert resp.status_code == 404
        # 本人仍可读到
        still_there = client.get_note(second_user["token"], owned.data["id"])
        assert still_there.status_code == 200
