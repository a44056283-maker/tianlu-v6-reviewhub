# 补丁草案索引 — V6.5.1 DCA L5 Force Rollout 集成
**生成时间**: 2026/05/04 15:30
**来源批次**: LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT_20260504
**生成角色**: 工部代理（汇总审查）
**状态**: PENDING — 待尚书省/爸确认后执行

---

## 补丁总览

| 编号 | 优先级 | 文件 | 位置 | 摘要 | 状态 |
|------|--------|------|------|------|------|
| P0-1 | CRITICAL | overlay configs (12个) | JSON top-level | DOGE冻结 (temporary_pair_freeze) | PENDING |
| P0-2 | CRITICAL | overlay configs (12个) | JSON top-level | SOL DCA暂停 (dca_pause_rules) | PENDING |
| P0-3 | P0 | v65_autopilot.py | ~line 6268-6272 | DCA触发不清除止损冷却（Bugfix） | PENDING |
| P0-4 | P0 | v65_autopilot.py | ~line 4670-4675 | 连续亏损绕过ExitDecisionGate修复 | PENDING |
| P0-5 | P1 | v65_autopilot.py | ~line 5267 | stagger_delay负数保护 | PENDING |
| P1-1 | P1 | console_server.py | imports区域 | ForceGuard审计日志常量 | PENDING |
| P1-2 | P1 | v65_autopilot.py | 状态区 | PostExitContinuation状态机 | PENDING |
| P1-3 | P1 | v65_autopilot.py | 状态区 | L5候选注册表+晋级闸门 | PENDING |
| P1-4 | P2 | api_*.py (M1-M5) | 各模块 | M1-M5证据载荷规范 | PENDING |

---

## P0-1 DOGE冻结 — Overlay配置补丁

**目标**: 全部12个bot（Mac A 8个 + Mac B 4个）
**修改内容**: 在overlay JSON末尾追加 `temporary_pair_freeze` 字段
**JSON内容**:
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

| 端口 | 交易所 | 文件路径 | 状态 |
|------|--------|----------|------|
| 9090 | Gate.io | ~/freqtrade_console/bt_tools/config_9090_overlay.json | PENDING |
| 9091 | Gate.io | ~/freqtrade/config_9091_overlay.json | PENDING |
| 9092 | Gate.io | ~/freqtrade/config_9092_overlay.json | PENDING |
| 9093 | OKX | ~/freqtrade/config_9093_overlay.json | PENDING |
| 9094 | OKX | ~/freqtrade/config_9094_overlay.json | PENDING |
| 9095 | OKX | ~/freqtrade/config_9095_overlay.json | PENDING |
| 9096 | OKX | ~/freqtrade/config_9096_overlay.json | PENDING |
| 9097 | OKX | ~/freqtrade/config_9097_overlay.json | PENDING |
| 8081 | Gate.io (Mac B) | ~/freqtrade_bots/config_8081_overlay.json | PENDING (SSH) |
| 8082 | Gate.io (Mac B) | ~/freqtrade_bots/config_8082_overlay.json | PENDING (SSH) |
| 8083 | Gate.io (Mac B) | ~/freqtrade_bots/config_8083_overlay.json | PENDING (SSH) |
| 8084 | Gate.io (Mac B) | ~/freqtrade_bots/config_8084_overlay.json | PENDING (SSH) |

---

## P0-2 SOL DCA暂停 — Overlay配置补丁

**目标**: 全部12个bot（Mac A 8个 + Mac B 4个）
**修改内容**: 在overlay JSON末尾追加 `dca_pause_rules` 字段
**JSON内容**:
```json
"dca_pause_rules": {
  "SOL/USDT:USDT:SHORT": {
    "enabled": true,
    "reason": "dca_full_layer_roe_negative",
    "block_new_dca": true
  }
}
```

| 端口 | 交易所 | 文件路径 | 状态 |
|------|--------|----------|------|
| 9090-9097 | Gate.io/OKX | 各overlay配置 | PENDING |
| 8081-8084 | Gate.io (Mac B) | 各overlay配置 | PENDING (SSH) |

---

## P0-3 DCA清除止损冷却修复

