# 03 仪表盘对照：Dashboard / 战场总览

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

- `/dashboard` 指向 `src/views/DashboardView.vue`
- 顶部导航中 `Dashboard` 入口会跳转到该页。
- `NavBar.vue` 中的 `Reset Layout` 会在 `/dashboard` 时调用 `layoutStore.resetDashboardLayout()`。

### 页面容器

`src/views/DashboardView.vue`

官方 Dashboard 使用 `GridLayout` / `GridItem` 组成可拖拽、可缩放的仪表盘。布局数据来自：

- `layoutStore.dashboardLayout`
- `layoutStore.getDashboardLayoutSm`
- `DashboardLayout.dailyChart`
- `DashboardLayout.botComparison`
- `DashboardLayout.allOpenTrades`
- `DashboardLayout.allClosedTrades`
- `DashboardLayout.cumChartChart`
- `DashboardLayout.walletHistoryChart`
- `DashboardLayout.profitDistributionChart`
- `DashboardLayout.tradesLogChart`

### 初始化数据

`onMounted()` 中必须保留：

- `botStore.allGetDaily({ timescale: 30 })`
- `botStore.activeBot.getOpenTrades()`
- `botStore.activeBot.getProfit()`

### 官方模块

必须保留这些 `DraggableContainer` 标题和内部组件：

| 官方模块标题 | 内部组件 | 设计表现 |
| --- | --- | --- |
| `Profit over time` | `PeriodBreakdown` | 战绩时间轴 |
| `Bot comparison` | `BotComparisonList` | Bot 战队对比表 |
| `Open Trades` | `TradeList active-trades` | 场上持仓卡牌 / 表格 |
| `Cumulative Profit` | `CumProfitChart` | 总收益曲线 |
| `Wallet History` | `WalletHistoryChart` | 金库历史曲线 |
| `Closed Trades` | `TradeList show-filter` | 已结算战报 |
| `Profit Distribution` | `ProfitDistributionChart` | 收益分布符文图 |
| `Trades Log` | `TradesLogChart` | 交易日志曲线 |

## 设计目标

页面风格命名：`战场总览 / Dashboard Battle Overview`

视觉元素：

- 顶部暗黑战场 HUD
- 四个符文指标卡：Active Bots、Open Trades、Closed Trades、Layout Mode
- 保留官方拖拽网格，不破坏用户布局
- 每个 `DraggableContainer` 改成金色卡牌边框
- 图表区域保持 ECharts / 官方组件，只改容器风格
- 表格在暗色背景下提升可读性

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| Active Bots | `botStore.botCount` / selected bots | 保留 |
| Open Trades | `botStore.allOpenTradesSelectedBots` | 保留 |
| Closed Trades | `botStore.allClosedTradesSelectedBots` | 保留 |
| Layout Mode | `layoutStore.layoutLocked` + breakpoint | 保留 |
| 拖拽布局 | `GridLayout` / `GridItem` | 保留 |
| 布局保存 | `layoutUpdatedEvent(newLayout)` | 保留 |
| 移动布局 | `responsiveGridLayouts` | 保留 |
| Reset Layout | `NavBar.vue` 调用 `layoutStore.resetDashboardLayout()` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/DashboardView.vue
src/styles/cardduel-dashboard.css
```

其中：

- `DashboardView.vue`：保留 script 中全部布局和数据逻辑，新增顶部 HUD 与四个指标卡，GridLayout 外层加 `cardduel-dashboard-page`。
- `cardduel-dashboard.css`：只改视觉、卡牌边框、响应式和图表容器样式。
- 本页不改 `DraggableContainer.vue`，通过父级 CSS 作用域美化。

## E2E / 功能兼容锚点

必须保留：

- `Profit over time`
- `Bot comparison`
- `Open Trades`
- `Cumulative Profit`
- `Wallet History`
- `Closed Trades`
- `Profit Distribution`
- `Trades Log`
- `drag-allow-from=".drag-header"`
- `@layout-updated="layoutUpdatedEvent"`
- `@update:breakpoint="breakpointChanged"`
- `:is-resizable="!isLayoutLocked"`
- `:is-draggable="!isLayoutLocked"`

## 移动端行为

- `> 1180px`：顶部 HUD + 四列符文指标卡 + 官方 GridLayout。
- `<= 1180px`：HUD 上下堆叠，指标卡两列。
- `<= 720px`：指标卡单列，GridLayout 使用官方 `getDashboardLayoutSm`，容器卡片圆角缩小。
- 表格不隐藏，保持 `overflow-auto`。
- 布局锁定状态始终可见。

## 安全边界

禁止改动：

- Dashboard 数据加载逻辑
- Bot 选择 / 多 Bot 聚合逻辑
- 图表组件内部计算逻辑
- TradeList 的点击跳转逻辑
- Open Trades / Closed Trades 数据来源
- Layout 保存、锁定、重置逻辑
- 后端 API 调用

只允许改视觉、布局、class、外层 summary computed 和响应式 CSS。
