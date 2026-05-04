# 02_DCA_PAUSE_READ_LOGIC_PATCH.md

## dca_pause_rules 读取逻辑补丁

**草案文件** | **禁止直接写入实盘**

---

## 1. 问题定位

Stage A 证明：`dca_pause_rules` 在 `v65_autopilot.py` 中**零读取路径**。

即：可以往 overlay config 写 `dca_pause_rules: {SOL: {...}}`，但 DCA 补仓逻辑从未读取此字段，任何满足条件的 DCA 都会触发。

**涉及文件**: `bt_tools/v65_autopilot.py`
**涉及函数**: DCA 触发路径（多处）
**主接入点**:
- `v65_autopilot.py:6246` — 主循环 DCA 触发（`_run_trigger_audit_or_dca`）
- `v65_autopilot.py:4126` — 已有仓位转 DCA 路径

---

## 2. 新增函数

**插入位置**: `v65_autopilot.py` `is_pair_temporarily_frozen()` 函数之后（~1910行附近）

```python
def is_dca_paused(pair: str, direction: str, cfg: dict | None = None,
                   now_ts: float | None = None) -> tuple[bool, str]:
    """
    检查指定交易对方向是否暂停 DCA 新增仓位。

    读取 overlay config 中的 dca_pause_rules 字段。
    只阻断 DCA 新增仓位，不影响已有持仓、不影响止损/止盈风控。

    参数:
        pair:      交易对，如 "SOL/USDT:USDT"
        direction: 持仓方向 "LONG" / "SHORT"
        cfg:       overlay config 字典
        now_ts:    当前时间戳（秒），用于测试

    返回:
        (is_paused: bool, reason: str)
        reason 非空时表示暂停原因，为空时表示未暂停
    """
    import time
    now_ts = now_ts if now_ts is not None else time.time()

    # 无 cfg 或空 cfg → 不过滤
    if not cfg:
        return False, ""

    rules = cfg.get("dca_pause_rules")
    if not rules:
        return False, ""

    # 尝试多个 key 格式
    pair_base = pair.replace(":USDT", "")
    pair_std  = pair.replace("/USDT:USDT", "")
    pair_slash = pair.replace(":USDT", "/USDT")
    pair_short = pair_base + "/USDT"

    keys_to_try = [
        f"{pair}:{direction}",
        f"{pair.replace(':USDT','')}:{direction}",
        f"{pair_std}:{direction}",
        f"{pair_base}:{direction}",
        pair,
        pair_std,
        pair_base,
    ]

    for key in keys_to_try:
        rule = rules.get(key)
        if not isinstance(rule, dict):
            continue
        # 未启用 → 跳过
        if not rule.get("enabled", False):
            continue
        # 已过期
        until_ts = rule.get("until_ts")
        if until_ts is not None:
            try:
                if now_ts >= float(until_ts):
                    continue  # 已过期，跳过
            except (TypeError, ValueError):
                pass
        # 检查阻断标志
        if rule.get("block_new_dca", False):
            reason = str(rule.get("reason", "dca_pause_rules"))
            _log(f"[DCA-Pause] {pair} {direction} DCA 已暂停: {reason}")
            return True, reason

    return False, ""
```

---

## 3. 接入点

### 3.1 主循环 DCA 触发路径（主接入点）

**文件**: `bt_tools/v65_autopilot.py`
**函数**: `_run_trigger_audit_or_dca()`（约 line 6246）
**行号**: ~6254（`check_dca_trigger()` 返回后，`dca_triggered` 为 True 时）

```python
                    # 使用check_dca_trigger验证补仓条件
                    dca_triggered, dca_reason, target_layer = check_dca_trigger(
                        direction, entry_price, current_price,
                        fund_flow, fund_flow_strength, current_layer,
                        near_support, near_resistance,
                        volume_data=_get_volume_baseline(pair),
                        leverage=int(lev)
                    )

                    # ── Stage B 新增：DCA pause 检查（主路径）─────────────────
                    _dca_cfg = _get_overlay_config()
                    dca_paused, pause_reason = is_dca_paused(pair, direction, _dca_cfg)
                    if dca_paused:
                        _log(f"  🚫 {pair} DCA 暂停中: {pause_reason}，跳过本轮DCA")
                        cycle_result["skipped"] += 1
                        cycle_result["details"].append({
                            "pair": pair, "success": False,
                            "reason": f"DCA暂停: {pause_reason}"
                        })
                        continue
                    # ── DCA pause 检查结束 ──────────────────────────────────

                    if not dca_triggered:
                        _log(f"  🚫 {pair} DCA条件未触发: {dca_reason} (ROE: {roe:.1f}%)")
```

**原则**: 在 `dca_triggered` 为 True 时拦截，避免改变 `check_dca_trigger()` 的原始逻辑。

### 3.2 已有仓位转 DCA 路径（备用接入点）

