# -*- coding: utf-8 -*-
"""pytest 全局 fixtures 与失败截图钩子。"""
import os
import sys
from pathlib import Path

import pytest

# 保证在任何目录下运行 pytest 都能 import config / pages
sys.path.insert(0, str(Path(__file__).parent))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config import BASE_URL, CHROMEDRIVER_PATH, HEADLESS, IMPLICIT_WAIT, PASSWORD, STUDENT
from pages.login_page import LoginPage


def _create_driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if CHROMEDRIVER_PATH:
        service = Service(CHROMEDRIVER_PATH)
        return webdriver.Chrome(service=service, options=options)

    from webdriver_manager.chrome import ChromeDriverManager, ChromeType

    # 环境变量 CHROMIUM=1 时使用 Chromium 对应驱动（本地是 Google Chrome 时保持默认）
    if os.getenv("CHROMIUM", "0") == "1":
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
    else:
        service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


@pytest.fixture(scope="function")
def driver():
    """每个用例独立的浏览器实例，用后自动关闭。"""
    driver = _create_driver()
    driver.implicitly_wait(IMPLICIT_WAIT)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def logged_in(driver):
    """已登录 standard_user 的会话，作为商品/购物车/结算用例的前置。"""
    driver.get(BASE_URL)
    LoginPage(driver).login(STUDENT, PASSWORD)
    return driver


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时自动截图到 screenshots/ 目录。"""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            shot_dir = Path("screenshots")
            shot_dir.mkdir(exist_ok=True)
            driver.save_screenshot(str(shot_dir / f"{item.name}.png"))
