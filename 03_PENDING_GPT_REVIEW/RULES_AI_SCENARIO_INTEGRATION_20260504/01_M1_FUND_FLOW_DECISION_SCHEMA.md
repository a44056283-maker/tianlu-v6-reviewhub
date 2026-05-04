# M1 资金流裁决 Schema
**Version:** 1.0 | **Date:** 2026-05-04 | **Status:** DRAFT - Pending GPT Review
**Author:** 户部代理 | **Scope:** Tianlu V6.5 M1 Fund Flow Decision Algorithm

---

## 1. 概述

M1 资金流是整个 V6.5 入场裁决体系的入口层，负责整合 Gate.io、OKX、Binance 三所的永续合约资金流数据，输出信任等级五档（A/B/C/D/E），供 api_autopilot（天眼AI）和 risk_engine（出山AI）消费。

**核心原则：**
- 只读计算，无任何交易副作用
- 三所平等，出现分歧时按规则降权而非丢弃
- 信任等级 D/E 一票禁止入场

---

## 2. 数据源规格

### 2.1 三所数据通道

| 交易所 | CCXT ID | 数据类型 | Symbol | 代理路径 | 默认 Type |
|--------|---------|---------|--------|----------|----------|
| Gate.io | `gateio` | 永续合约 OHLVC + Taker 统计 | BTC/USDT:USDT | 直连（无代理） | `swap`（perp） |
| OKX | `okx` | 永续合约 OHLVC + Taker 统计 | BTC/USDT:USDT | `http://127.0.0.1:10811`（SSH 隧道） | `swap` |
| Binance | `binance` | 永续合约 OHLVC | BTC/USDT:USDT | `http://127.0.0.1:10811`（SSH 隧道） | `future` |

### 2.2 原始数据字段（每所）

```python
exchange_data = {
    "ratio":       float,   # 量比 = 当根成交量 / 过去N根均值（核心指标）
    "netflow":     float,   # 净流入 = (买入成交量 - 卖出成交量) / 总成交量
    "whale_ratio": float,   # 大户比 = 大单成交量 / 总成交量（Gate/OKX 专属）
    "vol":         float,   # 当根成交量（绝对值）
    "score":       float,   # 该所独立评分（0-100）
    "signal":       str,     # "LONG" | "SHORT" | "NEUTRAL"
}
```

### 2.3 数据可用性状态

| 状态 | 说明 | trust_flags 值 |
|------|------|---------------|
| `FULL` | 三所数据完整 | 无标志 |
| `DEGRADED` | 仅两所有效 | `SINGLE_EXCHANGE`（若仅一所有效） |
| `PARTIAL` | 仅一所有效 | `SINGLE_EXCHANGE` |
| `STALE` | 数据过期（>10 分钟） | `V2_SHADOW_STALE` |
| `DEAD` | 无任何数据 | `NO_DATA` |

---

## 3. 三所一致性算法（Three-Exchange Consensus）

### 3.1 方向一致性计算

**输入：** 三所各自的 `signal`（LONG/SHORT/NEUTRAL）和 `taker_delta_ratio`

**步骤 1：提取有效信号**
```python
# 伪代码
exchange_signals = [
    ("gate", gate.signal,  gate.taker_delta_ratio),
    ("okx",  okx.signal,   okx.taker_delta_ratio),
    ("bnb",  bnb.signal,   None),   # Binance 无 taker_delta_ratio
]

# 过滤 NEUTRAL 信号（不参与一致性计算）
valid_signals = [(ex, sig, tdr) for ex, sig, tdr in exchange_signals if sig != "NEUTRAL"]
# valid_signals 示例：[("gate", "LONG", 0.72), ("okx", "LONG", 0.55)]
```

**步骤 2：计算方向共识**
```python
signals_only = [sig for _, sig, _ in valid_signals]
long_count  = signals_only.count("LONG")
short_count = signals_only.count("SHORT")

# 共识 = 与多数方向一致的交易所数 / 有效交易所总数
if len(signals_only) == 0:
    flow_consensus_score = 0.0
else:
    flow_consensus_score = max(long_count, short_count) / len(signals_only)
# 示例：3所全LONG → 3/3=1.0；2所LONG+1所SHORT → 2/3=0.67
```

**步骤 3：计算分歧度**
```python
flow_divergence_score = 1.0 - flow_consensus_score
# 0.0 = 完全一致，1.0 = 完全对立
```

