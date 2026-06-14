# tianlu-frequi-cardduel-full-ui-pack

天禄交易系统 · Freqtrade 官方 FreqUI 全量 UI 改造交付包。

## 本次完成

- 使用 image2 生成了全套 UI 概念总览图；完整 PNG 已打包在本地交付包 `design/assets/`。
- 按产品页面类别生成桌面端 SVG：22 个页面。
- 按移动端自适应生成移动端 SVG：15 个页面。
- 按策略子规则生成模块 SVG：20 个模块图。
- 新增响应式 HTML 原型：`design/prototype/responsive_full_pages.html`。
- 新增页面目录、模块矩阵、移动端规则文档。
- 新增可复用 Vue 组件与 CSS：`overlay/src/components/cardduel/`、`overlay/src/styles/cardduel-page-system.css`。

## 页面范围

已覆盖：登录、机器人首页、仪表盘、交易对列表、交易对详情/K线、持仓、历史交易、交易对牌组、余额、策略列表、策略编辑基础、买入规则、卖出规则、风控规则、高级代码、订单管理、回测、下载数据、Pairlist Config、日志、系统设置、API 连接契约。

## 移动端适配

- `< 768px`：单列卡牌、顶部菜单收起、底部 5 个核心入口。
- `768px - 1199px`：平板两列卡牌，保留主导航。
- `>= 1200px`：桌面左侧导航 + 顶部 HUD + 多列卡牌/表格。

## 应用到 FreqUI

```bash
bash freqtrade-cardduel-ui/scripts/import-upstream.sh tianlu-frequi-cardduel
cd tianlu-frequi-cardduel
pnpm install
pnpm run dev
```

生产构建：

```bash
pnpm run build
```

## 边界

- 本包是 UI 视觉与组件改造，不改 Freqtrade 交易逻辑。
- 不包含 API Key、Secret、交易数据库或钱包信息。
- 不使用 Riot/英雄联盟受版权保护素材；仅使用原创暗黑符文卡牌风格。
