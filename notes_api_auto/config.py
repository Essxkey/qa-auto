# -*- coding: utf-8 -*-
"""全局配置：被测接口地址、鉴权头、超时与重试策略、测试数据常量。"""

BASE_URL = "https://practice.expandtesting.com/notes/api"

# 鉴权方式：x-auth-token 请求头
AUTH_HEADER = "X-Auth-Token"

# 网络策略：单次请求超时 + 瞬时故障（502/503/网络抖动）重试次数与间隔（秒）
TIMEOUT = 20
RETRIES = 3
RETRY_BACKOFF = 3          # 每次重试前等待的秒数
RETRY_STATUS_CODES = (502, 503, 504)

# 合法分类（大小写敏感，来自接口校验规则）
VALID_CATEGORIES = ("Home", "Work", "Personal")

# 合法账号数据（注册/登录用；name 4~30 字符，password 6~30 字符，email 需合法格式）
VALID_NAME = "ApiTester"
VALID_PASSWORD = "Password123!"
EMAIL_DOMAIN = "example.com"

# 各字段边界（来自实测接口校验）
NAME_MIN, NAME_MAX = 4, 30
PASSWORD_MIN, PASSWORD_MAX = 6, 30
TITLE_MIN, TITLE_MAX = 4, 100
DESCRIPTION_MIN, DESCRIPTION_MAX = 4, 1000
