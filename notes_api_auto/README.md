# Notes API 接口自动化测试框架（Requests + Pytest + 数据驱动）

针对 [practice.expandtesting.com](https://practice.expandtesting.com/notes/api) 的 **Notes API** 编写，
是第 4~5 周接口自动化练习项目（延续第 1 周用例文档、第 2~3 周 Sauce Demo UI 自动化）。

## 一、覆盖范围

框架覆盖全部已实测可用的 11 个端点，共 **约 40 条用例**：

| 模块 | 覆盖内容 | 用例数 |
|---|---|---|
| 健康检查 | `GET /` 服务在线 | 1 |
| 用户-注册 | 成功、重复邮箱 409、非法邮箱/名字/密码边界（数据驱动 8 组） | 10 |
| 用户-登录 | 成功返回 token、密码错误 401、账号不存在 401、缺字段 400 | 4 |
| 用户-资料 | 查询一致、改名成功、非法名字 400 | 3 |
| 笔记-正向 | 创建、列表、单查、PUT 全量更新、PATCH 局部更新、完成状态切换、删除、删后 404 | 12 |
| 笔记-校验 | 标题/描述长度边界、非法分类（数据驱动 4 组）、PUT 缺字段、PATCH completed 非布尔（数据驱动 3 组） | 10 |
| 鉴权 | 无 token 401、非法 token 401、各端点鉴权要求 | 5 |
| 数据隔离 | 跨用户 读/改/删 他人笔记均 404 | 3 |

> 精确用例数以实际 pytest 收集为准（数据驱动参数化会展开为多条）。

## 二、项目结构

```
notes_api_auto/
├── config.py                    # 接口地址、鉴权头、超时/重试、字段边界
├── conftest.py                  # fixtures：client / new_user / second_user / created_note
├── pytest.ini                   # pytest 配置
├── requirements.txt             # requests / pytest / pytest-html
├── data/
│   └── test_data.json           # 数据驱动用例（注册/登录校验、非法分类、completed 类型）
├── api_client/
│   ├── __init__.py
│   └── notes_client.py          # NotesApiClient：11 个端点封装 + 瞬时故障重试 + 测试数据工厂
├── tests/
│   ├── __init__.py
│   ├── test_health.py           # 健康检查
│   ├── test_users.py            # 注册 / 登录 / 资料（数据驱动）
│   ├── test_notes_crud.py       # 笔记 CRUD 正向
│   ├── test_notes_validation.py # 笔记字段校验（数据驱动）
│   └── test_auth.py             # 鉴权 + 跨用户隔离
└── README.md
```

## 三、安装与运行

```bash
# 1. 进入项目目录并创建虚拟环境（推荐）
cd notes_api_auto
python -m venv venv
# Windows: venv\Scripts\activate     macOS/Linux: source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行全部用例
pytest

# 4. 运行单个模块 / 单条用例
pytest tests/test_users.py
pytest tests/test_notes_crud.py::TestNoteDelete::test_delete_note_success

# 5. 生成 HTML 测试报告
pytest --html=report.html --self-contained-html
```

环境要求：Python 3.9+，可联网访问 `practice.expandtesting.com`。
框架内置 **瞬时故障重试**（502/503/网络抖动自动退避重试 3 次），公网练习站偶发不稳定时用例不易误报。

## 四、已实测确认的接口行为（与断言依据一致）

| 端点 | 成功 | 关键错误 |
|---|---|---|
| `GET /` | 200 Notes API is Running | - |
| `POST /users/register` | 201 返回 id/name/email | 400 名字/邮箱/密码非法；409 邮箱已存在 |
| `POST /users/login` | 200 返回 token | 401 账号或密码错误；400 密码越界 |
| `GET /users/profile` | 200 返回资料 | 401 未鉴权 |
| `PATCH /users/profile` | 200 更新名字 | 400 名字越界 |
| `POST /notes` | 200 返回完整笔记 | 400 标题/描述/分类非法 |
| `GET /notes` | 200 返回列表 | 401 未鉴权 |
| `GET /notes/:id` | 200 返回单条 | 404 不存在或非本人 |
| `PUT /notes/:id` | 200 全量更新 | 400 字段非法；404 非本人 |
| `PATCH /notes/:id` | 200 局部更新 | 400 completed 必须为布尔；404 非本人 |
| `DELETE /notes/:id` | 200 删除成功 | 404 不存在或非本人 |

鉴权方式：请求头 `X-Auth-Token: <token>`。

字段规则（实测）：name 4~30 字符；password 6~30 字符；email 需合法格式；
title 4~100 字符；description 4~1000 字符；category 必须为 `Home` / `Work` / `Personal`（大小写敏感）。

## 五、调研中发现的被测系统行为差异（建议登记缺陷）

1. **列表筛选参数疑似未生效**：`GET /notes?category=Home` 与不带筛选返回相同结果，`page`/`limit` 分页参数也未生效——疑似接口未实现筛选/分页，仅按原样返回全部笔记。已按“不筛选”实测行为设计用例，未做筛选生效的断言。
2. **文档中的部分端点不存在**：`DELETE /notes`（删除全部）与 `DELETE /users/profile`（删除账号）实际返回 404 页面——官方文档列举的端点与线上实现不一致，接口测试时需以线上实测为准。
3. **PATCH 只生效 completed**：`PATCH /notes/:id` 仅处理 `completed` 字段——同时传入的 `title`/`description`/`category` 会被**静默忽略**（返回 200 但内容不变）；且 completed 必须为布尔或整数 0/1，字符串/null 会报 400“completed 必须为布尔”。与常规 REST 的“部分更新”语义不同，用例按此实测行为断言。

## 六、扩展方向（加分项）

1. **Allure 报告**：`pip install allure-pytest`，运行 `pytest --alluredir=allure-results` 后 `allure serve`。
2. **schemas 响应校验**：用 `jsonschema` 对每个端点的响应体做结构校验。
3. **接入 CI**：已与第 2~3 周 UI 框架一起接入 GitHub Actions（见仓库根目录 `.github/workflows/test-suite.yml`），push 后自动跑全部 54 条用例并上传 HTML 报告。
4. **性能冒烟**：用 `locust`/`pytest-benchmark` 对登录与笔记列表做简单压测。
