# EntryDecisionGate 完整规则规范
> 天眼院代理生成 | 日期: 2026-05-04 | 状态: PENDING REVIEW
> 参考: ExitDecisionGate (04_EXIT_DECISION_GATE_PATCH.md) / PostExitContinuation (04_POST_EXIT_CONTINUATION_SPEC.md)

---

## 一、概念定义

### 什么是 EntryDecisionGate？

**EntryDecisionGate**（入场统一裁决闸门）是所有入场信号必须经过的强制性门控：

> 所有入场信号（无论来自天眼AI还是V6.5本地规则L1/L2/L4）在执行前必须经过 EntryDecisionGate 裁决。Gate 根据 M1-M5 多维度数据输出 5 档裁决结果（A/B/C/D/E），只有 A 档允许自动驾驶入场，B 档须等待确认，C/D/E 档禁止入场。

**与 ExitDecisionGate 的对称设计：**

| 维度 | ExitDecisionGate | EntryDecisionGate |
|------|-----------------|-------------------|
| 管辖对象 | 所有出场动作 | 所有入场动作 |
| 核心保护 | 连续亏损后禁止自学习收紧 | 入场信号质量过滤 |
| 状态机 | post_exit_continuation 观察期 | entry_signal_quarantine |
| 裁决档位 | exit/observe/block/pass | A/B/C/D/E |
| 阻断动作 | auto_profit_tighten / auto_dca / auto_reentry | 全部 except A档 |

---

## 二、5档裁决定义

### 裁决档位总览

| 档位 | 裁决结果 | 含义 | 自动执行 | 人工确认 |
|------|---------|------|---------|---------|
| **A** | `APPROVED` | 可入场 | ✅ 是 | 不需要 |
| **B** | `OBSERVE` | 等待确认 | ❌ 否 | 需要第2轮AI确认 |
| **C** | `REJECTED_NOISE` | 噪音禁止 | ❌ 否 | 需要人工Override |
| **D** | `DATA_INSUFFICIENT` | 数据不足 | ❌ 否 | 数据恢复后重评 |
| **E** | `EXCHANGE_ANOMALY` | 单所异常降权 | ❌ 否 | 降权后重评或人工确认 |

### A档 — APPROVED（可入场）

**触发条件（须同时满足）：**
- M1 量比 >= 5.0x（L1标准）
- M1 flow_consensus_score >= 0.67（三所方向一致）
- M1 source_count >= 2（至少2所有效数据）
- M2 支撑/压力位有验证（双验以上）
- M3 无 HIGH>=3 反转猎杀风险
- M4 RSI 未极端（不在 FORBIDDEN 范围）
- 不在 DOGE 风险窗口内
- 不在 SOL DCA 风险期内

**输出示例：**
```json
{
  "verdict": "A",
  "action": "APPROVED",
  "auto_execute": true,
  "confidence": 85,
  "reason": "M1量比5.2x三所共振 + M2三验支撑紧贴0.5% + M3 GIANT阳2次 + M4 RSI中性",
  "gate_passed_rules": ["M1_RATIO", "M1_CONSENSUS", "M2_VALIDATION", "M3_NO_HUNT", "M4_RSI_OK", "DOGE_CLEAR"],
  "blocked_rules": []
}
```

---

### B档 — OBSERVE（等待确认）

**触发条件（满足任一即触发）：**
- M1 量比 >= 3.0x 但 < 5.0x（中等信号）
- M1 flow_consensus_score 在 0.50~0.66 之间（弱共识）
- M2 仅单验（无多所共振）
- M4 RSI 在偏强/偏弱区间（需额外确认）
- 天眼AI第一轮置信度在 50-60% 之间（未达 60% 确认门槛）

**规则行为：**
- 记录第一轮裁决
- 等待 15 分钟内第二轮天眼AI确认
- 连续两轮同向裁决 → 升级为 A 档
- 第二轮方向变化或超时 30 分钟 → 重置轮次，维持 B 档

**输出示例：**
```json
{
  "verdict": "B",
  "action": "OBSERVE",
  "auto_execute": false,
  "confidence": 55,
  "reason": "M1量比3.2x双所共振但1所偏离，M2单验支撑",
  "require_confirm_rounds": 2,
  "round_1_pending": true,
  "round_1_timestamp": 1746332400.0,
  "next_check_in_minutes": 15,
  "gate_passed_rules": ["M1_RATIO_OK", "M2_SOME_VALIDATION"],
  "blocked_rules": ["M1_CONSENSUS_WEAK", "M4_RSI_CONFIRM_NEEDED"]
}
```

---

### C档 — REJECTED_NOISE（噪音禁止）

**触发条件（满足任一即触发）：**
- M1 flow_divergence_score >= 0.60（单所拉偏严重）
- M1 exchange_outlier 检测到（某所量比偏离均值>=60%）
- M1 量价背离：量比>=2.0x + 净流出（或反向）
- M2 无有效 S/R 数据（S14场景）
- M2 M1/M2 方向背离（S05场景）
- M2 紧贴压力位禁止追多（S06场景）
- M3 单所单时线 GIANT 信号（M3-07/M3-08）
- M3 被动买入/卖出信号（M3-02/M3-04）
- 同一交易对在冷却期内（止损后4小时内）
- DOGE 风险窗口未解除

**规则行为：**
- 强制禁止自动入场
- 记录噪音类型和触发规则
- 4小时后或问题消除后自动重评
- 人工可 Override（需记录原因）

**输出示例：**
```json
{
  "verdict": "C",
  "action": "REJECTED_NOISE",
  "auto_execute": false,
  "confidence": 0,
  "reason": "M1单所极端量比4.5x + flow_divergence_score=0.62，单所拉偏噪音",
  "noise_type": "EXCHANGE_OUTLIER",
  "cooldown_until": 1746336000.0,
  "gate_passed_rules": [],
  "blocked_rules": [
    "M1_DIVERGENCE_SEVERE",
    "M1_OUTLIER_DETECTED",
    "DIVERGENCE_SCORE_OVER_60"
  ]
}
```

