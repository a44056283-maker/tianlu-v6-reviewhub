# 09 资金金库对照：Balance / Treasury

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

- `/balance` 直接指向 `src/components/ftbot/BotBalance.vue`。
- `/trade` 页的 `Balance` tab 也复用同一个 `BotBalance.vue`。
- 因此本页覆盖包会同时影响独立 Balance 页面和 Trade 页面内的 Balance tab。

### 页面组件

`src/components/ftbot/BotBalance.vue`

必须保留：

- `hideSmallBalances`
- `showBotOnly`
- `smallBalance`
- `canUseBotBalance`
- `balanceCurrencies`
- `tableData`
- `formatCurrency(value)`
- `chartValues`
- `tableFields`
- `tableColumns`
- `refreshBalance()`
- `onMounted(() => refreshBalance())`
- `BalanceChart`
- `UTable`

### 图表组件

`src/components/charts/BalanceChart.vue`

本页不改 `BalanceChart.vue`，只改外层容器。原因：该组件包含 ECharts pie chart、dataset、tooltip formatter、主题和 autoresize 逻辑。

## 设计目标

页面风格命名：`资金金库 / Balance Treasury`

视觉元素：

- 顶部金库 HUD：Scope、Assets、Stake Total、Starting Delta。
- Bot / Account Balance 切换改成金库视角切换按钮，但保留原布尔值。
- Hide small balances 改成尘埃过滤器按钮，但保留原逻辑。
- Refresh 改成同步金库按钮，但仍然调用 `refreshBalance()`。
- BalanceChart 放入水晶圆盘卡牌容器。
- UTable 放入资产卷轴容器，字段不变。
- balance note 显示为金库警示横幅。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 金库范围 | `showBotOnly` + `canUseBotBalance` | 保留 |
| 资产数量 | `balanceCurrencies.length` | 保留 |
| 当前总额 | `balance.total_bot` / `balance.total` | 保留 |
| 初始资金变化 | `balance.starting_capital_ratio` | 保留 |
| 小额过滤 | `hideSmallBalances` | 保留 |
| Bot 管理资产 | `is_bot_managed` filter | 保留 |
| 图表数据 | `chartValues` | 保留 |
| 表格数据 | `tableData` / `tableColumns` | 保留 |
| 刷新 | `refreshBalance()` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/components/ftbot/BotBalance.vue
src/styles/cardduel-balance.css
```

其中：

- `BotBalance.vue`：保留 script 中余额过滤、图表、表格和 refresh 逻辑，新增金库 HUD 和页面 class。
- `cardduel-balance.css`：新增资金金库页面视觉与响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Bot Balance`
- `Account Balance`
- `Balance`
- `Currency`
- `Available`
- `Total`
- `UTable` 的 data/columns 绑定
- `BalanceChart` 的 `:currencies="chartValues"`
- 切换 Bot / Account 的按钮行为
- 切换 Hide small balances 的按钮行为
- Refresh 按钮行为

## 移动端行为

- `> 1180px`：顶部 HUD + 左侧水晶图表 + 右侧资产卷轴。
- `<= 1180px`：HUD 两列，图表与表格上下堆叠。
- `<= 760px`：HUD 单列，按钮全宽换行。
- 表格保持横向滚动，不隐藏 Currency / Available / Stake value。
- balance note 在移动端仍然可见。

## 安全边界

禁止改动：

- 余额 API 调用 `getBalance()`
- Bot / Account 过滤逻辑
- 小额余额过滤逻辑
- `is_bot_managed` 判断
- `BalanceChart.vue` 内部 ECharts 逻辑
- `UTable` 的数据和列计算逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
