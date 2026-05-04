# ForceActionGuard 权限闸完整规则 — V6.5
**文件编号**: 09
**制定方**: 刑部代理
**生效日期**: 2026-05-04
**版本**: V1.0
**状态**: 待审批

---

## 1. 总则

ForceActionGuard 是所有高风险动作的统一入口守卫，负责权限校验、冷却管理、审计日志记录，以及待确认队列管理。

**所有 force_entry / force_exit / force_dca / emergency_exit / adjust_leverage 动作必须经过此守卫。**

**核心原则**:
- 默认拒绝（deny by default）
- 高风险动作必须人工确认
- 所有操作必须有审计日志
- 冷却期不可绕过

---

## 2. 动作权限矩阵

### 2.1 权限级别定义

| 级别 | 代码 | 说明 |
|------|------|------|
| 禁止 | `deny` | 无条件拦截，记录日志，返回403 |
| 待确认 | `confirm` | 进入 pending_approvals.json，等待人工审批 |
| 队列 | `pending` | 进入待确认队列，等待人工审批（同confirm，但日志标记不同） |
| 允许 | `allow` | 直接放行（仅用于低风险辅助动作） |

### 2.2 动作权限表

| # | 动作类型 | 代码策略 | 权限说明 | 备注 |
|---|---------|---------|---------|------|
| 1 | `force_entry` | `deny` | **禁止自动放行** | 必须人工确认（爸授权） |
| 2 | `force_exit` | `confirm` | **需要确认** | 人工确认后可执行 |
| 3 | `force_dca` | `confirm` | **建议确认** | 人工确认后可执行 |
| 4 | `emergency_exit` | `pending` | **紧急队列** | 紧急情况快速审批通道 |
| 5 | `emergency_increase` | `pending` | **紧急队列** | 紧急加仓 |
| 6 | `modify_dca` | `confirm` | **需要确认** | 修改DCA参数 |
| 7 | `adjust_leverage` | `confirm` | **需要确认** | 调整杠杆 |
| 8 | `cancel_trade` | `deny` | **禁止** | 取消订单（保留，仅用于特殊场景） |
| 9 | `full_close` | `confirm` | **需要确认** | 全平仓 |
| 10 | `partial_close` | `pending` | **待确认** | 部分平仓 |

### 2.3 权限来源矩阵

| 来源 | force_entry | force_exit | force_dca | emergency_exit |
|------|------------|------------|----------|----------------|
| HTTP API (`/api/force_entry`) | deny | confirm | confirm | pending |
| Monitor接口 (`/api/monitor/*`) | deny | confirm | confirm | pending |
| 兵部广播 (`broadcast()`) | deny | confirm | confirm | pending |
| 信号处理 (`signal分支`) | deny | confirm | confirm | pending |
| 人工操作（直接bot） | confirm | confirm | confirm | pending |
| 自动驾驶例程（autopilot） | deny | — | deny | — |
| 出山AI | deny | pending | deny | pending |
| 天眼AI | deny | pending | deny | pending |

> **重要**：`autopilot`、`chushan`、`tianyan` 作为 source 时，`force_entry` 策略为 `deny`，即禁止自动驾驶模块主动发起 force_entry。所有入场必须经过人工授权。

---

## 3. force_entry 权限要求

### 3.1 规则 3.1: force_entry 必须人工确认

```
条件: 所有 force_entry 请求，无论来源（API/monitor/broadcast/signal/autopilot）
动作: policy=deny → 拦截，返回 403
需人工操作: 爸通过 /api/force_entry?confirm=true 或 pending_approvals.json 审批
```

### 3.2 拦截场景

| 场景 | 拦截原因 | 返回码 |
|------|---------|--------|
| 任意 source 的 force_entry | `policy=deny [force_entry] is blocked by default` | 403 |
| DCA 满层后 force_entry（同pair） | `policy=deny DCA已达封顶层数` | 403 |
| DOGE 冻结期内 force_entry | `policy=deny DOGE临时冻结中` | 403 |
| 止损冷却期内 force_entry | `policy=deny 止损冷却剩余Xs` | 403 |

### 3.3 审计日志

```json
{
  "audit_id": "fa_{timestamp}_{random8}",
  "timestamp": "2026-05-04T15:00:00+08:00",
  "action_type": "force_entry",
  "pair": "BTC_USDT",
  "direction": "LONG",
  "source": "api",
  "bot_id": 9090,
  "policy": "deny",
  "decision": "DENIED",
  "reason": "policy=deny [force_entry] is blocked by default",
  "extra": {
    "entry_tag": "manual_force_entry",
    "leverage": 10,
    "stakeamount": 100.0
  }
}
```

