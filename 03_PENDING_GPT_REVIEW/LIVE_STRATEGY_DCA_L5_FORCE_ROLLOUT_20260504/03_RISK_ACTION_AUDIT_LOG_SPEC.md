# 高风险操作审计日志规范 — V6.5 现场部署
**文件**: `risk_audit_logger.py` + `force_action_guard.py`
**日志路径**: `~/.audit_logs/risk_actions.jsonl` + `force_action_audit.jsonl`
**审计时间**: 2026-05-04
**状态**: PENDING — 待GPT评审后部署

---

## 1. 日志文件结构

```
~/.audit_logs/
├── risk_actions.jsonl       # 高风险操作主审计日志（由 risk_audit_logger.py 写入）
└── force_action_audit.jsonl # ForceActionGuard 专用审计日志（由 force_action_guard.py 写入）
```

**格式**: JSON Lines（每行一条JSON记录，UTF-8编码）
**保留策略**: 建议保留90天，可通过日志轮转脚本压缩归档

---

## 2. 字段定义

### 2.1 risk_actions.jsonl 字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `audit_id` | string | 是 | 全局唯一审计ID，格式: `ra_{timestamp_ms}_{random8}` |
| `timestamp` | string | 是 | ISO8601时间戳（UTC+8），例: `2026-05-04T15:00:00+08:00` |
| `action` | string | 是 | 操作类型，见 2.1.1 Action类型表 |
| `pair` | string | 否 | 交易对，如 `BTC_USDT`，平仓操作可为空 |
| `direction` | string | 否 | 方向：`LONG` / `SHORT` / 空字符串 |
| `source` | string | 是 | 调用来源，见 2.1.2 Source类型表 |
| `bot_id` | int\|str | 是 | 机器人端口号或标识符 |
| `policy_decision` | string | 否 | ForceActionGuard策略决策结果 |
| `allowed` | bool | 是 | 动作是否被允许执行 |
| `reason` | string | 否 | 拒绝/允许/待确认的详细原因 |
| `extra` | dict | 否 | 扩展字段，见各action的extra规范 |

#### 2.1.1 action 类型

| action 值 | 说明 | 何时记录 |
|-----------|------|---------|
| `force_entry_request` | force_entry请求发起 | 刚进入guard检查时 |
| `force_entry_executed` | force_entry执行成功 | bot返回200时 |
| `force_entry_blocked` | force_entry被拦截 | policy=deny时 |
| `force_entry_confirmed` | force_entry待确认后被批准 | 审批队列通过后 |
| `force_exit_request` | force_exit请求发起 | 刚进入guard检查时 |
| `force_exit_executed` | force_exit执行成功 | bot返回200时 |
| `force_exit_blocked` | force_exit被拦截 | policy=deny时 |
| `force_exit_confirmed` | force_exit待确认后被批准 | 审批队列通过后 |
| `dca_blocked` | DCA被阻止（止损冷却/DOGE/SOL） | DCA入口检查失败时 |
| `dca_executed` | DCA执行成功 | DCA触发并完成时 |
| `leverage_change` | 杠杆调整 | 杠杆变动时 |
| `emergency_exit_triggered` | 紧急平仓触发 | 紧急平仓执行时 |

#### 2.1.2 source 类型

| source 值 | 说明 |
|-----------|------|
| `api` | HTTP API (`/api/force_entry`) |
| `monitor` | Monitor接口 (`/api/monitor/force_entry/exit`) |
| `broadcast` | 兵部广播 (`broadcast()` 函数) |
| `signal` | 信号处理 |
| `manual` | 手动操作（直接操作bot） |
| `autopilot` | 自动驾驶例程（v65_autopilot.py） |
| `chushan` | 出山AI |
| `tianyan` | 天眼AI |

#### 2.1.3 extra 字段扩展规范

**force_entry_request / force_entry_executed**:
```json
{
  "extra": {
    "entry_tag": "manual_force_entry",
    "leverage": 10,
    "stakeamount": 100.0,
    "add_pct": 10
  }
}
```

**force_exit_request / force_exit_executed**:
```json
{
  "extra": {
    "trade_id": "12345",
    "exit_pct": 100,
    "partial": false
  }
}
```

**dca_blocked**:
```json
{
  "extra": {
    "block_reason": "stoploss_cooldown",
    "cooldown_remaining_sec": 3600,
    "dca_layer": 1,
    "roe_pct": -8.5
  }
}
```

### 2.2 force_action_audit.jsonl 字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `audit_id` | string | 是 | 同上，格式: `fa_{timestamp_ms}_{random8}` |
| `timestamp` | string | 是 | ISO8601时间戳（UTC+8） |
| `action_type` | string | 是 | ForceActionGuard策略动作类型 |
| `pair` | string | 是 | 交易对 |
| `direction` | string | 是 | 方向 |
| `source` | string | 是 | 调用来源 |
| `bot_id` | int\|str | 是 | 机器人标识符 |
| `policy` | string | 是 | 命中的策略名称 |
| `decision` | string | 是 | 决策结果：`DENIED` / `PENDING_CONFIRM` / `QUEUED` / `ALLOWED` |
| `reason` | string | 是 | 决策原因 |
| `extra` | dict | 否 | 扩展参数 |

