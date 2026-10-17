# -*- coding: utf-8 -*-
"""结算页对象：信息填写页 + 概览页 + 完成页（对应 CHECKOUT 模块用例）。"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    # 信息填写页
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE_BTN = (By.ID, "continue")
    CANCEL_BTN = (By.ID, "cancel")
    ERROR = (By.CSS_SELECTOR, "h3[data-test='error']")
    # 概览页
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_TOTAL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX = (By.CLASS_NAME, "summary_tax_label")
    TOTAL = (By.CLASS_NAME, "summary_total_label")
    FINISH_BTN = (By.ID, "finish")
    # 完成页
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")

    # ---------- 信息填写页 ----------
    def fill_info(self, first_name: str, last_name: str, postal_code: str) -> "CheckoutPage":
        self.input_text(*self.FIRST_NAME, first_name)
        self.input_text(*self.LAST_NAME, last_name)
        self.input_text(*self.POSTAL_CODE, postal_code)
        self.click(*self.CONTINUE_BTN)
        return self

    def get_error(self) -> str:
        return self.get_text(*self.ERROR)

    def cancel(self):
        self.click(*self.CANCEL_BTN)

    # ---------- 概览页 ----------
    def get_item_count(self) -> int:
        return len(self.driver.find_elements(*self.CART_ITEMS))

    def get_item_total(self) -> float:
        return self.parse_money(self.get_text(*self.ITEM_TOTAL))

    def get_tax(self) -> float:
        return self.parse_money(self.get_text(*self.TAX))

    def get_total(self) -> float:
        return self.parse_money(self.get_text(*self.TOTAL))

    def finish(self) -> "CheckoutPage":
        self.click(*self.FINISH_BTN)
        return self

    # ---------- 完成页 ----------
    def get_complete_message(self) -> str:
        return self.get_text(*self.COMPLETE_HEADER)