---

### D档 — DATA_INSUFFICIENT（数据不足）

**触发条件（满足任一即触发）：**
- M1 source_count < 2（仅单所有效数据）
- M1 volume_ratio 所有交易所均为 0 或 None
- M1 数据新鲜度：最新K线时间距今 > 5 分钟（缓存过期）
- M2 无有效 S/R 数据（S14场景）
- M4 三所 RSI 全部缺失

**规则行为：**
- 暂停入场裁决，等待数据恢复
- 记录数据缺失类型
- 数据恢复后自动重评

**输出示例：**
```json
{
  "verdict": "D",
  "action": "DATA_INSUFFICIENT",
  "auto_execute": false,
  "confidence": 0,
  "reason": "M1仅Gate单所有效数据，OKX/BNB数据缺失",
  "missing_sources": ["okx", "bnb"],
  "stale_indicators": [],
  "gate_passed_rules": [],
  "blocked_rules": ["M1_SOURCE_COUNT_LOW", "M1_DATA_STALE"]
}
```

---

### E档 — EXCHANGE_ANOMALY（单所异常降权）

**触发条件（满足任一即触发）：**
- M1 exchange_outlier == True（某所量比偏离>=60%）
- M1 dominant_exchange 被标记为异常
- M1 量比极端（>=3.0x）但其他两所 < 1.5x
- M1 双所背离：两所方向相反且分歧度>=0.50

**规则行为：**
- 降低异常交易所权重至 0.3
- 使用剩余两所聚合信号重新评估
- 如果剩余两所仍满足 A 档条件 → 降权后通过
- 如果剩余两所不足 → 输出 E 档禁止

**输出示例：**
```json
{
  "verdict": "E",
  "action": "EXCHANGE_ANOMALY",
  "auto_execute": false,
  "confidence": 40,
  "reason": "Gate量比4.5x被标记为outlier（偏离均值60%），降权至0.3",
  "anomalous_exchange": "gate",
  "downweighted_exchanges": {"gate": 0.3, "okx": 1.0, "bnb": 1.0},
  "reassessed_with_downweight": true,
  "reassessed_result": "B",
  "gate_passed_rules": [],
  "blocked_rules": ["M1_EXCHANGE_OUTLIER"]
}
```

---

## 三、7条入场规则（必须同时满足）

> EntryDecisionGate.evaluate() 对每条规则逐一检查，全部通过才输出 A 档。

### 规则1：M1三所一致性不足时禁止A档

**检查逻辑：**
```python
if m1.source_count < 2:
    return "D"  # 数据不足
if m1.flow_consensus_score < 0.50:
    return "C"  # 三所分歧严重，噪音禁止
if m1.flow_consensus_score < 0.67:
    return "B"  # 弱共识，降为等待确认
```

**阈值：**
| flow_consensus_score | 裁决 |
|---------------------|------|
| >= 0.67 | 正常通过 |
| 0.50 ~ 0.66 | B档（等待确认） |
| < 0.50 | C档（噪音禁止） |

---

### 规则2：M1数据新鲜度不足时输出D档

**检查逻辑：**
```python
latest_kline_ts = m1.get("latest_kline_timestamp", 0)
age_seconds = time.time() - latest_kline_ts
if age_seconds > 300:  # 5分钟缓存TTL
    return "D"  # 数据不新鲜
```

**阈值：**
| 数据年龄 | 裁决 |
|---------|------|
| <= 300秒 | 正常通过 |
| > 300秒 | D档（数据不足） |

---

### 规则3：单所异常拉偏时输出E档

**检查逻辑：**
```python
if m1.exchange_outlier == True:
    # 降权异常交易所，重新聚合
    if reassessed_signal_valid():
        return "E_downgraded_pass"  # 降权后通过（视为B档）
    else:
        return "E"  # 降权后仍不足，禁止
```

**阈值：**
| exchange_outlier | 处理 |
|-----------------|------|
| False | 正常通过 |
| True | E档降权重评 |

---

### 规则4：M2位置质量不足时不允许A档

**检查逻辑：**
```python
sr_validation_count = m2.get("dual_count", 0) + m2.get("triple_count", 0)
dist_to_sr = m2.get("distance_to_sr_pct", 999)

if sr_validation_count >= 2 and dist_to_sr <= 1.0:
    pass  # M2质量合格
elif sr_validation_count >= 1 and dist_to_sr <= 1.0:
    return "B"  # M2质量中等
else:
    return "C"  # M2质量不足
```

**阈值：**
| M2验证数 | 距S/R距离 | 裁决 |
|---------|---------|------|
| >=2所 | <=1% | 正常通过（可A档） |
| >=1所 | <=1% | B档（等待确认） |
| 任意 | >1% | C档（位置不佳） |
| 0所 | 任意 | C档（无确认） |

---

### 规则5：M3巨量未确认时不允许直接入场

**检查逻辑：**
```python
high_count = m3.get("high_count", 0)
giant_bull = m3.get("giant_bull", 0)
giant_bear = m3.get("giant_bear", 0)
reversal_hunt = m3.get("reversal_hunt", False)

# 反转猎杀 → 禁止入场
if reversal_hunt:
    return "C"  # 反转猎杀存在

# 单所单时线 GIANT → 禁止
if (giant_bull > 0 or giant_bear > 0) and m1.source_count < 2:
    return "C"  # 单所不足

# HIGH>=3 + 方向确认 → A档
if high_count >= 3 and m1.signal_direction_confirmed:
    pass  # 强反转猎杀信号，高可信
```

---

### 规则6：M4多周期不一致时降级

