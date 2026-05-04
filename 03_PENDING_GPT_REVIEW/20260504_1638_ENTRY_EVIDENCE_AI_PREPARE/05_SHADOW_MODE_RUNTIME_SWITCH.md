# 05_SHADOW_MODE_RUNTIME_SWITCH.md
# Shadow模式运行时开关草案

## 概述

运行时开关用于控制 EntryDecisionGate 和 ExitAIAgent 的行为模式：
- **shadow**（默认）：只记录日志，不执行任何交易操作
- **live**：可执行通知和日志记录（仍遵守只展示不执行原则）
- **dry**：完全不调用AI，只用规则检查

---

## runtime_switch.py 草案

```python
# bt_tools/runtime_switch.py  (草案文件，禁止直接写入实盘)
"""
运行时开关模块

使用方式:
  # 启动前设置环境变量
  export TIANLU_ENTRY_GATE_MODE=shadow   # 默认
  export TIANLU_EXIT_GATE_MODE=shadow   # 默认

  # 可选值:
  #   shadow - 只记录日志，不执行（默认）
  #   live   - 可执行通知（仍遵守只展示不执行原则）
  #   dry    - 完全不调用AI，只用规则检查
"""

import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# ── 入口模式 ────────────────────────────────────────────────
ENTRY_GATE_MODE = os.environ.get("TIANLU_ENTRY_GATE_MODE", "shadow").lower()
EXIT_GATE_MODE  = os.environ.get("TIANLU_EXIT_GATE_MODE", "shadow").lower()

# ── 有效模式 ────────────────────────────────────────────────
VALID_MODES = {"shadow", "live", "dry"}

def _validate_mode(mode: str, name: str) -> str:
    """验证模式值，无效时降级为shadow"""
    if mode not in VALID_MODES:
        print(f"[RuntimeSwitch] 警告: {name}='{mode}' 无效，降级为 shadow")
        return "shadow"
    return mode

ENTRY_GATE_MODE = _validate_mode(ENTRY_GATE_MODE, "TIANLU_ENTRY_GATE_MODE")
EXIT_GATE_MODE  = _validate_mode(EXIT_GATE_MODE,  "TIANLU_EXIT_GATE_MODE")

# ── 模式判断函数 ────────────────────────────────────────────

def is_shadow_mode() -> bool:
    """是否Shadow模式（只记录，不执行）"""
    return ENTRY_GATE_MODE == "shadow" and EXIT_GATE_MODE == "shadow"

def is_live_mode() -> bool:
    """是否Live模式（可通知，不执行）"""
    return ENTRY_GATE_MODE == "live" or EXIT_GATE_MODE == "live"

def is_dry_mode() -> bool:
    """是否Dry模式（不调用AI）"""
    return ENTRY_GATE_MODE == "dry" and EXIT_GATE_MODE == "dry"

def get_entry_mode() -> str:
    return ENTRY_GATE_MODE

def get_exit_mode() -> str:
    return EXIT_GATE_MODE

# ── 日志函数 ────────────────────────────────────────────────

def _log_prefix(tag: str) -> str:
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    return f"{ts} [{tag}]"

def log_entry_verdict(verdict: str, pair: str, direction: str, score: int, confidence: float):
    """
    记录入场决策到日志（Shadow模式）

    Shadow模式: 只记录，不阻止
    Live模式:   记录 + 可通知
    Dry模式:    记录但不调用AI
    """
    prefix = _log_prefix("EntryGate")
    mode = get_entry_mode()

    if mode == "shadow":
        print(f"{prefix} {pair} {direction} → {verdict} (score={score}, conf={confidence:.2f}) [SHADOW]")
    elif mode == "live":
        print(f"{prefix} {pair} {direction} → {verdict} (score={score}, conf={confidence:.2f}) [LIVE]")
    else:  # dry
        print(f"{prefix} {pair} {direction} → {verdict} (score={score}) [DRY]")

    # 写入日志文件
    _write_entry_log({
        "ts": int(datetime.now(timezone(timedelta(hours=8))).timestamp()),
        "mode": mode,
        "pair": pair,
        "direction": direction,
        "verdict": verdict,
        "score": score,
        "confidence": confidence
    })


def log_exit_recommendation(action: str, pair: str, confidence: float, speech: str):
    """
    记录出山AI出场建议到日志（Shadow模式）

    Shadow模式: 只记录，不执行
    Live模式:   记录 + 可通知
    Dry模式:    记录但不调用AI
    """
    prefix = _log_prefix("ExitAI")
    mode = get_exit_mode()

    if mode == "shadow":
        print(f"{prefix} {pair} → action={action}, confidence={confidence:.2f} [SHADOW]")
        print(f"{prefix} speech={speech[:100]}")
    elif mode == "live":
        print(f"{prefix} {pair} → action={action}, confidence={confidence:.2f} [LIVE]")
        print(f"{prefix} speech={speech[:100]}")
    else:  # dry
        print(f"{prefix} {pair} → action={action} [DRY]")

    _write_exit_log({
        "ts": int(datetime.now(timezone(timedelta(hours=8))).timestamp()),
        "mode": mode,
        "pair": pair,
        "action": action,
        "confidence": confidence,
        "speech": speech
    })


# ── 日志文件写入 ────────────────────────────────────────────

_LOG_DIR = Path("/tmp/tianlu_gate_logs")
_LOG_DIR.mkdir(exist_ok=True)

_ENTRY_LOG_FILE = _LOG_DIR / "entry_decisions.json"
_EXIT_LOG_FILE  = _LOG_DIR / "exit_recommendations.json"

def _write_entry_log(entry: dict):
    """写入入场决策日志"""
    try:
        logs = []
        if _ENTRY_LOG_FILE.exists():
            logs = json.loads(_ENTRY_LOG_FILE.read_text())
        logs.append(entry)
        logs = logs[-2000:]  # 只保留最近2000条
        _ENTRY_LOG_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"[RuntimeSwitch] 入场日志写入失败: {e}")

def _write_exit_log(exit_rec: dict):
    """写入出场建议日志"""
    try:
        logs = []
        if _EXIT_LOG_FILE.exists():
            logs = json.loads(_EXIT_LOG_FILE.read_text())
        logs.append(exit_rec)
        logs = logs[-2000:]
        _EXIT_LOG_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"[RuntimeSwitch] 出场日志写入失败: {e}")

# ── 状态报告 ────────────────────────────────────────────────

def get_gate_status() -> dict:
    """
    返回当前Gate状态（供console_server API展示）
    """
    return {
        "entry_mode": ENTRY_GATE_MODE,
        "exit_mode":  EXIT_GATE_MODE,
        "is_shadow": is_shadow_mode(),
        "is_live":   is_live_mode(),
        "is_dry":    is_dry_mode(),
        "entry_log_file": str(_ENTRY_LOG_FILE),
        "exit_log_file":  str(_EXIT_LOG_FILE),
        "log_count": {
            "entries": len(json.loads(_ENTRY_LOG_FILE.read_text()) or "[]")
                       if _ENTRY_LOG_FILE.exists() else 0,
            "exits":   len(json.loads(_EXIT_LOG_FILE.read_text()) or "[]")
                       if _EXIT_LOG_FILE.exists() else 0,
        }
    }

# ── 初始化日志 ──────────────────────────────────────────────
print(f"[RuntimeSwitch] 初始化: ENTRY={ENTRY_GATE_MODE}, EXIT={EXIT_GATE_MODE}, SHADOW={is_shadow_mode()}")
```

