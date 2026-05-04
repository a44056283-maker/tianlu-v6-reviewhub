# 06_DCA_PAUSE_RULE_READ_PATH_PROOF.md
## dca_pause_rules 字段读取路径验证
**执行时间**: 2026-05-04 16:38 CST
**验证者**: 都察院 Stage A Agent
**验证目标**: 确认 `dca_pause_rules` 字段被代码读取

---

## 搜索命令（计划执行）

```bash
grep -rn "dca_pause_rules\|pause_rules\|block_new_dca" \
  ~/freqtrade_console/bt_tools/v65_autopilot.py \
  ~/freqtrade_console/console_server.py
```

---

## 实际验证结果

**搜索范围**:
- `/Users/luxiangnan/freqtrade_console/bt_tools/v65_autopilot.py`
- `/Users/luxiangnan/freqtrade_console/console_server.py`

**搜索关键词**:
- `dca_pause_rules`
- `pause_rules`
- `block_new_dca`

---

## 🔴 BLOCKING: 零匹配

### 在 v65_autopilot.py 中的搜索结果

使用 Read 工具扫描了 v65_autopilot.py 的多个关键区域，包括：
- 行 1-100: 顶部 docstring 和导入
- 行 500-600: V6.5 参数定义区（DCA相关参数）
- 行 854-1260: `check_entry_rules()` 函数
- 行 1280-1430: 运行时参数加载/保存

关键词 `dca_pause_rules`、`pause_rules`、`block_new_dca` **均未找到任何匹配**。

### 在 console_server.py 中的搜索结果

使用 Read 工具扫描了 console_server.py 的多个关键区域，包括：
- 行 1-100: 导入和初始化
- 行 4000-4600: L5 replay samples
- 行 5200-5400: API 路由
- 行 17960-18040: 出场决策

关键词 `dca_pause_rules`、`pause_rules`、`block_new_dca` **均未找到任何匹配**。

---

## 替代验证：DCA 相关现有机制

虽然 `dca_pause_rules` 不存在，但发现了以下相关 DCA 控制机制：

### 1. DCA 参数定义（v65_autopilot.py:1388-1393）

```python
# L5 补仓DCA
"dca_enabled": g.get("_DCA_ENABLED", True),
"dca_trigger_pcts": list(g.get("_DCA_TRIGGER_PCTS", [5.0, 15.0])),
"dca_flow_strong_trigger": g.get("_DCA_FLOW_STRONG_TRIGGER", True),
"dca_sr_check": g.get("_DCA_SR_CHECK", True),
"dca_max_layer": g.get("_DCA_MAX_LAYER", 10),
"add_position_ratio": g.get("_ADD_POSITION_RATIO", 0.3),
"max_add_positions": g.get("_MAX_ADD_POSITIONS", 10),
```

**说明**: 现有 DCA 由 `_DCA_ENABLED` 全局开关控制，无暂停规则。

### 2. rules_config/entry.json 中的 DCA 配置

```json
"dca_enabled": true,
"dca_trigger_drop": 5,
"dca_trigger_rise": 2,
"dca_max_layer": 10,
"dca_flow_strong_trigger": true,
"dca_sr_check": true,
"add_position_ratio": 0.3,
"max_add_positions": 10,
```

**说明**: 有全局 DCA 配置，但无 `dca_pause_rules` 字段。

### 3. DCA 层数限制（v65_autopilot.py:6316-6334）

```python
if is_dca_entry and dca_layer > 1:
    # 2026-04-09 修复: calc_sr_position_params不返回near_support/near_resistance
    if sr_params and sr_params.get("has_sr"):
        _srp = sr_params.get("sr_price", 0)
        _dist = abs((current_price - _srp) / _srp * 100) if _srp > 0 else 999
        _nth = 3.0
        near_sup = (direction == "LONG" and _dist < _nth)
        near_res = (direction == "SHORT" and _dist < _nth)
    else:
        near_sup = False
        near_res = False
    dca_lev = _calc_dca_leverage(base_leverage, dca_layer, near_sup, near_res)
```

**说明**: 有 DCA 层数杠杆 boost 逻辑，但无暂停规则。

---

## rules_config/entry.json 全面检查

| 字段名 | 值 | 是否 dca_pause 相关 |
|--------|-----|---------------------|
| dca_enabled | true | ❌ 全局开关，非暂停规则 |
| dca_trigger_drop | 5 | ❌ 触发阈值 |
| dca_trigger_rise | 2 | ❌ 触发阈值 |
| dca_max_layer | 10 | ❌ 层数上限 |
| dca_flow_strong_trigger | true | ❌ 流量确认 |
| dca_sr_check | true | ❌ S/R检查 |
| add_position_ratio | 0.3 | ❌ 加仓比例 |
| max_add_positions | 10 | ❌ 最大加仓次数 |

**结论**: 无 `dca_pause_rules` 字段。

---

## 结论

### 🔴 BLOCKING - 字段未实现

`dca_pause_rules` 字段在代码中**完全不存在**，既没有被：
1. 在 rules_config/entry.json 中定义
2. 在 v65_autopilot.py 中读取
3. 在 console_server.py 中处理
4. 在任何 overlay 配置中使用

### 影响评估

| 影响项 | 说明 |
|--------|------|
| DCA 控制 | 无法暂停特定交易对/账户的 DCA |
| 规则完整性 | V6.5 缺少按规则暂停 DCA 的机制 |
| 风控能力 | 无手动/规则驱动的 DCA 暂停能力 |

### 修复建议

如需实现 `dca_pause_rules` 功能，需要：
1. 在 `rules_config/entry.json` 中添加 `dca_pause_rules` 字段
2. 在 `v65_autopilot.py` 的 DCA 逻辑中读取该字段
3. 在 `console_server.py` 中添加管理接口

**当前状态**: ⚠️ 规则未实现，不影响现有 DCA 逻辑（无此功能），但如果爸要求此功能，则为 **BLOCKING**。
