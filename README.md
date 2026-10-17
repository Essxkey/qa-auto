# 软件测试自动化练习仓库（第 1~6 周）

两个自动化测试项目的持续集成仓库，覆盖 **Web UI 自动化 + 接口自动化** 两套用例，接入 GitHub Actions 每次提交自动运行。

## 一、仓库结构

```
├── .github/workflows/test-suite.yml   # CI 工作流（两个并行 job）
├── saucedemo_auto/                    # 第 2~3 周：Selenium + Pytest + PO 模式 UI 自动化（28 条）
├── notes_api_auto/                    # 第 4~5 周：Requests + Pytest + 数据驱动 接口自动化（54 条）
└── README.md                          # 本文件
```

各项目内部有独立 README：`saucedemo_auto/README.md`、`notes_api_auto/README.md`。

## 二、CI 工作流说明

| Job | 内容 | 环境 | 时长 |
|---|---|---|---|
| `ui-tests` | SauceDemo 28 条 UI 用例（无头 Chrome） | ubuntu-latest | 约 4~6 分钟 |
| `api-tests` | Notes API 54 条接口用例 | ubuntu-latest | 约 2~4 分钟 |

- 两个 job **并行**执行，互不依赖；
- 触发时机：push 到 `main`/`master`、任意 pull_request、或手动 `Run workflow`；
- 每次运行结束后，可在 Actions 运行页的 **Artifacts** 区域下载两份 HTML 测试报告（`saucedemo-ui-report`、`notes-api-report`），用例失败也会上传，方便定位；
- UI job 设 `HEADLESS=1` 无头运行；`--no-sandbox` 等参数已在框架内置，适配 CI root 环境；
- 接口框架内置网络重试，公网练习站抖动不会误报。

## 三、推送步骤（首次）

```bash
# 1. 在仓库根目录初始化 git
git init
git add .
git commit -m "feat: 接入 UI + API 两套测试用例与 GitHub Actions CI"

# 2. 关联远程仓库（把 <owner>/<repo> 换成你自己的，如 user/qa-auto）
git remote add origin https://github.com/<owner>/<repo>.git
git branch -M main
git push -u origin main
```

推送完成后：GitHub 仓库页面会显示 Actions 正在运行；两个 job 全绿后，可在 README 顶部加状态徽章：

```markdown
[![Test Suite CI](https://github.com/<owner>/<repo>/actions/workflows/test-suite.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/test-suite.yml)
```

## 四、本地复现 CI（可选）

CI 用的就是两个项目各自的本地命令，加了无头/报告参数：

```bash
# UI（与 CI 的 ui-tests 完全一致）
cd saucedemo_auto && HEADLESS=1 python -m pytest --html=report.html --self-contained-html

# 接口（与 CI 的 api-tests 完全一致）
cd notes_api_auto && python -m pytest --html=report.html --self-contained-html
```

> 注意：本地首次跑 UI 需要本机安装 Chrome/Chromium（见 `saucedemo_auto/README.md`）；
> GitHub Actions 的 ubuntu-latest 已预装 Chrome，无需额外配置。

## 五、扩展方向

1. **Allure 报告**：两套框架均可换 `--alluredir=allure-results` + `allure-pytest`，Actions 里加 Allure 插件发布到 Pages。
2. **定时回归**：给 workflow 加 `schedule: - cron: '0 2 * * *'` 每天凌晨自动回归。
3. **失败通知**：job 失败时用 `actions/github-script` 在 PR 上留言或发飞书/邮件通知。
