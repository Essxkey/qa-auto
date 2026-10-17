# -*- coding: utf-8 -*-
"""Requests 封装的 Notes API 客户端。

职责：
- 统一处理 Base URL、鉴权头、超时与瞬时故障重试；
- 覆盖全部已实测可用的端点（健康检查 / 用户注册登录资料 / 笔记 CRUD）；
- 返回轻量 ApiResponse（status_code + json + text），供测试层断言。
"""

from __future__ import annotations

import random
import string
import time

import requests

from config import (
    AUTH_HEADER,
    BASE_URL,
    RETRIES,
    RETRY_BACKOFF,
    RETRY_STATUS_CODES,
    TIMEOUT,
)


class ApiResponse:
    """轻量响应封装：保留状态码、JSON 体和原始文本，便于断言与排障。"""

    __slots__ = ("status_code", "json", "text")

    def __init__(self, status_code: int, json_body, text: str):
        self.status_code = status_code
        self.json = json_body
        self.text = text

    @property
    def success(self) -> bool:
        return bool(self.json and self.json.get("success"))

    @property
    def message(self) -> str:
        return (self.json or {}).get("message", "")

    @property
    def data(self):
        return (self.json or {}).get("data")

    def __repr__(self):
        return f"<ApiResponse {self.status_code} success={self.success} message={self.message!r}>"


class NotesApiClient:
    """Notes API 客户端：每个方法对应一个端点，返回 ApiResponse。"""

    def __init__(self, base_url: str = BASE_URL, timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ---------------------------------------------------------------- 基础请求
    def _request(self, method: str, path: str, body=None, token: str | None = None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        headers = {}
        if token:
            headers[AUTH_HEADER] = token

        last_exc = None
        for attempt in range(RETRIES):
            try:
                resp = self.session.request(
                    method, url, json=body, headers=headers, timeout=self.timeout
                )
                if resp.status_code in RETRY_STATUS_CODES and attempt < RETRIES - 1:
                    time.sleep(RETRY_BACKOFF)
                    continue
                return self._wrap(resp)
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_exc = exc
                if attempt < RETRIES - 1:
                    time.sleep(RETRY_BACKOFF)
        raise RuntimeError(f"请求失败（已重试 {RETRIES} 次）: {last_exc}")

    @staticmethod
    def _wrap(resp: requests.Response) -> ApiResponse:
        try:
            json_body = resp.json()
        except ValueError:
            json_body = None
        return ApiResponse(resp.status_code, json_body, resp.text)

    # ---------------------------------------------------------------- 健康检查
    def health(self) -> ApiResponse:
        return self._request("GET", "/")

    # ---------------------------------------------------------------- 用户
    def register(self, name: str, email: str, password: str) -> ApiResponse:
        return self._request("POST", "/users/register", {"name": name, "email": email, "password": password})

    def login(self, email: str, password: str) -> ApiResponse:
        return self._request("POST", "/users/login", {"email": email, "password": password})

    def get_profile(self, token: str) -> ApiResponse:
        return self._request("GET", "/users/profile", token=token)

    def patch_profile(self, token: str, name: str) -> ApiResponse:
        return self._request("PATCH", "/users/profile", {"name": name}, token=token)

    # ---------------------------------------------------------------- 笔记
    def create_note(self, token: str, title: str, description: str, category: str) -> ApiResponse:
        return self._request(
            "POST", "/notes", {"title": title, "description": description, "category": category}, token=token
        )

    def get_notes(self, token: str, query: str = "") -> ApiResponse:
        return self._request("GET", f"/notes{query}", token=token)

    def get_note(self, token: str, note_id: str) -> ApiResponse:
        return self._request("GET", f"/notes/{note_id}", token=token)

    def update_note(self, token: str, note_id: str, title: str, description: str, category: str, completed: bool) -> ApiResponse:
        return self._request(
            "PUT",
            f"/notes/{note_id}",
            {"title": title, "description": description, "category": category, "completed": completed},
            token=token,
        )

    def patch_note(self, token: str, note_id: str, body: dict) -> ApiResponse:
        return self._request("PATCH", f"/notes/{note_id}", body, token=token)

    def delete_note(self, token: str, note_id: str) -> ApiResponse:
        return self._request("DELETE", f"/notes/{note_id}", token=token)


# ---------------------------------------------------------------- 测试数据工厂
def random_email(prefix: str = "qa") -> str:
    """生成随机邮箱，避免注册冲突。"""
    from config import EMAIL_DOMAIN
    return f"{prefix}{random.randint(100000, 999999)}.{random.randint(100, 999)}@{EMAIL_DOMAIN}"


def random_name(prefix: str = "ApiTester") -> str:
    return f"{prefix}{random.randint(1000, 9999)}"


def random_text(prefix: str, length: int) -> str:
    """生成指定长度的随机文本（用于超长字段）。"""
    body = prefix + "".join(random.choices(string.ascii_letters, k=length))
    return body[:length]
