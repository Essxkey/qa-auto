# -*- coding: utf-8 -*-
"""BasePage：所有页面对象的基类，封装 Selenium 常用操作的显式等待。"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config import DEFAULT_TIMEOUT


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    # ---------- 基础操作 ----------
    def find(self, by, locator):
        """等待元素可见并返回。"""
        return self.wait.until(EC.visibility_of_element_located((by, locator)))

    def find_clickable(self, by, locator):
        """等待元素可点击并返回。"""
        return self.wait.until(EC.element_to_be_clickable((by, locator)))

    def click(self, by, locator):
        self.find_clickable(by, locator).click()

    def input_text(self, by, locator, text):
        el = self.find(by, locator)
        el.clear()
        el.send_keys(text)

    def get_text(self, by, locator):
        return self.find(by, locator).text

    def get_texts(self, by, locator):
        return [el.text for el in self.driver.find_elements(by, locator)]

    def select_option(self, by, locator, value):
        Select(self.wait.until(EC.presence_of_element_located((by, locator)))).select_by_value(value)

    def is_visible(self, by, locator, timeout=DEFAULT_TIMEOUT) -> bool:
        """元素在 timeout 内可见返回 True，否则返回 False（不抛异常）。"""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((by, locator)))
            return True
        except Exception:
            return False

    def parse_money(self, text: str) -> float:
        """把 '$7.99' / 'Item total: $7.99' 解析为浮点数。"""
        return float(text.split("$")[-1].replace(",", ""))
