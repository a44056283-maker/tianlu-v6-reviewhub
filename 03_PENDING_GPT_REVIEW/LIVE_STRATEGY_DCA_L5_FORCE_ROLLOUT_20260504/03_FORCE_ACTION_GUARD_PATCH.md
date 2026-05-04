# ForceActionGuard 统一入口补丁 — V6.5 现场部署
**文件**: `console_server.py` + `api_autopilot.py`
**审计时间**: 2026-05-04
**状态**: PENDING — 待GPT评审后部署

---

## 1. 高风险动作入口清单

通过代码审计，确认以下Force动作入口：

| # | 文件 | 行号 | 函数/路由 | 动作类型 | 当前策略 |
|---|------|------|-----------|---------|---------|
| 1 | console_server.py | 5087 | `broadcast()` 分支 | `force_exit` | 兵部接口，写冷却 |
| 2 | console_server.py | 5124 | `broadcast()` 分支 | `force_entry` | 兵部接口，有冷却检查 |
| 3 | console_server.py | 5613 | `api_force_entry()` | `force_entry` | HTTP API，无人确认 |
| 4 | console_server.py | 10159 | `api_monitor_force_entry()` | `force_entry` | monitor接口，有冷却检查 |
| 5 | console_server.py | 10192 | `api_monitor_force_exit()` | `force_exit` | monitor接口，写冷却 |
| 6 | console_server.py | 18281 | signal分支 | `force_exit` | 信号分支处理 |

**缺口分析**:
- `api_force_entry()` (line 5613) **无任何人确认流程**，直接发往bot
- `force_entry` 分支 (line 5124) **无audit log**
- `force_exit` 分支 (line 5087) **无audit log**

---

## 2. ForceActionGuard 统一类

**建议新增文件**: `~/freqtrade_console/force_action_guard.py`
（可被 `console_server.py` 和 `api_autopilot.py` 共同导入）

