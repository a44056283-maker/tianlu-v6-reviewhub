# 天禄 V6.5.1 规则与AI场景接入 — 总报告

> 生成时间：2026-05-04 14:50
> 审计类型：只读，多子代理协作（8个代理并行）
> 禁止修改实盘策略/机器人配置

---

## 执行摘要

**目标**：今天完成 V6.5.1 接入候选版，包括规则、话术、补丁草案、dry-run、回滚包。

8个子代理已完成，14个文件合计377KB，覆盖：
- M1-M5 完整字段映射与裁决规范
- EntryDecisionGate 入场统一闸门
- ExitDecisionGate 出场统一闸门
- 天眼AI 11个入场场景话术
- 出山AI 10个出场场景话术
- 12机器人兼容性矩阵
- DOGE/SOL 止血规则
- DCA/杠杆保护规则
- ForceActionGuard 权限闸
- L5 影子实验与晋级规则
- 补丁索引 + dry-run 测试日志
- 回滚计划 + QA检查清单

---

## P0 紧急止血补丁

### P0-1：冻结 DOGE/USDT 自动新增入场（24小时）
**根因**：8个bot同步做空 DOGE → 批量止损 → 立即重新入场，循环损耗。
**修复**：overlay配置添加 `temporary_pair_freeze`

### P0-2：暂停 SOL/USDT SHORT 自动 DCA
**根因**：SOL SHORT DCA满层，ROE -27.9%，继续加仓放大亏损。
**修复**：overlay配置添加 `dca_pause_rules`

### P0-3：DCA 触发清除止损冷却
**文件**：`v65_autopilot.py:6268-6272`
**修复**：删除 `del _stoploss_state[pair]`，止损冷却不可绕过

### P0-4：连续亏损收紧止盈绕过 ExitDecisionGate
**文件**：`v65_autopilot.py:4670-4675`
**修复**：ExitDecisionGate 门控裁决，连续亏损收紧必须经过门控确认

### P0-5：stagger_delay 负数保护
**文件**：`v65_autopilot.py:5267`
**修复**：`stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))`

---

## P1 新增架构补丁

### P1-1：ForceGuard 审计日志
**文件**：`console_server.py`
**内容**：force_entry/force_exit/force_dca 全部写入 `~/.tianlu/logs/force_action_audit.log`

### P1-2：PostExitContinuation 状态机
**文件**：`v65_autopilot.py`
**内容**：出场后30分钟观察期，禁止反向开仓，防止双杀

### P1-3：L5 候选注册表与晋级闸门
**文件**：`v65_autopilot.py`
**内容**：promotion_trials≥5 + win_rate≥0.55 + auto_apply_to_live=false

### P1-4：M1-M5 证据载荷规范
**文件**：`api_*.py`
**内容**：统一 evidence payload JSON Schema，天眼/出山AI可解释语言

---

## 核心规范

### M1 资金流裁决五档

| 档位 | 分值 | 说明 | 自动执行 |
|------|------|------|---------|
| A | ≥85% | 三所全一致 + 量比≥3.0x + 新鲜度≥0.8 | ✅ |
| B | 70-84% | ≥2所一致 + 量比≥2.0x | ⚠️ 等待确认 |
| C | 55-69% | 温和放量 | ❌ 噪音禁止 |
| D | 40-54% | 低置信 | ❌ 禁止入场 |
| E | <40% | 无数据/严重分歧 | ❌ 禁止入场 |

### EntryDecisionGate 五档裁决

| 档位 | 含义 | 自动执行 |
|------|------|---------|
| A | 可入场 | ✅ |
| B | 等待确认 | ⚠️ 需第二轮同向确认 |
| C | 噪音禁止 | ❌ |
| D | 数据不足 | ❌ |
| E | 单所异常降权 | ❌ |

### ExitDecisionGate 五档裁决

| 档位 | 含义 | 自动执行 |
|------|------|---------|
| G1 HOLD | 继续持有 | ✅ |
| G2 WATCH | 观察 | ⚠️ |
| G3 PARTIAL_EXIT | 建议部分止盈 | ⚠️ |
| G4 FULL_EXIT_REVIEW | 建议全平复核 | ❌ 需人工确认 |
| G5 EMERGENCY_REVIEW | 紧急风险复核 | ❌ 需人工确认 |

---

## Mac B 特殊说明

Mac B（192.168.13.104）SSH不可达，8081-8084补丁需手动执行。

---

## 下一步

1. 本报告 + 14个文件推送 GitHub
2. GPT 审核并给出执行批准
3. 根据 GPT 批准，分阶段执行（先 P0-1/P0-2 配置补丁，再 P0-3~P1-4 代码补丁）

---

*中书省监制 | 2026-05-04*