**文件**: `bt_tools/v65_autopilot.py`
**函数**: `force_entry_autopilot()` 约 line 4126
**行号**: ~4132（`check_dca_trigger()` 返回后）

```python
                        trig, reason, target_layer = check_dca_trigger(
                            direction, entry_price, current_price,
                            fund_flow, fund_flow_str, current_layer, ns, nr,
                            volume_data=_get_volume_baseline(pair),
                            leverage=int(ex_dict.get("leverage", 10))
                        )
                        # ── Stage B 新增：DCA pause 检查（备用路径）──────────
                        _dca_cfg2 = _get_overlay_config()
                        dca_p2, pause_r2 = is_dca_paused(pair, direction, _dca_cfg2)
                        if dca_p2:
                            _log(f"  🚫 {pair} DCA 暂停中: {pause_r2}，已有仓位转DCA被阻止")
                            return {"success": False, "reason": f"DCA暂停: {pause_r2}"}
                        # ── DCA pause 检查结束 ──────────────────────────────

                        if trig:
```

---

## 4. 与 temporary_pair_freeze 的关系

| 字段 | 阻断范围 | 影响 |
|------|----------|------|
| `temporary_pair_freeze.block_auto_entry` | 阻断**首次入场** | 只阻止新开仓 |
| `temporary_pair_freeze.block_auto_dca` | 阻断**首次入场附带 DCA** | 只阻止新仓的初始 DCA |
| `dca_pause_rules.block_new_dca` | 阻断**已有仓位的 DCA 补仓** | 不影响首次入场 |

**结论**: 三者互补，`block_auto_dca` + `block_new_dca` 覆盖两种 DCA 场景。

---

## 5. PATCH.diff 片段

```diff
diff --git a/bt_tools/v65_autopilot.py b/bt_tools/v65_autopilot.py
--- a/bt_tools/v65_autopilot.py
+++ b/bt_tools/v65_autopilot.py
@@ -6253,6 +6253,17 @@ def _run_trigger_audit_or_dca(...):
                         leverage=int(lev)
                     )

+                    # ── Stage B 新增：DCA pause 检查（主路径）─────────────────
+                    _dca_cfg = _get_overlay_config()
+                    dca_paused, pause_reason = is_dca_paused(pair, direction, _dca_cfg)
+                    if dca_paused:
+                        _log(f"  🚫 {pair} DCA 暂停中: {pause_reason}，跳过本轮DCA")
+                        cycle_result["skipped"] += 1
+                        cycle_result["details"].append({
+                            "pair": pair, "success": False,
+                            "reason": f"DCA暂停: {pause_reason}"
+                        })
+                        continue
+                    # ── DCA pause 检查结束 ──────────────────────────────────
+
                     if not dca_triggered:
```

---

## 6. grep 验证命令（Stage B 必须执行）

```bash
# 确认函数已定义
grep -n "def is_dca_paused" ~/freqtrade_console/bt_tools/v65_autopilot.py

# 确认接入点已存在
grep -n "is_dca_paused\|dca_pause_rules" ~/freqtrade_console/bt_tools/v65_autopilot.py

# 确认不新增平仓调用（DCA 只阻断新增，不平仓）
grep -n "force_exit\|close_position" ~/freqtrade_console/bt_tools/v65_autopilot.py | grep -v "#.*force_exit\|#.*close"
```

---

## 7. 测试用例

```python
import time

# 测试1：未暂停 → False, ""
cfg1 = {"dca_pause_rules": {"SOL/USDT:USDT:LONG": {"enabled": False}}}
assert is_dca_paused("SOL/USDT:USDT", "LONG", cfg1) == (False, "")

# 测试2：已暂停且未过期 → True, "dca_full_layer_roe_negative"
cfg2 = {"dca_pause_rules": {"SOL/USDT:USDT": {
    "enabled": True,
    "reason": "dca_full_layer_roe_negative",
    "block_new_dca": True,
    "until_ts": time.time() + 86400
}}}
assert is_dca_paused("SOL/USDT:USDT", "LONG", cfg2) == (True, "dca_full_layer_roe_negative")

# 测试3：key 格式兼容（SOL:LONG）→ True
cfg3 = {"dca_pause_rules": {"SOL:LONG": {
    "enabled": True, "reason": "test", "block_new_dca": True
}}}
assert is_dca_paused("SOL/USDT:USDT:USDT", "LONG", cfg3) == (True, "test")

# 测试4：已过期 → False, ""
cfg4 = {"dca_pause_rules": {"SOL/USDT:USDT:LONG": {
    "enabled": True, "block_new_dca": True,
    "until_ts": time.time() - 1
}}}
assert is_dca_paused("SOL/USDT:USDT", "LONG", cfg4) == (False, "")

# 测试5：无 cfg → False, ""
assert is_dca_paused("SOL/USDT:USDT", "LONG", None) == (False, "")
```