**文件**: ~/freqtrade_console/bt_tools/v65_autopilot.py
**位置**: ~line 6268-6272
**严重度**: P0

**问题描述**: DCA触发时删除止损冷却状态，导致4小时止损保护被绕过，连续亏损累积。

**修改内容**:
```diff
- if pair in _stoploss_state:
-     del _stoploss_state[pair]
+ # Bugfix 2026-05-04: DCA触发时不应清除止损冷却
+ if pair in _stoploss_state and not (_dca_triggered):
+     del _stoploss_state[pair]
```

**行为变更**: 只有外部全平/止损才清除止损冷却；DCA触发不再清除。

---

## P0-4 连续亏损绕过ExitDecisionGate修复

**文件**: ~/freqtrade_console/bt_tools/v65_autopilot.py
**位置**: ~line 4670-4675
**严重度**: P0

**问题描述**: 连续亏损>=2次时直接写入 `_temp_thresh_override=10`，绕过任何门控，导致"卖在黎明前"。

**修改内容**:
1. 新增 `ExitDecisionGate` 类（含观察期保护）
2. 替换直接写入逻辑为门控裁决

```diff
- if consec_losses >= 2 and profit_pct > 5:
-     thresh = 10
-     _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，收紧止盈触发至{thresh}%")
-     _temp_thresh_override[base] = thresh
+ if consec_losses >= 2 and profit_pct > 5:
+     gate = ExitDecisionGate()
+     if gate.request_threshold_override(base, 10):
+         _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，闸门批准收紧至10%")
+         _temp_thresh_override[base] = 10
+     else:
+         _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，闸门拒绝（观察期内）")
```

---

## P0-5 stagger_delay负数保护

**文件**: ~/freqtrade_console/bt_tools/v65_autopilot.py
**位置**: ~line 5267
**严重度**: P1

**问题描述**: 若 `_LISTEN_PORT < 9000`，`stagger_delay` 为负数，`time.sleep(负数)` 抛出 ValueError。

**修改内容**:
```diff
- stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
+ stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))
```

---

## P1-1 ForceGuard审计日志

**文件**: ~/freqtrade_console/console_server.py
**位置**: imports区域
**严重度**: P1

**修改内容**: 新增审计日志路径常量和记录函数
```python
# ── ForceGuard 审计日志路径 ───────────────────────────────────────────────
from pathlib import Path
_FORCE_AUDIT_LOG = Path.home() / ".tianlu" / "logs" / "force_action_audit.log"
_FORCE_AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

def _log_force_action(bot_id, action, pair, reason, confirmed_by):
    """记录所有强制操作到审计日志"""
    import datetime
    ts = datetime.datetime.now().isoformat()
    entry = f"{ts} | BOT={bot_id} | ACTION={action} | PAIR={pair} | REASON={reason} | CONFIRMED={confirmed_by}\n"
    with open(_FORCE_AUDIT_LOG, "a") as f:
        f.write(entry)
```

---

## P1-2 PostExitContinuation状态机

**文件**: ~/freqtrade_console/bt_tools/v65_autopilot.py
**位置**: 状态区（约line 1517附近）
**严重度**: P1

**修改内容**: 新增出场后观察期状态，防止连续亏损后立即反向开仓导致双杀

```python
# ── PostExitContinuation 状态 ─────────────────────────────────────────────
_post_exit_continuation = {}  # {pair: exit_timestamp}
POST_EXIT_OBSERVATION = 1800  # 30分钟观察窗口

def is_in_post_exit_continuation(pair):
    import time
    if pair not in _post_exit_continuation:
        return False
    return (time.time() - _post_exit_continuation[pair]) < POST_EXIT_OBSERVATION

def record_exit_for_continuation(pair):
    import time
    _post_exit_continuation[pair] = time.time()
```

---

## P1-3 L5候选注册表+晋级闸门

**文件**: ~/freqtrade_console/bt_tools/v65_autopilot.py
**位置**: 状态区（PostExitContinuation之后）
**严重度**: P1

**修改内容**: 新增 `L5CandidateRegistry` 和 `L5PromotionGate` 类，确保L5策略晋级必须经过影子实验验证

