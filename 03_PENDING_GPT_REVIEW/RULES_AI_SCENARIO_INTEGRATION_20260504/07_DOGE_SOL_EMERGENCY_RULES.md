# DOGE / SOL 紧急止血规则 — V6.5
**文件编号**: 07
**制定方**: 刑部代理
**生效日期**: 2026-05-04
**版本**: V1.0
**状态**: 待审批

---

## 1. 总则

本规则定义 DOGE / SOL 两个特殊交易对在异常市场条件下的紧急止血机制，包括自动触发条件、人工触发权限、冻结/暂停解除条件，以及配置JSON格式。

**核心原则**:
- DOGE 问题由交易所API/链上延迟引发，需全局冻结所有DOGE交易
- SOL 问题由VPS延迟/市场波动引发，需暂停SOL的DCA追加，不影响已开仓位
- 两种机制互相独立，互不干扰
- 冻结/暂停状态存储于进程内存，不持久化，重启后自动清除

---

## 2. DOGE 批量止损根因分析

### 2.1 事件回顾

2026-05-04 DOGE_USDT 出现批量止损，多个bot同时在短时间内触发止损单。

### 2.2 根因定位

| 因素 | 分析 |
|------|------|
| 交易所API | Gate.io DOGE市场偶发性延迟，订单簿深度不足 |
| 链上确认 | DOGE网络在高峰时段确认慢，部分止损单延迟成交 |
| 天禄DCA策略 | DOGE波动性高，量比信号频繁触发，导致连续补仓 |
| 风控缺口 | 无全局DOGE冻结机制，止损后4h冷却可被其他端口复用 |

### 2.3 风险路径

```
DOGE突发下跌
  → DCA量比信号触发（第1层）
  → 补仓后继续下跌
  → 触发止损
  → 止损后4h冷却
  → 冷却期内DOGE反弹
  → 错过反弹且无法入场（冷却保护正常）
  或者
  → 止损后立即被其他端口DCA追加（冷却被清除BUG）
  → 越亏越加
```

### 2.4 结论

DOGE问题本质是**交易所侧流动性不足 + 链上延迟**，天禄需在检测到此类问题时**全局冻结DOGE**，停止一切自动开仓和DCA行为。

---

## 3. DOGE 冻结规则（temporary_pair_freeze）

### 3.1 字段定义

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `temporary_pair_freeze` | dict | `{}` | 交易对临时冻结字典 |
| `temporary_pair_freeze.{pair}` | float | — | 冻结到期Unix时间戳（秒），None=未冻结 |
| `freeze_duration_sec` | int | 86400 (24h) | 默认冻结时长 |
| `freeze_reason` | str | `""` | 冻结原因（人工填写） |
| `freeze_initiator` | str | `""` | 冻结发起人（manual/auto/system） |

### 3.2 函数规范

```python
# 位置: v65_autopilot.py 或专用 freeze_manager.py

_DOGE_FREEZE_UNTIL: float | None = None   # Unix时间戳，None=未冻结
_DOGE_FREEZE_DURATION = 86400             # 默认24小时（秒）

def is_doge_freeze_active(pair: str) -> bool:
    """
    检查pair是否处于DOGE临时冻结状态
    Returns: True=冻结中，False=正常
    """
    if not pair.upper().startswith("DOGE"):
        return False
    if _DOGE_FREEZE_UNTIL is None:
        return False
    if time.time() > _DOGE_FREEZE_UNTIL:
        global _DOGE_FREEZE_UNTIL
        _DOGE_FREEZE_UNTIL = None   # 已过期，自动清除
        return False
    return True

def set_doge_freeze(duration_sec: int | None = None, reason: str = "", initiator: str = "manual") -> dict:
    """
    设置DOGE全局冻结

    Args:
        duration_sec: 冻结秒数
                      86400  = 24小时（标准值）
                      None   = 清除冻结（解除）
        reason: 冻结原因（记录到审计日志）
        initiator: 触发来源（manual/auto/system）

    Returns:
        {"success": True, "freeze_until": timestamp, "remaining_sec": N}
    """
    global _DOGE_FREEZE_UNTIL
    now = time.time()

    if duration_sec is None:
        _DOGE_FREEZE_UNTIL = None
        _log(f"[DOGE] 冻结已解除 (by {initiator})")
        return {"success": True, "freeze_until": None, "remaining_sec": 0}

    _DOGE_FREEZE_UNTIL = now + duration_sec
    _log(f"[DOGE] 冻结已设置: {duration_sec}秒 ({duration_sec//3600}h), 原因: {reason}")
    write_risk_audit_log(
        action="doge_freeze_set",
        source=initiator,
        reason=reason,
        extra={"duration_sec": duration_sec, "freeze_until": _DOGE_FREEZE_UNTIL}
    )
    return {"success": True, "freeze_until": _DOGE_FREEZE_UNTIL, "remaining_sec": duration_sec}

def get_doge_freeze_remaining() -> int:
    """返回DOGE冻结剩余秒数，0=未冻结"""
    if _DOGE_FREEZE_UNTIL is None:
        return 0
    remaining = int(_DOGE_FREEZE_UNTIL - time.time())
    return max(0, remaining)
```

