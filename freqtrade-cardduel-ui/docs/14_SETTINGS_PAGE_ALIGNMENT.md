# 14 系统设置对照：Settings / 符文设置大厅

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

- `/settings` 指向 `src/views/SettingsView.vue`。
- 顶部 FT 用户菜单中的 `Settings` 会跳转到该页。
- 页面只修改本地 FreqUI Store，不改交易机器人配置文件。

### 页面容器

`src/views/SettingsView.vue`

必须保留：

- `settingsStore`
- `colorStore`
- `layoutStore`
- `timezoneOptions`
- `openTradesOptions`
- `colorPreferenceOptions`
- `resetDynamicLayout()`
- `layoutStore.resetTradingLayout()`
- `layoutStore.resetDashboardLayout()`
- `showAlert('Layouts have been reset.')`
- `FtWsMessageTypes`
- `availableBacktestMetrics`

### 官方设置项

必须保留：

- `FreqUI Settings`
- `UI Version: {{ settingsStore.uiVersion }}`
- `UI settings`
- `Lock dynamic layouts`
- `Reset layout`
- `Show open trades in header`
- `UTC Timezone`
- `Background sync`
- `Show Confirm Dialog for Trade Exits`
- `Show Text on Multi Pane Buttons`
- `Chart settings`
- `Chart scale Side`
- `Use Heikin Ashi candles`
- `Only request necessary columns`
- `Default number of candles to display (defaults to 250)`
- `Candle Color Preference`
- `Notification Settings`
- `Entry notifications`
- `Exit notifications`
- `Entry Cancel notifications`
- `Exit Cancel notifications`
- `Backtesting settings`
- `Backtesting metrics`
- `id="backtestMetrics"`

## 设计目标

页面风格命名：`符文设置大厅 / Rune Settings Hall`

视觉元素：

- 顶部设置 HUD：UI Version、Layout、Timezone、Signals。
- UI settings 改成“核心符文”面板。
- Chart settings 改成“图表符文”面板。
- Notification Settings 改成“信号符文”面板。
- Backtesting settings 改成“试炼指标”面板。
- Reset layout、Confirm Dialog、Backtesting metrics 等行为不变。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| UI 版本 | `settingsStore.uiVersion` | 保留 |
| 布局锁定 | `layoutStore.layoutLocked` | 保留 |
| 重置布局 | `resetDynamicLayout()` | 保留 |
| 头部开仓显示 | `settingsStore.openTradesInTitle` | 保留 |
| 时区 | `settingsStore.timezone` | 保留 |
| 后台同步 | `settingsStore.backgroundSync` | 保留 |
| 强制退出确认 | `settingsStore.confirmDialog` | 保留 |
| 多面板按钮文字 | `settingsStore.multiPaneButtonsShowText` | 保留 |
| 图表刻度侧 | `settingsStore.chartLabelSide` | 保留 |
| Heikin Ashi | `settingsStore.useHeikinAshiCandles` | 保留 |
| 精简列请求 | `settingsStore.useReducedPairCalls` | 保留 |
| 默认蜡烛数 | `settingsStore.chartDefaultCandleCount` | 保留 |
| 涨跌颜色偏好 | `colorStore.colorPreference` | 保留 |
| 通知开关 | `settingsStore.notifications[...]` | 保留 |
| 回测指标 | `settingsStore.backtestAdditionalMetrics` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/SettingsView.vue
src/styles/cardduel-settings.css
```

其中：

- `SettingsView.vue`：保留全部 v-model、store 写入和 resetDynamicLayout 逻辑，新增符文设置大厅 HUD 与面板布局。
- `cardduel-settings.css`：新增设置页视觉、面板、按钮、表单与响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `FreqUI Settings`
- `Show pill in icon`
- `Show in title`
- `Show open trades in header`
- `Reset layout`
- `Backtesting metrics`
- `id="backtestMetrics"`
- FT 菜单进入 Settings 的路由不变
- `settingsStore.openTradesInTitle` 写入 localStorage `ftUISettings` 的行为不变

## 移动端行为

- `> 1180px`：顶部 HUD + 双列设置面板。
- `<= 1180px`：所有面板单列。
- `<= 720px`：HUD 单列，按钮和 slider 单列，metrics selector 全宽。
- Confirm Dialog、Reset layout、Backtesting metrics 不隐藏。

## 安全边界

禁止改动：

- settingsStore 持久化 key：`ftUISettings`
- colorStore 持久化 key：`ftUIColorSettings`
- `resetDynamicLayout()` 调用逻辑
- 所有 v-model 对应的 Store 字段
- `availableBacktestMetrics` 数据来源
- 通知类型 `FtWsMessageTypes`
- 任何后端交易配置或 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
