# 04_CHUSHAN_AI_INTEGRATION_DRAFT.md
# 出山AI调用接入草案

## 现有代码引用

| 功能 | 文件:行号 |
|------|----------|
| ExitAIAgent 类定义 | `console_server.py:15457` |
| `SYSTEM_PROMPT` | `console_server.py:15475-15555` |
| `__init__()` API Key加载 | `console_server.py:15886-15900` |
| `analyze()` 持仓评估方法 | `console_server.py:15920` |
| `_get_m2_sr_for_chushan()` | `console_server.py:15903` |
| `_build_prompt()` | `console_server.py:16061` |
| 出山AI页面路由 | `console_server.py:2855` |
| 出山AI飞书通知 | `console_server.py:11908` `_send_feishu_exit_ai_alert()` |
| ExitAI状态API | `console_server.py:30416` `/api/hero_cards/exit_ai_status` |

---

## 出山AI职责边界

> **核心原则：只展示，不执行**
>
> 出山AI职责（console_server.py:15461-15473）：
> 1. 动态止盈（V6.5 P1/P2/P3档位协调）
> 2. 回撤保护（从峰值回撤N%时锁利）
> 3. ATR移动止损（追踪动态强平线上方）
> 4. 多时线动量衰竭出场
> 5. 反转猎杀（大户量五指标全确认才执行）
>
> **禁止**：做DCA补仓建议（console_server.py:15492）

---

## 出山AI MiniMax API 调用草案

```python
# 出山AI调用草案（禁止直接写入实盘文件）
# 引用: console_server.py:15457-16000 ExitAIAgent

import ssl
import json
import urllib.request
import urllib.error
import os
from pathlib import Path

# ── 配置（从现有代码引用）────────────────────────────────────
_CHUSHAN_MINIMAX_URL = "https://api.minimaxi.com/v1/chat/completions"
_CHUSHAN_MODEL = "MiniMax-M2.7-highspeed"  # console_server.py:15889
_CHUSHAN_MAX_TOKENS = 8192
_CHUSHAN_TEMPERATURE = 0.3

# ── API Key: 禁止硬编码！ ──────────────────────────────────
def _get_minimax_key() -> str:
    """从环境变量读取 MiniMax API Key（禁止硬编码）"""
    key = os.environ.get("MINIMAX_API_KEY", "")
    if not key:
        keys_file = Path(__file__).parent / "tianyan_keys.json"
        if keys_file.exists():
            data = json.loads(keys_file.read_text())
            key = data.get("minimax", "")
    return key


def call_chushan_minimax(
    prompt: str,
    system_prompt: str,
    api_key: str = None
) -> dict:
    """
    调用出山AI MiniMax API

    参数:
      prompt: 用户输入（包含持仓数据 + M2/M3/M4 evidence）
      system_prompt: 系统提示词（出山V3.1角色定义）
      api_key: API Key（从环境变量读取）

    返回:
      {action, confidence, reason, speech, partial_reasons, data_gaps}

    重要: 只展示建议，不执行任何交易操作
    """
    key = api_key or _get_minimax_key()
    if not key:
        print("[出山AI] 警告: MINIMAX_API_KEY 未设置，AI分析跳过")
        return {"action": "SKIP", "confidence": 0.0, "reason": "API Key未设置",
                "speech": "", "partial_reasons": [], "data_gaps": []}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }

    payload = {
        "model": _CHUSHAN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt +
             "\n\n[重要]你必须且只能回复JSON,不要包含任何其他文字或markdown."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": _CHUSHAN_MAX_TOKENS,
        "temperature": _CHUSHAN_TEMPERATURE,
    }

    body = json.dumps(payload).encode("utf-8")
    CTX = ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(
            _CHUSHAN_MINIMAX_URL,
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60, context=CTX) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _parse_chushan_response(content)

    except Exception as e:
        print(f"[出山AI] API调用异常: {e}")
        return {"action": "ERROR", "confidence": 0.0, "reason": str(e),
                "speech": "", "partial_reasons": [], "data_gaps": []}


def _parse_chushan_response(raw: str) -> dict:
    """解析出山AI返回的JSON"""
    try:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {
                "action": data.get("action", "UNKNOWN"),
                "confidence": float(data.get("confidence", 0)),
                "reason": data.get("reason", ""),
                "speech": data.get("speech", data.get("ai_speech", "")),
                "partial_reasons": data.get("partial_reasons", []),
                "data_gaps": data.get("data_gaps", []),
                "raw_response": raw
            }
    except json.JSONDecodeError:
        print(f"[出山AI] JSON解析失败: {raw[:200]}")
    return {"action": "PARSE_ERROR", "confidence": 0.0, "reason": "JSON解析失败",
            "speech": raw[:200], "partial_reasons": [], "data_gaps": []}
```

