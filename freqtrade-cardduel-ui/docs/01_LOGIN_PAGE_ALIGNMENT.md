# 01 登录页对照：Login / 召唤师登录

## 官方版本锁定

- 后端：`freqtrade/freqtrade`
- 分支：`develop`
- Commit：`9aa5a628d891ca13f11d6647963dd413736fbb8c`
- 前端：`freqtrade/frequi`
- 分支：`main`
- Commit：`1745a9f77e4a9a7ae2386815ec6c56330b95cdce`

## 官方登录链路

### 路由

`src/router/index.ts`

- `/login` 指向 `src/views/LoginView.vue`
- `allowAnonymous: true`
- 其他需要登录的路由在没有 Bot 时会 redirect 到 `/login?redirect=...`

### 页面容器

`src/views/LoginView.vue`

当前官方页面只有一个 `DraggableContainer`，内部挂载 `BotLogin`。

### 登录表单

`src/components/BotLogin.vue`

必须保留的逻辑：

- `auth.botName`
- `auth.url`
- `auth.username`
- `auth.password`
- `handleSubmit()`
- `useLoginInfo(botId).login(auth.value)`
- 新增 Bot：`botStore.addBot(...)`
- 选择 Bot：`botStore.selectBot(botId)`
- 成功后 redirect 回原目标路由
- 401 时显示用户名 / 密码错误
- 非 401 时提示 API 不可达和 CORS
- Modal 模式下通过 `emit('loginResult', true)` 关闭

### 登录接口

`src/composables/loginInfo.ts`

`POST ${auth.url}/api/v1/token/login`

返回：

- `access_token`
- `refresh_token`

本次 UI 改造不改接口，不改 token 存储逻辑。

## 目标设计图拆解

设计元素：

- 暗黑战场背景
- 金色卡牌边框
- 中央紫蓝水晶徽章
- 标题：召唤师登录
- 输入框：用户名 / 密码
- 机器人名称、API 地址作为官方 FreqUI 必需字段保留
- 进入战场按钮
- 底部版本号

## 官方字段到设计字段的映射

| 设计稿字段 | 官方字段 | 是否保留 |
| --- | --- | --- |
| 召唤师 / 用户名 | `auth.username` | 保留 |
| 密码 / 密令 | `auth.password` | 保留 |
| 机器人名称 | `auth.botName` | 保留，设计上作为战斗代号 |
| API 地址 | `auth.url` | 保留，设计上作为后端战场入口 |
| 进入战场 | submit button | 保留 `type=submit` |
| 重置 | reset button | 保留 `type=reset` |
| 失败提示 | `errorMessage` + `UAlert` | 保留 |
| CORS 提示 | `errorMessageCORS` | 保留 |
| Modal 登录 | `LoginModal.vue` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/LoginView.vue
src/components/BotLogin.vue
src/components/LoginModal.vue
src/styles/cardduel-login.css
src/styles/tailwind.css
```

其中：

- `LoginView.vue`：从普通卡片改成完整登录舞台。
- `BotLogin.vue`：只替换 template，不改 script 登录逻辑。
- `LoginModal.vue`：只加视觉包装，不改关闭逻辑。
- `cardduel-login.css`：新增登录页专用主题。
- `tailwind.css`：新增 `@import './cardduel-login.css';`。

## E2E 兼容锚点

为避免破坏官方登录测试，补丁必须保留：

- `.card-header:has-text("Freqtrade bot Login")`
- `input[id=url-input]`
- `input[id=name-input]`
- `input[id=username-input]`
- `input[id=password-input]`
- `button[type=submit]`
- submit 按钮文本包含 `Submit`
- modal title 仍为 `Login to your bot`
- 错误标题仍为 `Login failed`
- 错误文案仍包含官方原文

## 移动端行为

- `> 980px`：左侧视觉故事面板 + 右侧登录表单。
- `<= 980px`：上下堆叠。
- `<= 640px`：单列输入框，按钮全宽，状态卡压缩为竖排。
- 危险信息 / 连接失败 / CORS 提示不隐藏。

## 安全边界

禁止改动：

- 登录 API 地址拼接逻辑
- token 获取逻辑
- token refresh 逻辑
- botStore 写入逻辑
- redirect 逻辑
- CORS 错误提示
- modal 登录关闭逻辑

只允许改视觉、布局、class 和响应式 CSS。
