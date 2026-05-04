# ExitDecisionGate 补丁规范
> 出山院代理生成 | 日期: 2026-05-04 | 状态: PENDING REVIEW

---

## 一、问题定位

### P0-4: 连续亏损后止盈收紧到10%的代码位置（无门控）

**文件**: `~/freqtrade_console/bt_tools/v65_autopilot.py`
**行号**: 4670-4675

```python
# 方案四: 连续亏损>2次 → 收紧止盈阈值（早卖）
if consec_losses >= 2 and profit_pct > 5:
    thresh = 10  # 盈利>5%就开始卖（比正常P1提前）
    _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，收紧止盈触发至{thresh}%")
    # 临时修改_L3_EXIT触发阈值（单次生效）
    _temp_thresh_override[base] = thresh
```

**问题**:
1. 触发后直接写入 `_temp_thresh_override`，未经 ExitDecisionGate 审批
2. L1盈利分批(4684-4734)使用该阈值时，完全绕过 L5 动态止盈门控
3. 无 post_exit_continuation 状态，无法区分「连续亏损观察期」和「正常交易」
4. 阈值10%固定写死，不可配置，无退出条件

---

## 二、7条出场路径优先级（已确认）

| 优先级 | 路径名称 | 代码位置 | 触发条件 | 动作 |
|--------|----------|----------|----------|------|
| P0 | 舆情猎杀出山AI | console_server.py | 舆情利空+出山指令 | 立即全平 |
| P1 | L1 ATR止损 | 4600-4649 | 触及ATR动态止损线 | 立即全平 |
| P2 | 自学习防御(方案二) | 4662-4668 | 方向错误率>50% | 立即全平 |
| P3 | **L1盈利分批** | 4684-4734 | profit_pct >= 动态阈值 | 部分/全平 |
| P4 | L5动态止盈(P1/P2/P3) | 4736-4923 | profit_pct >= 档位阈值 | 分批/全平 |
| P5 | L2时线止盈 | 4928-4965 | 触及S/R位+放量 | 部分/全平 |
| P6 | 峰值回撤保护 | 4971 | 浮盈创高后回撤5% | 全平 |

**注意**: 当前代码中 P2(自学习防御)和 P3(L1盈利分批)紧邻但分离，L5是独立代码块。L2(L3)时线止盈位于最后。

---

## 三、ExitDecisionGate 类设计