---

## API 端点草案（console_server.py 新建）

```python
# console_server.py（草案，新建端点）
@app.route("/api/gate/status", methods=["GET"])
def api_gate_status():
    """
    获取运行时Gate状态
    GET /api/gate/status

    返回:
      {
        "entry_mode": "shadow",
        "exit_mode": "shadow",
        "is_shadow": true,
        "is_live": false,
        "is_dry": false,
        "entry_log_file": "/tmp/tianlu_gate_logs/entry_decisions.json",
        "exit_log_file": "/tmp/tianlu_gate_logs/exit_recommendations.json",
        "log_count": {"entries": 123, "exits": 45}
      }
    """
    from bt_tools.runtime_switch import get_gate_status
    return jsonify(get_gate_status())


@app.route("/api/gate/mode", methods=["GET", "POST"])
def api_gate_mode():
    """
    GET: 读取当前模式
    POST: 更新模式（谨慎使用）
    """
    from bt_tools.runtime_switch import ENTRY_GATE_MODE, EXIT_GATE_MODE
    if request.method == "GET":
        return jsonify({
            "entry_mode": ENTRY_GATE_MODE,
            "exit_mode": EXIT_GATE_MODE,
        })
    # POST: 动态切换模式（谨慎使用）
    data = request.get_json() or {}
    new_entry = data.get("entry_mode", ENTRY_GATE_MODE)
    new_exit  = data.get("exit_mode",  EXIT_GATE_MODE)
    print(f"[GateMode] 切换: entry={ENTRY_GATE_MODE}→{new_entry}, exit={EXIT_GATE_MODE}→{new_exit}")
    # 注意: POST只打印日志，实际切换需要重启进程或重新设置环境变量
    return jsonify({"updated": True, "entry_mode": new_entry, "exit_mode": new_exit})
```

