# DCA / 杠杆保护完整规则 — V6.5
**文件编号**: 08
**制定方**: 刑部代理
**生效日期**: 2026-05-04
**版本**: V1.0
**状态**: 待审批

---

## 1. 总则

本规则定义 DCA 最大层数、触发阈值、杠杆使用规范、止损冷却与DCA冷却的独立关系，以及满层后的禁止追加规则。

**核心原则**:
- DCA 是逆势补仓，必须有严格层数封顶
- 杠杆随DCA层数叠加，必须有上限
- 止损冷却与DCA触发完全独立，互不干扰
- 任何BUG修复不得削弱止损冷却的保护效力

---

## 2. DCA 层数与触发阈值确认

### 2.1 _DCA_MAX_LAYER 配置确认

**代码位置**: `v65_autopilot.py:92`
**配置值**: `_DCA_MAX_LAYER = 2`

```
层数定义:
  layer=0  → 首单（无DCA）
  layer=1  → 第1次DCA追加（允许）
  layer=2  → 第2次DCA追加（封顶，禁止继续追加）
  layer>2  → 禁止任何DCA追加
```

**结论**: `_DCA_MAX_LAYER=2` 确认正确，符合"最大补仓层数（封顶2次）"注释。

### 2.2 _DCA_TRIGGER_PCTS 配置确认

**代码位置**: `v65_autopilot.py:98`
**配置值**: `_DCA_TRIGGER_PCTS = [5.0, 15.0]`

| 层 | 触发阈值 | 含义 |
|----|---------|------|
| L1 | 5.0% 逆向波动 | 第1次DCA：入场价±5%触发 |
| L2 | 15.0% 逆向波动 | 第2次DCA：入场价±15%触发 |

**实际触发公式**（杠杆修正）:
```
l1_trigger = _BASE_EXIT_P2_PROFIT * m   # 对标P2，10x = 20%
l2_trigger = _BASE_EXIT_P3_PROFIT * m   # 对标P3，10x = 25%
```

其中 `m = leverage / 10`，即：
- 5x 杠杆：L1触发 = 基准×0.5，L2触发 = 基准×0.5
- 10x 杠杆：L1触发 = 基准×1.0，L2触发 = 基准×1.0
- 20x 杠杆：L1触发 = 基准×2.0，L2触发 = 基准×2.0

**结论**: `_DCA_TRIGGER_PCTS=[5.0, 15.0]` 确认正确。动态杠杆修正由 `_calc_dca_trigger_by_leverage()` 处理。

---

## 3. P0-3 BUG 修复：DCA 不清除止损冷却

### 3.1 BUG 描述

**位置**: `v65_autopilot.py:6269-6272`
**严重度**: P0-3（中）

**问题代码**:
```python
# 原BUG代码（必须删除）
with _stoploss_lock:
    if pair in _stoploss_state and _stoploss_state[pair].get("direction") == direction:
        del _stoploss_state[pair]    # ← BUG: 清除止损冷却
        _log(f"  🔓 {pair} DCA触发，清除止损冷却")
```

### 3.2 风险分析

止损冷却（`STOPLOSS_COOLDOWN_SEC`，默认4小时）是核心保护机制：
- 止损后4小时内禁止任何方向开仓
- 防止"越亏越加"的恶性循环
- DCA触发时清除冷却 = 绕过此保护

### 3.3 修复规则

**规则 3.1: DCA 不清除止损冷却**

```
DCA触发时，禁止执行以下操作：
  - del _stoploss_state[pair]
  - 任何主动删除止损冷却记录的行为

止损冷却检查在 DCA 触发前执行：
  - 如果当前 pair 处于止损冷却期，DCA 直接拦截（不触发）
  - 冷却检查逻辑保持不变（v65_autopilot.py:6274-6285）
```

**正确流程**:
```
止损触发
  → 写入 _stoploss_state[pair]
  → 止损冷却开始计时（4小时）

在冷却期内：
  → check_dca_trigger() 被调用
  → 止损冷却检查通过（发现冷却记录）
  → DCA 被拦截，reason = "stoploss_cooldown"
  → 记录 dca_blocked 到审计日志

冷却到期后：
  → DCA 可以正常触发
```

### 3.4 修复代码

```diff
- # ── BUG: DCA触发时清除止损冷却，避免刚触发的DCA被冷却阻止 ──
- with _stoploss_lock:
-     if pair in _stoploss_state and _stoploss_state[pair].get("direction") == direction:
-         del _stoploss_state[pair]
-         _log(f"  🔓 {pair} DCA触发，清除止损冷却")
+ # P0-3修复 2026-05-04: DCA不清除止损冷却
+ # 止损冷却是4小时保护窗，DCA追加会放大亏损，不应绕过
+ # 止损冷却检查在下方通用检查块（line 6274-6285）统一处理
```

---

## 4. P0-5 修复：stagger_delay 负数保护

### 4.1 BUG 描述

**位置**: `v65_autopilot.py:5267`
**严重度**: P0-5（低）

**问题代码**:
```python
# 原问题代码
stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
time.sleep(stagger_delay)   # 如果 LISTEN_PORT < 9000，负数导致 ValueError
```