```python
# ═══════════════════════════════════════════════════════════════
# 出场裁决闸门（ExitDecisionGate）
# 优先级: P0(舆情) > P1(L1_ATR止损) > P2(自学习防御) >
#         P3(L1盈利分批) > P4(L5动态止盈) > P5(L2时线止盈) > P6(峰值回撤)
# ═══════════════════════════════════════════════════════════════

class ExitDecisionGate:
    """
    出场裁决闸门

    所有出场动作必须经过此门控，确保：
    1. 不在 post_loss_observation 观察期内执行自学习收紧
    2. 维护 7 条出场路径的互斥优先级
    3. 记录 post_exit_continuation 状态
    """

    def __init__(self):
        # 全局状态（与 v65_autopilot.py 共享）
        pass

    # ── 门控决策 ──────────────────────────────────────────────
    def evaluate(self, position, m1_payload=None, l5_payload=None) -> dict:
        """
        返回门控决策结果

        参数:
            position: v65_autopilot.py 持仓对象（含 pair, direction, profit_pct 等）
            m1_payload: M1舆情数据（可选）
            l5_payload: L5动态止盈档位数据（可选）

        返回:
            {
                "approved": bool,          # 是否批准出场
                "action": str,             # "exit", "observe", "block", "pass"
                "reason": str,             # 决策原因
                "exit_pct": float | None,  # 出场比例（仅 approved=True 时有效）
                "tier": str | None,       # 触发档位 P1/P2/P3/L1/L2
                "override_thresh": float | None,  # 临时阈值（仅自学习收紧场景）
                "blocked_reason": str | None,     # 被拦截原因（仅 action=block 时有效）
            }
        """
        pair = position.get("pair", "")
        direction = position.get("direction", "LONG")
        profit_pct = position.get("profit_pct", 0.0)

        # ── Step 1: 检查 post_loss_observation 观察期 ─────────
        post_state = self._get_post_exit_continuation(pair)
        if post_state and post_state.get("observation_active"):
            obs_end = post_state.get("observation_end_ts", 0)
            if time.time() < obs_end:
                # 观察期内：不允许自学习收紧，拦截 auto_profit_tighten
                if post_state.get("actions_blocked", []):
                    _log(f"[ExitDecisionGate] {pair} 在连续亏损观察期内，拦截自学习收紧")
                    return {
                        "approved": False,
                        "action": "observe",
                        "reason": f"post_loss_observation_active (剩余{self._remaining_obs_hours(post_state):.1f}h)",
                        "exit_pct": None,
                        "tier": None,
                        "override_thresh": None,
                        "blocked_reason": "auto_profit_tighten_blocked_in_observation",
                    }
            else:
                # 观察期结束：重置状态
                self._clear_post_exit_continuation(pair)

        # ── Step 2: 自学习连续亏损收紧必须走门控 ──────────────
        consec_losses = self._get_consecutive_losses(pair)
        if consec_losses >= 2:
            # 必须先经过门控，不能直接写 _temp_thresh_override
            base_thresh = self._calc_normal_p1_threshold(position)
            tightened_thresh = 10.0  # 可配置化，见下方配置常量
            return {
                "approved": False,  # 不自动收紧，等待人工确认或观察期结束
                "action": "block",
                "reason": f"consecutive_losses={consec_losses} >= 2, tighten_request_blocked",
                "exit_pct": None,
                "tier": None,
                "override_thresh": tightened_thresh,  # 记录但不下发
                "blocked_reason": "auto_tighten_blocked_require_observation",
            }

        # ── Step 3: 正常评估（不经任何拦截）─────────────────────
        return self._normal_evaluate(position, m1_payload, l5_payload)

    # ── 正常评估（无拦截）────────────────────────────────────
    def _normal_evaluate(self, position, m1_payload, l5_payload) -> dict:
        """
        正常出场门控评估流程

        评估顺序（对应7条路径优先级）:
        1. M1舆情 → P0
        2. L1 ATR止损 → P1
        3. 自学习防御(方案二: 方向错误率>50%) → P2
        4. L1盈利分批（含自学习临时阈值）→ P3
        5. L5动态止盈(P1/P2/P3档位) → P4
        6. L2时线止盈 → P5
        7. 峰值回撤保护 → P6
        """
        pair = position.get("pair", "")
        direction = position.get("direction", "LONG")
        profit_pct = position.get("profit_pct", 0.0)
        leverage = position.get("leverage", 10)

        # ── P0: M1舆情 ────────────────────────────────────────
        if m1_payload and m1_payload.get("sentiment") == "BEARISH":
            return {
                "approved": True,
                "action": "exit",
                "reason": "M1_BEARISH_SENTIMENT",
                "exit_pct": 100.0,
                "tier": "P0_M1_SENTIMENT",
                "override_thresh": None,
                "blocked_reason": None,
            }

        # ── P1: L1 ATR止损（在 check_exit_conditions 中已处理，此处兜底）──
        atr_stop = position.get("atr_stop_price", None)
        if atr_stop:
            current_price = position.get("current_price", 0)
            if direction == "LONG" and current_price <= atr_stop:
                return {
                    "approved": True,
                    "action": "exit",
                    "reason": f"L1_ATR_STOP hit (stop={atr_stop})",
                    "exit_pct": 100.0,
                    "tier": "P1_ATR",
                    "override_thresh": None,
                    "blocked_reason": None,
                }
            elif direction == "SHORT" and current_price >= atr_stop:
                return {
                    "approved": True,
                    "action": "exit",
                    "reason": f"L1_ATR_STOP hit (stop={atr_stop})",
                    "exit_pct": 100.0,
                    "tier": "P1_ATR",
                    "override_thresh": None,
                    "blocked_reason": None,
                }

        # ── P3: L1盈利分批（带自学习临时阈值）──────────────────
        temp_thresh = self._get_temp_thresh_override(pair)
        if temp_thresh and profit_pct >= temp_thresh:
            return {
                "approved": True,
                "action": "exit",
                "reason": f"L1_PROFIT_TIER (tightened={temp_thresh}%)",
                "exit_pct": min(_L3_EXIT_15_PCT or 50, 50),
                "tier": "P3_L1_TIGHTENED",
                "override_thresh": temp_thresh,
                "blocked_reason": None,
            }
        elif profit_pct >= 30 and _L3_EXIT_30_PCT > 0:
            return {
                "approved": True,
                "action": "exit",
                "reason": f"L1_PROFIT >= 30%",
                "exit_pct": _L3_EXIT_30_PCT,
                "tier": "P3_L1_30",
                "override_thresh": None,
                "blocked_reason": None,
            }

        # ── P4: L5动态止盈 ────────────────────────────────────
        if l5_payload:
            tier_idx = l5_payload.get("tier_idx", -1)
            trigger_pct = l5_payload.get("trigger_pct", 0)
            if profit_pct >= trigger_pct:
                return {
                    "approved": True,
                    "action": "exit",
                    "reason": f"L5_DYNAMIC_EXIT tier={tier_idx+1} ({trigger_pct}%)",
                    "exit_pct": l5_payload.get("exit_pct", 50),
                    "tier": f"P4_L5_T{tier_idx+1}",
                    "override_thresh": None,
                    "blocked_reason": None,
                }

        # ── P5: L2时线止盈 ────────────────────────────────────
        sr_payload = position.get("sr_exit_payload", None)
        if sr_payload and sr_payload.get("should_exit"):
            if self._v65_profit_exit_allowed(profit_pct, leverage, sr_payload.get("reason", "")):
                return {
                    "approved": True,
                    "action": "exit",
                    "reason": sr_payload.get("reason", "L2_SR_EXIT"),
                    "exit_pct": sr_payload.get("exit_pct", 100),
                    "tier": "P5_L2_SR",
                    "override_thresh": None,
                    "blocked_reason": None,
                }

        # ── P6: 峰值回撤保护 ──────────────────────────────────
        peak_profit = position.get("peak_profit_pct", 0)
        if peak_profit > 0 and profit_pct < peak_profit - 5.0:
            return {
                "approved": True,
                "action": "exit",
                "reason": f"PEAK_DRAWDOWN {peak_profit:.1f}% -> {profit_pct:.1f}%",
                "exit_pct": 100.0,
                "tier": "P6_PEAK_DRAWDOWN",
                "override_thresh": None,
                "blocked_reason": None,
            }

        # 无触发
        return {
            "approved": False,
            "action": "pass",
            "reason": "no_exit_triggered",
            "exit_pct": None,
            "tier": None,
            "override_thresh": None,
            "blocked_reason": None,
        }

    # ── 辅助方法 ──────────────────────────────────────────────
    def _get_post_exit_continuation(self, pair: str) -> dict | None:
        """从全局状态读取 post_exit_continuation"""
        return _post_exit_continuation.get(pair)

    def _clear_post_exit_continuation(self, pair: str) -> None:
        """清除 post_exit_continuation 状态"""
        _post_exit_continuation.pop(pair, None)

    def _get_consecutive_losses(self, pair: str) -> int:
        """代理到现有 _get_consecutive_losses"""
        return _get_consecutive_losses(pair)

    def _get_temp_thresh_override(self, pair: str) -> float | None:
        """读取临时止盈阈值（仅从已授权的全局状态）"""
        base = pair.split("/")[0]
        return _temp_thresh_override.get(base)

    def _calc_normal_p1_threshold(self, position) -> float:
        """计算正常P1触发阈值"""
        leverage = position.get("leverage", 10)
        return _BASE_EXIT_P1_PROFIT * (leverage / 10.0)

    def _remaining_obs_hours(self, post_state: dict) -> float:
        """计算观察期剩余小时数"""
        remaining = post_state.get("observation_end_ts", 0) - time.time()
        return max(0, remaining / 3600)

    def _v65_profit_exit_allowed(self, profit_pct: float, leverage: float, reason: str = "") -> bool:
        """代理到 v65_autopilot 内部函数"""
        return _v65_profit_exit_allowed(profit_pct, leverage, reason)
```

