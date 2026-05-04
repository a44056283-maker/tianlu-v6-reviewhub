# L5晋级链路补丁 #07 — L5 禁止直接写Runtime政策

> 生成时间：2026-05-04 15:00
> 状态：等待翰林院GPT审核 → 立即生效（Policy强制）

---

## 一、核心政策声明

```
╔══════════════════════════════════════════════════════════════╗
║  L5 ABSOLUTE RULE: NO DIRECT RUNTIME WRITE                  ║
║                                                              ║
║  L5生成的任何候选参数：                                       ║
║  • 绝对禁止直接写入实盘runtime                               ║
║  • 绝对禁止通过API修改bot参数                                ║
║  • 绝对禁止调用 force_entry / force_exit                    ║
║                                                              ║
║  合规路径（唯一合法路径）：                                   ║
║  L5影子实验室 → L5CandidateRegistry → 人工确认 → apply     ║
║  → runtime                                                   ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 二、违规检测机制

### 2.1 Runtime写入检测器

```python
#!/usr/bin/env python3
"""
L5 Runtime Write Detector — L5实盘写入违规检测器

此模块在 console_server 的关键路径上插入检测钩子，
任何来自 l5_evolution_lab 的参数写入请求都会被拦截和记录。

文件位置: ~/freqtrade_console/l5_evolution_lab/l5_runtime_guard.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent))


BASE = Path("/Users/luxiangnan/freqtrade_console/l5_evolution_lab")
GUARD_LOG = BASE / "logs" / "l5_runtime_guard.log"
VIOLATION_LOG = BASE / "l5_violations.jsonl"
VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)


class L5RuntimeGuard:
    """
    L5实盘写入守卫

    检测规则：
    1. 任何来自 L5 目录模块的 runtime 写入请求 → BLOCK + 告警
    2. 任何未经 L5CandidateRegistry 批准的写入 → BLOCK + 告警
    3. 任何未经人工确认的候选参数写入 → BLOCK + 告警

    告警渠道：
    - 飞书Webhook（尚书省）
    - 本地violation日志
    - console_server日志
    """

    APPROVED_SOURCES = {
        "console_server",
        "bot_manager",
        "manual_trader",
        "l5_candidate_registry:apply_to_live",  # 唯一批准的L5路径
    }

    # 禁止的写入来源（绝对禁止）
    BLOCKED_SOURCES = {
        "l5_evolution_lab",
        "m4_m5_shadow_lab",
        "l5_autopilot",
        "l5_strategy_generator",
        "l5_rule_evolution",
        "l5_auto_upgrade",
    }

    def __init__(self):
        self._init_log()

    def _init_log(self) -> None:
        GUARD_LOG.parent.mkdir(parents=True, exist_ok=True)
        VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)

    def check_write(
        self,
        source_module: str,
        candidate_id: Optional[str] = None,
        target_port: Optional[str] = None,
        params: Optional[dict] = None,
        operation: str = "write_params",
    ) -> dict[str, Any]:
        """
        检查runtime写入请求是否合规。

        调用方式（在 console_server.py 关键路径中）：
            guard = L5RuntimeGuard()
            result = guard.check_write(
                source_module=__name__,
                candidate_id="xxx",
                target_port="9090",
                params=params,
            )
            if not result["allowed"]:
                raise PermissionError(result["message"])

        Returns:
            {
                "allowed": bool,
                "guard_id": str,
                "message": str,
                "violation": bool,
                "action": "allow" | "block" | "warn"
            }
        """
        import uuid
        guard_id = str(uuid.uuid4())[:8]
        ts = int(time.time())

        # ---- 检测规则 ----

        violation = False
        blocked_reason = ""
        action = "allow"

        # 规则1：来自禁止来源
        if source_module in self.BLOCKED_SOURCES:
            violation = True
            blocked_reason = f"source_module={source_module} is in BLOCKED_SOURCES"
            action = "block"

        # 规则2：非批准来源且非l5_candidate_registry路径
        elif source_module not in self.APPROVED_SOURCES:
            # 检查是否通过Registry的apply_to_live路径
            if source_module == "l5_candidate_registry":
                if not candidate_id:
                    violation = True
                    blocked_reason = "l5_candidate_registry write without candidate_id"
                    action = "block"
                else:
                    # 进一步检查candidate状态
                    from l5_candidate_registry import L5CandidateRegistry, CandidateStatus
                    reg = L5CandidateRegistry()
                    pending = reg.list_pending()
                    approved_ids = [c["candidate_id"] for c in reg.list_approved()]
                    if candidate_id not in approved_ids:
                        violation = True
                        blocked_reason = f"candidate_id={candidate_id} not in approved list"
                        action = "block"

        # ---- 记录 ----
        entry = {
            "guard_id": guard_id,
            "ts": ts,
            "source_module": source_module,
            "candidate_id": candidate_id,
            "target_port": target_port,
            "operation": operation,
            "action": action,
            "violation": violation,
            "blocked_reason": blocked_reason,
        }

        self._log(guard_id, entry, violation)

        if violation:
            self._send_alert(entry)

        return {
            "allowed": action == "allow",
            "guard_id": guard_id,
            "message": f"[L5 GUARD] {action.upper()}: {blocked_reason}" if violation else "[L5 GUARD] ALLOWED",
            "violation": violation,
            "action": action,
        }

    def _log(self, guard_id: str, entry: dict, violation: bool) -> None:
        """写日志。"""
        ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["ts"]))
        log_line = f"[{ts_str}] [{guard_id}] {entry['source_module']} → {entry['operation']} port={entry.get('target_port')} cand={entry.get('candidate_id')} [{entry['action'].upper()}]"
        if violation:
            log_line += f" REASON: {entry['blocked_reason']}"

        with open(GUARD_LOG, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

        if violation:
            with open(VIOLATION_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _send_alert(self, entry: dict) -> None:
        """发送飞书告警。"""
        import urllib.request

        msg = (
            f"🚨 [L5安全告警] 违规写入实盘Runtime\n"
            f"模块: {entry['source_module']}\n"
            f"端口: {entry.get('target_port', 'N/A')}\n"
            f"候选ID: {entry.get('candidate_id', 'N/A')}\n"
            f"原因: {entry['blocked_reason']}\n"
            f"时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry['ts']))}\n"
            f"GuardID: {entry['guard_id']}\n"
            f"处理: BLOCKED（写入已阻止）"
        )

        webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/e6151d8f-bed3-474f-af25-9a8b130900b0"
        try:
            req = urllib.request.Request(
                webhook,
                data=json.dumps({"msg_type": "text", "content": {"text": msg}}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=5)
        except Exception:
            pass  # 告警失败不阻塞主流程


# ---- 全局单例 ----
_guard: Optional[L5RuntimeGuard] = None


def get_guard() -> L5RuntimeGuard:
    global _guard
    if _guard is None:
        _guard = L5RuntimeGuard()
    return _guard


# ---- 便捷装饰器 ----

def l5_guard(operation: str = "write_params"):
    """
    装饰器：保护任何runtime写入函数。

    用法：
        @l5_guard("update_strategy")
        def update_bot_params(bot_id, params):
            # 实际写入逻辑
            pass
    """
    import functools
    import inspect

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            guard = get_guard()
            sig = inspect.signature(func)
            # 尝试提取关键参数
            source = kwargs.get("source_module", __name__)
            cand_id = kwargs.get("candidate_id")
            port = kwargs.get("target_port") or kwargs.get("port") or kwargs.get("bot_id")
            params = kwargs.get("params") or kwargs.get("strategy_params")

            result = guard.check_write(
                source_module=source,
                candidate_id=cand_id,
                target_port=str(port) if port else None,
                params=params,
                operation=operation,
            )
            if not result["allowed"]:
                raise PermissionError(result["message"])
            return func(*args, **kwargs)

        return wrapper
    return decorator
```

---

## 三、在console_server.py中插入守卫

在 `console_server.py` 的参数写入路径中插入检测钩子：

```python
# === L5 Runtime Guard 插入点 ===
# 在 console_server.py 的 /api/strategy/apply-params 端点中
# 路径大约在 7000-8000 行附近（以实际文件为准）

# 在参数写入前插入：
try:
    from l5_evolution_lab.l5_runtime_guard import get_guard
    guard = get_guard()
    result = guard.check_write(
        source_module="console_server_api",
        target_port=port,
        params=params,
        operation="apply_strategy_params",
    )
    if not result["allowed"]:
        return {
            "ok": False,
            "error": f"[L5 SECURITY] {result['message']}",
            "guard_id": result["guard_id"],
            "remediation": "Use L5CandidateRegistry + human approval before writing to runtime",
        }
except ImportError:
    pass  # Guard未安装，降级放行（仅警告）
```

---

## 四、L5CandidateRegistry.apply_to_live() 内置检查

在 `l5_candidate_registry.py` 的 `apply_to_live()` 方法中：

```python
def apply_to_live(self, candidate_id: str, target_port: str, dry_run: bool = False):
    """
    将人工批准的候选参数写入实盘runtime。

    这是唯一合法的L5写runtime路径。
    所有其他L5直接写runtime的尝试都会被 l5_runtime_guard 拦截。
    """
    with sqlite3.connect(self.db_path) as conn:
        row = conn.execute("""
            SELECT status, runtime_written, params_json, human_approver
            FROM l5_candidates WHERE candidate_id = ?
        """, (candidate_id,)).fetchone()

        if not row:
            return {"ok": False, "error": "candidate not found"}

        status, written, params_json, approver = row

        # ---- 三重安全检查 ----

        # 检查1：必须在approved状态
        if status != CandidateStatus.APPROVED.value:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id : {candidate_id}\n"
                f"  current status: {status}\n"
                f"  required status: {CandidateStatus.APPROVED.value}\n"
                f"  human_approver: {approver or 'NONE'}\n"
                f"Reason: L5 candidates must be approved by human before writing to runtime."
            )

        # 检查2：必须有人工批准人
        if not approver:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id: {candidate_id}\n"
                f"  status: {status}\n"
                f"  human_approver: {approver}\n"
                f"Reason: No human approval found. L5 cannot self-approve."
            )

        # 检查3：必须未被写过
        if written:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id: {candidate_id}\n"
                f"  runtime_written: {written}\n"
                f"Reason: Candidate already written to runtime. Duplicate write blocked."
            )

        # ---- 通过所有检查，写入runtime ----
        if dry_run:
            return {"ok": True, "dry_run": True, "params": json.loads(params_json)}

        # 调用console_server API写runtime
        from l5_apply_runtime import apply_params_via_api
        result = apply_params_via_api(candidate_id, target_port, json.loads(params_json))

        if result.get("ok"):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE l5_candidates
                    SET runtime_written=1, ts_runtime=?, applied_to_port=?
                    WHERE candidate_id=?
                """, (int(time.time()), target_port, candidate_id))
                conn.commit()
            self._audit(candidate_id, "runtime_written", "system", {
                "target_port": target_port,
                "result": result,
            })

        return result
