# -*- coding: utf-8 -*-
"""商品列表页对象（对应 INV / 部分 CART、UI 用例）。"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT
from pages.base_page import BasePage


def to_slug(product_name: str) -> str:
    """'Sauce Labs Backpack' -> 'sauce-labs-backpack'（元素 ID 的组成部分）。"""
    return product_name.lower().replace(" ", "-")


class InventoryPage(BasePage):
    ITEMS = (By.CLASS_NAME, "inventory_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    ITEM_PRICES = (By.CLASS_NAME, "inventory_item_price")
    SORT_SELECT = (By.CLASS_NAME, "product_sort_container")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
    CART_LINK = (By.ID, "shopping_cart_container")
    BURGER_BTN = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")
    RESET_LINK = (By.ID, "reset_sidebar_link")
    MENU_LINKS = (By.CSS_SELECTOR, ".bm-menu a")

    # ---------- 商品 ----------
    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.ITEMS))

    def get_prices(self) -> list:
        return [self.parse_money(p) for p in self.get_texts(*self.ITEM_PRICES)]

    def get_names(self) -> list:
        return self.get_texts(*self.ITEM_NAMES)

    def sort_by(self, value: str):
        """value: az(名称升序) / za(名称降序) / lohi(价格升序) / hilo(价格降序)"""
        self.select_option(*self.SORT_SELECT, value)

    def open_product(self, product_name: str):
        self.click(By.XPATH,
                   f"//div[contains(@class,'inventory_item_name') and normalize-space(text())='{product_name}']")

    # ---------- 购物车 ----------
    def add_to_cart(self, product_name: str):
        self.click(By.ID, f"add-to-cart-{to_slug(product_name)}")

    def remove_from_cart(self, product_name: str):
        self.click(By.ID, f"remove-{to_slug(product_name)}")

    def is_added(self, product_name: str) -> bool:
        return self.is_visible(By.ID, f"remove-{to_slug(product_name)}")

    def get_cart_badge(self) -> int:
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self) -> "CartPage":
        self.click(*self.CART_LINK)
        from pages.cart_page import CartPage
        return CartPage(self.driver)

    # ---------- 菜单 ----------
    def open_burger_menu(self):
        self.click(*self.BURGER_BTN)

    def get_menu_items(self) -> list:
        # 菜单有展开动画，等待至少一个菜单项文本渲染完成再抓取
        WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            lambda d: any(a.text.strip() for a in d.find_elements(*self.MENU_LINKS)))
        return self.get_texts(*self.MENU_LINKS)

    def logout(self):
        if not self.is_visible(*self.LOGOUT_LINK):
            self.open_burger_menu()
        self.click(*self.LOGOUT_LINK)

    def reset_app_state(self):
        if not self.is_visible(*self.RESET_LINK):
            self.open_burger_menu()
        self.click(*self.RESET_LINK)
