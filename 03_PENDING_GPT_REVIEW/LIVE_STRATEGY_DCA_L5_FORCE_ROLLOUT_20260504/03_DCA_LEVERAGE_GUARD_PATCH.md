# DCA & 杠杆保护补丁 — V6.5 现场部署
**文件**: `bt_tools/v65_autopilot.py`
**审计时间**: 2026-05-04
**状态**: PENDING — 待GPT评审后部署

---

## 1. DCA_MAX_LAYER 配置确认

**位置**: `v65_autopilot.py:92`
```python
_DCA_MAX_LAYER = 2              # 最大补仓层数（封顶2次）
```

**确认**:
- `_DCA_MAX_LAYER = 2` — 当前设置为2层，符合V6.5规范
- 每层触发阈值定义在 `v65_autopilot.py:98`:
```python
_DCA_TRIGGER_PCTS = [5.0, 15.0]  # 分层触发跌幅/涨幅（%）
```
- 第1层DCA触发: 5%逆向波动
- 第2层DCA触发: 15%逆向波动

**风险**: 无，当前值正确。

---

## 2. stagger_delay 负数保护

**位置**: `v65_autopilot.py:5267-5268`
```python
# ── 错峰：各端口错开启动延迟（避免同时请求K线触发Rate Limit）──
stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
time.sleep(stagger_delay)
```

**问题**: 如果 `_LISTEN_PORT < 9000`（例如测试端口），`stagger_delay` 会变成负数，`time.sleep(负数)` 在 Python 中会抛出 ValueError。

**修复代码**:
```python
# ── 错峰：各端口错开启动延迟（避免同时请求K线触发Rate Limit）──
# Bugfix 2026-05-04: 防止负数导致 time.sleep 抛出 ValueError
stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))
time.sleep(stagger_delay)
```

**diff**:
```diff
- stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
+ stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))
```

---

## 3. P0-3 DCA清除止损冷却 — BUG修复

**位置**: `v65_autopilot.py:6268-6272`
**严重程度**: P0-3（中）

**问题描述**:
DCA触发时，代码主动删除了止损冷却状态，导致止损保护被绕过：

```python
# ── BUG: DCA触发时清除止损冷却，避免刚触发的DCA被冷却阻止 ──
with _stoploss_lock:
    if pair in _stoploss_state and _stoploss_state[pair].get("direction") == direction:
        del _stoploss_state[pair]
        _log(f"  🔓 {pair} DCA触发，清除止损冷却")
```

**风险**:
- 止损后4小时内禁止开仓是核心保护机制
- DCA触发时清除冷却 = 允许在止损保护期内追加仓位
- 可能导致连续亏损累积

**修复策略**: 不清除止损冷却，DCA在冷却期内应被阻止

**修复代码**:
```python
# P0-3修复 2026-05-04: DCA不应清除止损冷却
# 止损冷却是4小时保护窗，DCA追加会放大亏损，不应绕过
# ── 先检查止损冷却（与下方通用冷却检查合并）─────────────────
# 注意：止损冷却检查已在下方的通用检查块中进行（line 6274-6285）
# 此处删除 del _stoploss_state[pair] 操作
# 原BUG代码已删除，冷却检查逻辑保持不变
```

**diff**:
```diff
-                    # ── BUG修复: DCA触发时清除止损冷却，避免刚触发的DCA被冷却阻止 ──
-                    with _stoploss_lock:
-                        if pair in _stoploss_state and _stoploss_state[pair].get("direction") == direction:
-                            del _stoploss_state[pair]
-                            _log(f"  🔓 {pair} DCA触发，清除止损冷却")
+                    # P0-3修复 2026-05-04: DCA不清除止损冷却
+                    # 止损冷却检查在下方通用检查块（line 6274-6285）统一处理
```

**完整止损冷却检查块（line 6274-6285，不变）**:
```python
        # 止损冷却检查 (止损后4小时禁止任何方向开仓)
        with _stoploss_lock:
            _sl_info = _stoploss_state.get(pair)
        if _sl_info:
            _sl_elapsed = time.time() - _sl_info["time"]
            if _sl_elapsed < STOPLOSS_COOLDOWN_SEC:
                _sl_remain = int(STOPLOSS_COOLDOWN_SEC - _sl_elapsed)
                _log(f"  ⏳ {pair} 止损后冷却剩余{_sl_remain}s({_sl_remain//60}min)，禁止任何方向开仓")
                cycle_result["skipped"] += 1
                cycle_result["details"].append({"pair": pair, "success": False,
                    "reason": f"止损冷却{_sl_remain}s"})
                continue
```

---

## 4. DOGE临时冻结函数（新增）

**背景**: DOGE偶发性交易所API不稳定/链上延迟，需要临时冻结所有DOGE交易。

**建议新增函数**（建议添加在 `v65_autopilot.py` `_calc_dca_leverage` 函数附近，约 line 3705）:

```python
import time as _dca_time

# ── DOGE临时冻结配置 ───────────────────────────────────────────────
_DOGE_FREEZE_UNTIL: float | None = None   # Unix时间戳，None=未冻结
_DOGE_FREEZE_DURATION = 3600              # 默认冻结1小时（秒）

def is_doge_freeze_active(pair: str) -> bool:
    """检查pair是否处于DOGE临时冻结状态"""
    if not pair.upper().startswith("DOGE"):
        return False
    if _DOGE_FREEZE_UNTIL is None:
        return False
    if _dca_time.time() > _DOGE_FREEZE_UNTIL:
        global _DOGE_FREEZE_UNTIL
        _DOGE_FREEZE_UNTIL = None   # 已过期，自动清除
        return False
    return True

def set_doge_freeze(duration_sec: int | None = None) -> None:
    """设置DOGE冻结时间
    Args:
        duration_sec: 冻结秒数，None=清除冻结
    """
    global _DOGE_FREEZE_UNTIL
    if duration_sec is None:
        _DOGE_FREEZE_UNTIL = None
        _log("[DOGE] 冻结已解除")
    else:
        _DOGE_FREEZE_UNTIL = _dca_time.time() + duration_sec
        _log(f"[DOGE] 冻结已设置: {duration_sec}秒")

def get_doge_freeze_remaining() -> int:
    """返回DOGE冻结剩余秒数，0=未冻结"""
    if _DOGE_FREEZE_UNTIL is None:
        return 0
    remaining = int(_DOGE_FREEZE_UNTIL - _dca_time.time())
    return max(0, remaining)
```

**在 DCA 入口处调用**（在 `check_dca_trigger` 之前，约 line 6245 之前插入）:

```python
                    # ── DOGE临时冻结检查 ──────────────────────────────────────
                    if is_doge_freeze_active(pair):
                        _log(f"  🚫 {pair} DOGE临时冻结中，禁止DCA")
                        cycle_result["skipped"] += 1
                        cycle_result["details"].append({"pair": pair, "success": False,
                            "reason": "DOGE_temporary_freeze"})
                        continue
```

---

## 5. SOL DCA暂停函数（新增）

**背景**: SOL在特定市场环境下（如VPS延迟加大、交易所API不稳定）需暂停DCA追加。

**建议新增函数**（在 DOGE冻结函数附近）:

```python
# ── SOL DCA暂停配置 ───────────────────────────────────────────────
_SOL_DCA_PAUSE_UNTIL: float | None = None   # Unix时间戳，None=未暂停
_SOL_DCA_PAUSE_DURATION = 1800              # 默认暂停30分钟

def is_sol_dca_paused(pair: str, direction: str) -> bool:
    """检查SOL交易对的DCA是否被暂停"""
    if not pair.upper().startswith("SOL"):
        return False
    if _SOL_DCA_PAUSE_UNTIL is None:
        return False
    if _dca_time.time() > _SOL_DCA_PAUSE_UNTIL:
        global _SOL_DCA_PAUSE_UNTIL
        _SOL_DCA_PAUSE_UNTIL = None   # 已过期，自动清除
        return False
    return True

def set_sol_dca_pause(duration_sec: int | None = None) -> None:
    """设置SOL DCA暂停时间
    Args:
        duration_sec: 暂停秒数，None=清除暂停
    """
    global _SOL_DCA_PAUSE_UNTIL
    if duration_sec is None:
        _SOL_DCA_PAUSE_UNTIL = None
        _log("[SOL] DCA暂停已解除")
    else:
        _SOL_DCA_PAUSE_UNTIL = _dca_time.time() + duration_sec
        _log(f"[SOL] DCA暂停已设置: {duration_sec}秒")

def get_sol_dca_pause_remaining() -> int:
    """返回SOL DCA暂停剩余秒数，0=未暂停"""
    if _SOL_DCA_PAUSE_UNTIL is None:
        return 0
    remaining = int(_SOL_DCA_PAUSE_UNTIL - _dca_time.time())
    return max(0, remaining)
```

**在 DCA 入口处调用**（与DOGE冻结检查并列）:

```python
                    # ── SOL DCA暂停检查 ──────────────────────────────────────
                    if is_sol_dca_paused(pair, direction):
                        _log(f"  🚫 {pair} SOL DCA暂停中，禁止DCA")
                        cycle_result["skipped"] += 1
                        cycle_result["details"].append({"pair": pair, "success": False,
                            "reason": "SOL_DCA_paused"})
                        continue
```

---

## 6. 统一入场许可检查函数（新增）

**建议新增函数**，整合 DOGE/SOL 特殊处理:

```python
def should_allow_auto_entry(pair: str, direction: str) -> tuple[bool, str]:
    """统一入场许可检查
    Returns:
        (allowed: bool, reason: str)
    """
    # DOGE临时冻结
    if is_doge_freeze_active(pair):
        return False, "DOGE_temporary_freeze"
    # SOL DCA暂停
    if is_sol_dca_paused(pair, direction):
        return False, "SOL_DCA_paused"
    return True, "ok"
```

**替换位置**: `v65_autopilot.py` line 6245 之前，用以下逻辑替换原来的检查块:

```python
                    # ── 特殊交易对入场检查 ─────────────────────────────────────
                    allowed, block_reason = should_allow_auto_entry(pair, direction)
                    if not allowed:
                        _log(f"  🚫 {pair} 入场被阻止: {block_reason}")
                        cycle_result["skipped"] += 1
                        cycle_result["details"].append({"pair": pair, "success": False,
                            "reason": block_reason})
                        continue
```

---

## 7. 补丁汇总表

| 编号 | 严重度 | 位置 | 问题 | 修复类型 |
|------|--------|------|------|---------|
| P0-3-1 | P0-3 | line 5267 | stagger_delay负数 | Bugfix |
| P0-3-2 | P0-3 | line 6268-6272 | DCA清除止损冷却 | Bugfix |
| P0-3-3 | P1 | line 6245前 | DOGE冻结缺失 | 新增函数 |
| P0-3-4 | P1 | line 6245前 | SOL DCA暂停缺失 | 新增函数 |
| P0-3-5 | P2 | line 6245前 | 缺少统一入场检查 | 新增函数 |