**检查逻辑：**
```python
rsi_states = m4.get("rsi_by_timeframe", {})  # {15m, 1h, 4h, 1d}
avg_rsi = sum(rsi_states.values()) / len(rsi_states) if rsi_states else 50

# RSI极端 → 禁止
if avg_rsi > 75 or avg_rsi < 25:
    return "C"  # RSI极端，禁止任何入场

# 多周期衰竭（做多+RSI全>=70）→ 禁止做多
if direction == "LONG" and all(rsi >= 70 for rsi in rsi_states.values()):
    return "C"  # 多头衰竭，禁止做多

# 多周期衰竭（做空+RSI全<=30）→ 禁止做空
if direction == "SHORT" and all(rsi <= 30 for rsi in rsi_states.values()):
    return "C"  # 空头衰竭，禁止做空

# RSI偏强/偏弱 → B档（等待确认）
if direction == "LONG" and avg_rsi > 65:
    return "B"  # RSI偏强，追高风险
if direction == "SHORT" and avg_rsi < 35:
    return "B"  # RSI偏弱，追空风险
```

---

### 规则7：DOGE风险窗口内禁止自动新增

**检查逻辑：**
```python
# DOGE临时冻结列表（运行时动态维护）
_DOGE_FREEZE_PAIRS: dict = {}  # pair → freeze_until_ts

def _is_doge_frozen(pair: str) -> bool:
    if "DOGE" not in pair:
        return False
    freeze_entry = _DOGE_FREEZE_PAIRS.get(pair)
    if not freeze_entry:
        return False
    return time.time() < freeze_entry["freeze_until"]

# 兵部可调用 _freeze_doge(pair, hours=24) 冻结
# 24小时后自动解除或连续2次盈利主动解除

if _is_doge_frozen(pair):
    return "C"  # DOGE风险窗口内，禁止新增
```

**冻结触发条件：**
| 触发事件 | 冻结时长 |
|---------|---------|
| 全bot同向信号噪音 | 24小时 |
| 批量止损（>=5 bot同时止损） | 24小时 |
| 兵部人工冻结 | 人工指定 |
| 连续2次盈利 | 自动解除 |

---

## 四、DCA不能绕过 EntryDecisionGate

### 核心原则

> **DCA（定投加仓）是入场行为的一部分，必须经过 EntryDecisionGate 裁决。**

### 具体约束

**约束1：DCA 不能绕过 A/B/C/D/E 裁决**
```python
# 错误做法： DCA 直接下发 force_enter
if dca_triggered and not entry_decision_gate.approved:
    pass  # ❌ 禁止直接入场

# 正确做法： DCA 必须先过 Gate
gate = EntryDecisionGate()
gate_result = gate.evaluate(pair, m1_payload, m2_payload, m3_payload, m4_payload)
if gate_result["verdict"] != "A":
    log(f"[EntryDecisionGate] DCA blocked for {pair}, verdict={gate_result['verdict']}")
    skip_dca()
```

**约束2：DCA 层级的额外限制**
| DCA层级 | 允许的最大裁决档位 | 说明 |
|--------|-----------------|------|
| DCA L1（正常加仓） | A档 | 只允许最强信号加仓 |
| DCA L2（深度加仓） | A档 | 不降级，必须强信号 |
| DCA L3（极限加仓） | B档（需二次确认） | 极限加仓可降一档但需确认 |
| DCA L4（强制加仓） | A档 + 人工授权 | 强制加仓必须有A档+人工Override |

**约束3：连续加仓次数上限**
```python
if dca_count >= _DCA_MAX_LAYERS:  # 默认3次
    return "C"  # 超过加仓上限，禁止继续DCA
```

---

## 五、EntryDecisionGate 类 Python 伪代码设计

