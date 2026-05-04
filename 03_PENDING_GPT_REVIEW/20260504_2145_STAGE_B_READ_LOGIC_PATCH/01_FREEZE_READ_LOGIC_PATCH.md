# 01_FREEZE_READ_LOGIC_PATCH.md

## temporary_pair_freeze 读取逻辑补丁

**草案文件** | **禁止直接写入实盘**

---

## 1. 问题定位

Stage A 证明：`temporary_pair_freeze` 在 `v65_autopilot.py` 中**零读取路径**。

即：可以往 overlay config 写 `temporary_pair_freeze: {DOGE: {...}}`，但代码永远不读取这个字段，入场决策完全不受影响。

**涉及文件**: `bt_tools/v65_autopilot.py`
**涉及函数**: `check_entry_rules()` (line 854-1263)

---

## 2. 新增函数

**插入位置**: `v65_autopilot.py` 第 883 行之后（止盈冷却检查之后）

```python
def is_pair_temporarily_frozen(pair: str, cfg: dict | None = None,
                                 now_ts: float | None = None) -> tuple[bool, str]:
    """
    检查交易对是否被临时冻结。

    读取 overlay config 中的 temporary_pair_freeze 字段。
    仅阻断自动驾驶入场，不影响人工操作、不平仓、不影响已有仓位。

    参数:
        pair:      交易对，如 "DOGE/USDT:USDT"
        cfg:       overlay config 字典（从 config_XXXX_overlay.json 读取）
        now_ts:    当前时间戳（秒），用于测试

    返回:
        (is_frozen: bool, reason: str)
        reason 非空时表示冻结原因，为空时表示未冻结
    """
    import time
    now_ts = now_ts if now_ts is not None else time.time()

    # 无 cfg 或空 cfg → 不过滤
    if not cfg:
        return False, ""

    freeze_rules = cfg.get("temporary_pair_freeze")
    if not freeze_rules:
        return False, ""

    # 尝试多个 key 格式：原始、去掉 :USDT 后缀
    pair_variants = [pair, pair.replace(":USDT", ""),
                     pair.replace("/USDT:USDT", ""),
                     pair.replace("/USDT", "")]

    for variant in pair_variants:
        rule = freeze_rules.get(variant)
        if not isinstance(rule, dict):
            continue
        # 未启用 → 跳过
        if not rule.get("enabled", False):
            continue
        # 已过期（until_ts 早于当前时间）→ 解除冻结
        until_ts = rule.get("until_ts")
        if until_ts is not None:
            try:
                if now_ts >= float(until_ts):
                    continue  # 已过期，跳过此规则
            except (TypeError, ValueError):
                pass
        # 检查阻断标志
        if rule.get("block_auto_entry", False):
            reason = str(rule.get("reason", "temporary_pair_freeze"))
            _log(f"[Freeze] {pair} 被临时冻结: {reason}")
            return True, reason

    return False, ""
```

---

## 3. 接入点

**文件**: `bt_tools/v65_autopilot.py`
**函数**: `check_entry_rules()`
**行号**: ~891（在止盈冷却检查之后，L1 量比检查之前）

```python
    # ── 止盈后入场冷却检查（V6.5.1新增）───────────────────────────
    cooldown_msg = ""
    in_cooldown, cooldown_msg = _check_exit_cooldown(pair, direction)
    if in_cooldown:
        can_entry = False
        reasons.append(f"🚫 入场拦截【止盈冷却】{cooldown_msg}")
        details["l1_rejected"] = True
    # ── 止盈冷却检查结束 ─────────────────────────────────────────

    # ── Stage B 新增：temporary_pair_freeze 读取检查 ─────────────
    # 从 overlay config 读取 pair 冻结状态
    _freeze_cfg = _get_overlay_config()  # 新增：读取 overlay 的辅助函数
    frozen, freeze_reason = is_pair_temporarily_frozen(pair, _freeze_cfg)
    if frozen:
        can_entry = False
        reasons.append(f"🚫 入场拦截【临时冻结】{freeze_reason}")
        details["l1_rejected"] = True
    # ── temporary_pair_freeze 检查结束 ──────────────────────────

    # ── 天眼AI自学习：动态L1量比阈值 ─────────────────────────────
```

**接入原则**:
- 只阻断自动驾驶 `can_entry = False`
- 不触发平仓、不影响已有仓位
- 不删除 whitelist 中的交易对（只阻断自动驾驶路径）
- 冻结原因写入 `details["l1_rejected"]` 供监控展示

