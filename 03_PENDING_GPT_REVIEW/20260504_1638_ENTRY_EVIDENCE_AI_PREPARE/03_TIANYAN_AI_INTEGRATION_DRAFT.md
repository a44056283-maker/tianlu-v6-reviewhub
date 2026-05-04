# 03_TIANYAN_AI_INTEGRATION_DRAFT.md
# 天眼AI调用接入草案

## 现有代码引用

| 功能 | 文件:行号 |
|------|----------|
| TianyanAgent 类定义 | `console_server.py:13830` |
| `__init__()` API Key加载 | `console_server.py:13888-13899` |
| `analyze()` 核心方法 | `console_server.py:14419-14500` |
| `SYSTEM_PROMPT` | `console_server.py:13836-13998` |
| MiniMax API URL | `console_server.py:14395` |
| MiniMax API Model | `console_server.py:14396` (`MiniMax-M2.7-highspeed`) |
| API Key 环境变量 | `console_server.py:13612` (`MINIMAX_API_KEY`) |
| API Key 文件 | `console_server.py:13607` (`tianyan_keys.json`) |
| 天眼英雄卡页面路由 | `console_server.py:2835` |

---

## 现有天眼AI调用路径

```
用户/前端
  → GET /tianyan-ai  (console_server.py:2849)
    → 返回 tianyan-ai.html
      → 前端 JS 调用 /api/tianyan/status (console_server.py:12450)
        → TianyanAgent.__init__() 读取 API Key
        → TianyanAgent.analyze() 调用 MiniMax API
          → POST https://api.minimaxi.com/v1/chat/completions
            → body: {model, messages, max_tokens, temperature}
```

---

## 天眼AI MiniMax API 调用草案

### API Key 配置

```python
# 禁止硬编码 API Key！
# 使用环境变量占位符（草案中不写实际key）

TIANYAN_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
# 或者从配置文件读取（console_server.py:13607-13623）
TIANYAN_KEYS_FILE = Path(__file__).parent / "tianyan_keys.json"
```

### MiniMax API 调用代码草案

```python
# 天眼AI调用草案（禁止直接写入实盘文件）
# 引用: console_server.py:14470-14494

import ssl
import json
import urllib.request
import urllib.error

# ── 配置（从现有代码引用）────────────────────────────────────
_MINIMAX_URL = "https://api.minimaxi.com/v1/chat/completions"
_MODEL = "MiniMax-M2.7-highspeed"  # console_server.py:14396
_MAX_TOKENS = 8192
_TEMPERATURE = 0.3

# ── API Key: 禁止硬编码！使用环境变量占位符 ─────────────────
def _get_minimax_key() -> str:
    """
    从环境变量或配置文件读取 MiniMax API Key
    引用: console_server.py:13612, 13890-13893
    """
    key = os.environ.get("MINIMAX_API_KEY", "")
    if not key:
        # 尝试从 tianyan_keys.json 读取（console_server.py:13617-13623）
        keys_file = Path(__file__).parent / "tianyan_keys.json"
        if keys_file.exists():
            data = json.loads(keys_file.read_text())
            key = data.get("minimax", "") or data.get("MINIMAX_API_KEY", "")
    return key


def call_tianyan_minimax(
    prompt: str,
    system_prompt: str,
    api_key: str = None
) -> dict:
    """
    调用天眼AI MiniMax API

    参数:
      prompt: 用户输入（包含M1-M4 evidence数据）
      system_prompt: 系统提示词（天眼V5.3角色定义）
      api_key: API Key（优先从环境变量读取）

    返回:
      {verdict, confidence, reason, speech, raw_response}

    重要: shadow模式，只展示建议，不执行任何交易
    """
    key = api_key or _get_minimax_key()
    if not key:
        print("[天眼AI] 警告: MINIMAX_API_KEY 未设置，AI分析跳过")
        return {"verdict": "SKIP", "confidence": 0.0, "reason": "API Key未设置", "speech": ""}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }

    payload = {
        "model": _MODEL,
        "messages": [
            {"role": "system", "content": system_prompt +
             "\n\n[重要]你必须且只能回复JSON数组/对象,不要包含任何其他文字."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": _MAX_TOKENS,
        "temperature": _TEMPERATURE,
    }

    body = json.dumps(payload).encode("utf-8")
    CTX = ssl.create_default_context()
    CTX.check_hostname = False
    CTX.verify_mode = ssl.CERT_NONE

    try:
        req = urllib.request.Request(
            _MINIMAX_URL,
            data=body,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60, context=CTX) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _parse_tianyan_response(content)

    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"[天眼AI] HTTP错误 {e.code}: {err_body[:200]}")
        return {"verdict": "ERROR", "confidence": 0.0, "reason": f"HTTP {e.code}", "speech": ""}
    except Exception as e:
        print(f"[天眼AI] API调用异常: {e}")
        return {"verdict": "ERROR", "confidence": 0.0, "reason": str(e), "speech": ""}


def _parse_tianyan_response(raw: str) -> dict:
    """
    解析天眼AI返回的JSON
    引用: console_server.py:15233-15235（已有JSON解析逻辑）
    """
    try:
        # MiniMax偶尔会在JSON后追加文本，取第一个完整JSON对象即可
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            data = json.loads(match.group())
            return {
                "verdict": data.get("verdict", "UNKNOWN"),
                "confidence": float(data.get("confidence", 0)),
                "reason": data.get("reason", ""),
                "speech": data.get("speech", data.get("ai_speech", "")),
                "raw_response": raw
            }
    except json.JSONDecodeError:
        print(f"[天眼AI] JSON解析失败，原始返回: {raw[:200]}")
    return {"verdict": "PARSE_ERROR", "confidence": 0.0, "reason": "JSON解析失败", "speech": raw[:200]}
```