---

## 4. force_exit 权限要求

### 4.1 规则 4.1: force_exit 需要确认

```
条件: 所有 force_exit 请求
动作: policy=confirm → 进入 pending_approvals.json，等待审批
冷却: 写 exit_cooldown（同pair 30min）
```

### 4.2 放行条件

人工审批通过后，执行以下检查：

| 检查项 | 说明 |
|--------|------|
| 持仓检查 | trade_id 必须对应有效持仓 |
| 冷却检查 | `_check_exit_cooldown(port, pair)` |
| 权限检查 | pending_approvals 中审批记录存在 |

### 4.3 审计日志

```json
{
  "audit_id": "fa_{timestamp}_{random8}",
  "timestamp": "2026-05-04T15:01:00+08:00",
  "action_type": "force_exit",
  "pair": "ETH_USDT",
  "direction": "LONG",
  "source": "monitor",
  "bot_id": 9091,
  "policy": "confirm",
  "decision": "QUEUED",
  "reason": "policy=confirm [force_exit] requires explicit confirmation",
  "extra": {
    "trade_id": "12345",
    "exit_pct": 100
  }
}
```

---

## 5. force_dca 权限要求

### 5.1 规则 5.1: force_dca 建议人工确认

```
条件: 人工强制触发 DCA 追加
动作: policy=confirm → 进入 pending_approvals.json
冷却: 同自动 DCA 冷却规则（30min）
```

> **注意**：自动 DCA 由 autopilot 触发，force_entry/force_exit 策略覆盖。force_dca 特指人工强制追加的 DCA（不在常规检查路径中）。

### 5.2 限制条件

| 条件 | 限制 | 说明 |
|------|------|------|
| 层数限制 | `current_layer < _DCA_MAX_LAYER` | 满层禁止 force_dca |
| DOGE冻结 | `not is_doge_freeze_active(pair)` | DOGE冻结期间禁止 |
| SOL暂停 | `not is_sol_dca_paused(pair)` | SOL暂停期间禁止 |
| 止损冷却 | `not in stoploss_cooldown` | 止损冷却期间禁止 |

---

## 6. 冷却期规则

### 6.1 冷却类型

| 冷却类型 | 变量 | 默认时长 | 触发 | 清除条件 |
|---------|------|---------|------|---------|
| force_entry 冷却 | `_force_entry_cooldown` | 60min | force_entry执行后 | 超时或人工清除 |
| force_exit 冷却 | `_exit_cooldown` | 30min | force_exit执行后 | 超时 |
| DCA 冷却 | `_dca_cooldown_state` | 30min | DCA执行后 | 超时 |
| 止损冷却 | `_stoploss_state` | 4h | 止损触发后 | 超时（不得被DCA清除） |

### 6.2 冷却检查规则

**规则 6.1: 冷却期间，动作被拦截，不清除冷却记录**

```
DCA 触发时：
  ❌ 禁止 del _stoploss_state[pair]（BUG P0-3，必须修复）
  ✅ 冷却检查在 DCA 入口统一处理

冷却清除条件：
  ✅ 超时自动清除（唯一合法清除方式）
  ❌ 禁止任何代码主动删除冷却记录
```

### 6.3 冷却状态查询 API

```
GET /api/cooldown_status?port=9090&pair=DOGE_USDT

Response:
{
  "pair": "DOGE_USDT",
  "stoploss_cooldown_remaining_sec": 7200,
  "dca_cooldown_remaining_sec": 0,
  "force_entry_cooldown_remaining_sec": 1800,
  "force_exit_cooldown_remaining_sec": 0,
  "doge_freeze_remaining_sec": 0,
  "sol_dca_pause_remaining_sec": 0
}
```

---

## 7. 审计日志规范

### 7.1 审计日志文件

```
路径: ~/.tianlu/logs/force_action_audit.log
格式: JSON Lines（每行一条记录，UTF-8编码）
保留: 建议保留90天
轮转: 每周压缩归档（见查询示例）
```

> **注意**：路径为 `~/.tianlu/logs/`，与 `~/.audit_logs/`（`03_RISK_ACTION_AUDIT_LOG_SPEC.md` 定义）不同：
> - `~/.tianlu/logs/force_action_audit.log` — ForceActionGuard 专用审计日志
> - `~/.audit_logs/risk_actions.jsonl` — 全局风险操作审计日志（由 `risk_audit_logger.py` 写入）
> 两者互补，共同覆盖所有高风险操作。