```python
# ═══════════════════════════════════════════════════════════════
# 入场裁决闸门（EntryDecisionGate）
# 裁决档位: A(APPROVED) / B(OBSERVE) / C(REJECTED_NOISE) /
#           D(DATA_INSUFFICIENT) / E(EXCHANGE_ANOMALY)
# ═══════════════════════════════════════════════════════════════

from dataclasses import dataclass, field
from enum import Enum
import time
import json
from pathlib import Path

class Verdict(str, Enum):
    A = "A"    # APPROVED 可入场
    B = "B"    # OBSERVE 等待确认
    C = "C"    # REJECTED_NOISE 噪音禁止
    D = "D"    # DATA_INSUFFICIENT 数据不足
    E = "E"    # EXCHANGE_ANOMALY 单所异常降权


@dataclass
class EntrySignalPayload:
    """
    入场信号数据结构（对应M1-M5数据源）
    """
    pair: str = ""
    direction: str = "LONG"       # LONG / SHORT
    current_price: float = 0.0

    # M1资金流
    m1_gate_ratio: float | None = None
    m1_okx_ratio: float | None = None
    m1_bnb_ratio: float | None = None
    m1_gate_netflow: float = 0.0
    m1_okx_netflow: float = 0.0
    m1_bnb_netflow: float = 0.0
    m1_latest_kline_ts: float = 0.0

    # M2支撑压力
    m2_support: float = 0.0
    m2_resistance: float = 0.0
    m2_dual_count: int = 0
    m2_triple_count: int = 0
    m2_touch_count: int = 0
    m2_near_sr_pct: float = 999.0

    # M3巨量K线
    m3_high_count: int = 0
    m3_giant_bull: int = 0
    m3_giant_bear: int = 0
    m3_reversal_hunt: bool = False
    m3_liquidation_present: bool = False

    # M4技术指标
    m4_rsi_15m: float = 50.0
    m4_rsi_1h: float = 50.0
    m4_rsi_4h: float = 50.0
    m4_rsi_1d: float = 50.0
    m4_atr_pct: float = 3.0
    m4_oi_change_pct: float = 0.0
    m4_oi_ratio: float = 1.0
    m4_exhaust: str = "none"  # bull_exhaust / bear_exhaust / none

    # M5外部数据（舆情/冻结）
    m5_doge_frozen: bool = False
    m5_doge_freeze_until: float = 0.0


@dataclass
class EntryGateResult:
    """
    EntryDecisionGate 裁决结果
    """
    verdict: str                    # A / B / C / D / E
    action: str                     # APPROVED / OBSERVE / REJECTED_NOISE /
                                    # DATA_INSUFFICIENT / EXCHANGE_ANOMALY
    auto_execute: bool              # 是否允许自动执行
    confidence: float               # 置信度 0-100
    reason: str                     # 裁决原因摘要
    noise_type: str | None          # 噪音类型（C档时填写）
    missing_sources: list[str]      # 缺失数据源（D档时填写）
    anomalous_exchange: str | None # 异常交易所（E档时填写）
    cooldown_until: float | None   # 冷却截止时间戳
    gate_passed_rules: list[str]    # 通过的规则列表
    blocked_rules: list[str]       # 被阻断的规则列表
    downweighted_exchanges: dict   # 降权权重（E档时填写）
    timestamp: float = field(default_factory=time.time)


class EntryDecisionGate:
    """
    入场统一裁决闸门

    所有入场信号必须经过此门控，根据M1-M5数据输出5档裁决。
    DCA不能绕过此门控的约束。
    """

    # ── 配置常量 ──────────────────────────────────────────────
    _RATIO_THRESHOLD_STRONG: float = 5.0    # L1强信号量比
    _RATIO_THRESHOLD_MEDIUM: float = 3.0    # 中等信号量比
    _CONSENSUS_THRESHOLD_STRONG: float = 0.67  # 强共识
    _CONSENSUS_THRESHOLD_WEAK: float = 0.50    # 弱共识
    _DIVERGENCE_THRESHOLD_HIGH: float = 0.50    # 高分歧
    _DIVERGENCE_THRESHOLD_SEVERE: float = 0.60  # 严重分歧
    _OUTLIER_THRESHOLD: float = 0.60            # 单所异常阈值
    _DATA_FRESHNESS_TTL: int = 300              # 数据新鲜度TTL（秒）
    _OBSERVE_ROUND_WINDOW: int = 1800           # 观察轮次窗口（30分钟）
    _DOGE_FREEZE_DEFAULT_HOURS: int = 24        # DOGE默认冻结时长

    def __init__(self):
        # 轮次确认状态（pair → {round_count, first_verdict, first_ts}）
        self._observe_rounds: dict = {}
        # DOGE冻结状态（pair → {freeze_until, reason}）
        self._doge_freeze: dict = {}

    # ═══════════════════════════════════════════════════════════
    # 核心评估方法
    # ═══════════════════════════════════════════════════════════

    def evaluate(self, payload: EntrySignalPayload) -> EntryGateResult:
        """
        执行入场裁决

        评估顺序（7条入场规则）：
        1. 规则2：M1数据新鲜度 → D档
        2. 规则3：单所异常拉偏 → E档
        3. 规则1：M1三所一致性不足 → B/C档
        4. 规则7：DOGE风险窗口 → C档
        5. 规则6：M4多周期不一致 → B/C档
        6. 规则5：M3巨量未确认 → C档
        7. 规则4：M2位置质量不足 → B/C档
        8. 综合裁决 → A/B/C/D/E
        """
        passed: list[str] = []
        blocked: list[str] = []

        pair = payload.pair
        direction = payload.direction

        # ── 规则2：M1数据新鲜度 ──────────────────────────────
        if not self._check_m1_freshness(payload):
            return self._make_result("D", reason="M1数据不新鲜（缓存过期>5分钟）",
                                     blocked=["M1_DATA_STALE"], passed=[])

        # ── 规则3：单所异常拉偏检测 ──────────────────────────
        outlier_result = self._check_exchange_outlier(payload)
        if outlier_result["is_outlier"]:
            # 降权后重新评估
            reassessed = self._reassess_with_downweight(payload, outlier_result)
            if not reassessed["pass"]:
                return self._make_result("E",
                                         reason=f"单所异常降权后仍不足：{reassessed['reason']}",
                                         anomalous_exchange=outlier_result["exchange"],
                                         downweighted_exchanges=outlier_result["weights"],
                                         blocked=["M1_EXCHANGE_OUTLIER"], passed=[])
            else:
                # 降权后通过，但视为B档（降级）
                return self._make_result("B",
                                         reason=f"Gate降权至{outlier_result['weights'][outlier_result['exchange']]}后通过，需确认",
                                         anomalous_exchange=outlier_result["exchange"],
                                         downweighted_exchanges=outlier_result["weights"],
                                         blocked=[], passed=["M1_OUTLIER_REASSESSED"])

        # ── 规则1：M1三所一致性 ──────────────────────────────
        m1_check = self._check_m1_consistency(payload)
        if m1_check["verdict"] == "C":
            return self._make_result("C", reason=m1_check["reason"],
                                     blocked=m1_check["blocked"], passed=[])
        elif m1_check["verdict"] == "B":
            passed.append("M1_CONSENSUS_PASS_B")
        else:
            passed.append("M1_CONSENSUS_PASS_A")

        # ── 规则7：DOGE风险窗口 ──────────────────────────────
        if self._is_doge_frozen(pair):
            return self._make_result("C",
                                     reason="DOGE风险窗口内（批量止损后冻结24小时）",
                                     noise_type="DOGE_BATCH_STOP_LOSS",
                                     cooldown_until=self._get_doge_freeze_ts(pair),
                                     blocked=["DOGE_RISK_WINDOW"], passed=[])

        # ── 规则6：M4多周期一致性 ────────────────────────────
        m4_check = self._check_m4_cycles(payload)
        if m4_check["verdict"] in ("B", "C"):
            return self._make_result(m4_check["verdict"],
                                     reason=m4_check["reason"],
                                     blocked=m4_check["blocked"], passed=[])
        passed.append("M4_RSI_OK")

        # ── 规则5：M3巨量确认 ───────────────────────────────
        m3_check = self._check_m3_giant_confirmed(payload)
        if not m3_check["pass"]:
            return self._make_result("C", reason=m3_check["reason"],
                                     noise_type=m3_check["noise_type"],
                                     blocked=m3_check["blocked"], passed=[])
        passed.append("M3_CONFIRMED")

        # ── 规则4：M2位置质量 ───────────────────────────────
        m2_check = self._check_m2_position_quality(payload)
        if m2_check["verdict"] in ("B", "C"):
            return self._make_result(m2_check["verdict"],
                                     reason=m2_check["reason"],
                                     blocked=m2_check["blocked"], passed=[])
        passed.append("M2_POSITION_OK")

        # ── 综合裁决：全部通过 → A档 ─────────────────────────
        confidence = self._calc_confidence(payload, passed)
        return EntryGateResult(
            verdict="A",
            action="APPROVED",
            auto_execute=True,
            confidence=confidence,
            reason=f"A档可入场：M1量比{payload.m1_gate_ratio}x + M2双验支撑 + M3无反转猎杀 + M4 RSI正常",
            noise_type=None,
            missing_sources=[],
            anomalous_exchange=None,
            cooldown_until=None,
            gate_passed_rules=passed,
            blocked_rules=[],
            downweighted_exchanges={"gate": 1.0, "okx": 1.0, "bnb": 1.0},
        )

    # ═══════════════════════════════════════════════════════════
    # 7条入场规则的具体实现
    # ═══════════════════════════════════════════════════════════

    def _check_m1_freshness(self, p: EntrySignalPayload) -> bool:
        """规则2：M1数据新鲜度"""
        age = time.time() - p.m1_latest_kline_ts
        return age <= self._DATA_FRESHNESS_TTL

    def _check_exchange_outlier(self, p: EntrySignalPayload) -> dict:
        """
        规则3：单所异常拉偏检测

        返回: {
            "is_outlier": bool,
            "exchange": str | None,
            "weights": dict,
            "reassessed_ratio": float
        }
        """
        ratios = {}
        if p.m1_gate_ratio and p.m1_gate_ratio > 0:
            ratios["gate"] = p.m1_gate_ratio
        if p.m1_okx_ratio and p.m1_okx_ratio > 0:
            ratios["okx"] = p.m1_okx_ratio
        if p.m1_bnb_ratio and p.m1_bnb_ratio > 0:
            ratios["bnb"] = p.m1_bnb_ratio

        if len(ratios) < 2:
            return {"is_outlier": False, "exchange": None, "weights": {}, "reassessed_ratio": 0.0}

        others_mean = sum(ratios.values()) / len(ratios)
        for ex, ratio in ratios.items():
            deviation = (ratio - others_mean) / others_mean if others_mean > 0 else 0
            if deviation >= self._OUTLIER_THRESHOLD:
                weights = {k: (0.3 if k == ex else 1.0) for k in ratios}
                reassessed_ratio = sum(ratios[k] * weights[k] for k in ratios) / sum(weights.values())
                return {
                    "is_outlier": True,
                    "exchange": ex,
                    "weights": weights,
                    "reassessed_ratio": reassessed_ratio,
                }
        return {"is_outlier": False, "exchange": None, "weights": {}, "reassessed_ratio": 0.0}

    def _reassess_with_downweight(self, p: EntrySignalPayload, outlier_result: dict) -> dict:
        """降权后重新评估"""
        weights = outlier_result["weights"]
        reassessed_ratio = outlier_result["reassessed_ratio"]
        non_outlier_count = sum(1 for k, w in weights.items() if w > 0.3)

        if non_outlier_count >= 2 and reassessed_ratio >= self._RATIO_THRESHOLD_STRONG:
            return {"pass": True, "reason": "降权后双所聚合满足强信号"}
        elif non_outlier_count >= 1 and reassessed_ratio >= self._RATIO_THRESHOLD_MEDIUM:
            return {"pass": True, "reason": "降权后单所满足中等信号"}
        else:
            return {"pass": False, "reason": f"降权后量比{reassessed_ratio:.1f}x不足"}

    def _check_m1_consistency(self, p: EntrySignalPayload) -> dict:
        """
        规则1：M1三所一致性

        计算 flow_consensus_score 和 flow_divergence_score
        """
        ratios = [r for r in [p.m1_gate_ratio, p.m1_okx_ratio, p.m1_bnb_ratio] if r and r > 0]
        netflows = {
            "gate": p.m1_gate_netflow,
            "okx": p.m1_okx_netflow,
            "bnb": p.m1_bnb_netflow,
        }

        if len(ratios) < 2:
            return {"verdict": "D", "reason": "M1数据源不足", "blocked": ["M1_SOURCE_COUNT_LOW"]}

        # flow_consensus_score
        signs = [1 if netflows[k] > 0.1 else (-1 if netflows[k] < -0.1 else 0) for k in netflows]
        signs = [s for s in signs if s != 0]
        if signs:
            consensus = max(signs.count(1), signs.count(-1)) / len(signs)
        else:
            consensus = 0.0

        # flow_divergence_score
        if ratios:
            divergence = (max(ratios) - min(ratios)) / max(ratios)
        else:
            divergence = 1.0

        # 量价背离检测
        avg_ratio = sum(ratios) / len(ratios)
        avg_netflow = sum(netflows.values()) / len(netflows)
        price_volume_divergence = (avg_ratio >= 2.0 and avg_netflow < -0.5)

        if divergence >= self._DIVERGENCE_THRESHOLD_SEVERE:
            return {"verdict": "C",
                    "reason": f"M1严重分歧：flow_divergence={divergence:.2f}>=0.60，单所拉偏",
                    "blocked": ["M1_DIVERGENCE_SEVERE", "FLOW_DIVERGENCE_OVER_60"]}
        if price_volume_divergence:
            return {"verdict": "C",
                    "reason": "M1量价背离：放量>=2.0x但净流出",
                    "blocked": ["M1_PRICE_VOLUME_DIVERGENCE"]}
        if consensus < self._CONSENSUS_THRESHOLD_WEAK:
            return {"verdict": "C",
                    "reason": f"M1无共识：consensus={consensus:.2f}<0.50",
                    "blocked": ["M1_NO_CONSENSUS"]}
        if consensus < self._CONSENSUS_THRESHOLD_STRONG:
            return {"verdict": "B",
                    "reason": f"M1弱共识：consensus={consensus:.2f}<0.67，需第2轮确认",
                    "blocked": []}
        return {"verdict": "A", "reason": "", "blocked": []}

    def _is_doge_frozen(self, pair: str) -> bool:
        """规则7：DOGE风险窗口"""
        if "DOGE" not in pair:
            return False
        entry = self._doge_freeze.get(pair)
        if not entry:
            return False
        return time.time() < entry.get("freeze_until", 0)

    def _get_doge_freeze_ts(self, pair: str) -> float:
        entry = self._doge_freeze.get(pair, {})
        return entry.get("freeze_until", 0)

    def _check_m4_cycles(self, p: EntrySignalPayload) -> dict:
        """
        规则6：M4多周期一致性
        """
        rsi_values = [p.m4_rsi_15m, p.m4_rsi_1h, p.m4_rsi_4h, p.m4_rsi_1d]
        avg_rsi = sum(rsi_values) / len(rsi_values)

        # RSI极端
        if avg_rsi > 75 or avg_rsi < 25:
            direction_word = "做多" if p.direction == "LONG" else "做空"
            return {"verdict": "C",
                    "reason": f"M4 RSI极端{avg_rsi:.0f}，禁止{direction_word}",
                    "blocked": ["M4_RSI_EXTREME"]}

        # 多周期衰竭
        if p.direction == "LONG" and all(r >= 70 for r in rsi_values):
            return {"verdict": "C",
                    "reason": "M4多头衰竭：RSI 4周期全部>=70，禁止做多",
                    "blocked": ["M4_BULL_EXHAUST_MULTI_CYCLE"]}
        if p.direction == "SHORT" and all(r <= 30 for r in rsi_values):
            return {"verdict": "C",
                    "reason": "M4空头衰竭：RSI 4周期全部<=30，禁止做空",
                    "blocked": ["M4_BEAR_EXHAUST_MULTI_CYCLE"]}

        # RSI偏强/偏弱
        if p.direction == "LONG" and avg_rsi > 65:
            return {"verdict": "B",
                    "reason": f"M4 RSI偏强{avg_rsi:.0f}>65，追高风险，需确认",
                    "blocked": []}
        if p.direction == "SHORT" and avg_rsi < 35:
            return {"verdict": "B",
                    "reason": f"M4 RSI偏弱{avg_rsi:.0f}<35，追空风险，需确认",
                    "blocked": []}

        return {"verdict": "A", "reason": "", "blocked": []}

    def _check_m3_giant_confirmed(self, p: EntrySignalPayload) -> dict:
        """
        规则5：M3巨量未确认时禁止直接入场
        """
        # 反转猎杀存在 → 禁止
        if p.m3_reversal_hunt:
            return {"pass": False,
                    "reason": "M3反转猎杀存在，禁止入场",
                    "noise_type": "REVERSAL_HUNT",
                    "blocked": ["M3_REVERSAL_HUNT"]}

        # 单所单时线 GIANT → 禁止
        source_count = sum(1 for r in [p.m1_gate_ratio, p.m1_okx_ratio, p.m1_bnb_ratio] if r and r > 0)
        if (p.m3_giant_bull > 0 or p.m3_giant_bear > 0) and source_count < 2:
            return {"pass": False,
                    "reason": f"M3 GIANT信号存在但仅{source_count}所，单所不足",
                    "noise_type": "M3_SINGLE_EXCHANGE_GIANT",
                    "blocked": ["M3_SINGLE_EXCHANGE_GIANT"]}

        # 被动买入/卖出
        if p.m3_liquidation_present:
            return {"pass": False,
                    "reason": "M3存在爆仓流出，被动信号禁止入场",
                    "noise_type": "LIQUIDATION_OUTFLOW",
                    "blocked": ["M3_LIQUIDATION_OUTFLOW"]}

        return {"pass": True, "reason": "", "noise_type": None, "blocked": []}

    def _check_m2_position_quality(self, p: EntrySignalPayload) -> dict:
        """
        规则4：M2位置质量
        """
        validation_count = p.m2_dual_count + p.m2_triple_count * 2
        dist = p.m2_near_sr_pct

        if validation_count >= 2 and dist <= 1.0:
            return {"verdict": "A", "reason": "", "blocked": []}
        elif validation_count >= 1 and dist <= 1.0:
            return {"verdict": "B",
                    "reason": f"M2单验支撑，距S/R{dist:.1f}%，需第2轮确认",
                    "blocked": []}
        elif dist > 3.0:
            return {"verdict": "C",
                    "reason": f"M2位置远离S/R{dist:.1f}%，悬空高风险",
                    "blocked": ["M2_POSITION_FAR_FROM_SR"]}
        else:
            return {"verdict": "C",
                    "reason": f"M2无有效S/R验证，位置质量不足",
                    "blocked": ["M2_NO_VALIDATION"]}

    # ═══════════════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════════════

    def _calc_confidence(self, p: EntrySignalPayload, passed: list[str]) -> float:
        """计算综合置信度"""
        base = 50.0
        if "M1_CONSENSUS_PASS_A" in passed:
            base += 20
        if "M2_POSITION_OK" in passed:
            base += 15
        if "M3_CONFIRMED" in passed:
            base += 10
        if "M4_RSI_OK" in passed:
            base += 5
        return min(100.0, base)

    def _make_result(self, verdict: str, reason: str,
                     blocked: list[str] = None, passed: list[str] = None,
                     **kwargs) -> EntryGateResult:
        """构建裁决结果"""
        action_map = {
            "A": "APPROVED",
            "B": "OBSERVE",
            "C": "REJECTED_NOISE",
            "D": "DATA_INSUFFICIENT",
            "E": "EXCHANGE_ANOMALY",
        }
        return EntryGateResult(
            verdict=verdict,
            action=action_map.get(verdict, "UNKNOWN"),
            auto_execute=(verdict == "A"),
            confidence=0.0 if verdict in ("C", "D") else (60.0 if verdict == "B" else 85.0),
            reason=reason,
            noise_type=kwargs.get("noise_type"),
            missing_sources=kwargs.get("missing_sources", []),
            anomalous_exchange=kwargs.get("anomalous_exchange"),
            cooldown_until=kwargs.get("cooldown_until"),
            gate_passed_rules=passed or [],
            blocked_rules=blocked or [],
            downweighted_exchanges=kwargs.get("downweighted_exchanges", {}),
        )

    # ── DOGE冻结管理 ──────────────────────────────────────────
    def freeze_doge(self, pair: str, hours: int = None) -> None:
        """兵部/系统调用：冻结DOGE新增入场"""
        if hours is None:
            hours = self._DOGE_FREEZE_DEFAULT_HOURS
        self._doge_freeze[pair] = {
            "freeze_until": time.time() + hours * 3600,
            "reason": "batch_stop_loss",
        }
        _log(f"[EntryDecisionGate] DOGE冻结：{pair} 冻结{hours}小时")

    def unfreeze_doge(self, pair: str) -> None:
        """解除DOGE冻结（连续2次盈利或人工解除）"""
        if pair in self._doge_freeze:
            self._doge_freeze.pop(pair)
            _log(f"[EntryDecisionGate] DOGE解冻：{pair}")

    # ── 轮次确认管理 ──────────────────────────────────────────
    def record_round(self, pair: str, verdict: str) -> EntryGateResult:
        """
        记录观察轮次，用于B档等待确认

        逻辑：
        - 第一轮B档 → 记录，等待第二轮
        - 第二轮同向B档 → 升级为A档
        - 第二轮方向变化 → 重置，维持B档
        - 超时30分钟 → 重置轮次
        """
        now = time.time()
        state = self._observe_rounds.get(pair)

        if state is None:
            # 第一轮
            self._observe_rounds[pair] = {
                "round_count": 1,
                "first_verdict": verdict,
                "first_ts": now,
            }
            return self._make_result("B",
                                     reason=f"第1轮B档，等待第2轮确认（30分钟内）",
                                     passed=["ROUND_1_B_RECORDED"])
        else:
            elapsed = now - state["first_ts"]
            if elapsed > self._OBSERVE_ROUND_WINDOW:
                # 超时，重置轮次
                self._observe_rounds.pop(pair)
                return self.record_round(pair, verdict)

            if state["round_count"] == 1:
                if verdict == state["first_verdict"]:
                    # 第二轮同向 → 升级A档
                    self._observe_rounds.pop(pair)
                    return self._make_result("A",
                                             reason="第2轮确认同向，升级A档",
                                             passed=["ROUND_2_CONFIRMED_UPGRADE"])
                else:
                    # 第二轮方向变化 → 重置
                    self._observe_rounds.pop(pair)
                    return self._make_result("B",
                                             reason="第2轮方向变化，重置轮次",
                                             passed=["ROUND_2_VERDICT_CHANGED"])
            return self._make_result("B",
                                     reason="轮次状态异常",
                                     passed=["ROUND_STATE_ERROR"])

    def clear_round(self, pair: str) -> None:
        """清除轮次状态（任何档位输出A档后调用）"""
        self._observe_rounds.pop(pair, None)


# ═══════════════════════════════════════════════════════════════
# 与 v65_autopilot.py 的集成接口
# ═══════════════════════════════════════════════════════════════

def _entry_gate_check(pair: str, direction: str,
                      m1_payload: dict, m2_payload: dict,
                      m3_payload: dict, m4_payload: dict,
                      m5_payload: dict = None) -> EntryGateResult:
    """
    v65_autopilot.py 调用的统一入口

    使用示例：
        gate_result = _entry_gate_check(
            pair="BTC/USDT",
            direction="LONG",
            m1_payload=m1_data,
            m2_payload=m2_data,
            m3_payload=m3_data,
            m4_payload=m4_data,
        )
        if gate_result.verdict == "A":
            proceed_with_entry()
        else:
            log(f"[EntryDecisionGate] 入场被拒: {gate_result.verdict} {gate_result.reason}")
    """
    gate = EntryDecisionGate()
    payload = EntrySignalPayload(
        pair=pair,
        direction=direction,
        m1_gate_ratio=m1_payload.get("gate_ratio"),
        m1_okx_ratio=m1_payload.get("okx_ratio"),
        m1_bnb_ratio=m1_payload.get("bnb_ratio"),
        m1_gate_netflow=m1_payload.get("gate_netflow", 0),
        m1_okx_netflow=m1_payload.get("okx_netflow", 0),
        m1_bnb_netflow=m1_payload.get("bnb_netflow", 0),
        m1_latest_kline_ts=m1_payload.get("latest_kline_ts", 0),
        m2_support=m2_payload.get("support", 0),
        m2_resistance=m2_payload.get("resistance", 0),
        m2_dual_count=m2_payload.get("dual_count", 0),
        m2_triple_count=m2_payload.get("triple_count", 0),
        m2_near_sr_pct=m2_payload.get("distance_to_sr_pct", 999),
        m3_high_count=m3_payload.get("high_count", 0),
        m3_giant_bull=m3_payload.get("giant_bull", 0),
        m3_giant_bear=m3_payload.get("giant_bear", 0),
        m3_reversal_hunt=m3_payload.get("reversal_hunt", False),
        m3_liquidation_present=m3_payload.get("liquidation_present", False),
        m4_rsi_15m=m4_payload.get("rsi_15m", 50),
        m4_rsi_1h=m4_payload.get("rsi_1h", 50),
        m4_rsi_4h=m4_payload.get("rsi_4h", 50),
        m4_rsi_1d=m4_payload.get("rsi_1d", 50),
        m4_atr_pct=m4_payload.get("atr_pct", 3.0),
        m4_oi_change_pct=m4_payload.get("oi_change_pct", 0),
        m4_oi_ratio=m4_payload.get("oi_ratio", 1.0),
        m4_exhaust=m4_payload.get("exhaust", "none"),
        m5_doge_frozen=(m5_payload or {}).get("doge_frozen", False),
        m5_doge_freeze_until=(m5_payload or {}).get("doge_freeze_until", 0),
    )
    return gate.evaluate(payload)
```