---

## 天眼AI输入：M1-M4 Evidence JSON

### 输入数据格式

```json
{
  "pair": "BTC/USDT",
  "direction": "LONG",
  "current_price": 96500.00,
  "timestamp": 1746345600,
  "m1_evidence": {
    "pair": "BTC/USDT",
    "ratio": 5.234,
    "netflow": 1234567.89,
    "signal": "LONG",
    "gate_ratio": 4.5,
    "okx_ratio": 5.8,
    "bnb_ratio": 5.2,
    "valid_count": 3,
    "tf_15m": {"ratio": 5.234, "netflow": 1234567.89, "signal": "LONG"},
    "tf_1h":  {"ratio": 3.1,   "netflow": 8901234.56, "signal": "LONG"},
    "tf_4h":  {"ratio": 2.2,   "netflow": 34567890.12, "signal": "LONG"}
  },
  "m2_evidence": {
    "pair": "BTC/USDT",
    "has_sr": true,
    "sr_type": "support",
    "sr_price": 95234.56,
    "sr_touches": 4,
    "dist_to_price": -0.45,
    "data_source": "m2_triple_exchange"
  },
  "m3_evidence": {
    "pair": "BTC/USDT",
    "atr_15m": 45.67,
    "atr_1h": 98.23,
    "giant_count": 2,
    "squeeze_count": 1,
    "volatility_level": "HIGH"
  },
  "m4_evidence": {
    "pair": "BTC/USDT",
    "rsi_15m": 68.5,
    "rsi_1h": 62.3,
    "oi_change_pct": 5.2,
    "oi_signal": "INCREASING"
  }
}
```

---

## 天眼AI输出格式

```json
{
  "verdict": "EXECUTE_LONG",
  "confidence": 0.88,
  "reason": "三所共振做多信号确认，M1量比5.2x+M2支撑触底4次+M3 GIANT阳线",
  "speech": "BTC/USDT 15m量比5.2x突破三所共振确认，Gate+OKX+BNB净流入同向，M2支撑位95234触底4次，M3 GIANT阳线机构吸筹信号，多时线共振做多，建议轻仓介入。",
  "allowed_directions": ["LONG"],
  "data_gaps": [],
  "blocked_fields": []
}
```

### Verdict 枚举值