### 3.3 触发条件

#### 自动触发（AUTO）

满足以下任一条件，自动触发DOGE冻结：

| 条件 | 阈值 | 说明 |
|------|------|------|
| DOGE止损触发次数 | ≥3次 / 1小时内 | 批量止损信号 |
| DOGE订单失败率 | ≥50% / 10笔内 | API不稳定信号 |
| DOGE止损后ROE | ≤-15% 单笔 | 异常亏损信号 |

自动触发写入审计日志 `action: "doge_freeze_auto_triggered"`，并推送飞书通知。

#### 人工触发（MANUAL）

- 权限：爸（使用者）或具备 ADMIN 角色的接口
- 触发方式：调用 `set_doge_freeze(duration_sec=86400, reason="...", initiator="manual")`
- API路由：`POST /api/admin/doge_freeze`

### 3.4 解除条件

| 类型 | 条件 | 说明 |
|------|------|------|
| 超时自动解除 | 到达 `_DOGE_FREEZE_UNTIL` 时间戳 | 自动清除，无需人工操作 |
| 人工解除 | 爸调用 `set_doge_freeze(None)` | 立即解除，写入审计日志 |
| 重新冻结 | 冻结到期前再次满足触发条件 | 重新计时 |

### 3.5 DCA入口拦截

在所有DCA触发路径入口添加检查：

```python
# 伪代码（插入 check_dca_trigger() 之前）
if is_doge_freeze_active(pair):
    _log(f"  🚫 {pair} DOGE临时冻结中，禁止DCA")
    cycle_result["skipped"] += 1
    cycle_result["details"].append({"pair": pair, "reason": "DOGE_temporary_freeze"})
    continue
```

---

## 4. SOL DCA 满层根因分析

### 4.1 事件回顾

SOL_USDT SHORT 仓位发生 ROE -27.9% 的极端亏损，核心问题是 DCA 追加到了满层（layer=2），但价格继续朝着不利方向移动，导致亏损远超预期。

### 4.2 根因定位

| 因素 | 分析 |
|------|------|
| DCA满层机制 | `_DCA_MAX_LAYER=2` 封顶2次，但满层后仍有止损保护 |
| 止损冷却清除BUG | `v65_autopilot.py:6269-6272` DCA触发时清除止损冷却 | P0-3 高风险 |
| 杠杆叠加 | 每层DCA +0.5x杠杆，layer=2时实际杠杆已放大 |
| VPS延迟 | SOL波动剧烈，VPS处理延迟导致量比信号失真 |
| 出场规则 | V6.5出场规则未覆盖"满层后继续下跌"场景 |

### 4.3 风险路径

```
SOL下跌信号
  → DCA L1触发（5%逆向波动）
  → 继续下跌
  → DCA L2触发（15%逆向波动，已满层）
  → 止损冷却被DCA触发时清除（BUG）
  → 止损触发（冷却已清除，立即生效）
  → 或继续持有等待反弹
  → ROE -27.9%（杠杆+方向+波动性三重叠加）
```

### 4.4 结论

SOL问题的本质是：
1. **杠杆叠加**：满层DCA后实际杠杆过高
2. **止损冷却被清除BUG**：导致止损保护失效
3. **无SOL暂停机制**：VPS延迟期间无法主动暂停SOL DCA

---

## 5. SOL DCA 暂停规则（dca_pause_rules）

