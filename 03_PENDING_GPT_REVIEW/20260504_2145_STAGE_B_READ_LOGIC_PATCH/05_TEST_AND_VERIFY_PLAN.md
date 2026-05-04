# 05_TEST_AND_VERIFY_PLAN.md

## Dry-run 测试与验证计划

**草案文件** | **禁止直接写入实盘**

---

## 1. 测试原则

Stage B 测试**不涉及任何实盘操作**：
- ❌ 不执行交易
- ❌ 不调用交易所 API
- ❌ 不重启机器人
- ❌ 不修改 12 个 bot overlay
- ✅ 只执行 py_compile、grep、JSON 验证
- ✅ 只记录 Shadow 模式日志

---

## 2. py_compile 验证

### 2.1 当前基线（补丁应用前）

```bash
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo "✅ 基线 py_compile OK"
```

### 2.2 补丁应用后（Stage C 执行）

```bash
# 应用补丁
cd ~/freqtrade_console
patch -p1 < PATCH.diff

# 验证
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo "✅ 补丁后 py_compile OK"
```

---

## 3. grep 读取路径验证

### 3.1 temporary_pair_freeze 读取路径

```bash
# 预期：至少 3 个匹配
# 1. 函数定义
# 2. 接入 check_entry_rules()
# 3. _get_overlay_config() 中读取

RESULT=$(grep -n "is_pair_temporarily_frozen\|temporary_pair_freeze" \
    ~/freqtrade_console/bt_tools/v65_autopilot.py)
echo "=== temporary_pair_freeze 读取路径验证 ==="
echo "$RESULT"
COUNT=$(echo "$RESULT" | grep -v "^$" | wc -l | tr -d ' ')
echo "匹配行数: $COUNT"
if [ "$COUNT" -ge 3 ]; then
    echo "✅ 读取路径存在（$COUNT 处）"
else
    echo "❌ 读取路径不足，需检查"
fi
```

### 3.2 dca_pause_rules 读取路径

```bash
RESULT=$(grep -n "is_dca_paused\|dca_pause_rules" \
    ~/freqtrade_console/bt_tools/v65_autopilot.py)
echo "=== dca_pause_rules 读取路径验证 ==="
echo "$RESULT"
COUNT=$(echo "$RESULT" | grep -v "^$" | wc -l | tr -d ' ')
echo "匹配行数: $COUNT"
if [ "$COUNT" -ge 3 ]; then
    echo "✅ 读取路径存在（$COUNT 处）"
else
    echo "❌ 读取路径不足，需检查"
fi
```

---

## 4. 函数单元测试

在 Python REPL 或测试文件中执行：

```python
import sys
sys.path.insert(0, '/Users/luxiangnan/freqtrade_console')
# 模拟 is_pair_temporarily_frozen 和 is_dca_paused 函数（复制函数体到测试文件）
# 运行以下测试用例

import time

def is_pair_temporarily_frozen(pair, cfg, now_ts=None):
    now_ts = now_ts or time.time()
    if not cfg: return False, ""
    freeze_rules = cfg.get("temporary_pair_freeze", {})
    for variant in [pair, pair.replace(":USDT", ""),
                    pair.replace("/USDT:USDT", ""), pair.replace("/USDT", "")]:
        rule = freeze_rules.get(variant)
        if not isinstance(rule, dict): continue
        if not rule.get("enabled", False): continue
        until_ts = rule.get("until_ts")
        if until_ts is not None:
            try:
                if now_ts >= float(until_ts): continue
            except: pass
        if rule.get("block_auto_entry", False):
            return True, str(rule.get("reason", "temporary_pair_freeze"))
    return False, ""

def is_dca_paused(pair, direction, cfg, now_ts=None):
    now_ts = now_ts or time.time()
    if not cfg: return False, ""
    rules = cfg.get("dca_pause_rules", {})
    pair_base = pair.replace(":USDT", "")
    keys = [f"{pair}:{direction}", f"{pair_base}:{direction}",
            pair, pair_base]
    for key in keys:
        rule = rules.get(key)
        if not isinstance(rule, dict): continue
        if not rule.get("enabled", False): continue
        until_ts = rule.get("until_ts")
        if until_ts is not None:
            try:
                if now_ts >= float(until_ts): continue
            except: pass
        if rule.get("block_new_dca", False):
            return True, str(rule.get("reason", "dca_pause_rules"))
    return False, ""

# ── 测试用例 ──────────────────────────────────────────────────
tests_passed = 0
tests_failed = 0

# Freeze 测试
test_cases = [
    (is_pair_temporarily_frozen, "DOGE/USDT:USDT", None, (False, ""), "无cfg"),
    (is_pair_temporarily_frozen, "DOGE/USDT:USDT", {"temporary_pair_freeze": {}}, (False, ""), "空freeze"),
    (is_pair_temporarily_frozen, "DOGE/USDT:USDT", {
        "temporary_pair_freeze": {"DOGE/USDT:USDT": {
            "enabled": True, "block_auto_entry": True, "reason": "test",
            "until_ts": time.time() + 86400}}}, (True, "test"), "有效冻结"),
    (is_pair_temporarily_frozen, "DOGE/USDT:USDT", {
        "temporary_pair_freeze": {"DOGE/USDT:USDT": {
            "enabled": False, "block_auto_entry": True}}}, (False, ""), "disabled"),
    (is_pair_temporarily_frozen, "DOGE/USDT:USDT", {
        "temporary_pair_freeze": {"DOGE/USDT:USDT": {
            "enabled": True, "block_auto_entry": True,
            "until_ts": time.time() - 1}}}, (False, ""), "已过期"),
    # DCA 测试
    (is_dca_paused, "SOL/USDT:USDT", "LONG", None, (False, ""), "无cfg"),
    (is_dca_paused, "SOL/USDT:USDT", "LONG", {"dca_pause_rules": {}}, (False, ""), "空rules"),
    (is_dca_paused, "SOL/USDT:USDT", "LONG", {
        "dca_pause_rules": {"SOL/USDT:USDT:LONG": {
            "enabled": True, "block_new_dca": True, "reason": "roe_neg",
            "until_ts": time.time() + 86400}}}, (True, "roe_neg"), "有效暂停"),
    (is_dca_paused, "SOL/USDT:USDT", "LONG", {
        "dca_pause_rules": {"SOL:LONG": {
            "enabled": True, "block_new_dca": True, "reason": "short_key"}}},
        (True, "short_key"), "短key格式"),
    (is_dca_paused, "SOL/USDT:USDT", "LONG", {
        "dca_pause_rules": {"SOL/USDT:USDT:LONG": {
            "enabled": True, "block_new_dca": True,
            "until_ts": time.time() - 1}}}, (False, ""), "DCA已过期"),
]

for tc in test_cases:
    if len(tc) == 5:
        fn, pair, cfg, expected, name = tc
        result = fn(pair, cfg)
    else:
        fn, pair, direction, cfg, expected, name = tc
        result = fn(pair, direction, cfg)
    status = "✅" if result == expected else "❌"
    print(f"{status} {name}: {result} == {expected}")
    if result == expected:
        tests_passed += 1
    else:
        tests_failed += 1

print(f"\n总计: {tests_passed} 通过, {tests_failed} 失败")
```

