# 13 日志中心对照：Logs / 战报水晶塔

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

- `/logs` 指向 `src/views/LogView.vue`。
- 顶部导航中 `Logs` 入口会跳转到该页。
- 页面用于查看 Bot 后端日志，不直接执行交易。

### 页面容器

`src/views/LogView.vue`

官方当前页面只包含：

```vue
<div class="p-1 md:p-4 md:pe-2 h-full">
  <LogViewer />
</div>
```

### 日志查看组件

`src/components/ftbot/LogViewer.vue`

必须保留：

- `botStore.activeBot.getLogs()`
- `onMounted(async () => refreshLogs())`
- `refreshLogs()`
- `scrollToBottom()`
- `scrollContainer`
- `getLogColor(logLevel)`
- `WARNING -> text-yellow-500`
- `ERROR -> text-red-500`
- default -> `text-neutral-500`
- `botStore.activeBot.lastLogs`
- `log[0]` 时间
- `log[2]` logger/module
- `log[3]` level
- `log[4]` message
- `id="refresh-logs"`
- `title="Reload Logs"`
- `title="Scroll to bottom"`

## 设计目标

页面风格命名：`战报水晶塔 / Log Crystal Tower`

视觉元素：

- 顶部日志 HUD：Total、INFO、WARNING、ERROR、Last Level。
- 日志流改成暗黑战报卷轴。
- 每条日志保持 `<pre>` 语义和等宽排版。
- WARNING / ERROR 用黄色 / 红色符文标记。
- Refresh Logs 改成“同步水晶”技能按钮，但仍调用 `refreshLogs()`。
- Scroll to bottom 改成“回到底部”技能按钮，但仍调用 `scrollToBottom()`。
- 空日志状态显示水晶塔待机，不伪造日志。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 日志总数 | `botStore.activeBot.lastLogs.length` | 保留 |
| INFO 数量 | `lastLogs.filter(log => log[3] === 'INFO')` | 保留，仅 summary |
| WARNING 数量 | `lastLogs.filter(log => log[3] === 'WARNING')` | 保留，仅 summary |
| ERROR 数量 | `lastLogs.filter(log => log[3] === 'ERROR')` | 保留，仅 summary |
| 最后等级 | `lastLogs[lastLogs.length - 1]?.[3]` | 保留，仅 summary |
| 刷新日志 | `refreshLogs()` | 保留 |
| 滚到底部 | `scrollToBottom()` | 保留 |
| 日志颜色 | `getLogColor(log[3])` | 保留 |
| 日志内容 | `log[4]` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/LogView.vue
src/components/ftbot/LogViewer.vue
src/styles/cardduel-logs.css
```

其中：

- `LogView.vue`：新增页面舞台 class 和样式入口。
- `LogViewer.vue`：保留脚本中刷新、滚动、颜色映射和日志数组访问，template 改成战报水晶塔布局。
- `cardduel-logs.css`：新增日志页视觉、等级标记、按钮、空状态和响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `id="refresh-logs"`
- `title="Reload Logs"`
- `title="Scroll to bottom"`
- `WARNING`
- `ERROR`
- `INFO`
- `botStore.activeBot.lastLogs` 的渲染来源
- `pre` 日志行
- `scrollContainer`

## 移动端行为

- `> 1180px`：顶部 HUD 四列 + 右侧技能按钮栏 + 日志卷轴。
- `<= 1180px`：HUD 两列，按钮栏仍在右侧。
- `<= 760px`：HUD 单列，按钮栏移动到顶部横排。
- 日志行保持横向滚动，不强行折断关键时间戳和模块名。
- Refresh 和 Scroll to bottom 在移动端不隐藏。

## 安全边界

禁止改动：

- `getLogs()` API 调用逻辑
- `refreshLogs()` 调用顺序
- `scrollToBottom()` 行为
- 日志数组字段读取结构
- `getLogColor()` 等级映射
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