```python
"""
ForceActionGuard — 高风险动作统一守卫
========================================
所有 force_entry / force_exit / emergency_exit / modify_dca / adjust_leverage
动作必须经过此守卫，记录audit log并执行策略检查。

导入:
    from force_action_guard import ForceActionGuard, force_guard

使用:
    allowed, requires_confirm, audit_id = force_guard.check(
        action_type="force_entry",
        pair="BTC_USDT",
        direction="LONG",
        source="api",
        bot_id=9090
    )
"""

import time
import uuid
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Literal

# ── Audit Log 路径 ────────────────────────────────────────────────
_AUDIT_LOG_DIR = os.path.expanduser("~/freqtrade_console/.audit_logs")
_AUDIT_LOG_FILE = os.path.join(_AUDIT_LOG_DIR, "force_action_audit.jsonl")

os.makedirs(_AUDIT_LOG_DIR, exist_ok=True)


class ForceActionGuard:
    """
    高风险动作统一守卫类

    Policy 说明:
    - deny       : 默认禁止，无条件拦截
    - confirm    : 需要二次确认（进入 pending_approvals.json）
    - pending    : 进入待确认队列，等待审批
    - allow      : 直接放行（仅用于低风险辅助动作）
    """

    # 默认策略矩阵
    DEFAULT_POLICY: dict[str, Literal["deny", "confirm", "pending", "allow"]] = {
        "force_entry":      "deny",       # 默认禁止force_entry
        "force_exit":       "confirm",     # 默认需要确认
        "emergency_exit":    "pending",     # 紧急平仓→待确认队列
        "modify_dca":       "confirm",     # 修改DCA参数→确认
        "adjust_leverage":   "confirm",    # 调整杠杆→确认
        "cancel_trade":     "deny",        # 取消订单→禁止
        "full_close":       "confirm",      # 全平仓→确认
        "partial_close":    "pending",      # 部分平仓→待确认
    }

    def __init__(self, policy_overrides: dict | None = None):
        """
        Args:
            policy_overrides: 覆盖默认策略，如 {"force_entry": "confirm"}
        """
        self.policy = dict(self.DEFAULT_POLICY)
        if policy_overrides:
            self.policy.update(policy_overrides)

    def check(
        self,
        action_type: str,
        pair: str,
        direction: str,
        source: str,       # "api" | "monitor" | "broadcast" | "signal" | "manual"
        bot_id: int | str,
        extra: dict | None = None
    ) -> tuple[bool, bool, str, str]:
        """
        检查动作是否允许执行

        Returns:
            (allowed, requires_confirm, audit_id, reason)
            - allowed           : 是否可直接执行
            - requires_confirm  : 是否需要进入确认队列
            - audit_id         : 本次操作的唯一审计ID
            - reason            : 允许/拒绝/待确认的原因
        """
        policy = self.policy.get(action_type, "deny")
        audit_id = f"fa_{int(time.time()*1000)}_{uuid.uuid4().hex[:8]}"
        ts = datetime.now(timezone(timedelta(hours=8))).isoformat()

        # 构建审计记录
        audit_record = {
            "audit_id": audit_id,
            "timestamp": ts,
            "action_type": action_type,
            "pair": pair,
            "direction": direction,
            "source": source,
            "bot_id": bot_id,
            "policy": policy,
            "extra": extra or {},
        }

        if policy == "deny":
            audit_record["decision"] = "DENIED"
            audit_record["reason"] = f"policy=deny [{action_type}] is blocked by default"
            self._write_audit(audit_record)
            return False, False, audit_id, audit_record["reason"]

        if policy == "confirm":
            audit_record["decision"] = "PENDING_CONFIRM"
            audit_record["reason"] = f"policy=confirm [{action_type}] requires explicit confirmation"
            self._write_audit(audit_record)
            self._enqueue_confirmation(audit_record)
            return False, True, audit_id, audit_record["reason"]

        if policy == "pending":
            audit_record["decision"] = "QUEUED"
            audit_record["reason"] = f"policy=pending [{action_type}] queued for review"
            self._write_audit(audit_record)
            self._enqueue_confirmation(audit_record)
            return False, True, audit_id, audit_record["reason"]

        # policy == "allow"
        audit_record["decision"] = "ALLOWED"
        audit_record["reason"] = f"policy=allow [{action_type}]"
        self._write_audit(audit_record)
        return True, False, audit_id, audit_record["reason"]

    def _write_audit(self, record: dict) -> None:
        """追加写入audit log文件"""
        try:
            with open(_AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[ForceActionGuard] audit write failed: {e}")

    def _enqueue_confirmation(self, record: dict) -> None:
        """将待确认记录写入 pending_approvals.json"""
        pending_file = os.path.expanduser(
            "~/freqtrade_console/pending_approvals.json"
        )
        try:
            pending = []
            if os.path.exists(pending_file):
                with open(pending_file, "r", encoding="utf-8") as f:
                    pending = json.load(f)
            pending.append(record)
            with open(pending_file, "w", encoding="utf-8") as f:
                json.dump(pending, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ForceActionGuard] enqueue failed: {e}")

    def get_policy(self, action_type: str) -> str:
        """查询某动作类型的当前策略"""
        return self.policy.get(action_type, "deny")

    def set_policy(self, action_type: str, policy: str) -> None:
        """动态修改某动作类型的策略"""
        if policy not in ("deny", "confirm", "pending", "allow"):
            raise ValueError(f"Invalid policy: {policy}")
        self.policy[action_type] = policy

    def load_recent_audits(self, limit: int = 100) -> list[dict]:
        """读取最近N条审计记录"""
        records = []
        if not os.path.exists(_AUDIT_LOG_FILE):
            return records
        try:
            with open(_AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    records.append(json.loads(line.strip()))
                except:
                    continue
        except Exception:
            pass
        return records


# ── 全局单例 ──────────────────────────────────────────────────────
force_guard = ForceActionGuard()
```

---

## 3. 集成到 console_server.py

### 3.1 导入（在文件顶部 import 区添加）

```python
# 新增导入（约在 console_server.py line 50-100 import 区）
try:
    from force_action_guard import ForceActionGuard, force_guard
    _FORCE_GUARD_AVAILABLE = True
except ImportError:
    _FORCE_GUARD_AVAILABLE = False
    force_guard = None
    class _DummyGuard:
        def check(self, *args, **kwargs):
            return True, False, "", "guard_unavailable"
    force_guard = _DummyGuard()
```

### 3.2 api_force_entry 改造（line 5613-5662）

**当前代码问题**: 直接发往bot，无任何人确认，无audit log。