---

## 六、裁决结果格式规范

### 标准 JSON 输出格式

```json
{
  "verdict": "A",
  "action": "APPROVED",
  "auto_execute": true,
  "confidence": 85.0,
  "reason": "M1量比5.2x三所共振 + M2三验支撑紧贴0.5% + M3 GIANT阳2次 + M4 RSI中性",
  "noise_type": null,
  "missing_sources": [],
  "anomalous_exchange": null,
  "cooldown_until": null,
  "gate_passed_rules": [
    "M1_CONSENSUS_PASS_A",
    "M2_POSITION_OK",
    "M3_CONFIRMED",
    "M4_RSI_OK",
    "DOGE_CLEAR"
  ],
  "blocked_rules": [],
  "downweighted_exchanges": {
    "gate": 1.0,
    "okx": 1.0,
    "bnb": 1.0
  },
  "timestamp": 1746332400.0
}
```

### 各档位必需字段

| 档位 | 必需字段 | 可选字段 |
|------|---------|---------|
| A | verdict, action, auto_execute, confidence, reason, passed_rules | blocked_rules |
| B | verdict, action, auto_execute, confidence, reason, blocked_rules | passed_rules |
| C | verdict, action, auto_execute=flase, confidence=0, reason, noise_type, blocked_rules | cooldown_until |
| D | verdict, action, auto_execute=flase, confidence=0, reason, missing_sources, blocked_rules | — |
| E | verdict, action, auto_execute=flase, confidence, reason, anomalous_exchange, downweighted_exchanges, blocked_rules | passed_rules |