---

## 四、与L5动态止盈的接口

```python
# ExitDecisionGate 与 L5 的接口约定

# 1. L5 调用门控前准备 payload
l5_payload = {
    "tier_idx": tier_idx,           # 当前档位索引
    "trigger_pct": trigger_pct,      # 本档触发涨幅（杠杆计算后）
    "exit_pct": exit_pct,            # 本档卖出比例
    "at_sr": at_sr,                  # 是否在S/R位
    "dist_pct": dist_pct,            # 距S/R位距离%
}

# 2. 调用门控
gate = ExitDecisionGate()
decision = gate.evaluate(position, m1_payload=None, l5_payload=l5_payload)

# 3. 根据决策执行
if decision["approved"]:
    if decision["tier"].startswith("P4"):
        # L5动态止盈被批准
        _execute_partial_exit(trade_id, decision["exit_pct"])
    elif decision["tier"].startswith("P3"):
        # L1盈利分批被批准
        _execute_partial_exit(trade_id, decision["exit_pct"])
    elif decision["action"] == "observe":
        # 观察期，禁止所有自学习收紧
        _log(f"[Gate] BLOCKED: {decision['blocked_reason']}")
    elif decision["action"] == "block":
        # 自学习收紧被拦截（连续亏损>=2）
        _log(f"[Gate] AUTO-TIGHTEN BLOCKED: {decision['blocked_reason']}")
        _temp_thresh_override.pop(base, None)  # 清除待下发的收紧阈值
```