### 3.2 量比分歧度计算

**目的：** 检测量比（ratio）的极端偏离，不同于方向分歧。

```python
def compute_ratio_divergence(gate_ratio: float, okx_ratio: float, bnb_ratio: float) -> float:
    ratios = [r for r in [gate_ratio, okx_ratio, bnb_ratio] if r > 0]
    if len(ratios) < 2:
        return 0.0  # 无法计算分歧，单所或无数据

    max_ratio = max(ratios)
    min_ratio = min(ratios)

    if max_ratio == 0:
        return 0.0

    divergence = (max_ratio - min_ratio) / max_ratio
    return round(divergence, 3)

# 示例：Gate=4.5, OKX=2.1, BNB=1.8 → (4.5-1.8)/4.5 = 0.60（严重分歧）
# 示例：Gate=3.0, OKX=2.8, BNB=2.5 → (3.0-2.5)/3.0 = 0.17（低分歧）
```

**量比分歧阈值：**

| 分歧度 | 等级 | 含义 | 动作 |
|--------|------|------|------|
| < 0.30 | 低分歧 | 三所量比接近 | 正常处理 |
| 0.30 - 0.49 | 中分歧 | 一所偏高但可接受 | 关注但执行 |
| 0.50 - 0.59 | 高分歧 | 单所极端，需关注 | 降噪观望 |
| >= 0.60 | 严重分歧 | 单所拉偏可能性高 | 禁止执行 |

---

## 4. Exchange Outlier 判断标准

### 4.1 异常交易所定义

**Exchange Outlier：** 三所中某交易所的数据与其他两所显著偏离，可能被该交易所的局部事件（大户操纵、API 异常、交易所维护）拉偏，需要降低其权重或排除。

### 4.2 方向 Outlier 检测

```python
def detect_direction_outlier(gate_signal, okx_signal, bnb_signal,
                             aggregated_signal) -> str | None:
    """
    检测方向 Outlier：唯一与多数方向冲突的交易所。
    返回 outlier 交易所名，或 None（无异常）。
    """
    signals = {"gate": gate_signal, "okx": okx_signal, "bnb": bnb_signal}
    for exchange, sig in signals.items():
        if sig != "NEUTRAL" and sig != aggregated_signal:
            return exchange
    return None

# 示例：gate=LONG, okx=LONG, bnb=SHORT → outlier="bnb"
# 示例：gate=LONG, okx=SHORT, bnb=NEUTRAL → outlier="gate"（bnb 被忽略）
```

### 4.3 量比 Outlier 检测

```python
def detect_ratio_outlier(gate_ratio: float, okx_ratio: float, bnb_ratio: float,
                         threshold: float = 0.60) -> str | None:
    """
    检测量比 Outlier：某所量比超过其他均值 threshold(60%) 则标记为异常。
    threshold=0.60: 该所量比超过其他均值+60%则标记为异常。
    """
    ratios = {"gate": gate_ratio, "okx": okx_ratio, "bnb": bnb_ratio}
    active = {k: v for k, v in ratios.items() if v > 0}

    if len(active) < 2:
        return None

    for exchange, ratio in active.items():
        others = [v for k, v in active.items() if k != exchange]
        other_mean = sum(others) / len(others)
        if other_mean <= 0:
            continue
        deviation = (ratio - other_mean) / other_mean
        if deviation >= threshold:
            return exchange
    return None

# 示例：gate_ratio=5.0, okx_ratio=2.0, bnb_ratio=1.8
# gate 偏离：(5.0-1.9)/1.9=1.63 > 0.60 → outlier="gate"
```

### 4.4 Outlier 降权规则

```python
def apply_outlier_downweight(exchange_data: dict, outlier: str | None) -> dict:
    """
    当某所被标记为 Outlier 时，其置信度贡献降至 30%。
    仅影响 score 和权重，不删除数据。
    """
    if outlier is None:
        return exchange_data

    result = dict(exchange_data)
    for record in [result.get("gate"), result.get("okx"), result.get("bnb")]:
        if record and record.get("exchange") == outlier:
            record["_outlier_flagged"] = True
            record["_weight"] = 0.3  # 降权至 30%
    return result
```

---

## 5. Data Freshness Score 计算

### 5.1 计算公式

