# 06 持仓页对照：Open Trades / 场上持仓卡牌

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

- `/open_trades` 指向 `src/views/MobileTradesListView.vue`。
- `/trade_history` 也指向同一个组件，并通过 `props: { history: true }` 切换历史交易模式。
- 因此本页覆盖包会同时影响持仓列表和移动端历史交易列表的外观。

### 页面容器

`src/views/MobileTradesListView.vue`

必须保留：

- `history?: boolean` props
- `botStore.activeBot.openTrades`
- `botStore.activeBot.closedTrades`
- `botStore.activeBot.detailTradeId`
- `botStore.activeBot.tradeDetail`
- `botStore.activeBot.setDetailTrade(null)`
- `CustomTradeList`
- `TradeDetail`
- `Back` 按钮

### 持仓卡片列表

`src/components/ftbot/CustomTradeList.vue`

必须保留：

- `trades` props
- `activeTrades` props
- `stakeCurrencyDecimals` props
- `currentPage`
- `perPage`
- `filteredTrades` 分页切片
- `tradeClick(trade)` 调用 `botStore.activeBot.setDetailTrade(trade)`
- `UPagination`
- `UInput` 的 `placeholder="Filter"`
- `id="tradeList"`

### 卡片条目

`src/components/ftbot/CustomTradeListEntry.vue`

必须保留：

- `trade.pair`
- `trade.trade_id`
- `trade.amount`
- `trade.open_rate`
- `trade.current_rate`
- `trade.open_timestamp`
- `trade.close_timestamp`
- `TradeProfit`

### 交易详情

`src/components/ftbot/TradeDetail.vue`

必须保留：

- `Show custom data` 按钮和 `showTradeCustomData({ tradeId })`
- General 区块全部字段
- Stoploss 区块全部字段
- Futures/Margin 区块全部字段
- Orders 折叠区块
- `Details` 折叠区块
- `TradeProfit` 三种 mode 展示

## 设计目标

页面风格命名：`场上持仓卡牌 / Open Trade Cards`

视觉元素：

- 顶部持仓 HUD：Open Trades、Selected Trade、Mode。
- 每条持仓改成卡牌，保留 pair、trade id、amount、rate、date、profit。
- 点击卡牌仍然进入官方 TradeDetail。
- TradeDetail 改成 General / Risk Shield 双面板。
- Stoploss、Orders、Futures/Margin 信息必须移动端可见。
- 空状态显示暗黑卡牌占位，但不创建模拟交易。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 场上卡牌数量 | `activeBot.openTrades.length` | 保留 |
| 历史战报数量 | `activeBot.closedTrades.length` | 保留 |
| 当前选中交易 | `activeBot.detailTradeId` | 保留 |
| 点击卡牌 | `setDetailTrade(trade)` | 保留 |
| 返回列表 | `setDetailTrade(null)` | 保留 |
| 收益徽章 | `TradeProfit` | 保留 |
| 自定义数据 | `showTradeCustomData` | 保留 |
| 风险护盾 | `stop_loss_ratio` / `stop_loss_abs` | 保留 |
| 订单记录 | `trade.orders` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/MobileTradesListView.vue
src/components/ftbot/CustomTradeList.vue
src/components/ftbot/CustomTradeListEntry.vue
src/components/ftbot/TradeDetail.vue
src/styles/cardduel-open-trades.css
```

其中：

- `MobileTradesListView.vue`：保留数据选择逻辑，新增持仓 HUD 与卡牌舞台。
- `CustomTradeList.vue`：保留分页与点击详情逻辑，template 改成卡牌列表。
- `CustomTradeListEntry.vue`：保留字段展示，template 改成持仓卡片。
- `TradeDetail.vue`：保留全部字段，template 改成双面板详情。
- `cardduel-open-trades.css`：新增持仓页视觉与响应式。

## E2E / 功能兼容锚点

必须保留：

- `Open trades`
- `Trade history`
- `No open Trades.`
- `No closed trades so far.`
- `Back`
- `Show custom data`
- `General`
- `Stoploss`
- `Futures/Margin`
- `Orders`
- `Details`
- `id="tradeList"`
- `placeholder="Filter"`

## 移动端行为

- `> 1180px`：顶部 HUD + 多列持仓卡牌。
- `<= 1180px`：HUD 堆叠，状态卡三列。
- `<= 760px`：HUD 状态卡单列，持仓卡牌单列。
- `TradeDetail` 在移动端从双栏变单栏。
- Stoploss、Orders、Futures/Margin 不隐藏。
- 详情返回按钮始终可见。

## 安全边界

禁止改动：

- `activeBot.openTrades` / `activeBot.closedTrades` 数据来源
- `activeBot.setDetailTrade(trade)` 和 `setDetailTrade(null)`
- `TradeDetail` 字段条件判断
- `showTradeCustomData` 调用
- `TradeProfit` 计算逻辑
- 分页逻辑
- 任何 ForceExit、Cancel order、Delete trade 相关确认链路
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