---

## 七、与天眼AI的集成

### 集成流程

```
天眼AI评测（M1-M5数据）
    ↓
EntryDecisionGate.evaluate(payload)
    ↓
┌─────────────────────────────────────────┐
│ verdict == "A" → 天眼AI执行 force_enter │
│ verdict == "B" → 等待第2轮确认           │
│ verdict == "C" → 禁止，记录噪音日志       │
│ verdict == "D" → 禁止，等待数据恢复       │
│ verdict == "E" → 降权重评或人工确认       │
└─────────────────────────────────────────┘
```

### 天眼AI调用 Gate 示例

```python
# 天眼AI决策后，强制过 EntryDecisionGate
tianyan_result = call_tianyan_ai(m1_data, m2_data, m3_data, m4_data)
gate_result = _entry_gate_check(pair, direction, m1_data, m2_data, m3_data, m4_data)

# Gate 裁决覆盖天眼AI决策
if gate_result.verdict != "A":
    log(f"[天眼+Gate] 入场被Gate拦截: verdict={gate_result.verdict} reason={gate_result.reason}")
    skip_entry()
    return

# A档：执行天眼AI决策
if tianyan_result.verdict in ("EXECUTE_LONG", "EXECUTE_SHORT"):
    execute_force_enter(pair, direction, tianyan_result.leverage)
```