---

## 五、全局状态变量（需新增）

```python
# ── post_exit_continuation 状态 ───────────────────────────
# pair → {
#     "observation_active": bool,
#     "consecutive_losses": int,
#     "observation_start_ts": float,
#     "observation_end_ts": float,
#     "loss_threshold": int,
#     "actions_blocked": list[str],
#     "last_loss_pair": str,
# }
_post_exit_continuation: dict = {}
```

---

## 六、需删除/修改的原问题代码

### 删除：行 4670-4675（连续亏损收紧绕过门控）

```python
# 【需删除】方案四: 连续亏损>2次 → 收紧止盈阈值（早卖）
# 这段代码绕过 ExitDecisionGate，直接写 _temp_thresh_override
# 替换方案：改为调用 ExitDecisionGate.evaluate() 并遵循返回值
#
# OLD CODE (lines 4670-4675):
#     if consec_losses >= 2 and profit_pct > 5:
#         thresh = 10  # 盈利>5%就开始卖（比正常P1提前）
#         _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，收紧止盈触发至{thresh}%")
#         _temp_thresh_override[base] = thresh
```

### 替换为：

```python
# 【新增】ExitDecisionGate 门控评估
if _SELF_LEARNING_ENABLED:
    try:
        base = pair.split("/")[0]
        err_rate = _get_direction_error_rate(pair, hours=24)
        consec_losses = _get_consecutive_losses(pair)
        gate = ExitDecisionGate()
        gate_result = gate.evaluate(
            position={"pair": pair, "direction": direction,
                      "profit_pct": profit_pct, "leverage": leverage},
            m1_payload=None,
            l5_payload=None
        )
        # 记录状态（供日志和下游使用）
        _LEARNED_EXIT_PARAMS[base] = {
            "err_rate": err_rate,
            "consec_losses": consec_losses,
            "gate_action": gate_result.get("action"),
            "gate_blocked": gate_result.get("blocked_reason"),
        }
        # P2: 方向错误率>50% → 强制全平（绕过门控，因为是防御性）
        if gate_result.get("action") == "exit" and gate_result.get("tier") == "P2_SELF_LEARNING":
            _log(f"[自学习防御] {pair} 方向错误率{err_rate:.0%}>50%，盈利{profit_pct:.1f}%强制提前出场")
            _cancel_exchange_stoploss(pair)
            rpc._rpc_force_exit(str(trade_id), ordertype="market")
            _exit_cooldown[f"{base}_{direction}"] = time.time()
            _profit_exit_log[pair] = time.time()
            _pair_exit_done.add(pair)
            continue
    except Exception as _e:
        _log(f"  ⚠️ 自学习出场防御异常 {pair}: {_e}")
```

