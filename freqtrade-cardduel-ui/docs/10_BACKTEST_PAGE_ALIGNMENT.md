# 10 回测分析对照：Backtest / 试炼战绩大厅

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

- `/backtest` 指向 `src/views/BacktestingView.vue`。
- 该页只在 Webserver 模式下可运行回测；非 Webserver 模式显示 `Bot must be in webserver mode to enable Backtesting.`。
- 顶部导航中 `Backtest` 入口只在 `botStore.canRunBacktest` 场景下显示。

### 页面容器

`src/views/BacktestingView.vue`

必须保留：

- `BtRunModes`
- `hasBacktestResult`
- `hasMultiBacktestResult`
- `timeframe`
- `showLeftBar`
- `btFormMode`
- `pollInterval`
- `selectBacktestResult()`
- `watch(selectedBacktestResultKey)`
- `onMounted(() => botStore.activeBot.getState())`
- `watch(backtestRunning)` 中的 `setInterval(botStore.activeBot.pollBacktest, 1000)`
- `backtestTabs`
- `BacktestResultSelect`
- `BacktestHistoryLoad`
- `BacktestRun`
- `BacktestResultAnalysis`
- `BacktestResultComparison`
- `BacktestGraphs`
- `BacktestResultChart`

### 回测运行表单

`src/components/ftbot/BacktestRun.vue`

必须保留 `clickBacktest()` 的 payload 构造逻辑：

- `strategy`
- `timerange`
- `enable_protections`
- `max_open_trades`
- `stake_amount`
- `dry_run_wallet`
- `timeframe`
- `timeframe_detail`
- `backtest_cache`
- `freqaimodel`
- `freqai.identifier`
- `botStore.activeBot.startBacktest(btPayload)`

必须保留控制按钮：

- `Start backtest`，id：`start-backtest`
- `Load backtest result`
- `Stop Backtest`
- `Reset Backtest`

### 历史结果

`src/components/ftbot/BacktestHistoryLoad.vue`

必须保留：

- `getBacktestHistory()`
- `getBacktestHistoryResult(row.original)`
- `deleteBacktestResult(result)` 的确认弹窗：`Delete result`
- `deleteBacktestHistoryResult(result)`
- `filterText`
- `id="trade-filter"`
- `placeholder="Filter results"`
- `UTable`、virtualize、sticky

### 结果分析

必须保留：

- `generateBacktestMetricRows`
- `generateBacktestSettingRows`
- `BacktestResultTablePer`
- `BacktestResultPeriodBreakdown`
- `TradeList`
- `BacktestResultComparison`
- `BacktestGraphs`
- `BacktestResultChart`
- `getBacktestMarketChange()`
- `getBacktestWalletChange()`
- `refreshOHLCV()` 中的 `getPairHistory(payload)`

## 设计目标

页面风格命名：`试炼战绩大厅 / Backtest Trial Hall`

视觉元素：

- 顶部试炼 HUD：Strategy、Loaded Results、Mode、Progress。
- 左侧结果抽屉改成“战报档案卷轴”。
- Run backtest 表单改成“试炼参数符文盘”。
- Start / Load / Stop / Reset 改成技能槽按钮，但行为不变。
- Analyze result 表格改成金边数据卷轴，字段不变。
- Visualize summary 图表放入试炼图谱容器，图表组件不改内部。
- Visualize result 使用左右导航战场，PairSummary / TradeListNav 行为不变。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 当前策略 | `btStore.strategy` / `selectedBacktestResult.strategy_name` | 保留 |
| 已加载战报 | `backtestHistory` keys | 保留 |
| 当前模式 | `btFormMode` | 保留 |
| 进度 | `backtestRunning` / `backtestStep` / `backtestProgress` | 保留 |
| 运行回测 | `clickBacktest()` | 保留 |
| 停止回测 | `stopBacktest()` | 保留 |
| 重置回测 | `removeBacktest()` | 保留 |
| 加载历史结果 | `getBacktestHistoryResult()` | 保留 |
| 删除历史文件 | `deleteBacktestResult()` + confirm | 保留 |
| 结果对比 | `BacktestResultComparison` | 保留 |
| 图表可视化 | `BacktestGraphs` / `BacktestResultChart` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/BacktestingView.vue
src/components/ftbot/BacktestRun.vue
src/components/ftbot/BacktestHistoryLoad.vue
src/components/ftbot/BacktestResultSelect.vue
src/components/ftbot/BacktestResultSelectEntry.vue
src/components/ftbot/BacktestResultAnalysis.vue
src/components/ftbot/BacktestResultComparison.vue
src/components/ftbot/BacktestResultChart.vue
src/components/ftbot/BacktestGraphs.vue
src/styles/cardduel-backtest.css
```

其中：

- `BacktestingView.vue`：保留 tabs、polling、结果选择和全部子组件，新增试炼 HUD 和页面外层 class。
- `BacktestRun.vue`：保留 payload 和按钮行为，template 改成符文参数盘。
- `BacktestHistoryLoad.vue`：保留过滤、加载、删除确认和 UTable。
- `BacktestResultSelect.vue`：保留结果选择、删除、备注更新事件。
- `BacktestResultAnalysis.vue`：保留所有统计表和 TradeList。
- `BacktestResultChart.vue`：保留 chart 导航、OHLCV payload 和 CandleChartContainer。
- `BacktestGraphs.vue`：保留所有图表组件和异步数据加载。
- `cardduel-backtest.css`：新增回测页视觉、数据表、按钮、响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Backtesting`
- `Bot must be in webserver mode to enable Backtesting.`
- `Load Results`
- `Run backtest`
- `Analyze result`
- `Compare results`
- `Visualize summary`
- `Visualize result`
- `Backtesting parameters`
- `Backtesting summary`
- `Start backtest`
- `Load backtest result`
- `Stop Backtest`
- `Reset Backtest`
- `id="start-backtest"`
- `id="trade-filter"`
- `placeholder="Filter results"`
- `Delete result`
- `Available results:`
- `Strategy settings`
- `Metrics`
- `Single trades`
- `Backtest running:`

## 移动端行为

- `> 1180px`：左侧结果卷轴 + 右侧试炼大厅，HUD 四列。
- `<= 1180px`：结果卷轴可折叠，HUD 两列。
- `<= 860px`：回测参数表单改成单列，按钮自动换行。
- `<= 640px`：HUD 单列，tabs 横向滚动，图表和表格保持滚动。
- Start / Stop / Reset 不隐藏，禁用状态仍可见。
- 删除历史结果仍必须先确认。

## 安全边界

禁止改动：

- 回测 payload 构造逻辑
- `startBacktest` / `stopBacktest` / `pollBacktest` / `removeBacktest` 调用逻辑
- `backtestRunning` polling 逻辑
- 历史结果加载、删除、备注保存 API 调用
- 删除历史文件确认弹窗
- 结果选择和 `selectBacktestResult()` 参数回填逻辑
- 图表 `refreshOHLCV` payload 结构
- Backtest metrics 计算逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