```python
# 改造后的 api_force_entry()
@app.route("/api/force_entry", methods=["POST"])
def api_force_entry():
    """手动强制入场 — ForceActionGuard 保护"""
    data = request.json
    port = data.get("port")
    pair = data.get("pair")

    if not pair:
        return jsonify({"success": False, "error": "缺少参数"}), 400

    target_ports = data.get("ports")
    if target_ports in (None, [], "all") and str(port).lower() in ("", "0", "none", "all"):
        target_ports = list(PORTS.keys())
    elif target_ports in (None, []):
        target_ports = [port]
    if isinstance(target_ports, (str, int)):
        target_ports = [target_ports]

    direction = data.get("side", data.get("direction", "long")).lower()
    direction = "LONG" if direction in ("long", "Long", "LONG") else "SHORT"

    # ── ForceActionGuard 检查 ─────────────────────────────────────
    allowed, requires_confirm, audit_id, reason = force_guard.check(
        action_type="force_entry",
        pair=pair,
        direction=direction,
        source="api",
        bot_id=target_ports[0] if target_ports else 0,
        extra={
            "entry_tag": data.get("entry_tag", "manual_force_entry"),
            "leverage": data.get("leverage"),
            "stakeamount": data.get("stakeamount", data.get("stake_amount")),
        }
    )

    # 写 risk_audit_log（见 03_RISK_ACTION_AUDIT_LOG_SPEC.md）
    write_risk_audit_log(
        action="force_entry_request",
        pair=pair,
        direction=direction,
        source="api",
        bot_id=target_ports[0] if target_ports else 0,
        audit_id=audit_id,
        policy_decision=reason,
        allowed=allowed,
    )

    if not allowed:
        return jsonify({
            "success": False,
            "error": "force_entry blocked by policy",
            "reason": reason,
            "audit_id": audit_id,
            "requires_confirm": requires_confirm,
        }), 403

    if requires_confirm:
        return jsonify({
            "success": False,
            "error": "force_entry requires confirmation",
            "reason": reason,
            "audit_id": audit_id,
            "requires_confirm": True,
            "pending_approval_url": "/api/approvals/pending",
        }), 202  # 202 Accepted

    # ── 通过检查，执行 force_entry ─────────────────────────────────
    body = {
        "pair": pair,
        "side": direction.lower(),
        "entry_tag": data.get("entry_tag", "manual_force_entry"),
    }
    if data.get("stakeamount") is not None or data.get("stake_amount") is not None:
        body["stakeamount"] = data.get("stakeamount", data.get("stake_amount"))
    if data.get("leverage") is not None:
        body["leverage"] = data.get("leverage")

    results = {}
    ok_ports = []
    for p in target_ports:
        p = int(p)
        if p not in PORTS:
            results[p] = {"success": False, "error": "未知端口"}
            continue
        try:
            r = requests.post(
                f"{_get_rpc_url(p)}/api/v1/forceenter",
                auth=get_auth(p),
                json=body,
                proxies=NO_PROXY,
                timeout=10
            )
            results[p] = {
                "success": r.status_code == 200,
                "status": r.status_code,
                "audit_id": audit_id,
                "result": r.json() if r.status_code == 200 else r.text[:200]
            }
            if r.status_code == 200:
                ok_ports.append(p)
        except Exception as e:
            results[p] = {"success": False, "error": str(e)}

    write_risk_audit_log(
        action="force_entry_executed",
        pair=pair,
        audit_id=audit_id,
        executed_ports=ok_ports,
        results=results,
    )

    return jsonify({
        "success": len(ok_ports) > 0,
        "audit_id": audit_id,
        "ports": results,
    })
```

### 3.3 api_monitor_force_entry 改造（line 10159-10189）

**当前代码**: 已有冷却检查，但无audit log。