```python
def compute_freshness_score(cache_timestamp: int,
                             staleness_threshold_sec: int = 600) -> float:
    """
    数据新鲜度 = max(0, 1 - age_sec / staleness_threshold_sec)

    staleness_threshold_sec = 600 (10分钟): 三所数据的最长可接受间隔
    若 age >= 600秒 → freshness = 0（完全过期）
    若 age = 0秒    → freshness = 1.0（完全新鲜）

    V2 shadow DB 使用 600秒阈值（10分钟无更新 = STALE）。
    """
    import time
    age_sec = int(time.time()) - cache_timestamp
    freshness = max(0.0, 1.0 - age_sec / staleness_threshold_sec)
    return round(freshness, 3)

# 示例：数据5分钟前 → freshness = 1 - 300/600 = 0.5
# 示例：数据30秒前  → freshness = 1 - 30/600  = 0.95
```

### 5.2 V2 Shadow DB 新鲜度

```python
def check_v2_shadow_freshness(v2_db_path: str) -> dict:
    """
    检查 V2 shadow 数据库的最后更新时间。
    超过 10 分钟无快照 → status = "STALE"
    数据库不存在      → status = "MISSING"
    """
    import sqlite3, time
    try:
        conn = sqlite3.connect(v2_db_path, timeout=3.0)
        row = conn.execute(
            "SELECT ts FROM fund_flow_v2_snapshots ORDER BY ts DESC LIMIT 1"
        ).fetchone()
        conn.close()

        if row is None:
            return {"status": "MISSING", "last_snap_ts": None, "last_snap_age_sec": None}

        last_ts = row[0]
        age_sec = int(time.time()) - last_ts
        status = "LIVE" if age_sec < 600 else "STALE"
        return {"status": status, "last_snap_ts": last_ts, "last_snap_age_sec": age_sec}
    except Exception:
        return {"status": "MISSING", "last_snap_ts": None, "last_snap_age_sec": None}
```

---

## 6. M1 Signal Trust Level 五档定义

### 6.1 综合评分公式

```python
def compute_trust_score(consensus: float,
                         ratio: float,
                         freshness: float,
                         divergence: float) -> float:
    """
    综合信任评分 = 加权组合（满分 100）

    组成：
      共识贡献   (consensus * 40):   三所方向一致程度
      量比贡献   (normalized_ratio * 30): 成交量放大程度
      新鲜度贡献 (freshness * 20):   数据时效性
      稳定性贡献 ((1 - divergence) * 10): 分歧越小稳定性越高

    归一化：ratio / 5.0 上限，防止量比极端值过度影响
    """
    normalized_ratio = min(ratio / 5.0, 1.0) if ratio > 0 else 0.0

    score = (
        consensus          * 40.0 +
        normalized_ratio   * 30.0 +
        freshness          * 20.0 +
        (1.0 - divergence) * 10.0
    )
    return round(score, 1)  # 0.0 - 100.0
```

### 6.2 五档阈值表

| 等级 | 评分范围 | 量比要求 | 净流入要求 | 共识要求 | 新鲜度要求 | 入场许可 |
|------|---------|---------|---------|---------|----------|---------|
| **A** | >= 85 | >= 3.0x | >= 0.8 | 三所全一致 | >= 0.8 | **完全执行** |
| **B** | 70 - 84 | >= 2.0x | >= 0.5 | >= 2所一致 | >= 0.7 | **建议执行**（需二次确认） |
| **C** | 55 - 69 | 1.5 - 2.0x | >= 0.4 | >= 2所一致 | >= 0.5 | **谨慎观察**（不自动执行） |
| **D** | 40 - 54 | < 1.5x | 任意 | < 2所一致 | < 0.5 | **禁止入场** |
| **E** | < 40 | 极低/无数据 | 无 | < 2所 | 任意 | **禁止入场**（记录警告） |

### 6.3 档位判定算法

