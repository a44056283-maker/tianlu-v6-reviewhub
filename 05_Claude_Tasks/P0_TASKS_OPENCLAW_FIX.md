# 天禄 V6.5 OpenClaw 修复任务清单

> 来源：GPT 全面审计 + 诊断报告
> 日期：2026-05-04
> 状态：P0-1已完成 ✓

---

## P0-1 ✅ 已完成 ✓ OpenClaw embedded agent / cron 走 /v1/responses 导致 404

### 根因
- provider 配置为 `minimax2-7`，但 OpenClaw 内置 `normalizeTransport` hook 只认 `minimax`
- embedded agent 的 cfg 缺少 `models.providers`，fallback 到 `openai-responses` → MiniMax CN API 返回 404
- 影响：飞书/微信/cron/embedded agent 无响应

### 修复步骤
1. 备份：`cp ~/.openclaw/agents/tianlu/agent/models.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/`
2. 修改 `models.json`：把 provider 名称从 `minimax2-7` 改为 `minimax`
3. 重启 gateway：`launchctl stop ai.openclaw.gateway && launchctl start ai.openclaw.gateway`
4. 验证：飞书发消息 → 有响应

---

## P0-2 🔴 force_entry / force_exit 统一权限闸缺失

### 现状
- 多个入口可触发 force_entry/exit（Feishu/微信/OpenClaw CLI/console_server）
- 无统一权限验证

### 待生成文档
- `FORCE_ACTION_PERMISSION_MAP.md` — 列出所有触发入口 + 权限要求

---

## P0-3 🔴 DCA_MAX_LAYER=10 与"封顶2次"注释冲突

### 现状
- 代码：`dca_max_layer = 10`
- 注释："封顶2次"
- 两者矛盾，需核查哪个是真实意图

### 待生成文档
- `STRATEGY_SOURCE_OF_TRUTH.md` — 策略真实规则，无歧义

---

## P0-4 🟠 策略规则无单一真相源

### 待生成文档
- `STRATEGY_SOURCE_OF_TRUTH.md`

内容应包含：
- 入场规则（L1 量比 / L2 资金流 / L4 S/R）
- 出场规则（P1/P2/P3 止盈标准）
- DCA 规则（层数/间隔/金额）
- 禁止事项清单

---

## P0-5 🟠 12 个 Bot 配置一致性矩阵缺失

### 待生成文档
- `12_BOT_CONSISTENCY_MATRIX.md`

矩阵维度：
- Bot ID / 端口 / 交易所 / 账号 / 数据目录 / 代理配置 / 策略版本 / 杠杆 / 止盈参数

---

## P0-6 🟡 L5 晋级规则文档缺失

### 待生成文档
- `L5_PROMOTION_GATE_RULES.md`

包含：
- 晋级条件（连续盈利 / 胜率 / 最大回撤）
- 降级条件
- 晋级审批流程

---

## 当前执行顺序

```
1. P0-1 → OpenClaw fix（最高优先，影响所有通讯）
2. P0-4 → STRATEGY_SOURCE_OF_TRUTH.md
3. P0-3 → 核查 DCA 冲突并修正
4. P0-5 → 12_BOT_CONSISTENCY_MATRIX.md
5. P0-2 → FORCE_ACTION_PERMISSION_MAP.md
6. P0-6 → L5_PROMOTION_GATE_RULES.md
```

---

## 禁止事项（GPT 审计确认）

- 不扩功能
- 不直接优化收益
- 先定源头、定权限、定闸门、定一致性