```python
@app.route("/api/monitor/force_entry", methods=["POST"])
def api_monitor_force_entry():
    """手动干预 - 强制开仓 — ForceActionGuard + Audit"""
    data = request.json or {}
    port = data.get("port")
    pair = data.get("pair")
    side = data.get("side", "long")

    if not port or not pair:
        return jsonify({"ok": False, "error": "缺少 port 或 pair"}), 400

    direction = "LONG" if side in ("long", "Long", "LONG") else "SHORT"
    pair_clean = pair.split(":")[0] if ":" in pair else pair

    # ── ForceActionGuard 检查 ─────────────────────────────────────
    allowed, requires_confirm, audit_id, reason = force_guard.check(
        action_type="force_entry",
        pair=pair_clean,
        direction=direction,
        source="monitor",
        bot_id=int(port),
    )
    write_risk_audit_log(
        action="force_entry_request",
        pair=pair_clean,
        direction=direction,
        source="monitor",
        bot_id=int(port),
        audit_id=audit_id,
        policy_decision=reason,
        allowed=allowed,
    )

    if not allowed:
        return jsonify({"ok": False, "error": f"force_entry blocked: {reason}", "audit_id": audit_id}), 403
    if requires_confirm:
        return jsonify({"ok": False, "error": "requires confirmation", "audit_id": audit_id, "requires_confirm": True}), 202

    # ── 冷却检查 ──────────────────────────────────────────────────
    cd = _check_bot_cooldown(int(port), pair_clean, direction)
    if cd.get("blocked"):
        write_risk_audit_log(action="force_entry_blocked", pair=pair_clean, reason=cd["reason"], audit_id=audit_id)
        return jsonify({"ok": False, "error": f"冷却拦截: {cd['reason']}", "audit_id": audit_id}), 429

    body = {"pair": pair}
    if side == "short":
        body["side"] = "short"
        body["enter_side"] = "short"
    if data.get("stakeamount") is not None:
        body["stakeamount"] = data.get("stakeamount")
    if data.get("leverage") is not None:
        body["leverage"] = data.get("leverage")

    r = _post_to_bot(int(port), "/api/v1/forceenter", body)

    write_risk_audit_log(action="force_entry_executed", pair=pair_clean, bot_id=int(port), audit_id=audit_id, result=r.get("ok"))

    return jsonify({**r, "audit_id": audit_id, "trade_id": r.get("data", {}).get("trade_id") if r.get("ok") else None})
```

### 3.4 api_monitor_force_exit 改造（line 10192-10229）

**当前代码**: 有写冷却，但无audit log。

```python
@app.route("/api/monitor/force_exit", methods=["POST"])
def api_monitor_force_exit():
    """手动干预 - 强制平仓 — ForceActionGuard + Audit"""
    data = request.json or {}
    port = data.get("port")
    trade_id = data.get("trade_id")

    if not port:
        return jsonify({"ok": False, "error": "缺少 port"}), 400

    # ── ForceActionGuard 检查 ─────────────────────────────────────
    allowed, requires_confirm, audit_id, reason = force_guard.check(
        action_type="force_exit",
        pair="",  # 平仓不针对特定pair，留空
        direction="",
        source="monitor",
        bot_id=int(port),
        extra={"trade_id": trade_id}
    )
    write_risk_audit_log(
        action="force_exit_request",
        source="monitor",
        bot_id=int(port),
        audit_id=audit_id,
        policy_decision=reason,
        allowed=allowed,
    )

    if not allowed:
        return jsonify({"ok": False, "error": f"force_exit blocked: {reason}", "audit_id": audit_id}), 403
    if requires_confirm:
        return jsonify({"ok": False, "error": "requires confirmation", "audit_id": audit_id, "requires_confirm": True}), 202

    # ── 获取持仓信息（写冷却用）──
    pre_info = {"pair": "", "direction": "LONG"}
    if trade_id:
        try:
            r_ps = requests.get(f"{_get_rpc_url(port)}/api/v1/status", auth=_get_bot_auth(int(port)), proxies=_NO_PROXY, timeout=10)
            if r_ps.status_code == 200:
                for pos in r_ps.json():
                    if str(pos.get("trade_id")) == str(trade_id):
                        pair_raw = pos.get("pair", "")
                        pre_info["pair"] = pair_raw.split(":")[0] if ":" in pair_raw else pair_raw
                        pre_info["direction"] = "SHORT" if pos.get("is_short", False) else "LONG"
                        break
        except Exception:
            pass

    body = {}
    if trade_id:
        body["tradeid"] = str(trade_id)

    r = _post_to_bot(int(port), "/api/v1/forceexit", body)

    # ── 写冷却 + Audit ───────────────────────────────────────────
    if r.get("ok") and pre_info["pair"]:
        _write_exit_cooldown_to_bot(int(port), pre_info["pair"], pre_info["direction"])

    write_risk_audit_log(
        action="force_exit_executed",
        pair=pre_info["pair"],
        direction=pre_info["direction"],
        bot_id=int(port),
        audit_id=audit_id,
        result=r.get("ok"),
    )

    return jsonify({**r, "audit_id": audit_id})
```