---

## 出山AI输入：持仓数据 + M2/M3/M4 Evidence

### 输入数据格式

```json
{
  "position": {
    "pair": "BTC/USDT",
    "direction": "LONG",
    "entry_price": 92000.00,
    "current_price": 96500.00,
    "profit_percent": 4.89,
    "unrealized_pl": 489.00,
    "leverage": 10,
    "amount": 1000.0,
    "open_date": 1746300000
  },
  "m2_sr_evidence": {
    "has_sr": true,
    "sr_type": "support",
    "sr_price": 95234.56,
    "sr_touches": 4,
    "dist_to_price": 1.33
  },
  "m3_evidence": {
    "atr_15m": 45.67,
    "atr_1h": 98.23,
    "giant_count": 2,
    "volatility_level": "HIGH"
  },
  "m4_evidence": {
    "rsi_15m": 68.5,
    "rsi_1h": 62.3,
    "oi_change_pct": 5.2,
    "oi_signal": "INCREASING"
  },
  "l5_evidence": {
    "scene_type": "BREAKOUT",
    "liquidation_wave": "LONG",
    "fear_greed": 65
  },
  "v65_p_status": {
    "p1_triggered": false,
    "p2_triggered": false,
    "p3_triggered": false,
    "current_profit_percent": 4.89
  }
}
```

---

## 出山AI输出格式

```json
{
  "action": "OBSERVE",
  "confidence": 0.72,
  "reason": "回撤保护观察：盈利回撤10%+资金流净流出持续2个15m周期",
  "speech": "BTC/USDT持仓从峰值回撤10%，1h RSI 62.3偏多但15m资金流连续2根净流出，建议观察30分钟，不急于止盈。",
  "partial_reasons": [
    "回撤幅度10% + 资金流净流出持续2个15m周期",
    "RSI1h 62.3 未超卖，多头结构仍完整"
  ],
  "data_gaps": [],
  "atr_stop_loss": 95800.00,
  "suggested_exit_percent": 0,
  "cooldown_minutes": 30
}
```

### Action 枚举值

| action | 含义 | 置信度要求 | 执行方式 |
|--------|------|-----------|---------|
| EXIT_FULL | 立即全平 | >= 50% | **只通知**，写日志，人工确认 |
| EXIT_HALF | 半仓止盈 | >= 50% | **只通知**，写日志，人工确认 |
| REDUCE_HALF | 减半仓 | >= 50% | **只通知**，写日志，人工确认 |
| OBSERVE | 观察 | 任何 | 写日志 |
| HOLD | 继续持有 | 任何 | 写日志 |
| ATR_STOP | ATR止损触发 | 任何 | **只通知**，写日志，人工确认 |
| HUNT_REVERSE | 反转猎杀 | >= 70% | **只通知+30分钟冷却**，人工确认 |
| SKIP | 跳过（无建议） | - | 写日志 |

---

## Shadow 模式：只展示不执行

```python
# 出山AI Shadow模式实现
# 重要: 出山AI建议只写日志，不直接平仓

EXIT_GATE_MODE = os.environ.get("TIANLU_EXIT_GATE_MODE", "shadow")

def evaluate_position_chushan(position: dict, m2, m3, m4, l5) -> dict:
    """
    出山AI持仓评测（Shadow模式）

    重要原则（console_server.py:15494-15505）:
    1. 出山AI只能生成出场/减险候选，不能阻止V6.5 P3全平
    2. 所有执行决策必须先确认机器人端该持仓仍存在
    3. execute=true 只表示请求9099执行链路，不代表已完成平仓
    4. **shadow模式：只展示建议，写日志，不执行任何操作**
    """
    if EXIT_GATE_MODE == "dry":
        print(f"[出山AI][DRY] {position['pair']} 不调用AI")
        return {"action": "DRY_MODE", "confidence": 0.0, "reason": "dry模式跳过AI"}

    # 组装提示词（复用 ExitAIAgent._build_prompt()）
    prompt = _build_chushan_prompt(position, m2, m3, m4, l5)
    system_prompt = ExitAIAgent.SYSTEM_PROMPT  # console_server.py:15475

    result = call_chushan_minimax(prompt, system_prompt)

    # Shadow模式：只写日志，不执行
    _log_chushan_result(position, result, mode=EXIT_GATE_MODE)

    return result


def _log_chushan_result(position: dict, result: dict, mode: str):
    """
    记录出山AI结果（Shadow模式）

    禁止:
    - 在shadow模式下调用机器人平仓API
    - 在shadow模式下修改机器人参数
    - 在shadow模式下执行反转猎杀
    """
    action = result.get("action", "UNKNOWN")
    confidence = result.get("confidence", 0)
    speech = result.get("speech", "")
    pair = position.get("pair", "")

    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

    if mode == "shadow":
        print(f"{ts} [出山AI][SHADOW] {pair} → action={action}, confidence={confidence:.2f}")
        print(f"{ts} [出山AI][SHADOW] reason={result.get('reason', '')}")
        print(f"{ts} [出山AI][SHADOW] speech={speech[:150]}")
        # 写日志文件（shadow模式）
        _write_chushan_log(pair, action, confidence, speech, result.get("reason", ""))
        # 禁止执行任何交易
    else:
        # live模式：可以通知（但仍需遵守只展示不执行原则）
        print(f"{ts} [出山AI][LIVE] {pair} → action={action}, confidence={confidence:.2f}")


def _write_chushan_log(pair: str, action: str, confidence: float,
                       speech: str, reason: str):
    """写入出山AI日志文件（只记录，不执行）"""
    log_file = Path("/tmp/tianlu_chushan_log.json")
    try:
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        logs.append({
            "ts": int(time.time()),
            "pair": pair,
            "action": action,
            "confidence": confidence,
            "reason": reason,
            "speech": speech,
            "mode": "shadow"
        })
        # 只保留最近1000条
        logs = logs[-1000:]
        log_file.write_text(json.dumps(logs, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"[出山AI] 日志写入失败: {e}")
```