```

---

## 五、违规处理流程

```
检测到违规写入
    ↓
L5RuntimeGuard.check_write() 返回 allowed=False
    ↓
PermissionError 抛出（写入被拦截）
    ↓
飞书告警发送至尚书省
    ↓
违规日志写入 l5_violations.jsonl
    ↓
console_server 返回 403 Forbidden
    ↓
翰林院审查违规日志
    ↓
决定：忽略（误报）/ 修复L5模块 / 通知爸
```

---

## 六、禁止清单

以下L5模块/功能**绝对禁止**直接写runtime：

| 模块/功能 | 禁止原因 |
|----------|---------|
| `m4_m5_shadow_lab.py` | 影子实验室，只读 |
| `l5_autopilot` | 禁止L5自动驾驶 |
| `l5_strategy_generator` | 禁止生成器直接写参数 |
| `l5_rule_evolution` | 禁止规则演化直接升级参数 |
| `l5_auto_upgrade` | 禁止自动晋级 |
| 任何 `force_entry` / `force_exit` 调用 | 禁止强制下单 |
| `whale_alert` 自动跟单 | 禁止跟单写入 |

---

## 七、合规路径图

```
L5影子实验模块
(m4_m5_shadow_lab.py 等 — 只读)
        ↓ 读取数据，生成候选
