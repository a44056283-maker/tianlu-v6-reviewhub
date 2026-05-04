# DCA风险审计报告
**审计时间**: 2026-05-04 14:30
**审计人**: 刑部代理
**文件**: v65_autopilot.py

---

## 1. dca_max_layer 实际值

**代码位置**: `/Users/luxiangnan/freqtrade_console/bt_tools/v65_autopilot.py:92`

```python
_DCA_MAX_LAYER = 2              # 最大补仓层数（封顶2次）
```

**运行时默认值**: 2（层）
**UI可调范围**: 1 ~ 20 (`bt_tools/v65_autopilot.py:7870`)

---

## 2. "封顶2次"注释对应的代码位置

| 注释位置 | 代码 | 说明 |
|---------|------|------|
| `v65_autopilot.py:92` | `_DCA_MAX_LAYER = 2  # 最大补仓层数（封顶2次）` | 全局常量定义 |
| `v65_autopilot.py:1392` | `"dca_max_layer": g.get("_DCA_MAX_LAYER", 10)` | 状态上报 |
| `v65_autopilot.py:1870` | `if current_layer >= _DCA_MAX_LAYER: return False, "已达最大补仓层数"` | 触发检查逻辑 |
| `v65_autopilot.py:7167-7169` | `_DCA_MAX_LAYER = int(params["dca_max_layer"])` | 动态参数更新 |
| `v65_autopilot.py:7320` | `"dca_max_layer": _DCA_MAX_LAYER` | 状态获取 |

**核心检查函数**: `check_dca_trigger()` (v65_autopilot.py:1843)

---

## 3. DCA层数与代码是否冲突

### 层数语义定义

| 层级 | 含义 | 触发条件 |
|------|------|---------|
| layer=0 | 首单（无DCA） | 入场信号 |
| layer=1 | 第1次DCA补仓 | 逆势跌幅≥阈值 + S/R位置 + 资金流同向 |
| layer=2 | 第2次DCA补仓 | 同上，layer_idx=2 |

### 关键冲突检查

**冲突点**: 代码中同时存在两套DCA配置：

1. **旧配置** (`v65_autopilot.py:93-95`):
   ```python
   _DCA_RATIOS = [0.10, 0.20]       # 各层仓位比例（第1次10%，第2次20%）
   _ADD_POSITION_RATIO = 0.3        # DCA加仓比例 30%
   _MAX_ADD_POSITIONS = 10          # 最大加仓层数
   ```

2. **新配置** (`v65_autopilot.py:92`):
   ```python
   _DCA_MAX_LAYER = 2               # 最大补仓层数（封顶2次）
   ```

**结论**: 存在配置冲突。
- `_MAX_ADD_POSITIONS = 10` 与 `_DCA_MAX_LAYER = 2` 不一致
- `_DCA_RATIOS` 定义了2层比例，但逻辑中从未被引用
- 实际使用的是 `check_dca_trigger()` 中的动态阈值

### 动态阈值计算 (`_calc_dca_trigger_by_leverage`):
```python
l1_trigger = _BASE_EXIT_P2_PROFIT * m   # 对标P2，10x=20%
l2_trigger = _BASE_EXIT_P3_PROFIT * m   # 对标P3，10x=25%
```
触发涨幅 = 基准% × (杠杆/10)

---

## 4. stagger_delay 配置

**代码位置**: `v65_autopilot.py:5267`

```python
stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
time.sleep(stagger_delay)
```

| 端口 | 延迟（秒） |
|------|-----------|
| 9090 | 4.5s |
| 9091 | 4.55s |
| 9092 | 4.6s |
| 9093 | 4.65s |
| ... | ... |
| 9097 | 4.85s |

**用途**: 各bot错峰启动，避免同时请求K线触发交易所Rate Limit
**是否合理**: 合理（仅用于启动错峰，不影响DCA决策）

---

## 5. DCA是否在放大错误方向风险（亏损时加仓）

### DCA触发条件分析

`check_dca_trigger()` 包含三重验证：

1. **量基线检查**: 量比必须 ≥ `_VOL_SIGNAL_MULT`（通常2.5x）
2. **S/R位置检查**: 必须接近支撑位（多单）或压力位（空单）
3. **资金流检查**: 资金流必须与持仓方向同向

### 核心风险点

| 风险场景 | 代码保护 | 评估 |
|---------|---------|------|
| 逆势加仓接飞刀 | ✅ S/R位置+资金流同向要求 | 已保护 |
| 层数无限增长 | ✅ `_DCA_MAX_LAYER=2` 封顶 | 已保护 |
| 杠杆叠加放大风险 | ⚠️ `_calc_dca_leverage()` 每深一层+0.5x | **需关注** |
| DCA触发后止损冷却被清除 | ⚠️ `v65_autopilot.py:6269-6272` | **高风险** |

### 关键风险代码

```python
# v65_autopilot.py:6269-6272
with _stoploss_lock:
    if pair in _stoploss_state and _stoploss_state[pair].get("direction") == direction:
        del _stoploss_state[pair]
        _log(f"  🔓 {pair} DCA触发，清除止损冷却")
```

**风险说明**: DCA触发时会清除止损冷却记录，允许立即加仓。这在连续止损场景下可能导致"越亏越加"的恶性循环。

---

## 6. 是否建议暂停自动DCA

### 审计结论：**建议审查，不建议直接暂停**

#### 支持继续运行的理由
- S/R位置 + 资金流双重保护
- 层数封顶2次
- 量比基线要求

#### 建议整改项
1. **【高优先级】** 修复止损冷却清除逻辑（v65_autopilot.py:6269-6272）
   - DCA触发不应清除止损冷却，应叠加判断
2. **【中优先级】** 清理废弃配置（`_MAX_ADD_POSITIONS=10`、`_DCA_RATIOS`）
3. **【低优先级】** 限制DCA杠杆Boost上限（当前layer_boost最高3.0x）
4. **【建议】** 增加DCA连续触发次数限制（防止同一仓位多次DCA）

---

## 附录：DCA关键代码路径

```
check_dca_trigger()       # v65_autopilot.py:1843
  └─ layer检查            # v65_autopilot.py:1870
  └─ 量基线检查           # v65_autopilot.py:1874-1878
  └─ 动态阈值计算         # v65_autopilot.py:1830-1840
  └─ S/R位置检查          # v65_autopilot.py:1895-1912
  └─ 资金流检查           # v65_autopilot.py:1914-1923

DCA执行                   # v65_autopilot.py:6250-6275
  └─ 更新dca_counts       # v65_autopilot.py:6264
  └─ 清除止损冷却         # v65_autopilot.py:6269-6272 ⚠️
  └─ 计算DCA杠杆          # v65_autopilot.py:6319-6332
    └─ _calc_dca_leverage() # v65_autopilot.py:3707
```