---

## 七、配置常量（建议新增）

```python
# ── ExitDecisionGate 配置 ──────────────────────────────────
_EXIT_GATE_LOSS_THRESHOLD = 2        # 连续亏损N次后进入观察期
_EXIT_GATE_OBSERVATION_HOURS = 24    # 观察期时长（小时）
_EXIT_GATE_TIGHTEN_THRESHOLD = 10.0  # 连续亏损后收紧止盈阈值（%）
_EXIT_GATE_BLOCKED_ACTIONS = [        # 观察期内被禁止的动作
    "auto_profit_tighten",            # 自学习自动收紧止盈
    "auto_dca",                       # 自动DCA加仓
    "auto_reentry",                   # 自动反向入场
]
```

---

## 八、patch-diff（核心变更）

```diff
--- a/v65_autopilot.py
+++ b/v65_autopilot.py
@@ -1517,6 +1517,10 @@ _temp_thresh_override: dict = {}  # pair_base → 临时止盈阈值（自学习应急调整）

 _pair_exit_done: set = set()

+# ── post_exit_continuation 状态 ───────────────────────────
+_post_exit_continuation: dict = {}   # pair → {observation_active, consecutive_losses, ...}
+
 _SR_EXIT_TOLERANCE = 0.5

@@ -4669,10 +4673,16 @@ def check_exit_conditions(...):
             # 方案四（已删除，直接写_temp_thresh_override）
-            if consec_losses >= 2 and profit_pct > 5:
-                thresh = 10
-                _log(f"[自学习微调] {pair} 连续亏损{consec_losses}次，收紧止盈触发至{thresh}%")
-                _temp_thresh_override[base] = thresh
+            # 【patch】方案四改为 ExitDecisionGate 门控
+            gate = ExitDecisionGate()
+            gate_result = gate.evaluate(
+                position={"pair": pair, "direction": direction,
+                          "profit_pct": profit_pct, "leverage": leverage},
+                m1_payload=None, l5_payload=None)
+            # blocked → 不下发收紧阈值（观察期保护生效）
+            if gate_result.get("action") in ("block", "observe"):
+                _temp_thresh_override.pop(base, None)  # 清除待下发阈值

             # ── L1 盈利分批检测（优先级最高） ──
             temp_thresh = _temp_thresh_override.get(base, None)
```

---

## 九、验证检查清单

- [ ] `_post_exit_continuation` 全局变量已声明
- [ ] `ExitDecisionGate` 类已插入到 `check_exit_conditions()` 函数之前
- [ ] 原 4670-4675 行已被门控调用替换
- [ ] `_LEARNED_EXIT_PARAMS` 增加 `gate_action` 和 `gate_blocked` 字段
- [ ] L1盈利分批(4684)仍使用 `_temp_thresh_override`，但门控已拦截下发
- [ ] L5动态止盈(4736)增加了 `ExitDecisionGate.evaluate()` 调用
- [ ] 连续亏损>=2时，`_temp_thresh_override[base]` 不再被写入
- [ ] 观察期结束后，`_post_exit_continuation[pair]` 被正确清除