---

## 4. 辅助函数 `_get_overlay_config()`

需要新增一个辅助函数来读取当前 bot 对应的 overlay config：

**插入位置**: 紧邻 `is_pair_temporarily_frozen()` 函数定义之前

```python
_overlay_config_cache: dict | None = None
_overlay_config_ts: float = 0.0
_OVERLAY_CONFIG_CACHE_TTL: float = 60.0  # 缓存60秒，避免频繁读文件

def _get_overlay_config() -> dict:
    """
    读取当前 bot 对应的 overlay config。
    缓存在 _overlay_config_cache 中，TTL 60秒。
    """
    import time, json as _json, os as _os
    global _overlay_config_cache, _overlay_config_ts

    now = time.time()
    if _overlay_config_cache is not None and (now - _overlay_config_ts) < _OVERLAY_CONFIG_CACHE_TTL:
        return _overlay_config_cache

    # 获取当前 bot 配置文件路径（端口感知）
    mode = _this_mode_exchange()
    paths = _APIKEY_CONFIG_PATHS.get(mode, _APIKEY_CONFIG_PATHS.get("gate_9090", []))
    for raw_path in paths:
        path = _os.path.expanduser(raw_path)
        if _os.path.exists(path):
            try:
                with open(path) as f:
                    cfg = _json.load(f)
                _overlay_config_cache = cfg
                _overlay_config_ts = now
                return cfg
            except Exception:
                pass
    return {}
```

---

## 5. PATCH.diff 片段

```diff
diff --git a/bt_tools/v65_autopilot.py b/bt_tools/v65_autopilot.py
--- a/bt_tools/v65_autopilot.py
+++ b/bt_tools/v65_autopilot.py
@@ -891,6 +891,78 @@ def check_entry_rules(pair: str, direction: str, score: float,
     # ── 止盈冷却检查结束 ─────────────────────────────────────────

+    # ── Stage B 新增：temporary_pair_freeze 读取检查 ─────────────
+    _freeze_cfg = _get_overlay_config()
+    frozen, freeze_reason = is_pair_temporarily_frozen(pair, _freeze_cfg)
+    if frozen:
+        can_entry = False
+        reasons.append(f"🚫 入场拦截【临时冻结】{freeze_reason}")
+        details["l1_rejected"] = True
+    # ── temporary_pair_freeze 检查结束 ──────────────────────────
+
     # ── 天眼AI自学习：动态L1量比阈值 ─────────────────────────────
```

---

## 6. 测试用例

```python
# 测试1：未冻结的币对 → False, ""
cfg1 = {"temporary_pair_freeze": {"DOGE/USDT:USDT": {"enabled": False}}}
assert is_pair_temporarily_frozen("DOGE/USDT:USDT", cfg1) == (False, "")

# 测试2：已冻结且未过期 → True, "batch_stoploss_loop"
import time
cfg2 = {"temporary_pair_freeze": {"DOGE/USDT:USDT": {
    "enabled": True,
    "reason": "batch_stoploss_loop",
    "block_auto_entry": True,
    "until_ts": time.time() + 86400  # 24小时后过期
}}}
assert is_pair_temporarily_frozen("DOGE/USDT:USDT", cfg2) == (True, "batch_stoploss_loop")

# 测试3：已过期 → False, ""
cfg3 = {"temporary_pair_freeze": {"DOGE/USDT:USDT": {
    "enabled": True,
    "block_auto_entry": True,
    "until_ts": time.time() - 1  # 已过期
}}}
assert is_pair_temporarily_frozen("DOGE/USDT:USDT", cfg3) == (False, "")

# 测试4：无 cfg → False, ""
assert is_pair_temporarily_frozen("DOGE/USDT:USDT", None) == (False, "")
```

---

## 7. grep 验证命令（Stage B 必须执行）

```bash
# 确认函数已定义
grep -n "def is_pair_temporarily_frozen" ~/freqtrade_console/bt_tools/v65_autopilot.py

# 确认接入点已存在
grep -n "is_pair_temporarily_frozen\|temporary_pair_freeze" ~/freqtrade_console/bt_tools/v65_autopilot.py

# 确认不修改已有仓位逻辑
grep -n "force_exit\|close_position\|cancel_order" ~/freqtrade_console/bt_tools/v65_autopilot.py | wc -l
# 增量应为 0（不新增任何平仓调用）
```
