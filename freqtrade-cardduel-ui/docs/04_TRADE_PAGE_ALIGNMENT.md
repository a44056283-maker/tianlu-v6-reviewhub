# 04 交易主页面对照：Trade / 交易对卡牌战场

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

- `/trade` 指向 `src/views/TradingView.vue`
- 顶部导航中 `Trade` 入口会跳转到该页。
- `NavBar.vue` 中的 `Reset Layout` 会在 `/trade` 时调用 `layoutStore.resetTradingLayout()`。

### 页面容器

`src/views/TradingView.vue`

官方 Trade 页面使用 `GridLayout` / `GridItem` 组成可拖拽、可缩放的交易工作台。布局数据来自：

- `layoutStore.tradingLayout`
- `layoutStore.getTradingLayoutSm`
- `TradeLayout.multiPane`
- `TradeLayout.openTrades`
- `TradeLayout.tradeHistory`
- `TradeLayout.tradeDetail`
- `TradeLayout.chartView`

### 官方模块

必须保留这些 `DraggableContainer` 标题和内部组件：

| 官方模块标题 | 内部组件 | 设计表现 |
| --- | --- | --- |
| `Multi Pane` | `BotControls` + `UTabs` | 交易指挥台 |
| `Pairs combined` tab | `PairSummary` | 交易对卡牌牌组 |
| `General` tab | `BotStatus` | Bot 状态面板 |
| `Performance` tab | `BotPerformance` | 战绩面板 |
| `Balance` tab | `BotBalance` | 金库面板 |
| `Time Breakdown` tab | `PeriodBreakdown` | 时间战绩 |
| `Pairlist` tab | `PairListLive` | 白名单/黑名单牌组 |
| `Pair Locks` tab | `PairLockList` | 锁定牌组 |
| `Open Trades` | `TradeList active-trades` | 场上持仓 |
| `Closed Trades` | `TradeList show-filter` | 已结算战报 |
| `Trade Detail` | `TradeDetail` | 单笔交易详情 |
| `Chart` | `CandleChartContainer` | K线战场 |

### 交易控制

`src/components/ftbot/BotControls.vue`

必须保留这些危险操作确认链路：

- Stop Bot：`confirm({ title: 'Stop Bot' ... })` 后才 `stopBot()`
- Pause / StopBuy：`confirm({ title: 'Pause - Stop Entering' ... })` 后才 `stopBuy()`
- Reload Config：`confirm({ title: 'Reload Config' ... })` 后才 `reloadConfig()`
- ForceExit all：`confirm({ title: 'ForceExit all' ... })` 后才 `forceexit({ tradeid: 'all' })`
- ForceEntry：继续通过 `useForceTrade().forceEntryDialog(...)`

### 交易对列表

`src/components/ftbot/PairSummary.vue`

必须保留：

- `filterText`
- `combinedPairList`
- Pair 锁定状态 `currentLocks`
- 开仓交易聚合 `trades.filter((el) => el.pair === pair)`
- `sortMethod === 'profit'` 的排序逻辑
- 点击交易对时 `botStore.activeBot.selectedPair = comb.pair`
- `TradeProfit`
- `ProfitPill`

### Pairlist 白黑名单

`src/components/ftbot/PairListLive.vue`

必须保留：

- `getWhitelist()`
- `getBlacklist()`
- `addBlacklist({ blacklist: [...] })`
- `deleteBlacklist(pairlist)`
- `botFeatures.botBlacklistModify`
- `blacklistSelectClick(key)`
- `blacklist-submit` 按钮 ID

## 设计目标

页面风格命名：`交易对卡牌战场 / Trade Arena`

视觉元素：

- 顶部交易 HUD：Selected Pair、Open Trades、Whitelist、Layout。
- Multi Pane 改成指挥台，BotControls 改成技能槽。
- PairSummary 从纯列表改成交易对卡牌网格。
- Pairlist 白名单/黑名单改成牌组 token。
- Open Trades / Closed Trades / Trade Detail / Chart 保留官方组件，只改外层卡牌边框与暗黑背景。
- 不新增交易行为，不隐藏危险操作。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 当前卡牌 | `botStore.activeBot.selectedPair` | 保留 |
| 场上持仓数 | `botStore.activeBot.openTrades.length` | 保留 |
| 牌组规模 | `botStore.activeBot.whitelist.length` | 保留 |
| 布局状态 | `layoutStore.layoutLocked` + breakpoint | 保留 |
| 拖拽布局 | `GridLayout` / `GridItem` | 保留 |
| 交易对筛选 | `filterText` + `trade-filter` | 保留 |
| 选择交易对 | `selectedPair = comb.pair` | 保留 |
| 开仓收益 | `TradeProfit` | 保留 |
| 回测收益 | `ProfitPill` | 保留 |
| 白名单 | `activeBot.whitelist` | 保留 |
| 黑名单 | `activeBot.blacklist` | 保留 |
| 删除黑名单 | `deletePairs()` | 保留 |
| 强制操作 | `BotControls` confirm 链路 | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/TradingView.vue
src/components/ftbot/PairSummary.vue
src/components/ftbot/PairListLive.vue
src/components/ftbot/BotControls.vue
src/styles/cardduel-trade.css
```

其中：

- `TradingView.vue`：保留全部布局、GridLayout 和 refreshOHLCV 逻辑，新增顶部 HUD 与页面外层 class。
- `PairSummary.vue`：保留 script 与 computed 逻辑，template 改成卡牌网格。
- `PairListLive.vue`：保留 script 与黑名单增删逻辑，template 改成牌组 token。
- `BotControls.vue`：保留确认弹窗和 API 调用，按钮增加技能槽标签。
- `cardduel-trade.css`：新增交易页视觉与响应式。

## E2E / 功能兼容锚点

必须保留：

- `Multi Pane`
- `Open Trades`
- `Closed Trades`
- `Trade Detail`
- `Chart`
- `Pairs combined`
- `General`
- `Performance`
- `Balance`
- `Time Breakdown`
- `Pairlist`
- `Pair Locks`
- `id="trade-filter"`
- `placeholder="Filter"`
- `id="blacklist-submit"`
- `drag-allow-from=".drag-header"`
- `@update:breakpoint="breakpointChanged"`
- `:is-resizable="!isLayoutLocked"`
- `:is-draggable="!isLayoutLocked"`

## 移动端行为

- `> 1180px`：顶部 HUD + 官方 GridLayout + Pair 卡牌多列。
- `<= 1180px`：HUD 上下堆叠，统计卡两列。
- `<= 720px`：HUD 单列，Pair 卡牌单列，控制按钮自动换行。
- Pairlist token 单列显示，黑名单新增/删除按钮不隐藏。
- ForceExit、Stop、StopEntry、Reload 在移动端不隐藏，仍走确认弹窗。
- 表格和图表不强行缩小，外层保持滚动。

## 安全边界

禁止改动：

- startBot / stopBot / stopBuy / reloadConfig / forceexit / forceEntryDialog 调用逻辑
- 所有危险操作的 confirm 标题、消息和流程
- selectedPair 赋值逻辑
- Pair 锁定、排序、收益计算逻辑
- 白名单 / 黑名单 API 调用
- Chart 的 OHLCV refresh 逻辑
- TradeList、TradeDetail、CandleChartContainer 内部逻辑
- Layout 保存、锁定、重置逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