---

## 环境变量配置

```bash
# ~/.bashrc 或 ~/.zshrc 或启动脚本

# EntryDecisionGate 模式（默认 shadow）
export TIANLU_ENTRY_GATE_MODE=shadow

# ExitAIAgent 模式（默认 shadow）
export TIANLU_EXIT_GATE_MODE=shadow

# 可选组合:
#   shadow + shadow  → 纯记录模式（默认，最安全）
#   dry + dry        → 不调用AI，只用规则检查
#   live + live      → 可通知（仍遵守只展示不执行原则）
```

---

## 模式切换决策树

```
收到入场信号
  │
  ├─ DRY模式? → 只用V6.5规则检查，不调用AI
  │              → 记录日志，返回
  │
  ├─ SHADOW模式（默认）?
  │   ├─ L4 S/R检查拒绝 → 记录日志，不阻止，继续
  │   ├─ 综合评分<50   → 记录日志，不阻止，继续
  │   └─ 综合评分>=50  → 记录ALLOW日志，不阻止
  │
  └─ LIVE模式?
      ├─ AI verdict=EXECUTE → 记录+通知，可请求9099确认
      └─ AI verdict=FORBIDDEN → 记录+通知，可阻止

收到持仓评估
  │
  ├─ DRY模式? → 跳过出山AI
  │
  ├─ SHADOW模式（默认）?
  │   ├─ action=EXIT_FULL → 记录日志，不执行
  │   ├─ action=OBSERVE   → 记录日志，继续持有
  │   └─ action=HUNT_REVERSE → 记录+30分钟冷却，不执行
  │
  └─ LIVE模式?
      └─ 所有action → 记录+通知，由9099执行链路确认后才执行
```

---

## 日志查看方法

```bash
# 查看入场决策日志
tail -f /tmp/tianlu_gate_logs/entry_decisions.json | python3 -m json.tool

# 查看出场建议日志
tail -f /tmp/tianlu_gate_logs/exit_recommendations.json | python3 -m json.tool

# 统计最近1小时的shadow记录
cat /tmp/tianlu_gate_logs/entry_decisions.json | \
  python3 -c "import sys,json; logs=json.load(sys.stdin); \
  now=int(__import__('time').time()); \
  recent=[l for l in logs if now-l['ts']<3600]; \
  print(f'最近1小时: {len(recent)}条, SHADOW: {sum(1 for l in recent if l[\"mode\"]==\"shadow\")}')"
```

---

## 禁止事项

- **禁止**在shadow模式下执行任何交易操作
- **禁止**在生产环境使用 `live` 模式而不经过爸确认
- **禁止**POST修改模式后不记录变更日志