```python
def compute_trust_grade(data: dict) -> tuple[str, dict]:
    """
    计算 M1 信任等级和完整 evidence 字典。
    纯函数，无 I/O，无副作用。
    """
    agg      = data.get("aggregated", {})
    ratio    = agg.get("ratio", 0) or 0
    netflow  = agg.get("netflow", 0) or 0
    signal   = agg.get("signal", "NEUTRAL")
    vc       = agg.get("valid_count", 0)

    gate = data.get("gate") or {}
    okx  = data.get("okx")  or {}
    bnb  = data.get("bnb")   or {}

    g_sig = gate.get("signal", "NEUTRAL")
    o_sig = okx.get("signal",  "NEUTRAL")
    b_sig = bnb.get("signal",  "NEUTRAL")

    # ── Consensus ──
    exchange_sigs = [s for s in [g_sig, o_sig, b_sig] if s != "NEUTRAL"]
    agreeing = [s for s in exchange_sigs if s == signal]
    consensus = len(agreeing) / max(len(exchange_sigs), 1)
    divergence = 1.0 - consensus

    # ── Outlier ──
    outlier = None
    all_sigs = {"gate": g_sig, "okx": o_sig, "bnb": b_sig}
    for ex, sig in all_sigs.items():
        if sig not in ("NEUTRAL", signal) and sig != "NEUTRAL":
            outlier = ex
            break

    # ── Freshness ──
    freshness = data.get("evidence", {}).get("data_freshness_score", 0.95)

    # ── Trust Flags ──
    flags = []
    if vc == 0:   flags.append("NO_DATA")
    elif vc == 1: flags.append("SINGLE_EXCHANGE")
    if divergence >= 0.5: flags.append("SPLIT_HIGH")
    if outlier: flags.append(f"OUTLIER_{outlier.upper()}")

    # ── Composite Score ──
    score = (
        consensus              * 40.0 +
        min(ratio / 5.0, 1.0) * 30.0 +
        freshness              * 20.0 +
        (1.0 - divergence)    * 10.0
    )

    # ── Grade ──
    if   score >= 85: grade = "A"
    elif score >= 70: grade = "B"
    elif score >= 55: grade = "C"
    elif score >= 40: grade = "D"
    else:            grade = "E"

    evidence = {
        "m1_signal_trust_level":   grade,
        "flow_consensus_score":    round(consensus, 3),
        "flow_divergence_score":   round(divergence, 3),
        "exchange_outlier":        outlier,
        "data_freshness_score":   freshness,
        "source_count":           vc,
        "valid_exchange_count":    len(agreeing),
        "trust_flags":            flags,
        "computed_at":            datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return grade, evidence
```

---

## 7. Flow Consensus Score 阈值定义

| 阈值范围 | 共识等级 | 含义 | 建议动作 |
|---------|---------|------|---------|
| `>= 1.0` | 完美共识 | 三所方向完全一致，无 NEUTRAL | 信任信号，全权执行 |
| `0.67 - 0.99` | 强共识 | 2/3 所以上同向，仅一所偏离 | 高置信执行 |
| `0.50 - 0.66` | 弱共识 | 仅 2 所同向，1 所偏离 | 降权执行或观望 |
| `< 0.50` | 无共识 | 三所分歧严重，或 NEUTRAL 过多 | **强制观望，禁止入场** |

---

## 8. 异常交易所降权规则

### 8.1 降权矩阵

| 异常类型 | 检测条件 | 降权动作 | 影响范围 |
|---------|---------|---------|---------|
| 方向 Outlier | 某所 signal != 聚合 signal，且非 NEUTRAL | 该所权重降至 **30%** | 仅影响 consensus 分子计算 |
| 量比 Outlier | 某所 ratio > 其他均值 × 1.60 | 该所 ratio 降至其他均值水平 | 仅影响聚合 ratio |
| 单所数据 | `valid_count == 1` | 整体置信度降至 **35%**，禁止执行 | 全局 |
| 交易所缺失 | 某所返回 null（API 超时/Key 缺失） | 从共识计算中排除该所 | 共识分母减小 |
| Spot 模式 | Gate `defaultType="spot"` 被检测 | `trust_flags += ["GATE_SPOT_MODE"]`，降权 Gate | Gate 权重 -50% |

### 8.2 降权后重新聚合

```python
def reaggregate_with_downweight(gate, okx, bnb,
                                  direction_outlier=None,
                                  ratio_outlier=None) -> dict:
    """
    对被降权的交易所数据进行重新聚合。
    方向：Outlier 交易所不参与共识投票
    量比：Outlier 交易所 ratio 替换为其他均值
    """
    def downweighted_ratio(ratio, exchange, outlier):
        if exchange == outlier and ratio > 0:
            others = [v for ex, v in [("gate",gate),("okx",okx),("bnb",bnb)]
                      if ex != exchange and v > 0]
            return sum(others) / len(others) if others else ratio
        return ratio

    gate_r = downweighted_ratio(gate.get("ratio", 0), "gate", ratio_outlier)
    okx_r  = downweighted_ratio(okx.get("ratio", 0),  "okx",  ratio_outlier)
    bnb_r  = downweighted_ratio(bnb.get("ratio", 0),  "bnb",  ratio_outlier)

    agg_ratio = (gate_r + okx_r + bnb_r) / 3.0  # 简单平均
    return {"agg_ratio": round(agg_ratio, 3)}
```

