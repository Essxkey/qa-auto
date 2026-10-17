# -*- coding: utf-8 -*-
"""全局配置：URL、账号、测试数据、超时时间。"""
import os

# 被测环境
BASE_URL = "https://www.saucedemo.com/"

# 账号（密码对所有用户统一）
STUDENT = "standard_user"           # 正常用户
LOCKED_USER = "locked_out_user"     # 被锁定用户
PROBLEM_USER = "problem_user"       # 问题用户（图片异常）
GLITCH_USER = "performance_glitch_user"  # 性能异常用户
ERROR_USER = "error_user"           # 错误用户
VISUAL_USER = "visual_user"         # 视觉用户
PASSWORD = "secret_sauce"
WRONG_PASSWORD = "wrong_pass"

# 结算测试数据
FIRST_NAME = "张三"
LAST_NAME = "测试"
POSTAL_CODE = "330000"

# 超时（秒）
DEFAULT_TIMEOUT = 10
IMPLICIT_WAIT = 5

# 浏览器驱动：手动指定时设置环境变量 CHROMEDRIVER_PATH，否则自动下载
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "")
HEADLESS = os.getenv("HEADLESS", "0") == "1"
