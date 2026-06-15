# 11 下载数据对照：Download Data / 数据水晶矿场

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

- `/download_data` 指向 `src/views/DownloadDataView.vue`。
- 该入口在 `NavBar.vue` 中只有当 `botStore.isWebserverMode && botStore.activeBot.botFeatures.downloadDataView` 为真时显示。
- 页面用于向后端提交历史行情下载任务，不直接参与交易执行。

### 页面容器

`src/views/DownloadDataView.vue`

官方当前页面只有：

```vue
<DownloadDataMain class="pt-4" />
```

### 主组件

`src/components/ftbot/DownloadDataMain.vue`

必须保留：

- `pairs`
- `timeframes`
- `timeSelection.useCustomTimerange`
- `timeSelection.timerange`
- `timeSelection.days`
- `pairTemplates`
- `exchange.customExchange`
- `exchange.selectedExchange`
- `advancedOptions.erase`
- `advancedOptions.prepend_data`
- `advancedOptions.downloadTrades`
- `advancedOptions.candleTypes`
- `isAdvancedOpen`
- `candleTypes`
- `addPairs(_pairs)`
- `replacePairs(_pairs)`
- `startDownload()`
- `DownloadDataPayload`
- `botStore.activeBot.startDataDownload(payload)`
- `BackgroundJobTracking`
- `BaseStringList`
- `TimeRangeSelect`
- `BaseCollapsible`
- `ExchangeSelect`

### Payload 逻辑

`startDownload()` 必须保持：

- `pairs: pairs.value.filter((pair) => pair !== '')`
- `timeframes: timeframes.value.filter((tf) => tf !== '')`
- custom timerange 时写入 `payload.timerange`
- 非 custom timerange 时写入 `payload.days`
- 只有 `isAdvancedOpen.value` 为真时才应用高级参数
- `erase`
- `download_trades`
- custom exchange 时写入 `exchange`、`trading_mode`、`margin_mode`
- 有 candle types 功能且已选择时写入 `candle_types`
- 有 prepend 功能且已启用时写入 `prepend_data`

## 设计目标

页面风格命名：`数据水晶矿场 / Data Crystal Mine`

视觉元素：

- 顶部矿场 HUD：Pairs、Timeframes、Range、Advanced Gate。
- BackgroundJobTracking 改成数据矿车进度条外观，但不改组件内部。
- Downloading Data 容器改成水晶采集主卡。
- Select Pairs 改成“交易对矿脉”。
- Pairs from template 改成“预设矿脉卡”。
- Select timeframes 改成“时间晶体”。
- Time Selection 改成“采集时间轴”。
- Advanced options 改成“高级矿场阀门”。
- Start Download 改成“启动采集”风格，但按钮文本保留 `Start Download`。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 交易对矿脉数 | `pairs.filter(Boolean).length` | 保留 |
| 时间晶体数 | `timeframes.filter(Boolean).length` | 保留 |
| 采集范围 | `timerange` 或 `days` | 保留 |
| 高级阀门 | `isAdvancedOpen` | 保留 |
| 预设矿脉 | `pairTemplates` | 保留 |
| Pairlist Config 导入 | `replacePairs(pairlistStore.whitelist)` | 保留 |
| 自定义交易所 | `exchange.customExchange` | 保留 |
| 启动采集 | `startDownload()` | 保留 |
| 后台进度 | `BackgroundJobTracking` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/DownloadDataView.vue
src/components/ftbot/DownloadDataMain.vue
src/styles/cardduel-download-data.css
```

其中：

- `DownloadDataView.vue`：只加页面舞台 class，不改业务。
- `DownloadDataMain.vue`：保留 script 中 payload 构造和 `startDataDownload` 调用，template 改成数据矿场布局。
- `cardduel-download-data.css`：新增下载数据页面视觉、表单、按钮、响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Downloading Data`
- `Select Pairs`
- `Pairs from template`
- `Use Pairs from Pairlist Config`
- `Select timeframes`
- `Time Selection`
- `Use custom timerange`
- `Days to download:`
- `Advanced options`
- `Erase existing data`
- `Prepend data when downloading`
- `Download Trades instead of OHLCV data`
- `Select Candle Types`
- `Custom Exchange`
- `Start Download`
- `aria-label="Days to download"`
- `placeholder="Pair"`
- `placeholder="Timeframe"`

## 移动端行为

- `> 1180px`：顶部 HUD + 双列矿场表单 + 右侧预设矿脉。
- `<= 1180px`：HUD 两列，Pair / Timeframe 上下堆叠。
- `<= 760px`：HUD 单列，预设按钮和 Start Download 全宽。
- Advanced options 内部控件单列。
- Start Download 在移动端不隐藏。
- BackgroundJobTracking 始终显示在页面顶部。

## 安全边界

禁止改动：

- `DownloadDataPayload` 构造逻辑
- `startDataDownload(payload)` 调用逻辑
- pair / timeframe 过滤逻辑
- custom timerange 与 days 二选一逻辑
- advanced options 只在展开时生效的逻辑
- exchange / trading_mode / margin_mode payload 逻辑
- candle_types / prepend_data 功能判断
- 后台任务追踪逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
