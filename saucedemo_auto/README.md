# Sauce Demo 自动化测试框架（Selenium + Pytest + PO 模式）

针对 Sauce Demo（https://www.saucedemo.com/）的 Web UI 自动化测试项目，覆盖第 1 周测试用例文档中的 30 条用例（登录 8 + 商品列表 4 + 购物车 5 + 结算 8 + 通用 UI 3）。

## 一、项目结构

```
saucedemo_auto/
├── config.py              # 全局配置：URL、账号、测试数据、超时
├── conftest.py            # pytest fixtures（浏览器、登录前置）+ 失败自动截图
├── pytest.ini             # pytest 配置
├── requirements.txt       # 依赖清单
├── README.md              # 本文件
├── pages/                 # 页面对象层（Page Object 模式）
│   ├── base_page.py       #   基类：封装显式等待与常用操作
│   ├── login_page.py      #   登录页
│   ├── inventory_page.py  #   商品列表页
│   ├── cart_page.py       #   购物车页
│   └── checkout_page.py   #   结算页（信息填写 / 概览 / 完成）
└── tests/                 # 测试用例层
    ├── test_login.py      #   LOGIN-01 ~ 08
    ├── test_inventory.py  #   INV-01 ~ 05
    ├── test_cart.py       #   CART-01 ~ 05
    ├── test_checkout.py   #   CHECKOUT-01 ~ 08
    └── test_ui.py         #   UI-01 ~ 03
```

## 二、安装与运行

```bash
# 1. 创建虚拟环境（可选但推荐）
python -m venv venv
# Windows: venv\Scripts\activate    Linux/macOS: source venv/bin/activate

# 2. 安装依赖（webdriver-manager 会自动下载与本地 Chrome 匹配的 chromedriver）
pip install -r requirements.txt

# 3. 运行全部用例
pytest

# 4. 运行单个模块 / 单条用例
pytest tests/test_login.py
pytest tests/test_login.py::TestLogin::test_login_success

# 5. 生成 HTML 测试报告
pytest --html=report.html --self-contained-html
```

## 三、环境要求

- Python 3.9+
- 本地安装 Chrome 浏览器
- 首次运行会自动下载 chromedriver；若失败，可手动下载并设置：
  ```bash
  # Windows
  set CHROMEDRIVER_PATH=D:\chromedriver.exe
  # Linux/macOS
  export CHROMEDRIVER_PATH=/path/to/chromedriver
  ```
- 无界面环境（服务器/CI）可加无头模式：`set HEADLESS=1`（Windows）或 `export HEADLESS=1`（Linux/macOS）

## 四、用例与测试用例文档对照

| 测试文件 | 对应用例 |
|---|---|
| test_login.py | LOGIN-01 登录成功 / 02 错误密码 / 03 空用户名 / 04 空密码 / 05 全空 / 06 锁定用户 / 07 大小写敏感 / 08 登出 |
| test_inventory.py | INV-01 默认 6 商品 / 02 价格升序 / 03 价格降序 / 05 商品详情 |
| test_cart.py | CART-01 添加单个 / 02 添加多个 / 03 移除 / 04 购物车信息 / 05 空购物车 |
| test_checkout.py | CHECKOUT-01 全流程 / 02-04 必填校验 / 05 总额计算 / 06 概览数量 / 07 取消 / 08 下单后清空 |
| test_ui.py | UI-02 汉堡菜单 / 03 Reset 重置（UI-01 品牌标题并入登录页校验） |

> 说明：INV-04（名称 A-Z 排序）与 INV-06（详情返回）未单独成脚本，属低优先级 UI 校验；
> 需要时在 test_inventory.py 中仿照 INV-02 增加即可（排序 value 为 `az`）。

## 五、扩展框架（加分项）

1. **数据驱动**：把登录测试数据抽到 `data.json`，用 `@pytest.mark.parametrize` 批量跑。
2. **Allure 报告**：`pip install allure-pytest`，运行 `pytest --alluredir=allure-results` 再 `allure serve`。
3. **持续集成**：已接入 GitHub Actions（见仓库根目录 `.github/workflows/test-suite.yml`），push 后自动无头跑全部 28 条用例并上传 HTML 报告。
4. **接口层**：在 PO 之上增加 Requests 接口测试，形成 UI + API 双层覆盖（第 4~5 周已在 `notes_api_auto` 落地）。