### 5.1 字段定义

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `dca_pause_rules` | dict | `{}` | DCA暂停规则字典 |
| `dca_pause_rules.{pair}` | float | — | 暂停到期Unix时间戳（秒），None=未暂停 |
| `pause_duration_sec` | int | 1800 (30min) | 默认暂停时长 |
| `pause_reason` | str | `""` | 暂停原因 |
| `pause_initiator` | str | `""` | 暂停发起人 |
| `pause_affects` | list | `["dca"]` | 暂停影响的操作类型（仅DCA） |

> **注意**：SOL DCA暂停**不影响已有持仓**，仅阻止新的DCA追加。已有持仓的止损、风控出场规则照常生效。

### 5.2 函数规范

```python
# 位置: v65_autopilot.py 或专用 pause_manager.py

_SOL_DCA_PAUSE_UNTIL: float | None = None   # Unix时间戳，None=未暂停
_SOL_DCA_PAUSE_DURATION = 1800              # 默认30分钟（秒）

def is_sol_dca_paused(pair: str, direction: str = "") -> bool:
    """
    检查SOL交易对的DCA是否被暂停
    注意：暂停仅影响DCA追加，不影响普通入场或出场

    Args:
        pair: 交易对，如 "SOL_USDT"
        direction: 持仓方向（可选，用于日志）

    Returns: True=暂停中，False=正常
    """
    if not pair.upper().startswith("SOL"):
        return False
    if _SOL_DCA_PAUSE_UNTIL is None:
        return False
    if time.time() > _SOL_DCA_PAUSE_UNTIL:
        global _SOL_DCA_PAUSE_UNTIL
        _SOL_DCA_PAUSE_UNTIL = None   # 已过期，自动清除
        return False
    return True

def set_sol_dca_pause(duration_sec: int | None = None, reason: str = "", initiator: str = "manual") -> dict:
    """
    设置SOL DCA暂停

    Args:
        duration_sec: 暂停秒数
                      1800  = 30分钟（标准值）
                      3600  = 1小时（加强）
                      None  = 清除暂停（解除）
        reason: 暂停原因（记录到审计日志）
        initiator: 触发来源（manual/auto/system）

    Returns:
        {"success": True, "pause_until": timestamp, "remaining_sec": N}
    """
    global _SOL_DCA_PAUSE_UNTIL
    now = time.time()

    if duration_sec is None:
        _SOL_DCA_PAUSE_UNTIL = None
        _log(f"[SOL] DCA暂停已解除 (by {initiator})")
        write_risk_audit_log(
            action="sol_dca_pause_cleared",
            source=initiator,
            reason=reason,
        )
        return {"success": True, "pause_until": None, "remaining_sec": 0}

    _SOL_DCA_PAUSE_UNTIL = now + duration_sec
    _log(f"[SOL] DCA暂停已设置: {duration_sec}秒 ({duration_sec//60}min), 原因: {reason}")
    write_risk_audit_log(
        action="sol_dca_pause_set",
        source=initiator,
        reason=reason,
        extra={"duration_sec": duration_sec, "pause_until": _SOL_DCA_PAUSE_UNTIL}
    )
    return {"success": True, "pause_until": _SOL_DCA_PAUSE_UNTIL, "remaining_sec": duration_sec}

def get_sol_dca_pause_remaining() -> int:
    """返回SOL DCA暂停剩余秒数，0=未暂停"""
    if _SOL_DCA_PAUSE_UNTIL is None:
        return 0
    remaining = int(_SOL_DCA_PAUSE_UNTIL - time.time())
    return max(0, remaining)
```

### 5.3 触发条件

#### 自动触发（AUTO）

满足以下任一条件，自动触发SOL DCA暂停：

| 条件 | 阈值 | 说明 |
|------|------|------|
| SOL DCA满层触发 | layer=2时触发止损 | DCA追加后立即止损 = 信号失真 |
| SOL单笔ROE | ≤-20% 单笔 | 极端亏损 |
| SOL止损触发 | 24h内≥2次止损 | 频繁止损信号 |

#### 人工触发（MANUAL）

- 权限：爸
- 触发方式：调用 `set_sol_dca_pause(duration_sec=1800, reason="...", initiator="manual")`
- API路由：`POST /api/admin/sol_pause`

### 5.4 解除条件

| 类型 | 条件 | 说明 |
|------|------|------|
| 超时自动解除 | 到达 `_SOL_DCA_PAUSE_UNTIL` 时间戳 | 自动清除 |
| 人工解除 | 爸调用 `set_sol_dca_pause(None)` | 立即解除 |
| 重新暂停 | 到期前再次满足触发条件 | 重新计时 |