---

## 八、日志规范

### 各档位日志话术

| 档位 | 日志前缀 | 话术模板 |
|------|---------|---------|
| A | `[EntryDecisionGate]` | `A档通过：{pair} M1量比{ratio}x + M2{M2} + M3{M3} + M4{M4}，置信度{conf}%` |
| B | `[EntryDecisionGate]` | `B档观察：{pair} {reason}，等待第2轮确认` |
| C | `[EntryDecisionGate]` | `C档禁止：{pair} {reason}，noise_type={noise_type}` |
| D | `[EntryDecisionGate]` | `D档禁止：{pair} {reason}，missing={missing_sources}` |
| E | `[EntryDecisionGate]` | `E档降权：{pair} {anomalous_exchange}被降权至{weight}，{reason}` |

---

## 九、验证检查清单

- [ ] EntryDecisionGate 类已实现（参照伪代码）
- [ ] 5档裁决（A/B/C/D/E）定义完整
- [ ] 7条入场规则逐一实现
- [ ] DCA 不能绕过 EntryDecisionGate 的约束已写入代码
- [ ] DOGE 冻结机制已实现
- [ ] 轮次确认机制已实现（B档两轮确认）
- [ ] 与 v65_autopilot.py 的集成接口 `_entry_gate_check()` 已定义
- [ ] 与天眼AI的集成流程已规范
- [ ] 裁决结果 JSON 格式符合规范
- [ ] 日志话术符合规范