---

## 反转猎杀场景处理

```python
# 反转猎杀（HUNT_REVERSE）特殊处理
# 引用: console_server.py:15469 触发条件

def handle_hunt_reverse(position: dict, result: dict) -> dict:
    """
    反转猎杀场景处理（Shadow模式）

    触发条件（全部满足才执行）:
    1. 持仓盈利（非浮亏）
    2. A-E五个反转指标全部确认
    3. 系统层面检测到>=2个Bot同时出现反转信号

    重要（console_server.py:15498）:
    - 必须先全平成功，再由9099按V6.5反向硬门控确认新方向
    - 不得直接市价反手
    - shadow模式：只记录，不执行
    """
    pair = position.get("pair", "")
    action = result.get("action", "")

    if action != "HUNT_REVERSE":
        return result

    print(f"[出山AI][HUNT_REVERSE][SHADOW] {pair} 反转猎杀信号已记录")
    print(f"[出山AI][HUNT_REVERSE][SHADOW] speech={result.get('speech', '')[:200]}")

    # B3反转猎杀写30分钟冷却（console_server.py:15444）
    # shadow模式：只记录，不实际写入冷却
    _write_hunt_cooldown(pair, minutes=30)

    return result


def _write_hunt_cooldown(pair: str, minutes: int):
    """写入反转猎杀冷却记录（shadow模式：只记录，不实际触发冷却）"""
    cooldown_file = Path(f"/tmp/tianlu_hunt_cooldown_{pair.replace('/','_')}.json")
    try:
        cooldown_file.write_text(json.dumps({
            "pair": pair,
            "cooldown_minutes": minutes,
            "ts": int(time.time()),
            "mode": "shadow",
            "note": "shadow模式：只记录，未实际触发机器人冷却"
        }, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"[出山AI][HUNT_REVERSE] 冷却记录失败: {e}")
```

---

## 与现有 ExitAIAgent 的对接

```python
# 草案：复用现有 ExitAIAgent 的 analyze() 方法
# console_server.py:15920

def call_chushan_ai(position: dict, m2: dict, m3: dict, m4: dict, l5: dict) -> dict:
    """
    调用出山AI（复用现有 ExitAIAgent）
    引用: console_server.py:15920 ExitAIAgent.analyze()

    方案: 直接复用现有 ExitAIAgent.analyze()
    """
    # agent = ExitAIAgent(api_key=None)  # 内部自动读取环境变量
    # result = agent.analyze(
    #     position=[position],
    #     r2_health=...,      # 需从现有数据构造
    #     r3_plan=None,
    #     fund_flow=m1_flow,  # 需从现有数据构造
    #     m2_sr=m2,
    #     m1_mtf=m1_mtf,     # 需从现有数据构造
    #     m3_giant=m3,
    #     m4_data=m4,
    #     l5_data=l5
    # )
    # return _extract_chushan_result(result)
    raise NotImplementedError("call_chushan_ai() 需对接 ExitAIAgent.analyze()")
```

---

## 禁止事项

- **禁止**在shadow模式下执行实际平仓
- **禁止**在shadow模式下修改机器人参数
- **禁止**在shadow模式下直接市价反手
- **禁止**硬编码API Key
- **禁止**将出山AI建议作为机器人直接执行指令
- **必须**通过9099执行链路确认后才能执行（console_server.py:15482）