### 7.2 字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `audit_id` | string | 是 | 唯一ID，格式 `fa_{timestamp_ms}_{random8}` |
| `timestamp` | string | 是 | ISO8601时间戳（UTC+8） |
| `action_type` | string | 是 | 动作类型（见权限矩阵） |
| `pair` | string | 是 | 交易对（如 DOGE_USDT） |
| `direction` | string | 是 | 方向（LONG / SHORT / 空字符串） |
| `source` | string | 是 | 来源（见source类型表） |
| `bot_id` | int\|str | 是 | 机器人端口或标识符 |
| `policy` | string | 是 | 命中的策略名称 |
| `decision` | string | 是 | 决策结果（DENIED/PENDING_CONFIRM/QUEUED/ALLOWED） |
| `reason` | string | 是 | 决策原因 |
| `extra` | dict | 否 | 扩展参数 |
| `confirmed_by` | string | 否 | 审批人（审批通过后填充） |
| `confirmed_at` | string | 否 | 审批时间（ISO8601） |

### 7.3 source 类型

| source | 说明 | 可触发 force_entry |
|--------|------|-------------------|
| `api` | HTTP API | ❌ deny |
| `monitor` | Monitor接口 | ❌ deny |
| `broadcast` | 兵部广播 | ❌ deny |
| `signal` | 信号处理 | ❌ deny |
| `manual` | 人工操作 | ✅ confirm |
| `autopilot` | 自动驾驶 | ❌ deny |
| `chushan` | 出山AI | ❌ deny |
| `tianyan` | 天眼AI | ❌ deny |

### 7.4 完整审计日志格式

```json
{
  "audit_id": "fa_1746345600000_a1b2c3d4",
  "timestamp": "2026-05-04T15:00:00+08:00",
  "action_type": "force_entry",
  "pair": "BTC_USDT",
  "direction": "LONG",
  "source": "api",
  "bot_id": 9090,
  "policy": "deny",
  "decision": "DENIED",
  "reason": "policy=deny [force_entry] is blocked by default",
  "extra": {
    "entry_tag": "manual_force_entry",
    "leverage": 10,
    "stakeamount": 100.0
  }
}
```

### 7.5 审计日志记录时机

| 时机 | action_type | decision |
|------|------------|---------|
| 进入guard检查 | `force_entry_request` | — |
| 检查通过，执行成功 | `force_entry_executed` | ALLOWED |
| 检查拒绝（deny） | `force_entry_blocked` | DENIED |
| 检查通过，待确认 | `force_entry_pending` | PENDING_CONFIRM |
| 人工审批通过 | `force_entry_confirmed` | CONFIRMED |
| 人工审批拒绝 | `force_entry_rejected` | REJECTED |
| 紧急平仓请求 | `emergency_exit_request` | QUEUED |
| 杠杆调整请求 | `leverage_change_request` | PENDING_CONFIRM |

---

## 8. 高风险动作（EMERGENCY系列）额外确认要求

### 8.1 EMERGENCY 系列定义

| 动作 | 触发场景 | 额外确认要求 |
|------|---------|------------|
| `emergency_exit` | 极端行情，立即出场 | 必须通过 /api/emergencies/pending 审批 |
| `emergency_increase` | 极端行情，紧急加仓 | 必须电话/语音确认 |
| `emergency_adjust` | 紧急调整参数 | 需在30秒内响应 |

### 8.2 额外确认流程（EMERGENCY）

```
EMERGENCY 请求到达
  → ForceActionGuard 标记为 QUEUED
  → 写入 pending_approvals.json（高优先级标记 priority=high）
  → 推送飞书兵部（加急🔴）
  → 同时发送手机推送（如果配置）

审批人（爸）操作：
  → 飞书消息中点击"批准"按钮
  → 或访问 /api/emergencies/pending
  → 或直接调用 /api/emergencies/approve?audit_id=xxx

执行结果：
  → 写入审计日志（confirmed_by, confirmed_at）
  → 执行 EMERGENCY 动作
  → 通知兵部执行结果
```

### 8.3 紧急审批超时规则

| 优先级 | 超时时间 | 超时动作 |
|--------|---------|---------|
| `critical` | 30秒 | 自动拒绝，发飞书警告 |
| `high` | 5分钟 | 自动拒绝 |
| `normal` | 30分钟 | 自动过期 |

---

## 9. ForceActionGuard 类规范

### 9.1 类签名