---

## 5. JSON Schema 验证

```bash
# 验证 9090 overlay JSON 语法
python3 -m json.tool ~/freqtrade/config_9090_overlay.json >/dev/null && echo "✅ 9090 JSON OK"

# 验证新增字段格式
python3 -c "
import json, sys
cfg = json.load(open('$HOME/freqtrade/config_9090_overlay.json'))

# 检查 temporary_pair_freeze 字段
freeze = cfg.get('temporary_pair_freeze', {})
for pair, rule in freeze.items():
    assert isinstance(rule, dict), f'{pair} rule 不是 dict'
    assert 'enabled' in rule, f'{pair} 缺少 enabled'
    assert 'reason' in rule, f'{pair} 缺少 reason'
    assert 'block_auto_entry' in rule, f'{pair} 缺少 block_auto_entry'
    print(f'✅ {pair}: enabled={rule[\"enabled\"]} reason={rule[\"reason\"]}')

# 检查 dca_pause_rules 字段
dca_rules = cfg.get('dca_pause_rules', {})
for key, rule in dca_rules.items():
    assert isinstance(rule, dict), f'{key} rule 不是 dict'
    assert 'enabled' in rule, f'{key} 缺少 enabled'
    assert 'reason' in rule, f'{key} 缺少 reason'
    assert 'block_new_dca' in rule, f'{key} 缺少 block_new_dca'
    print(f'✅ {key}: enabled={rule[\"enabled\"]} reason={rule[\"reason\"]}')

print(f'验证完成: {len(freeze)} freeze规则, {len(dca_rules)} DCA暂停规则')
"
```

---

## 6. Shadow 模式验证（Stage C 执行）

```bash
# 验证 Shadow 模式标志存在
grep -n "_SHADOW_MODE\|_FREEZE_SHADOW\|_DCA_PAUSE_SHADOW" \
    ~/freqtrade_console/bt_tools/v65_autopilot.py

# 模拟 Shadow 模式日志输出
# 在 Shadow 模式下，以下日志应出现（不执行实际阻断）：
# [Freeze] DOGE/USDT:USDT 被临时冻结: shadow_test_no_freeze
# DCA 暂停中: dca_pause_test
```

---

## 7. 测试日志记录

所有测试结果记录到 `TEST_LOG.md`。

---

## 8. 禁止执行清单

| 禁止项 | 确认 |
|--------|------|
| 不执行任何交易 | ⬜ |
| 不调用交易所 API | ⬜ |
| 不重启机器人 | ⬜ |
| 不修改 12 个 bot overlay | ⬜ |
| 不删除 whitelist 币对 | ⬜ |
| 不修改 `config_9090_overlay.json` | ⬜ |
