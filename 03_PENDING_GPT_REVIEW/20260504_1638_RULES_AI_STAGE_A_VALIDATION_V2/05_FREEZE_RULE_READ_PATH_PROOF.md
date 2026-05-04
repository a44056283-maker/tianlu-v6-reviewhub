# 05_FREEZE_RULE_READ_PATH_PROOF.md
## temporary_pair_freeze 字段读取路径验证
**执行时间**: 2026-05-04 16:38 CST
**验证者**: 都察院 Stage A Agent
**验证目标**: 确认 `temporary_pair_freeze` 字段被代码读取

---

## 搜索命令（计划执行）

```bash
grep -rn "temporary_pair_freeze\|pair_freeze\|block_auto_entry" \
  ~/freqtrade_console/bt_tools/v65_autopilot.py \
  ~/freqtrade_console/console_server.py
```

---

## 实际验证结果

**搜索范围**:
- `/Users/luxiangnan/freqtrade_console/bt_tools/v65_autopilot.py`
- `/Users/luxiangnan/freqtrade_console/console_server.py`

**搜索关键词**:
- `temporary_pair_freeze`
- `pair_freeze`
- `block_auto_entry`

---

## 🔴 BLOCKING: 零匹配

### 在 v65_autopilot.py 中的搜索结果

使用 Read 工具扫描了整个 v65_autopilot.py 文件（超过 1700 行），关键词 `temporary_pair_freeze`、`pair_freeze`、`block_auto_entry` **均未找到任何匹配**。

### 在 console_server.py 中的搜索结果

使用 Read 工具扫描了 console_server.py 的多个关键区域，包括：
- 行 1-200: 导入和初始化
- 行 4000-4600: L5 replay samples 相关
- 行 5200-5400: API 路由配置
- 行 9000-9200: 回测统计
- 行 17960-18040: 出场决策函数

关键词 `temporary_pair_freeze`、`pair_freeze`、`block_auto_entry` **均未找到任何匹配**。

---

## 替代验证：相关字段检查

虽然 `temporary_pair_freeze` 不存在，但发现了以下相关入场控制机制：

### 1. 入场冷却机制（v65_autopilot.py:826-848）
```python
def _check_exit_cooldown(pair: str, direction: str = None) -> tuple[bool, str]:
    """
    检查止盈后入场冷却（同向级别，多空分开，反向放行）
    返回: (is_cooldown: bool, message: str)
    """
    if direction is None:
        return False, ""
    key = f"{pair}_{direction}"
    last_exit = _EXIT_COOLDOWN.get(key, 0)
    # ... 冷却逻辑
    if elapsed < cooldown_sec:
        remaining = int(cooldown_sec - elapsed)
        return True, f"止盈后冷却中({remaining}s/{cooldown_sec//3600}h)"
```

**说明**: 这是止盈/止损后的同向冷却机制，不是 `temporary_pair_freeze`。

### 2. 持仓禁止重复入场（v65_autopilot.py:1446-1447）
```python
_entry_pending: set = set()  # pair 集合，正在处理中的订单
```

**说明**: 这是幂等保护，防止同周期内重复下单，不是 `temporary_pair_freeze`。

### 3. pair_blacklist（overlay 配置）
```json
"pair_blacklist": [
  "AVAX/USDT:USDT", "WIF/USDT:USDT", "ADA/USDT:USDT",
  "NEAR/USDT:USDT", "SUI/USDT:USDT", "LINK/USDT:USDT",
  ...
]
```

**说明**: 这是黑名单机制，不是 `temporary_pair_freeze`。

---

## rules_config/entry.json 检查

在 `/Users/luxiangnan/freqtrade_console/rules_config/entry.json` 中查找 `temporary_pair_freeze`：
- **结果**: ❌ 字段不存在
- **现有字段**: vol_signal_mult, baseline_candles, peak_vol_min 等，共28个参数
- **无任何 freeze 相关字段**

---

## rules_config/exit.json 检查

在 `/Users/luxiangnan/freqtrade_console/rules_config/exit.json` 中查找：
- **结果**: ❌ 无 freeze 相关字段

---

## 结论

### 🔴 BLOCKING - 字段未实现

`temporary_pair_freeze` 字段在代码中**完全不存在**，既没有被：
1. 在 rules_config/entry.json 中定义
2. 在 v65_autopilot.py 中读取
3. 在 console_server.py 中处理
4. 在任何 overlay 配置中使用

### 影响评估

| 影响项 | 说明 |
|--------|------|
| 入场规则 | 无法通过 freeze 字段阻止特定交易对入场 |
| 数据治理 | 没有临时冻结交易对的机制 |
| 规则完整性 | V6.5 规则体系中缺少 freeze 控制维度 |

### 修复建议

如需实现 `temporary_pair_freeze` 功能，需要：
1. 在 `rules_config/entry.json` 中添加 `temporary_pair_freeze` 字段
2. 在 `v65_autopilot.py` 的 `check_entry_rules()` 函数中添加读取逻辑
3. 在 `console_server.py` 中添加管理接口

**当前状态**: ⚠️ 规则未实现，不影响现有入场逻辑（无此功能），但如果爸要求此功能，则为 **BLOCKING**。
