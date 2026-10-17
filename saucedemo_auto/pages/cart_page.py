# -*- coding: utf-8 -*-
"""购物车页对象（对应 CART 模块用例）。"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")
    CHECKOUT_BTN = (By.ID, "checkout")
    CONTINUE_SHOPPING = (By.ID, "continue-shopping")

    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def get_item_names(self) -> list:
        return self.get_texts(*self.ITEM_NAMES)

    def is_empty(self) -> bool:
        return len(self.driver.find_elements(*self.CART_ITEMS)) == 0

    def checkout(self) -> "CheckoutPage":
        self.click(*self.CHECKOUT_BTN)
        from pages.checkout_page import CheckoutPage
        return CheckoutPage(self.driver)

    def continue_shopping(self):
        self.click(*self.CONTINUE_SHOPPING)
