# 07 历史交易页对照：Trade History / 已结算战报档案

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

- `/trade_history` 指向 `src/views/MobileTradesListView.vue`。
- 该路由通过 `props: { history: true }` 进入历史交易模式。
- `/open_trades` 也复用同一个组件，因此本页 UI 不能破坏上一页持仓列表。

### 页面容器

`src/views/MobileTradesListView.vue`

历史交易模式必须保留：

- `history?: boolean` props
- `isHistory` 判断
- `botStore.activeBot.closedTrades`
- `botStore.activeBot.detailTradeId`
- `botStore.activeBot.tradeDetail`
- `botStore.activeBot.setDetailTrade(null)`
- `CustomTradeList`
- `TradeDetail`
- `Back` 按钮

### 历史交易卡片列表

`src/components/ftbot/CustomTradeList.vue`

必须保留：

- `trades` props
- `activeTrades` props
- `stakeCurrencyDecimals` props
- `currentPage`
- `perPage`
- `UPagination`
- `tradeClick(trade)` 调用 `botStore.activeBot.setDetailTrade(trade)`
- `id="tradeList"`
- `UInput` 的 `placeholder="Filter"`

本页允许在不改数据源的前提下，让官方已有 `filterText` 参与前端显示过滤；过滤只影响当前列表展示和分页，不写入后端、不改交易数据。

### 历史交易卡片条目

`src/components/ftbot/CustomTradeListEntry.vue`

必须保留：

- `trade.pair`
- `trade.trade_id`
- `trade.amount`
- `trade.open_rate`
- `trade.close_rate`
- `trade.open_timestamp`
- `trade.close_timestamp`
- `trade.exit_reason`
- `TradeProfit`

### 交易详情

`src/components/ftbot/TradeDetail.vue`

历史交易详情继续沿用上一页双面板详情，必须保留：

- `Show custom data`
- `General`
- `Details`
- `Stoploss`
- `Futures/Margin`
- `Orders`
- `TradeProfit`
- `showTradeCustomData({ tradeId })`

## 设计目标

页面风格命名：`已结算战报档案 / Closed Trade Archive`

视觉元素：

- 顶部战报 HUD：Closed Trades、Selected Trade、Win/Loss Archive、Stake Currency。
- 历史交易列表改成战报卡牌。
- 每张卡片显示 Pair、Trade ID、Open/Close Rate、Open/Close Date、Exit Reason、收益徽章。
- 胜利 / 亏损使用不同边框，但不改官方收益颜色配置。
- 搜索过滤只作为前端列表辅助，不改后端数据。
- 点击卡片仍进入官方 TradeDetail。
- 分页继续使用官方 `UPagination`。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 已结算战报数 | `activeBot.closedTrades.length` | 保留 |
| 当前查看战报 | `activeBot.detailTradeId` | 保留 |
| 战报卡片 | `CustomTradeListEntry` | 保留字段 |
| 过滤搜索 | `filterText` + `placeholder="Filter"` | 保留并补全前端过滤 |
| 分页 | `UPagination` | 保留 |
| 进入详情 | `setDetailTrade(trade)` | 保留 |
| 返回列表 | `setDetailTrade(null)` | 保留 |
| 收益结果 | `TradeProfit` | 保留 |
| 退出原因 | `trade.exit_reason` | 保留 |
| 订单记录 | `trade.orders` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/MobileTradesListView.vue
src/components/ftbot/CustomTradeList.vue
src/components/ftbot/CustomTradeListEntry.vue
src/components/ftbot/TradeDetail.vue
src/styles/cardduel-trade-history.css
```

其中：

- `MobileTradesListView.vue`：复用持仓页逻辑，但在 `history=true` 时显示战报档案文案和历史统计。
- `CustomTradeList.vue`：保留分页与点击详情逻辑，补全官方已有 `filterText` 的前端过滤。
- `CustomTradeListEntry.vue`：保留字段展示，增加已结算 / 盈亏 / exit reason 视觉标签。
- `TradeDetail.vue`：保留全部字段和详情链路，继续使用双面板战报详情。
- `cardduel-trade-history.css`：新增历史交易页视觉与响应式。

## E2E / 功能兼容锚点

必须保留：

- `Trade history`
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
- `aria-controls="tradeList"`

## 移动端行为

- `> 1180px`：顶部 HUD + 多列历史交易卡牌。
- `<= 1180px`：HUD 堆叠，状态卡三列。
- `<= 760px`：HUD 状态卡单列，战报卡牌单列，搜索框全宽。
- 历史详情在移动端从双栏变单栏。
- Orders、Details、Stoploss 不隐藏。
- Back 按钮固定在详情上方，始终可见。

## 安全边界

禁止改动：

- `activeBot.closedTrades` 数据来源
- `activeBot.setDetailTrade(trade)` 和 `setDetailTrade(null)`
- `TradeDetail` 字段条件判断
- `showTradeCustomData` 调用
- `TradeProfit` 计算逻辑
- 分页总数与分页组件链路
- 任何 ForceExit、Cancel order、Delete trade 相关确认链路
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed、前端显示过滤和响应式 CSS。