### 3.5 broadcast 函数内 force_entry/exit 分支（line 5087-5159）

**当前问题**: 无audit log。

在 `elif act == "force_exit":` 开头添加:
```python
            # ── ForceActionGuard + Audit ─────────────────────────────
            allowed, requires_confirm, audit_id, reason = force_guard.check(
                action_type="force_exit",
                pair="",
                direction="",
                source="broadcast",
                bot_id=port,
                extra={"trade_id": t_id, "exit_pct": exit_pct}
            )
            write_risk_audit_log(
                action="force_exit_request",
                source="broadcast",
                bot_id=port,
                audit_id=audit_id,
                policy_decision=reason,
                allowed=allowed,
            )
            if not allowed:
                print(f"[broadcast force_exit] BLOCKED by policy: {reason}")
                continue
```

在 `elif act == "force_entry":` 开头添加:
```python
            # ── ForceActionGuard + Audit ─────────────────────────────
            allowed, requires_confirm, audit_id, reason = force_guard.check(
                action_type="force_entry",
                pair=pair_clean,
                direction=entry_direction,
                source="broadcast",
                bot_id=port,
                extra={"add_pct": add_pct}
            )
            write_risk_audit_log(
                action="force_entry_request",
                pair=pair_clean,
                direction=entry_direction,
                source="broadcast",
                bot_id=port,
                audit_id=audit_id,
                policy_decision=reason,
                allowed=allowed,
            )
            if not allowed:
                print(f"[broadcast force_entry] BLOCKED by policy: {reason}")
                continue
```

---

## 4. write_risk_audit_log 函数（新增）

**新增文件**: `~/freqtrade_console/risk_audit_logger.py`
**导入**: `from risk_audit_logger import write_risk_audit_log`

```python
"""
Risk Audit Logger — 高风险操作结构化日志
=========================================
所有 force_entry / force_exit / dca_blocked / leverage_change 操作
必须通过此模块写入审计日志。

日志格式: JSON Lines（每行一条记录）
日志路径: ~/freqtrade_console/.audit_logs/risk_actions.jsonl
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Any

_AUDIT_DIR = os.path.expanduser("~/freqtrade_console/.audit_logs")
_AUDIT_FILE = os.path.join(_AUDIT_DIR, "risk_actions.jsonl")
os.makedirs(_AUDIT_DIR, exist_ok=True)


def write_risk_audit_log(
    action: str,
    pair: str = "",
    direction: str = "",
    source: str = "",
    bot_id: int | str = 0,
    audit_id: str = "",
    policy_decision: str = "",
    allowed: bool = False,
    reason: str = "",
    extra: dict | None = None,
    **kwargs
) -> str:
    """
    写入结构化审计日志

    字段定义详见: 03_RISK_ACTION_AUDIT_LOG_SPEC.md

    Returns:
        audit_id: 本次记录的审计ID
    """
    if not audit_id:
        audit_id = f"ra_{int(time.time()*1000)}"

    record = {
        "audit_id": audit_id,
        "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "action": action,
        "pair": pair,
        "direction": direction,
        "source": source,
        "bot_id": bot_id,
        "policy_decision": policy_decision,
        "allowed": allowed,
        "reason": reason,
        "extra": extra or {},
        **{k: v for k, v in kwargs.items() if v is not None},
    }

    try:
        with open(_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[RiskAuditLog] write failed: {e}")

    return audit_id
```

---

## 5. 补丁汇总表

| 编号 | 严重度 | 位置 | 问题 | 修复类型 |
|------|--------|------|------|---------|
| FAG-1 | P0 | console_server.py:5613 | `api_force_entry` 无guard/audit | 新增Guard |
| FAG-2 | P1 | console_server.py:10159 | `api_monitor_force_entry` 无audit | 新增audit |
| FAG-3 | P1 | console_server.py:10192 | `api_monitor_force_exit` 无audit | 新增audit |
| FAG-4 | P1 | console_server.py:5087 | `broadcast force_exit` 无guard/audit | 新增Guard |
| FAG-5 | P1 | console_server.py:5124 | `broadcast force_entry` 无guard/audit | 新增Guard |
| FAG-6 | P2 | console_server.py | `write_risk_audit_log` 缺失 | 新增模块 |
| FAG-7 | P2 | 新文件 | `force_action_guard.py` 缺失 | 新增模块 |