```python
class L5CandidateRegistry:
    def __init__(self):
        self._candidates = {}

    def register(self, strategy_name):
        if strategy_name not in self._candidates:
            self._candidates[strategy_name] = {
                "registered_at": None,
                "promotion_trials": 0,
                "win_rate": 0.0,
                "auto_apply_to_live": False  # 硬编码禁止自动写入
            }

    def is_promotion_ready(self, strategy_name):
        c = self._candidates.get(strategy_name, {})
        return (c.get("promotion_trials", 0) >= 5 and
                c.get("win_rate", 0) >= 0.55 and
                c.get("auto_apply_to_live") is False)

class L5PromotionGate:
    def try_promote(self, strategy_name):
        if self._registry.is_promotion_ready(strategy_name):
            return True
        return False

_L5_REGISTRY = L5CandidateRegistry()
_L5_PROMOTION_GATE = L5PromotionGate()
```

**晋级条件**: 影子实验>=5次 AND 胜率>=55% AND auto_apply_to_live==False

---

## P1-4 M1-M5证据载荷规范

**文件**: api_tianyan.py (M1), api_chushan.py (M2), api_hero_card.py (M3-M5) 等
**位置**: 各api_*.py模块
**严重度**: P2

**修改内容**: 规范M1-M5各模块向出山AI/天眼AI提交的证据载荷格式

| 模块 | 载荷内容 | 使用位置 |
|------|----------|----------|
| M1 (舆情) | sentiment, confidence, key_events[] | 出场评分入参 |
| M2 (出山AI) | chushan_verdict, chushan_score, atr_stop_px | 出场决策入参 |
| M3 (K线形态) | volume_ratio, pattern_type, sr_level_hit | 入场确认 |
| M4 (资金流) | net_flow_pct, flow_direction, flow_confidence | 入场确认 |
| M5 (持仓卫士) | drawdown_pct, roi_pct, holding_hours | 回撤保护决策 |

---

## 执行顺序建议

```
阶段1 (P0补丁 - 无需重启机器人):
  1. P0-1 + P0-2: 12个overlay配置（重启bot后生效）
  2. P0-3: v65_autopilot.py（DCA清除止损冷却修复）
  3. P0-5: v65_autopilot.py（stagger_delay保护）

阶段2 (P1补丁 - 需重启console_server):
  4. P0-4: v65_autopilot.py（ExitDecisionGate + P1-2 + P1-3）
  5. P1-1: console_server.py（ForceGuard审计日志）
  → 重启console_server（机器人不重启）

阶段3 (P2补丁 - 代码规范):
  6. P1-4: api_*.py（M1-M5载荷规范）
```

---

## 补丁差异汇总表

| 编号 | 文件 | 行变化 | 类型 | 风险 |
|------|------|--------|------|------|
| P0-1 | 12x overlay JSON | +14行/文件 | 配置新增 | 低 |
| P0-2 | 12x overlay JSON | +10行/文件 | 配置新增 | 低 |
| P0-3 | v65_autopilot.py | -1/+3 | Bugfix | 中（行为变更） |
| P0-4 | v65_autopilot.py | -5/+9 | Bugfix | 中（门控逻辑） |
| P0-5 | v65_autopilot.py | -1/+1 | Bugfix | 低 |
| P1-1 | console_server.py | +15 | 审计日志 | 低 |
| P1-2 | v65_autopilot.py | +11 | 状态机新增 | 中 |
| P1-3 | v65_autopilot.py | +45 | 新增类 | 中 |
| P1-4 | api_*.py | 待确认 | 规范文档 | 低 |

---

## 回滚触发条件

- P0-1/P0-2: 将末尾新增字段删除，恢复 } 结尾
- P0-3: 将 `and not (_dca_triggered)` 条件删除
- P0-4: 恢复直接写入 `_temp_thresh_override` 的旧逻辑
- P0-5: 移除 `max(0, ...)` 包装
- P1-1: 删除审计日志常量定义
- P1-2/P1-3: 删除新增状态变量和类定义
- P1-4: 恢复各api模块原始载荷格式

**回滚命令**: 备份文件位于 `~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/`
