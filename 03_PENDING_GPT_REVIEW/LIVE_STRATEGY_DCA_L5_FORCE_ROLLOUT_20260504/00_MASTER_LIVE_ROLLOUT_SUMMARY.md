# 今日实盘改造准备任务 — 总报告

> 生成时间：2026-05-04 14:25
> 审计类型：只读，多子代理协作
> 禁止修改实盘策略/机器人配置

---

## 执行摘要

**目标**：为 V6.5 实盘改造（DCA + 出场门控 + L5晋级 + ForceGuard）建立完整补丁规范，交付 GPT 审核。

12个子报告已完成，覆盖：
- 12机器人配置一致性 ✅
- M1-M5证据层规范 ✅
- DCA杠杆保护 ✅
- ForceGuard审计日志 ✅
- ExitDecisionGate ✅
- PostExitContinuation ✅
- L5候选注册表 ✅
- L5晋级闸门 ✅
- L5禁止自动实盘写入 ✅

---

## P0 紧急止血补丁

### P0-1：冻结 DOGE/USDT 自动新增入场（24小时）

**根因**：8个bot同步做空 DOGE/USDT → 批量止损 → 立即重新入场，循环损耗。

**操作**：在所有12个bot的overlay配置添加：
```json
"temporary_pair_freeze": {
  "DOGE/USDT:USDT": {
    "enabled": true,
    "duration_hours": 24,
    "reason": "batch_stoploss_loop",
    "block_auto_entry": true,
    "block_auto_dca": true
  }
}
```

### P0-2：暂停 SOL/USDT SHORT 自动 DCA

**根因**：SOL/USDT SHORT DCA已满层，ROE -27.9%，继续加仓放大亏损。

**操作**：在所有12个bot的overlay配置添加：
```json
"dca_pause_rules": {
  "SOL/USDT:USDT:SHORT": {
    "enabled": true,
    "reason": "dca_full_layer_roe_negative",
    "block_new_dca": true
  }
}
```

---

## 核心 Bug 修复补丁

### P0-3：DCA 触发清除止损冷却（高优先级）

**文件**：`v65_autopilot.py:6268-6272`
**严重程度**：高

DCA 触发时会删除 `_stoploss_state[pair]`，导致止损冷却被清除，下一次止损立即触发而不等待冷却期。

**修复**：移除 `del _stoploss_state[pair]` 或将其替换为设置标志位（保留冷却状态）。

---

### P0-4：连续亏损收紧止盈绕过 ExitDecisionGate（高优先级）

**文件**：`v65_autopilot.py:4670-4675`
**严重程度**：高

连续亏损≥2次时，将止盈阈值固定收紧到10%，绕过 L5 动态止盈门控，可能造成"卖在黎明前"。

**修复**：新增 `ExitDecisionGate` 类，所有出场决策必须经过门控审批。连续亏损收紧逻辑需门控确认。

---

### P0-5：stagger_delay 负数保护（低优先级）

**文件**：`v65_autopilot.py:5267`
**严重程度**：低

如果 `_LISTEN_PORT < 9000`，`stagger_delay` 变为负数，`time.sleep(负数)` 抛出 ValueError。

**修复**：`stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))`

---

## P1 新增架构补丁

### P1-1：ForceGuard 强制操作审计日志

**文件**：`console_server.py`
**新增**：`FORCE_ACTION_AUDIT_LOG` 常量路径

所有 force_entry / force_exit / force_dca 操作必须写入审计日志（含时间戳、bot_id、操作类型、理由、人工确认）。

### P1-2：PostExitContinuation 状态机

**文件**：`v65_autopilot.py`
**新增**：`post_exit_continuation` 状态字段

出场后进入观察期，期间不执行新的自学习收紧，不允许反向开仓（防止连续亏损→立即反向→双杀）。

### P1-3：L5 候选注册表与晋级闸门

**文件**：`v65_autopilot.py` + `L5_SHADOW_LAB_DB`
**新增**：`L5CandidateRegistry` 类 + `L5PromotionGate` 类

- L5晋级必须经过影子实验验证：`promotion_trials >= 5` 且 `win_rate >= 0.55`
- `auto_apply_to_live: false` 硬编码禁止自动写入实盘
- 晋级闸门全部未满足，实盘保持隔离

### P1-4：M1-M5 证据载荷规范

**文件**：`api_m1.py` / `api_m2.py` 等
**新增**：`_build_evidence_payload()` 统一接口

为天眼AI/出山AI提供标准化的 M1-M5 证据载荷，包含：资金流裁决、市场情绪、入场评分、持仓追踪、技术分析。

---

## Mac B 特殊说明

Mac B（192.168.13.104）4个bot（8081-8084）SSH被拒绝，仅生成占位符补丁。需手动SSH到Mac B执行。

---

## 下一步

1. 本报告 + 12个子报告 + PATCH.diff + 备份推送 GitHub
2. GPT 审核并给出执行批准
3. 根据 GPT 批准，执行 P0-1（P0-2）止血补丁（仅修改配置文件，不改代码）
4. 根据 GPT 批准，执行 P0-3~P0-5 代码补丁（需重启 console_server）
5. Mac B 手动执行补丁

---

*中书省监制 | 2026-05-04*