### 4.2 风险场景

| 场景 | LISTEN_PORT | stagger_delay | 后果 |
|------|------------|---------------|------|
| 正常端口 9090 | 9090 | 4.5s | 正常 |
| 测试端口 8080 | 8080 | -6.0s | ValueError |
| 调试端口 8000 | 8000 | -50s | ValueError |

### 4.3 修复规则

**规则 4.1: stagger_delay 不得为负数**

```
stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))
```

**修复代码**:
```diff
- stagger_delay = ((_LISTEN_PORT - 9000) * 0.05)
+ # P0-5修复 2026-05-04: 防止负数导致 time.sleep 抛出 ValueError
+ stagger_delay = max(0, ((_LISTEN_PORT - 9000) * 0.05))
```

---

## 5. DCA 冷却与止损冷却独立规则

### 5.1 两种冷却的定义

| 冷却类型 | 变量名 | 默认时长 | 触发条件 | 作用 |
|---------|--------|---------|---------|------|
| 止损冷却 | `_stoploss_state` | 4小时 | 止损触发 | 禁止任何方向开仓 |
| DCA冷却 | `_dca_cooldown_state` | 建议30min | DCA执行后 | 禁止同pair短时间内再次DCA |

### 5.2 独立规则矩阵

| 场景 | 止损冷却 | DCA冷却 | DCA是否允许 |
|------|---------|---------|------------|
| 止损后4h内 | 生效中 | — | **禁止**（止损冷却优先） |
| DCA执行后30min内 | — | 生效中 | **禁止**（DCA冷却） |
| 止损后4h内又触发DCA信号 | 生效中 | — | **禁止**（不变） |
| DCA执行后立即止损 | — | — | 止损正常触发 |

### 5.3 检查顺序

```
check_dca_trigger(pair, direction)
  │
  ├─ [1] 层数检查: if current_layer >= _DCA_MAX_LAYER → 拦截
  │
  ├─ [2] DOGE冻结检查: is_doge_freeze_active(pair) → 拦截
  │
  ├─ [3] SOL DCA暂停检查: is_sol_dca_paused(pair) → 拦截
  │
  ├─ [4] 止损冷却检查（独立，不被DCA清除）
  │     if pair in _stoploss_state and 未到期 → 拦截
  │
  ├─ [5] DCA冷却检查（新增）
  │     if pair in _dca_cooldown_state and 未到期 → 拦截
  │
  └─ [6] 量比+S/R+资金流检查 → 通过后触发DCA
```

### 5.4 冷却状态管理

```python
# 止损冷却（已有，不修改）
_STOPSLOSS_COOLDOWN_SEC = 14400   # 4小时

# DCA冷却（新增）
_DCA_COOLDOWN_SEC = 1800          # 30分钟，建议值
_dca_cooldown_state: dict = {}    # {pair: {"time": timestamp, "layer": int}}

def check_dca_cooldown(pair: str) -> tuple[bool, int]:
    """
    检查DCA冷却状态
    Returns: (in_cooldown: bool, remaining_sec: int)
    """
    if pair not in _dca_cooldown_state:
        return False, 0
    info = _dca_cooldown_state[pair]
    elapsed = time.time() - info["time"]
    if elapsed >= _DCA_COOLDOWN_SEC:
        del _dca_cooldown_state[pair]
        return False, 0
    return True, int(_DCA_COOLDOWN_SEC - elapsed)

def set_dca_cooldown(pair: str, layer: int) -> None:
    """DCA执行后设置冷却"""
    _dca_cooldown_state[pair] = {"time": time.time(), "layer": layer}
```

---

## 6. 杠杆使用规范

### 6.1 杠杆上限确认

**规则 6.1: DCA 追加后总杠杆不得超过 5x**

```
入场杠杆限制:
  - 普通入场（无DCA）: 最高 10x（策略参数）
  - DCA L1后: 最高 5x
  - DCA L2后: 最高 5x（封顶）

注意：SOL SHORT / DOGE LONG 等高波动方向，建议入场杠杆 ≤ 5x
```

### 6.2 DCA 杠杆计算

**位置**: `v65_autopilot.py:3707` `_calc_dca_leverage()`

```python
def _calc_dca_leverage(base_leverage: float, current_layer: int, max_layer: int = 2) -> float:
    """
    计算DCA后的目标杠杆

    规则:
      - 每深一层 +0.5x 杠杆
      - 层数封顶 max_layer=2
      - 最终杠杆不得超过 5x

    Args:
        base_leverage: 入场时设定的杠杆
        current_layer: 当前层数（0=首单，1=L1，2=L2）

    Returns:
        建议杠杆值（不超过5x）
    """
    layer_boost = min(current_layer * 0.5, 1.0)   # 最多+1.0x（2层）
    dca_leverage = min(base_leverage + layer_boost, 5.0)
    return dca_leverage
```

### 6.3 杠杆警告规则