| verdict | 含义 | 置信度要求 |
|---------|------|-----------|
| EXECUTE_LONG | 建议做多 | >= 50% |
| EXECUTE_SHORT | 建议做空 | >= 50% |
| OBSERVE | 观望 | 任何 |
| FORBIDDEN | 禁止 | 任何 |
| UNKNOWN | 未知/异常 | - |

---

## Shadow 模式实现

```python
# runtime_switch.py 草案（详见 05_SHADOW_MODE_RUNTIME_SWITCH.md）
ENTRY_GATE_MODE = os.environ.get("TIANLU_ENTRY_GATE_MODE", "shadow")

def call_tianyan_ai_entry(m1, m2, m3, m4) -> dict:
    """
    天眼AI入场评估（Shadow模式实现）
    重要: shadow模式只展示建议，不执行任何入场
    """
    if ENTRY_GATE_MODE == "dry":
        print("[天眼AI][DRY] 不调用AI，只用规则检查")
        return {"verdict": "DRY_MODE", "confidence": 0.0, "reason": "dry模式跳过AI"}

    # 组装提示词（复用 TianyanAgent._build_prompt() 逻辑）
    prompt = _build_entry_prompt(m1, m2, m3, m4)
    system_prompt = TianyanAgent.ENTRY_PROMPT  # console_server.py:13837

    result = call_tianyan_minimax(prompt, system_prompt)

    # Shadow模式：只记录，不执行
    _log_tianyan_result(result, mode=ENTRY_GATE_MODE)

    return result


def _log_tianyan_result(result: dict, mode: str):
    """
    记录天眼AI结果到日志（Shadow模式）
    禁止: 在shadow模式下修改机器人参数、调用交易API
    """
    verdict = result.get("verdict", "UNKNOWN")
    confidence = result.get("confidence", 0)
    speech = result.get("speech", "")
    reason = result.get("reason", "")

    if mode == "shadow":
        print(f"[天眼AI][SHADOW] verdict={verdict}, confidence={confidence:.2f}")
        print(f"[天眼AI][SHADOW] reason={reason}")
        print(f"[天眼AI][SHADOW] speech={speech[:100]}")
        # 禁止执行任何交易操作
    else:
        # live模式：可以执行（但仍需遵守置信度门槛）
        print(f"[天眼AI][LIVE] verdict={verdict}, confidence={confidence:.2f}")
```

---

## 调用频率限制

```python
# 避免刷API：入场评估每个pair每60秒最多调用1次
import time as _time

_tianyan_call_timestamps: dict[str, float] = {}  # {pair: last_call_ts}
_TIANyan_CALL_INTERVAL = 60  # 秒

def _can_call_tianyan(pair: str) -> bool:
    """检查是否允许调用天眼AI（频率限制）"""
    now = _time.time()
    last = _tianyan_call_timestamps.get(pair, 0)
    if now - last < _TIANyan_CALL_INTERVAL:
        return False
    _tianyan_call_timestamps[pair] = now
    return True
```

---

## 与现有 TianyanAgent 的对接

```python
# 草案：复用现有 TianyanAgent 的 analyze() 方法
# console_server.py:14419-14498

def call_tianyan_ai(m1: dict, m2: dict, m3: dict, m4: dict) -> dict:
    """
    调用天眼AI（复用现有 TianyanAgent）
    引用: console_server.py:14419 TianyanAgent.analyze()
    """
    # 方案1: 直接复用现有 TianyanAgent（推荐）
    # agent = TianyanAgent(api_key=None)  # 内部自动读取环境变量
    # positions = [{"pair": pair, ...}]   # 构造虚拟持仓
    # decisions = agent.analyze(positions, dot_blacklist={}, dca_status={})
    # return _extract_verdict(decisions)

    # 方案2: 独立调用（草案）
    system_prompt = TianyanAgent.ENTRY_PROMPT  # console_server.py:13837
    prompt = _build_entry_prompt(m1, m2, m3, m4)
    return call_tianyan_minimax(prompt, system_prompt)
```

---

## 禁止事项

- **禁止**在 shadow 模式下执行实际交易
- **禁止**硬编码 API Key（必须从环境变量读取）
- **禁止**调用频率超过每pair每60秒1次
- **禁止**将 AI verdict 直接作为机器人执行指令
