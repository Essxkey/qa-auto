# -*- coding: utf-8 -*-
"""登录页对象（对应 LOGIN 模块用例）。"""
from selenium.webdriver.common.by import By

from config import BASE_URL
from pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "h3[data-test='error']")

    def open(self) -> "LoginPage":
        self.driver.get(BASE_URL)
        return self

    def login(self, username: str, password: str) -> "LoginPage":
        self.input_text(*self.USERNAME, username)
        self.input_text(*self.PASSWORD, password)
        self.click(*self.LOGIN_BTN)
        return self

    def get_error(self) -> str:
        return self.get_text(*self.ERROR)