```python
class ForceActionGuard:
    DEFAULT_POLICY: dict[str, str] = {
        "force_entry":       "deny",
        "force_exit":        "confirm",
        "force_dca":         "confirm",
        "emergency_exit":    "pending",
        "emergency_increase": "pending",
        "modify_dca":        "confirm",
        "adjust_leverage":   "confirm",
        "cancel_trade":     "deny",
        "full_close":       "confirm",
        "partial_close":    "pending",
    }

    def check(
        self,
        action_type: str,
        pair: str,
        direction: str,
        source: str,
        bot_id: int | str,
        extra: dict | None = None,
    ) -> tuple[bool, bool, str, str]:
        """
        Returns: (allowed, requires_confirm, audit_id, reason)
        """

    def write_audit(self, record: dict) -> None:
        """写入 ~/.tianlu/logs/force_action_audit.log"""

    def enqueue_confirmation(self, record: dict) -> None:
        """写入 pending_approvals.json"""

    def get_policy(self, action_type: str) -> str:
        """查询当前策略"""

    def set_policy(self, action_type: str, policy: str) -> None:
        """动态修改策略（仅运行时，进程重启后恢复）"""
```

### 9.2 全局单例

```python
# 全局单例（console_server.py 和 api_autopilot.py 共用）
force_guard = ForceActionGuard()
```

### 9.3 与 risk_audit_logger 的联动

ForceActionGuard 写入 `~/.tianlu/logs/force_action_audit.log`，同时调用 `write_risk_audit_log()` 写入 `~/.audit_logs/risk_actions.jsonl`，保证两个审计日志同步。

```python
# ForceActionGuard.check() 内部同时调用
def check(...):
    # ...
    audit_record = {...}
    self.write_audit(audit_record)          # → ~/.tianlu/logs/force_action_audit.log
    write_risk_audit_log(                   # → ~/.audit_logs/risk_actions.jsonl
        action=f"{action_type}_request",
        pair=pair,
        direction=direction,
        source=source,
        bot_id=bot_id,
        audit_id=audit_id,
        policy_decision=reason,
        allowed=allowed,
        extra=extra,
    )
    # ...
```

---

## 10. 待确认队列规范

### 10.1 pending_approvals.json 格式

```json
[
  {
    "audit_id": "fa_1746345600000_a1b2c3d4",
    "timestamp": "2026-05-04T15:00:00+08:00",
    "action_type": "force_entry",
    "pair": "BTC_USDT",
    "direction": "LONG",
    "source": "api",
    "bot_id": 9090,
    "policy": "deny",
    "decision": "PENDING_CONFIRM",
    "reason": "policy=deny [force_entry] is blocked by default",
    "extra": {"leverage": 10},
    "priority": "normal"
  }
]
```

### 10.2 审批API

```
POST /api/approvals/confirm
Body: {"audit_id": "fa_1746345600000_a1b2c3d4"}

DELETE /api/approvals/reject
Body: {"audit_id": "fa_1746345600000_a1b2c3d4", "reason": "理由"}

GET /api/approvals/pending
Response: pending_approvals.json 内容
```

---

## 11. 集成到代码的要求

### 11.1 必须集成的入口

| # | 文件 | 行号 | 入口函数 | 必须集成 |
|---|------|------|---------|---------|
| 1 | console_server.py | 5613 | `api_force_entry()` | ✅ ForceActionGuard + audit |
| 2 | console_server.py | 10159 | `api_monitor_force_entry()` | ✅ ForceActionGuard + audit |
| 3 | console_server.py | 10192 | `api_monitor_force_exit()` | ✅ ForceActionGuard + audit |
| 4 | console_server.py | 5087 | `broadcast()` - force_exit | ✅ ForceActionGuard + audit |
| 5 | console_server.py | 5124 | `broadcast()` - force_entry | ✅ ForceActionGuard + audit |
| 6 | console_server.py | 18281 | signal分支 - force_exit | ✅ ForceActionGuard + audit |
| 7 | api_autopilot.py | — | 所有force动作 | ✅ ForceActionGuard |

### 11.2 导入规范

```python
try:
    from force_action_guard import ForceActionGuard, force_guard
    _FORCE_GUARD_AVAILABLE = True
except ImportError:
    _FORCE_GUARD_AVAILABLE = False
    class _DummyGuard:
        def check(self, *args, **kwargs):
            return True, False, "", "guard_unavailable"
    force_guard = _DummyGuard()
```

---

## 12. 规则版本

| 版本 | 日期 | 制定方 | 变更 |
|------|------|--------|------|
| V1.0 | 2026-05-04 | 刑部代理 | 初始版本，统一 ForceActionGuard 权限闸规范 |
