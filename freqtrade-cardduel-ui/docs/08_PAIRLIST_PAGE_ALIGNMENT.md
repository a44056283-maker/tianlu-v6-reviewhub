# 08 交易对牌组对照：Pairlist / 白名单黑名单卡牌

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

- `/pairlist` 直接指向 `src/components/ftbot/PairListLive.vue`。
- `/trade` 页的 `Pairlist` tab 也复用同一个 `PairListLive.vue`。
- 因此本页覆盖包会同时影响独立 Pairlist 页面和 Trade 页面内的 Pairlist tab。

### 页面组件

`src/components/ftbot/PairListLive.vue`

必须保留：

- `newblacklistpair`
- `blacklistSelect`
- `initBlacklist()`
- `getWhitelist()`
- `getBlacklist()`
- `addBlacklist({ blacklist: [newblacklistpair.value] })`
- `blacklistSelectClick(key)`
- `deleteBlacklist(pairlist)`
- `botFeatures.botBlacklistModify`
- `id="blacklist-submit"`
- `Whitelist Methods`
- `Whitelist`
- `Blacklist`
- `Add Pair to Blacklist`
- `No Blacklist Available.`
- `List Unavailable. Please Login and make sure server is running.`

## 设计目标

页面风格命名：`交易对牌组 / Pair Deck Control`

视觉元素：

- 顶部牌组 HUD：Whitelist、Blacklist、Methods、Selected。
- Whitelist Methods 改成紫色符文方法卡。
- Whitelist 改成蓝色盟友牌组 token。
- Blacklist 改成红色放逐牌组 token。
- 点击黑名单 token 仍然只是选择待删除项，不直接删除。
- 新增黑名单仍使用官方 Popover + 表单 + `blacklist-submit`。
- 删除黑名单仍使用官方 `deletePairs()` 逻辑。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 牌组方法数量 | `activeBot.pairlistMethods.length` | 保留 |
| 白名单数量 | `activeBot.whitelist.length` | 保留 |
| 黑名单数量 | `activeBot.blacklist.length` | 保留 |
| 待删除数量 | `blacklistSelect.length` | 保留 |
| 方法 token | `activeBot.pairlistMethods` | 保留 |
| 白名单 token | `activeBot.whitelist` | 保留 |
| 黑名单 token | `activeBot.blacklist` | 保留 |
| 黑名单选择 | `blacklistSelectClick(key)` | 保留 |
| 新增黑名单 | `addBlacklistPair()` | 保留 |
| 删除黑名单 | `deletePairs()` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/components/ftbot/PairListLive.vue
src/styles/cardduel-pairlist.css
```

其中：

- `PairListLive.vue`：保留 script 中黑名单、白名单和初始化逻辑，template 改成牌组 token 页面。
- `cardduel-pairlist.css`：新增交易对牌组页面视觉与响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Whitelist Methods`
- `Whitelist`
- `Blacklist`
- `Add Pair to Blacklist`
- `Pair`
- `Add`
- `id="blacklist-submit"`
- 白名单 pair 仍然是 `li`，可通过 `getByRole('listitem', { name: 'BTC/USDT' })` 找到
- 黑名单 pair 仍然是 `li`，点击后切换 `active`
- `No Blacklist Available.`
- `List Unavailable. Please Login and make sure server is running.`

## 移动端行为

- `> 1180px`：顶部 HUD + 三列牌组面板。
- `<= 1180px`：方法面板独占一行，白名单 / 黑名单两列。
- `<= 760px`：所有面板单列，HUD 单列。
- 黑名单新增按钮和删除按钮不隐藏。
- Pair 名称过长时省略，不挤压按钮。

## 安全边界

禁止改动：

- 白名单/黑名单初始化 API 调用
- 新增黑名单 API 调用
- 删除黑名单 API 调用
- 黑名单选择逻辑
- `botFeatures.botBlacklistModify` 权限判断
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
