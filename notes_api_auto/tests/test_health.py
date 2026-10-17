# -*- coding: utf-8 -*-
"""健康检查：确认被测接口服务在线。"""

import pytest

pytestmark = pytest.mark.smoke


class TestHealth:
    def test_health_check(self, client):
        resp = client.health()
        assert resp.status_code == 200
        assert resp.success is True
        assert resp.json["message"] == "Notes API is Running"
