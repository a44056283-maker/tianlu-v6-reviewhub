# 02 机器人首页对照：Home / 召唤大厅

## 官方版本锁定

- 后端：`freqtrade/freqtrade`
- 分支：`develop`
- Commit：`9aa5a628d891ca13f11d6647963dd413736fbb8c`
- 前端：`freqtrade/frequi`
- 分支：`main`
- Commit：`1745a9f77e4a9a7ae2386815ec6c56330b95cdce`

## 官方页面定位

### 路由

`src/router/index.ts`

- `/` 指向 `src/views/HomeView.vue`
- 这是登录成功后的首页和 Bot 管理入口。
- 当没有 Bot 登录时，顶部导航仍会显示 `No bot selected` 和 `Login` 入口。
- `Login` 按钮会打开 `LoginModal.vue`，不是跳转交易逻辑。

### 页面容器

`src/views/HomeView.vue`

官方当前页面结构：

- 顶部显示 `BotList`
- 中部显示 `AppIcon`
- 标题：`Welcome to the FreqtradeUI`
- 文案：`This page allows you to control your trading bot.`
- 文档链接：`Freqtrade Documentation`
- 结尾：`Have fun - wishes you the Freqtrade team`

### Bot 列表

`src/components/BotList.vue`

必须保留的逻辑：

- `botStore.availableBotsSorted`
- `useSortable(sortContainer, botListComp, ...)`
- 拖拽排序后调用 `botStore.updateBot(...)`
- 点击 Bot 后调用 `botStore.selectBot(bot.botId)`
- 编辑名称：`editBot()` / `BotRename`
- 重新登录：`editBotLogin()` / `useLoginDialog()`
- 新增 Bot：`loginDialog({})`
- Add new Bot 按钮文本必须保留

### Bot 条目

`src/components/BotEntry.vue`

必须保留的逻辑：

- `selectedBotStore.autoRefresh`
- `selectedBotStore.setAutoRefresh(newValue)`
- 在线 / 离线 / 登录过期状态
- 编辑 Bot 事件：`emit('edit', bot.botId)`
- 重新登录事件：`emit('editLogin', bot.botId)`
- 删除 Bot 前必须调用 `useConfirmBox()`
- 删除确认标题：`Logout confirmation`
- 确认后才调用 `botStore.removeBot(...)`

## 设计目标

页面风格命名：`召唤大厅 / Bot Hub`

视觉元素：

- 左侧暗黑符文品牌面板
- 中央水晶徽章
- 首页标题保持官方测试锚点：`Welcome to the FreqtradeUI`
- 右侧 Bot 卡牌牌组
- Bot 卡牌显示：名称、URL、在线状态、自动刷新、编辑、重新登录、删除
- Add new Bot 改成“新增召唤契约”风格，但按钮真实文本保留 `Add new Bot`
- 文档链接保留 `Freqtrade Documentation`

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 召唤大厅 | `/` + `HomeView.vue` | 保留 |
| Bot 牌组 | `BotList.vue` | 保留 |
| Bot 卡牌名称 | `bot.botName || bot.botId` | 保留 |
| 战场入口地址 | `bot.botUrl` | 保留 |
| 在线状态宝石 | `selectedBotStore.isBotOnline` | 保留 |
| 登录过期 | `selectedBotStore.isBotLoggedIn` | 保留 |
| 自动刷新开关 | `autoRefreshLoc` | 保留 |
| 编辑 Bot | `emit('edit', bot.botId)` | 保留 |
| 重新登录 | `emit('editLogin', bot.botId)` | 保留 |
| 删除 Bot | `removeBotQuestion()` | 保留确认弹窗 |
| 新增 Bot | `loginDialog({})` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/HomeView.vue
src/components/BotList.vue
src/components/BotEntry.vue
src/components/BotRename.vue
src/styles/cardduel-bot-hub.css
```

其中：

- `HomeView.vue`：从普通欢迎页改成双栏召唤大厅。
- `BotList.vue`：只替换 template，不改排序、选择、编辑、重新登录逻辑。
- `BotEntry.vue`：只替换 template，不改自动刷新、状态、删除确认逻辑。
- `BotRename.vue`：只加 class，不改保存逻辑。
- `cardduel-bot-hub.css`：新增首页视觉与响应式样式。

## E2E 兼容锚点

必须保留：

- `h1` 文本包含 `Welcome to the FreqtradeUI`
- 按钮文本 `Add new Bot`
- 顶部导航里的 `Login` 行为不变
- Modal 标题仍由 `LoginModal.vue` 提供 `Login to your bot`
- 登录成功后 Bot 名称仍以独立文本节点出现，例如 `TestBot`
- `FT` 用户菜单入口不改
- 删除 Bot 必须继续走 `Logout confirmation`

## 移动端行为

- `> 1100px`：左侧品牌面板 + 右侧 Bot 牌组。
- `<= 1100px`：上下堆叠，品牌面板在上，Bot 牌组在下。
- `<= 720px`：Bot 卡片单列，状态、开关和操作按钮换行显示。
- Bot URL 超长时省略，不挤压操作按钮。
- 删除、重新登录、自动刷新开关在移动端不隐藏。

## 安全边界

禁止改动：

- Bot 登录信息存储逻辑
- Bot 选择逻辑
- Bot 排序逻辑
- 自动刷新逻辑
- 删除前确认逻辑
- LoginModal 打开方式
- 后端 API 调用

只允许改视觉、布局、class 和响应式 CSS。