---

## 9. 入场拦截规则（决策树）

```
输入: evidence{}

├─ freshness < 0.7
│   └─ BLOCK → "STALE_DATA"
│
├─ m1_signal_trust_level == "E"
│   └─ BLOCK → "TRUST_LEVEL_E_NO_DATA"
│
├─ m1_signal_trust_level == "D"
│   └─ BLOCK → "TRUST_LEVEL_D_LOW_CONFIDENCE"
│
├─ flow_consensus_score < 0.4
│   └─ BLOCK → "EXTREME_DIVERGENCE"
│
├─ exchange_outlier == dominant_exchange
│   └─ WARN + DISCOUNT(weight *= 0.3)
│
├─ "SPLIT_HIGH" in trust_flags AND volume_ratio < 2.0
│   └─ WATCH → "HIGH_DIVERGENCE_LOW_VOLUME"
│
├─ flow_consensus_score >= 0.67 AND volume_ratio >= 3.0
│   └─ APPROVE → "GRADE_A_STRONG_CONSENSUS"
│
└─ (其他情况)
    └─ EVALUATE → 传递至天眼AI综合评分
```

---

## 10. Schema 校验规则（JSON Schema）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "M1 Fund Flow Decision Schema",
  "type": "object",
  "required": ["pair", "ts", "aggregated", "evidence"],
  "properties": {
    "pair":     { "type": "string" },
    "ts":       { "type": "integer" },
    "gate":     { "oneOf": [{ "type": "null" }, { "$ref": "#/definitions/exchange" }] },
    "okx":      { "oneOf": [{ "type": "null" }, { "$ref": "#/definitions/exchange" }] },
    "bnb":      { "oneOf": [{ "type": "null" }, { "$ref": "#/definitions/exchange" }] },
    "aggregated": {
      "type": "object",
      "required": ["ratio", "netflow", "score", "signal", "valid_count"],
      "properties": {
        "ratio":       { "type": "number", "minimum": 0 },
        "netflow":     { "type": "number" },
        "score":       { "type": "number" },
        "signal":      { "type": "string", "enum": ["LONG", "SHORT", "NEUTRAL"] },
        "valid_count": { "type": "integer", "minimum": 0, "maximum": 3 }
      }
    },
    "evidence": {
      "type": "object",
      "required": ["m1_signal_trust_level", "flow_consensus_score",
                   "flow_divergence_score", "data_freshness_score",
                   "source_count", "valid_exchange_count"],
      "properties": {
        "m1_signal_trust_level":  { "type": "string", "enum": ["A","B","C","D","E"] },
        "flow_consensus_score":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "flow_divergence_score":  { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "exchange_outlier":       { "type": ["string","null"], "enum": ["gate","okx","bnb",null] },
        "dominant_exchange":      { "type": ["string","null"], "enum": ["gate","okx","bnb",null] },
        "data_freshness_score":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "source_count":           { "type": "integer", "minimum": 0, "maximum": 3 },
        "valid_exchange_count":   { "type": "integer", "minimum": 0, "maximum": 3 },
        "book_taker_alignment":   { "type": "number", "minimum": -1.0, "maximum": 1.0 },
        "taker_oi_alignment":     { "type": "number", "minimum": -1.0, "maximum": 1.0 },
        "funding_pressure_state": { "type": "string", "enum": ["POSITIVE","NEGATIVE","NEUTRAL"] },
        "trust_flags":            { "type": "array", "items": { "type": "string" } },
        "computed_at":            { "type": "string", "format": "date-time" }
      }
    }
  },
  "definitions": {
    "exchange": {
      "type": "object",
      "properties": {
        "ratio":       { "type": "number" },
        "netflow":     { "type": "number" },
        "whale_ratio": { "type": "number" },
        "vol":         { "type": "number" },
        "score":       { "type": "number" },
        "signal":      { "type": "string", "enum": ["LONG","SHORT","NEUTRAL"] }
      }
    }
  }
}
```
