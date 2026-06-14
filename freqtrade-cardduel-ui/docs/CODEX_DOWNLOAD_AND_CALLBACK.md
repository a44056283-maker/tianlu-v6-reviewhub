# Codex 下载与回调说明

用途：让 Codex 把 Freqtrade 官方交易机器人与 FreqUI 前端拉到本地，并基于本分支的天禄卡牌对战 UI 蓝图继续实现、测试、回传。

## 1. 仓库地址

### 天禄 UI 改造说明仓库

```bash
REVIEW_REPO=https://github.com/a44056283-maker/tianlu-v6-reviewhub.git
REVIEW_BRANCH=freqtrade-cardduel-ui
PACKAGE_DIR=freqtrade-cardduel-ui
```

浏览地址：

```text
https://github.com/a44056283-maker/tianlu-v6-reviewhub/tree/freqtrade-cardduel-ui/freqtrade-cardduel-ui
```

### 官方原版源码

```bash
BACKEND_REPO=https://github.com/freqtrade/freqtrade.git
FRONTEND_REPO=https://github.com/freqtrade/frequi.git
```

说明：

- `freqtrade/freqtrade` 是交易机器人后端。
- `freqtrade/frequi` 是官方 WebUI 前端，也是主要改造目标。
- 本仓库当前保存 UI 改造蓝图、模块矩阵、Codex 回调契约；完整实现应由 Codex 在本地 clone 官方源码后落地。

## 2. 本地下载与组装

```bash
mkdir -p ~/tianlu-freqtrade-cardduel
cd ~/tianlu-freqtrade-cardduel

# 1) 下载天禄 UI 改造说明仓库
git clone --branch "$REVIEW_BRANCH" "$REVIEW_REPO" reviewhub

# 2) 下载 Freqtrade 官方后端
git clone "$BACKEND_REPO" freqtrade-backend

# 3) 下载 FreqUI 官方前端
git clone "$FRONTEND_REPO" tianlu-frequi-cardduel
cd tianlu-frequi-cardduel
git remote rename origin upstream
git checkout -b tianlu/cardduel-ui
```

## 3. Codex 实现任务

请基于以下文件实现全量 UI：

```text
reviewhub/freqtrade-cardduel-ui/README.md
reviewhub/freqtrade-cardduel-ui/docs/PAGE_BLUEPRINTS.md
reviewhub/freqtrade-cardduel-ui/docs/MODULE_RULE_MATRIX.md
reviewhub/freqtrade-cardduel-ui/docs/CODEX_DOWNLOAD_AND_CALLBACK.md
```

实现要求：

1. 保留 FreqUI 原始路由、API、Pinia store、登录链路、危险操作确认链路。
2. 只改视觉层、布局层、响应式层，不改交易执行逻辑。
3. 所有页面按卡牌对战风格重做：暗黑战场、金色边框、符文状态、卡牌面板、战报日志。
4. 移动端必须自适应：表格转卡片，核心风险状态不可隐藏，底部导航变技能槽。
5. 不使用 Riot、英雄联盟、英雄头像、Logo、图标或原始美术素材；只做原创同类型暗黑卡牌风格。
6. 不提交 `.env`、API Key、Secret、Passphrase、数据库、交易日志、钱包私钥。

## 4. 建议本地命令

```bash
cd ~/tianlu-freqtrade-cardduel/tianlu-frequi-cardduel
pnpm install
pnpm run typecheck
pnpm run lint
pnpm run build
```

如需后端联调：

```bash
cd ~/tianlu-freqtrade-cardduel/freqtrade-backend
# 按 Freqtrade 官方文档启用 webserver/API，优先 dry-run，不允许实盘密钥进入仓库。
```

## 5. 回调 / 交付方法

Codex 完成后，请把结果回传到本仓库新分支或 PR。推荐分支名：

```bash
codex/freqtrade-cardduel-ui-implementation
```

回调目录：

```text
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/
```

必须提交以下文件：

```text
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/REPORT.md
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/PATCH.diff
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/TEST_LOG.md
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/RISK_CHECK.md
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/ROLLBACK.md
03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/SCREENSHOT_INDEX.md
```

文件内容要求：

- `REPORT.md`：完成了哪些页面、哪些组件、哪些移动端适配。
- `PATCH.diff`：相对官方 `freqtrade/frequi` 的完整 diff。
- `TEST_LOG.md`：`pnpm install`、`typecheck`、`lint`、`build`、浏览器自测结果。
- `RISK_CHECK.md`：确认没有改交易逻辑、没有绕过强制平仓/取消订单确认、没有提交密钥。
- `ROLLBACK.md`：如何回滚到官方 FreqUI 原版。
- `SCREENSHOT_INDEX.md`：桌面端与移动端截图清单。

生成 diff 示例：

```bash
cd ~/tianlu-freqtrade-cardduel/tianlu-frequi-cardduel
git diff upstream/main...HEAD > ../reviewhub/03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/PATCH.diff
```

提交示例：

```bash
cd ~/tianlu-freqtrade-cardduel/reviewhub
git checkout -b codex/freqtrade-cardduel-ui-implementation
mkdir -p 03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI
# 写入 REPORT.md / PATCH.diff / TEST_LOG.md / RISK_CHECK.md / ROLLBACK.md / SCREENSHOT_INDEX.md
git add 03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI
git commit -m "codex: implement freqtrade cardduel ui review package"
git push -u origin codex/freqtrade-cardduel-ui-implementation
```

然后创建 PR：

```text
base: main
head: codex/freqtrade-cardduel-ui-implementation
title: codex: implement Freqtrade Cardduel UI
```

## 6. GPT 审核入口

PR 创建后，在 PR 描述中标明：

```text
请 GPT 审核：03_PENDING_GPT_REVIEW/CODEX_FREQTRADE_CARDUEL_UI/
重点检查：交易逻辑未改、危险操作确认未弱化、移动端核心风险状态可见、构建通过。
```