### 5.5 DCA入口拦截

```python
# 伪代码（插入 check_dca_trigger() 之前，与DOGE冻结检查并列）
if is_sol_dca_paused(pair):
    _log(f"  🚫 {pair} SOL DCA暂停中，禁止DCA")
    cycle_result["skipped"] += 1
    cycle_result["details"].append({"pair": pair, "reason": "SOL_DCA_paused"})
    continue
```

---

## 6. 统一入场许可检查

```python
def should_allow_auto_entry(pair: str, direction: str = "") -> tuple[bool, str]:
    """
    统一入场许可检查入口

    Returns:
        (allowed: bool, reason: str)
        - allowed=True, reason="ok"  : 正常入场
        - allowed=False, reason="DOGE_temporary_freeze"
        - allowed=False, reason="SOL_DCA_paused"
    """
    # DOGE临时冻结（全局，任意方向）
    if is_doge_freeze_active(pair):
        return False, "DOGE_temporary_freeze"
    # SOL DCA暂停（仅阻止DCA追加，不阻止普通入场）
    # 注意：SOL DCA暂停不在此处拦截普通force_entry
    # 仅在DCA检查路径中拦截
    return True, "ok"
```

---

## 7. 配置JSON格式

### 7.1 全局配置字段

```json
{
  "doge_freeze_config": {
    "enabled": true,
    "default_duration_sec": 86400,
    "auto_trigger_conditions": {
      "doge_stoploss_count_1h": 3,
      "doge_order_failure_rate": 0.5,
      "doge_single_roe_threshold": -0.15
    }
  },
  "sol_dca_pause_config": {
    "enabled": true,
    "default_duration_sec": 1800,
    "auto_trigger_conditions": {
      "sol_dca_full_layer_stoploss": true,
      "sol_single_roe_threshold": -0.20,
      "sol_stoploss_count_24h": 2
    }
  }
}
```

### 7.2 运行时状态字段（内存，不持久化）

```json
{
  "temporary_pair_freeze": {
    "DOGE_USDT": {
      "freeze_until": 1746438400.123,
      "freeze_reason": "批量止损3次/1h，交易所API不稳定",
      "freeze_initiator": "auto",
      "set_at": "2026-05-04T15:00:00+08:00"
    }
  },
  "dca_pause_rules": {
    "SOL_USDT": {
      "pause_until": 1746435700.456,
      "pause_reason": "DCA满层后触发止损，VPS延迟",
      "pause_initiator": "auto",
      "set_at": "2026-05-04T14:30:00+08:00"
    }
  }
}
```

---

## 8. 审计日志

| action | 触发时机 | 记录字段 |
|--------|---------|---------|
| `doge_freeze_set` | DOGE冻结设置 | `duration_sec`, `freeze_until`, `reason`, `initiator` |
| `doge_freeze_cleared` | DOGE冻结解除 | `reason`, `initiator` |
| `doge_freeze_auto_triggered` | DOGE自动冻结 | `trigger_condition`, `count`, `reason` |
| `sol_dca_pause_set` | SOL暂停设置 | `duration_sec`, `pause_until`, `reason`, `initiator` |
| `sol_dca_pause_cleared` | SOL暂停解除 | `reason`, `initiator` |
| `sol_dca_pause_auto_triggered` | SOL自动暂停 | `trigger_condition`, `roe_pct`, `layer` |

---

## 9. 通知规则

| 事件 | 通知渠道 | 内容 |
|------|---------|------|
| DOGE自动冻结 | 飞书兵部 | `🚨 DOGE自动冻结24h，条件：X次止损/1h` |
| DOGE人工冻结 | 飞书兵部 | `🔒 DOGE已人工冻结，by {initiator}` |
| DOGE冻结解除 | 无需通知 | 自动解除，用户可查询状态 |
| SOL自动暂停 | 飞书兵部 | `⚠️ SOL DCA自动暂停30min，条件：满层+止损` |
| SOL人工暂停 | 飞书兵部 | `🔒 SOL DCA已人工暂停，by {initiator}` |
| SOL暂停解除 | 无需通知 | 自动解除 |

---

## 10. 规则版本

| 版本 | 日期 | 制定方 | 变更 |
|------|------|--------|------|
| V1.0 | 2026-05-04 | 刑部代理 | 初始版本，基于SOL ROE -27.9%和DOGE批量止损事件 |
