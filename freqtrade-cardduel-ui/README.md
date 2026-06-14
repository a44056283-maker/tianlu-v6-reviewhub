# tianlu-frequi-cardduel

> 天禄交易系统 · Freqtrade 官方 FreqUI 改造包  
> 目标：把 Freqtrade 官方 WebUI 改造成原创的“暗黑符文卡牌对战”交易驾驶舱风格。

## 上游来源

- 后端交易机器人：`freqtrade/freqtrade`
- 官方前端 UI：`freqtrade/frequi`
- 本改造包基于官方 FreqUI 的 Vue / Vite / Nuxt UI 架构进行覆盖式改造。

## 当前状态

已开始落地 P0 级 UI 改造：

- 全局主题变量与暗黑战场背景。
- 顶部导航改成卡牌战场 HUD。
- 主内容区增加符文舞台容器。
- 移动底栏改成卡牌技能槽。
- 品牌标识改成原创“天禄决策核心”。
- 不改交易逻辑、不改 API、不改 Freqtrade 后端。

## 重要许可说明

FreqUI 使用 GPL-3.0 license。复制、修改和分发时必须保留原始许可证、版权声明，并且衍生版本也需要遵守 GPL-3.0 的开源义务。

本改造包不使用 Riot、英雄联盟、英雄头像、Logo、技能图标或原始美术素材；视觉方向采用原创的“暗黑符文、金属边框、卡牌战场、战报面板”风格，避免直接侵权。

## 使用方式

在本仓库根目录执行：

```bash
bash freqtrade-cardduel-ui/scripts/import-upstream.sh tianlu-frequi-cardduel
```

脚本会：

1. 克隆官方 FreqUI 原版源码。
2. 新建本地项目目录 `tianlu-frequi-cardduel`。
3. 把官方远端重命名为 `upstream`。
4. 新建改造分支 `tianlu/cardduel-ui`。
5. 覆盖 `overlay/` 中的首批改造文件。

然后进入新项目：

```bash
cd tianlu-frequi-cardduel
pnpm install
pnpm run dev
```

生产构建：

```bash
pnpm run build
```

## 改造路线

P0：全局主题、导航、主舞台、移动底栏、品牌标识。  
P1：Dashboard 卡牌化、Trade 页面战斗面板化、Open Trades 变成“场上卡牌”。  
P2：Chart 页面符文地图化、Logs 页面战报化、Settings 页面符文书化。  
P3：Backtest / Download Data / Pairlist Config 全量皮肤统一。  
P4：E2E、暗色主题稳定性、响应式、无障碍与构建检查。

## 安全边界

- 不改交易逻辑。
- 不保存 API Key / Secret / Passphrase。
- 不上传 `.env`、交易数据库、钱包私钥或任何敏感凭据。
- 强制平仓、停止交易、登录、布局锁定等功能保留原有交互链路，只改视觉呈现。
