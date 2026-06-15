# 05 图表页对照：Graph / K线符文战场

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

- `/graph` 指向 `src/views/ChartsView.vue`
- 顶部导航中 `Chart` 入口会跳转到该页。
- 这是 FreqUI 的 K 线、指标、交易标记和历史数据查看页面。

### 页面容器

`src/views/ChartsView.vue`

官方逻辑必须保留：

- `finalTimeframe`
- `availablePairs`
- `onMounted()` 中根据 Webserver / Trade 模式加载 pairlist
- `refreshOHLCV(pair, columns)`
- Webserver 模式下调用 `getPairHistory(payload)`
- Trade 模式下调用 `getPairCandles({ pair, timeframe, columns })`
- `exchange.customExchange`
- `chartStore.useLiveData` watch 中调用 `getMarkets(payload)`
- Settings 区块只影响图表视图，不影响 Bot 实际配置

### 图表容器

`src/components/charts/CandleChartContainer.vue`

必须保留：

- `botStore.activeBot.plotMultiPairs`
- `singlePairSelection`
- `settingsStore.multiPairSelection`
- `settingsStore.showMarkArea`
- `settingsStore.useHeikinAshiCandles`
- `PlotConfigSelect`
- `PlotConfigurator`
- `showPlotConfigModal`
- `refresh()` 对每个 pair emit `refreshData(pair, plotStore.usedColumns)`
- `refreshIfNecessary()` 和 pair 切换加载逻辑

### 单图容器

`src/components/charts/SingleCandleChartContainer.vue`

必须保留：

- historicView 时读取 `activeBot.history[pair__timeframe]`
- live/trade 模式时读取 `activeBot.candleData[pair__timeframe]`
- `LoadingStatus` 判断
- `noDatasetText`
- `plotStore.usedColumns` 检查和 reduced pair calls 刷新逻辑
- `CandleChart` 全部 props
- `Long entries`、`Long exit`、`Short entries`、`Short exits` 信号统计

### 核心 ECharts

`src/components/charts/CandleChart.vue`

本页不改 `CandleChart.vue`。原因：这里包含 ECharts option、K线、信号、tooltip、mark area、dataZoom、heikin ashi、subplot、legend 和交易点绘制逻辑。当前阶段只改外层图表战场皮肤，避免破坏图表计算。

## 设计目标

页面风格命名：`K线符文战场 / Chart Rune Battlefield`

视觉元素：

- 顶部图表 HUD：Pair Deck、Timeframe、Data Source、Chart Mode。
- Webserver 设置面板改成符文图表设置。
- 交易所选择、Strategy、Use Live Data、Timeframe、Timerange 保持原交互。
- Pair 选择器、Multi pair、Show Chart Areas、Heikin Ashi、Plot Config 改成技能槽工具条。
- K线图表保留 ECharts，只加暗色边框、金色卡牌容器和移动端滚动。
- Plot Configurator 继续使用官方 DraggableModal。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| Pair Deck | `availablePairs.length` | 保留 |
| Timeframe | `finalTimeframe` | 保留 |
| Data Source | `chartStore.useLiveData` / `isWebserverMode` | 保留 |
| Chart Mode | `settingsStore.multiPairSelection` | 保留 |
| 自定义交易所 | `exchange.customExchange` | 保留 |
| 策略选择 | `chartStore.strategy` | 保留 |
| 使用实时数据 | `chartStore.useLiveData` | 保留 |
| 时间范围 | `chartStore.timerange` | 保留 |
| 交易对选择 | `plotMultiPairs` / `singlePairSelection` | 保留 |
| 刷新图表 | `refresh()` / `refreshData` | 保留 |
| 指标配置 | `PlotConfigSelect` / `PlotConfigurator` | 保留 |
| K线图 | `CandleChart` | 保留，不改内部 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/ChartsView.vue
src/components/charts/CandleChartContainer.vue
src/components/charts/SingleCandleChartContainer.vue
src/styles/cardduel-graph.css
```

其中：

- `ChartsView.vue`：保留全部数据加载与 refreshOHLCV 逻辑，新增顶部 HUD 与页面外层 class。
- `CandleChartContainer.vue`：保留 script，template 改成图表工具条与战场容器。
- `SingleCandleChartContainer.vue`：保留 script，template 改成单图卡牌容器。
- `cardduel-graph.css`：新增图表页视觉、ECharts 容器、响应式与移动端样式。

## E2E / 功能兼容锚点

必须保留：

- `Settings`
- `Custom Exchange`
- `Current Exchange:`
- `Strategy`
- `Use Live Data`
- `Timeframe`
- `Select pairs to plot`
- `Refresh chart`
- `Multi pair`
- `Show Chart Areas`
- `Heikin Ashi`
- `Plot configurator`
- `Plot Configurator`
- `Configure chart plot indicators and subplots`
- `No pair selected`
- `Long entries`
- `Long exit`
- `Short entries`
- `Short exits`
- `This is taking longer than expected ... Hold on ...`

## 移动端行为

- `> 1180px`：顶部 HUD + Settings 横向表单 + 单图/双图战场。
- `<= 1180px`：HUD 堆叠，统计卡两列。
- `<= 860px`：工具条换行，Pair 选择、Plot Config 占满宽度。
- `<= 640px`：统计卡单列，Settings 单列，图表容器保持最小高度和横向滚动能力。
- 图表不强行缩小到不可读；移动端优先保留滚动与缩放交互。

## 安全边界

禁止改动：

- `refreshOHLCV` payload 结构
- `getPairHistory` / `getPairCandles` 调用逻辑
- `getMarkets` 调用逻辑
- `availablePairs` 选择逻辑
- `plotMultiPairs` 切换逻辑
- `plotStore.usedColumns` 与 reduced pair calls 逻辑
- `CandleChart.vue` 内部 ECharts option 和图表计算
- Trade 数据过滤与信号统计逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
