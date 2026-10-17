# -*- coding: utf-8 -*-
"""通用 UI 用例：UI-01 ~ UI-03。"""
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage


class TestUI:
    def test_login_page_brand(self, driver):
        """UI-01 登录页标题与品牌展示"""
        page = LoginPage(driver).open()
        assert "Swag Labs" in page.driver.title
        assert page.is_visible(*page.LOGIN_BTN), "登录页应显示登录表单"

    def test_burger_menu_items(self, logged_in):
        """UI-02 汉堡菜单功能完整"""
        page = InventoryPage(logged_in)
        page.open_burger_menu()
        menu_texts = [t.strip() for t in page.get_menu_items() if t.strip()]
        expected = ["All Items", "Dynamic Catalog", "About", "Logout", "Reset App State"]
        assert menu_texts == expected, f"菜单项应为 {expected}，实际 {menu_texts}"

    def test_reset_app_state(self, logged_in):
        """UI-03 Reset App State 重置购物车"""
        page = InventoryPage(logged_in)
        page.add_to_cart("Sauce Labs Backpack")
        assert page.get_cart_badge() == 1
        page.reset_app_state()
        assert page.get_cart_badge() == 0, "重置后购物车角标应清空"
        # 注意：当前版本 Reset 后商品按钮仍保持 Remove（未恢复为 Add to cart），
        # 属于被测系统行为差异/潜在缺陷，建议按缺陷模板登记，此处仅断言核心行为。