---

## 3. 示例记录

### 3.1 force_entry 被 policy deny 拦截
```json
{
  "audit_id": "ra_1746345600000_a1b2c3d4",
  "timestamp": "2026-05-04T15:00:00+08:00",
  "action": "force_entry_request",
  "pair": "DOGE_USDT",
  "direction": "LONG",
  "source": "api",
  "bot_id": 9090,
  "policy_decision": "policy=deny [force_entry] is blocked by default",
  "allowed": false,
  "reason": "force_entry blocked by policy",
  "extra": {"entry_tag": "manual_force_entry"}
}
```

### 3.2 force_entry 需要确认
```json
{
  "audit_id": "ra_1746345600001_e5f6g7h8",
  "timestamp": "2026-05-04T15:01:00+08:00",
  "action": "force_entry_request",
  "pair": "BTC_USDT",
  "direction": "LONG",
  "source": "monitor",
  "bot_id": 9091,
  "policy_decision": "policy=confirm [force_entry] requires explicit confirmation",
  "allowed": false,
  "reason": "force_entry requires confirmation",
  "extra": {"leverage": 10}
}
```

### 3.3 DCA被止损冷却阻止
```json
{
  "audit_id": "ra_1746345600002_i9j0k1l2",
  "timestamp": "2026-05-04T15:02:00+08:00",
  "action": "dca_blocked",
  "pair": "ETH_USDT",
  "direction": "LONG",
  "source": "autopilot",
  "bot_id": 9092,
  "policy_decision": "",
  "allowed": false,
  "reason": "stoploss_cooldown",
  "extra": {
    "block_reason": "stoploss_cooldown",
    "cooldown_remaining_sec": 7200,
    "dca_layer": 1,
    "roe_pct": -12.3
  }
}
```

### 3.4 force_exit 执行成功
```json
{
  "audit_id": "ra_1746345600003_m3n4o5p6",
  "timestamp": "2026-05-04T15:03:00+08:00",
  "action": "force_exit_executed",
  "pair": "SOL_USDT",
  "direction": "LONG",
  "source": "monitor",
  "bot_id": 9093,
  "policy_decision": "policy=confirm [force_exit] requires explicit confirmation",
  "allowed": true,
  "reason": "",
  "extra": {"trade_id": "67890", "exit_pct": 100}
}
```

---

## 4. 查询示例

### 4.1 查询指定pair的所有操作
```bash
grep '"pair": "BTC_USDT"' ~/.audit_logs/risk_actions.jsonl | jq .
```

### 4.2 查询被阻止的force_entry
```bash
grep '"action": "force_entry_blocked"' ~/.audit_logs/risk_actions.jsonl | jq '.audit_id, .timestamp, .pair, .reason'
```

### 4.3 查询最近1小时内的高风险操作
```bash
# 获取1小时前时间戳（毫秒）
cutoff=$(date -v-1H +%s)000
grep -v '"action": "heartbeat"' ~/.audit_logs/risk_actions.jsonl \
  | jq -c 'select((.timestamp | sub("T"; " ") | sub("\\+08:00"; "") | strptime("%Y-%m-%d %H:%M:%S") | mktime) * 1000 > '$cutoff')'
```

### 4.4 统计各source的force_entry请求量
```bash
grep '"action": "force_entry' ~/.audit_logs/risk_actions.jsonl \
  | jq -r '.source' | sort | uniq -c | sort -rn
```

### 4.5 查询某audit_id的完整记录链
```bash
grep '"audit_id": "ra_1746345600000' ~/.audit_logs/risk_actions.jsonl | jq .
```

### 4.6 查询所有DCA被阻止的记录
```bash
grep '"action": "dca_blocked"' ~/.audit_logs/risk_actions.jsonl | jq '.pair, .extra.block_reason, .reason'
```

---

## 5. 日志轮转建议

```bash
# 每周归档一次，压缩保留90天
0 3 * * 0 find ~/.audit_logs/ -name "*.jsonl" -mtime +7 -exec gzip {} \;
0 4 * * 0 find ~/.audit_logs/ -name "*.jsonl.gz" -mtime +90 -delete
```

---

## 6. 与 pending_approvals.json 的联动

当 `ForceActionGuard.check()` 返回 `requires_confirm=True` 时，记录会被同时写入：

1. `force_action_audit.jsonl` — 标记为 `PENDING_CONFIRM`
2. `~/freqtrade_console/pending_approvals.json` — 进入待确认队列

审批通过后，应追加一条 `force_entry_confirmed` / `force_exit_confirmed` 记录到 `risk_actions.jsonl`，并从 `pending_approvals.json` 中移除对应记录。

---

## 7. 字段完整性检查

建议在 `write_risk_audit_log()` 中加入必填字段校验：

```python
REQUIRED_FIELDS = ["audit_id", "timestamp", "action", "source", "bot_id", "allowed"]

def _validate_record(record: dict) -> None:
    missing = [f for f in REQUIRED_FIELDS if f not in record or record[f] is None]
    if missing:
        raise ValueError(f"RiskAuditLog: missing required fields: {missing}")
```