L5CandidateRegistry.register()
        ↓ 写入pending状态
翰林院审查台（人工）
        ↓ 爸点击"批准"
L5CandidateRegistry.approve()
        ↓ 状态改为 approved
翰林院点击"应用到实盘"
        ↓
L5CandidateRegistry.apply_to_live()
        ↓ 三重安全检查
        ↓ (PermissionError 如果不合规)
console_server API
        ↓
runtime 参数更新（bot重启生效）
        ↓
runtime_written = 1
        ↓
审计日志记录完成
```

---

## 八、违规日志格式

```jsonl
{"guard_id":"a1b2c3d4","ts":1746345600,"source_module":"l5_autopilot","candidate_id":null,"target_port":"9090","operation":"write_params","action":"block","violation":true,"blocked_reason":"source_module=l5_autopilot is in BLOCKED_SOURCES"}
```

---

## 九、监察接口

翰林院可通过以下接口查看L5合规状态：

```bash
# 查看违规历史
cat ~/freqtrade_console/l5_evolution_lab/logs/l5_runtime_guard.log

# 查看所有违规记录（JSONL）
cat ~/freqtrade_console/l5_evolution_lab/l5_violations.jsonl | python3 -m json.tool

# 检查候选Registry状态
python3 ~/freqtrade_console/l5_evolution_lab/l5_candidate_registry.py summary

# 手动触发晋级闸门检查
python3 ~/freqtrade_console/l5_evolution_lab/l5_promotion_gate.py
```