| 场景 | 警告级别 | 动作 |
|------|---------|------|
| DCA后总杠杆 > 5x | ERROR | 强制限制为5x，禁止继续追加 |
| DCA后总杠杆 > 3x | WARN | 日志警告，通知飞书 |
| DCA后总杠杆 = 5x 且在L1 | WARN | 提示L2将超出上限 |

---

## 7. DCA 满层后禁止继续加仓规则

### 7.1 规则定义

**规则 7.1: DCA 满层（layer >= _DCA_MAX_LAYER）后，禁止任何追加**

```
触发条件:
  current_layer >= _DCA_MAX_LAYER (即 current_layer >= 2)

禁止操作:
  - 任何自动 DCA 追加
  - 任何人工 force_entry（同pair）
  - 任何调高杠杆的操作

允许操作:
  - 止损触发（按出场规则）
  - 止盈触发（按出场规则）
  - 人工 force_exit（需要确认）
```

### 7.2 满层后风控规则

```python
# 满层后增强监控
if current_layer >= _DCA_MAX_LAYER:
    _log(f"[满层警告] {pair} DCA已达封顶({_DCA_MAX_LAYER}层)，禁止追加")

    # 通知飞书
    send_feishu_alert(
        f"⚠️ DCA满层警告\n"
        f"pair: {pair}\n"
        f"direction: {direction}\n"
        f"当前层数: {current_layer}\n"
        f"建议: 检查止损设置，等待反弹或人工出场"
    )

    # 记录审计日志
    write_risk_audit_log(
        action="dca_max_layer_reached",
        pair=pair,
        direction=direction,
        source="autopilot",
        reason=f"DCA已达封顶层数{_DCA_MAX_LAYER}",
    )

    # 禁止继续追加
    return False, f"已达最大补仓层数({_DCA_MAX_LAYER}层)"
```

### 7.3 满层后的止损加速规则

**规则 7.2: DCA 满层后，若 ROE ≤ -15%，自动收紧止损**

```
条件:
  current_layer >= _DCA_MAX_LAYER  AND
  roe_pct <= -15%

动作:
  - 止损触发阈值从标准值收紧50%
  - 立即写入止损单，不等待冷却
  - 通知飞书兵部
```

---

## 8. 配置参数汇总

### 8.1 全局常量

```python
# DCA 层数
_DCA_MAX_LAYER = 2              # 最大补仓层数（封顶2次）✅ 确认

# DCA 触发阈值
_DCA_TRIGGER_PCTS = [5.0, 15.0]  # 分层触发跌幅/涨幅（%）✅ 确认

# 止损冷却
_STOPSLOSS_COOLDOWN_SEC = 14400   # 4小时（不变）

# DCA 冷却（新增）
_DCA_COOLDOWN_SEC = 1800          # 30分钟（建议值）

# DOGE 冻结
_DOGE_FREEZE_DURATION = 86400     # 24小时

# SOL DCA 暂停
_SOL_DCA_PAUSE_DURATION = 1800    # 30分钟

# 杠杆上限
_MAX_LEVERAGE_WITH_DCA = 5.0      # DCA后最高5x
```

### 8.2 UI 可调参数

| 参数 | 代码位置 | 默认值 | 可调范围 | 说明 |
|------|---------|--------|---------|------|
| `dca_max_layer` | v65_autopilot.py:7870 | 2 | 1~20 | 最大DCA层数 |
| `dca_cooldown_sec` | 新增 | 1800 | 300~7200 | DCA冷却时长 |
| `doge_freeze_hours` | 新增 | 24 | 1~168 | DOGE冻结时长 |
| `sol_pause_minutes` | 新增 | 30 | 5~360 | SOL暂停时长 |

---

## 9. 审计日志要求

| action | 触发时机 | 记录字段 |
|--------|---------|---------|
| `dca_blocked` | DCA被阻止 | `block_reason: stoploss_cooldown / dca_cooldown / max_layer / doge_freeze / sol_pause` |
| `dca_executed` | DCA执行 | `dca_layer`, `roe_pct`, `leverage`, `pair` |
| `dca_max_layer_reached` | 满层 | `pair`, `direction`, `roe_pct` |
| `dca_leverage_capped` | 杠杆超限被限制 | `requested_leverage`, `actual_leverage` |
| `stoploss_cooldown_triggered` | 止损冷却开始 | `pair`, `direction`, `roe_pct` |
| `stoploss_cooldown_bypassed_attempt` | 试图绕过冷却（应无此日志，如有=发现BUG） | `pair` |

---

## 10. 规则冲突处理

| 冲突场景 | 处理优先级 |
|---------|----------|
| 止损冷却 & DCA冷却 同时生效 | 止损冷却优先（更严格） |
| DOGE冻结 & DCA冷却 | DOGE冻结优先（全局） |
| SOL暂停 & 止损冷却 | 两者独立，互不覆盖 |
| 满层 & 人工force_entry请求 | force_entry被满层规则拦截（ForceActionGuard） |

---

## 11. 规则版本

| 版本 | 日期 | 制定方 | 变更 |
|------|------|--------|------|
| V1.0 | 2026-05-04 | 刑部代理 | 初始版本，基于SOL ROE -27.9%根因分析 |
