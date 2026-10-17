# -*- coding: utf-8 -*-
"""登录模块用例：LOGIN-01 ~ LOGIN-08。"""
from config import BASE_URL, LOCKED_USER, PASSWORD, STUDENT, WRONG_PASSWORD
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class TestLogin:
    def test_login_success(self, driver):
        """LOGIN-01 正确账号密码登录成功"""
        LoginPage(driver).open().login(STUDENT, PASSWORD)
        assert driver.current_url.endswith("/inventory.html"), \
            f"登录后应跳转商品列表页，实际 URL: {driver.current_url}"

    def test_wrong_password(self, driver):
        """LOGIN-02 错误密码登录失败"""
        lp = LoginPage(driver).open().login(STUDENT, WRONG_PASSWORD)
        assert "do not match any user" in lp.get_error()

    def test_empty_username(self, driver):
        """LOGIN-03 用户名为空"""
        lp = LoginPage(driver).open().login("", PASSWORD)
        assert "Username is required" in lp.get_error()

    def test_empty_password(self, driver):
        """LOGIN-04 密码为空"""
        lp = LoginPage(driver).open().login(STUDENT, "")
        assert "Password is required" in lp.get_error()

    def test_both_empty(self, driver):
        """LOGIN-05 用户名密码均为空"""
        lp = LoginPage(driver).open().login("", "")
        assert "Username is required" in lp.get_error()

    def test_locked_out_user(self, driver):
        """LOGIN-06 锁定用户无法登录"""
        lp = LoginPage(driver).open().login(LOCKED_USER, PASSWORD)
        assert "locked out" in lp.get_error()

    def test_username_case_sensitive(self, driver):
        """LOGIN-07 用户名大小写敏感"""
        lp = LoginPage(driver).open().login("Standard_User", PASSWORD)
        assert "do not match any user" in lp.get_error()

    def test_logout(self, driver, logged_in):
        """LOGIN-08 登录成功后登出"""
        page = InventoryPage(logged_in)
        page.logout()
        assert logged_in.current_url == BASE_URL, "登出后应回到登录页"
        assert LoginPage(logged_in).is_visible(*LoginPage.LOGIN_BTN), "登出后应显示登录按钮"
