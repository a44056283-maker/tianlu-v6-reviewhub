# 15 全局外壳对照：NavBar / NavFooter / BodyLayout / 卡牌战场 HUD

## 官方版本锁定

- 后端：`freqtrade/freqtrade`
- 分支：`develop`
- Commit：`9aa5a628d891ca13f11d6647963dd413736fbb8c`
- 前端：`freqtrade/frequi`
- 分支：`main`
- Commit：`1745a9f77e4a9a7ae2386815ec6c56330b95cdce`

## 官方页面定位

### 应用外壳

`src/App.vue`

必须保留：

- `useSettingsStore()`
- `useColorStore()`
- `setTimezone(settingsStore.timezone)`
- `colorStore.updateProfitLossColor()`
- timezone watch
- `:style="colorStore.cssVars"`
- `<NavBar />`
- `<BodyLayout />`
- `<NavFooter />`

### 顶部导航

`src/components/layout/NavBar.vue`

必须保留：

- `Favico` open trade pill 逻辑
- `pingInterval` 每 60 秒调用 `botStore.pingAll`
- `settingsStore.loadUIVersion()`
- `setTitle()`
- `setOpenTradesAsPill()`
- `resetDynamicLayout()` 中 `/trade` 调用 `layoutStore.resetTradingLayout()`
- `resetDynamicLayout()` 中 `/dashboard` 调用 `layoutStore.resetDashboardLayout()`
- `clickLogout()`
- `editBotLogin(botId)`
- `useLoginDialog()`
- `ThemeSelect`
- `BotEntry`
- `BotSelect`
- `ReloadControl`
- `UDropdownMenu` 的 `menuItems`

### 导航路由

必须保留：

- `Trade` -> `/trade`
- `Dashboard` -> `/dashboard`
- `Chart` -> `/graph`
- `Logs` -> `/logs`
- `Settings` -> `/settings`
- `Backtest` -> `/backtest`
- `Download Data` -> `/download_data`
- `Pairlist Config` -> `/pairlist_config`
- `Login` button -> `loginDialog({})`
- `Logout` menu item -> `clickLogout()`
- `Lock Layout` / `Unlock Layout`
- `Reset Layout`

### 主体布局

`src/components/layout/BodyLayout.vue`

必须保留：

- `<RouterView />`

### 移动底栏

`src/components/layout/NavFooter.vue`

必须保留：

- `Trades` -> `/open_trades`
- `History` -> `/trade_history`
- `Pairlist` -> `/pairlist`
- `Balance` -> `/balance`
- `Dashboard` -> `/dashboard`
- `v-if="!botStore.canRunBacktest"`

## 设计目标

页面风格命名：`全局卡牌战场外壳 / Global Card Duel Shell`

视觉元素：

- 顶部导航改成暗黑金边战场 HUD。
- 品牌标识改成原创“TL 决策核心”，但保留 `FreqtradeUI` 文本。
- 主导航按钮改成符文胶囊按钮。
- Bot 状态区域改成 Selected Bot HUD。
- Confirm Dialog 关闭提示改成黄色风险警示符文。
- 用户菜单保留 `FT` Avatar。
- 移动端底栏改成五个技能槽：Trades、History、Pairlist、Balance、Dashboard。
- BodyLayout 增加暗黑符文背景，不改任何页面路由。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 当前 Bot | `botStore.activeBot.botName` | 保留 |
| 无 Bot 文案 | `No bot selected` | 保留 |
| 版本号 | `settingsStore.uiVersion` | 保留 |
| 开仓数标题/徽章 | `openTradesInTitle` + `openTradeCount` | 保留 |
| 布局锁定 | `layoutStore.layoutLocked` | 保留 |
| 重置布局 | `resetDynamicLayout()` | 保留 |
| 登录弹窗 | `loginDialog({})` | 保留 |
| 编辑 Bot 登录 | `editBotLogin(botId)` | 保留 |
| Reload | `ReloadControl` | 保留 |
| 主题切换 | `ThemeSelect` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/App.vue
src/components/layout/NavBar.vue
src/components/layout/NavFooter.vue
src/components/layout/BodyLayout.vue
src/components/AppIcon.vue
src/components/AppText.vue
src/styles/cardduel-shell.css
```

其中：

- `App.vue`：只增加 `import './styles/cardduel-shell.css';` 和外壳 class。
- `NavBar.vue`：保留 script 全部逻辑，只替换 template 为战场 HUD。
- `NavFooter.vue`：保留移动端 routes 和 labels，只替换成技能槽皮肤。
- `BodyLayout.vue`：保留 `<RouterView />`，增加符文背景容器。
- `AppIcon.vue` / `AppText.vue`：使用原创 TL 标识，保留 `FreqtradeUI` 文本。
- `cardduel-shell.css`：新增全局暗黑背景、顶部 HUD、移动底栏和响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Trade`
- `Dashboard`
- `Chart`
- `Logs`
- `Settings`
- `Backtest`
- `Download Data`
- `Pairlist Config`
- `Login`
- `Logout`
- `Lock Layout`
- `Unlock Layout`
- `Reset Layout`
- `No bot selected`
- `FT`
- `Version:`
- `Trades`
- `History`
- `Pairlist`
- `Balance`
- `FreqtradeUI`

## 移动端行为

- `> 1180px`：完整顶部 HUD，主导航横向显示。
- `<= 900px`：品牌文案隐藏，仅显示 TL 徽章。
- `<= 768px`：顶部使用 Slideover 导航，底部技能槽显示。
- `<= 720px`：主内容底部增加 safe-area padding，避免被技能槽遮挡。
- 移动端不隐藏 Reload、BotSelect 和核心导航入口。

## 安全边界

禁止改动：

- Bot 登录/登出逻辑
- Bot 选择逻辑
- Bot ping 逻辑
- Favico open trade pill 逻辑
- document.title 更新逻辑
- layout lock/reset 逻辑
- ThemeSelect / BotSelect / ReloadControl 内部逻辑
- Nav route 映射
- `<RouterView />`
- 后端 API 调用

只允许改视觉、布局、class、品牌展示和响应式 CSS。
