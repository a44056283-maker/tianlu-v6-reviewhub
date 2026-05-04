# M1-M5 Evidence Payload Specification
**Version:** 6.5.1 | **Date:** 2026-05-04 | **Status:** DRAFT - Pending GPT Review
**Author:** 户部代理 | **Scope:** Tianlu V6.5.1 M1-M5 Capital Flow Evidence Layer - Complete Spec

> **版本说明：** 本文档为 V6.5 初始版（2026-05-04）的更新版本，整合了 M1 审计报告、三所一致性算法、信任等级五档制及 L5 进化实验室数据格式。

---

## 1. 概述

### 1.1 定位

本文档是天禄 V6.5.1 量化交易系统中 **M1-M5 五层证据Payload** 的完整规范定义。所有数据模块共享统一信封格式，供以下消费者使用：

- **天眼AI** (`api_autopilot.py`)：M1-M4 综合入场裁决
- **出山AI** (`risk_engine.py`)：回撤保护 + ATR 止损 + 反转猎杀
- **L5 进化实验室** (`l5_evolution_lab/`)：影子规则晋升与候选参数管理
- **Console Server** (`console_server.py`)：前端英雄卡展示与实时监控

### 1.2 设计原则

1. **向后兼容**：现有 `aggregated{}` 字段（ratio, netflow, score, signal, valid_count）原样保留，新增字段以新 key 注入
2. **显式溯源**：每个 Payload 携带来源文件、数据年龄、交易所覆盖率，消费者可自行拒绝过期数据
3. **零交易副作用**：所有证据计算只读，不触发交易所 API 操作
4. **五档信任制**：A/B/C/D/E 信任等级，同时服务机器裁决和人工复核

---

## 2. 证据层职责边界

### 2.1 各层职责定义

| 层级 | 名称 | 核心职责 | 数据来源 | 裁决权重 |
|------|------|---------|---------|---------|
| **M1** | 资金流裁决层 | 三所量比+净流入+共识评分，输出信任等级 | Gate/OKX/Binance 永续 OHLCV | **入口守门人**（一票拦截） |
| **M2** | 支撑压力层 | 最近支撑/阻力位+触及次数+假突破风险 | 近期高低点+成交量分布 | 入场位置验证 |
| **M3** | 巨量K线层 | 巨量K线检测+延续/反转概率 | 成交量突增 K 线 | 入场量能确认 |
| **M4** | 技术面层 | MACD/RSI/ATR/布林带/多时线对齐 | 各交易所技术指标 | 出场触发主导 |
| **L5** | 进化实验室 | 影子规则晋升+候选参数+噪音评分 | 历史表现统计 | 进化修正 |

### 2.2 数据流向图

```
Gate/OKX/Binance API
        │
        ▼
┌─────────────────────────────────────────────────┐
│  api_m1.py (M1 资金流采集 + 信任裁决)           │
│  calc_fund_flow_for_pair()                      │
│  compute_trust_grade()  ──→ evidence{}          │
└────────────────┬────────────────────────────────┘
                 │ aggregated{} + evidence{}
                 ▼
┌─────────────────────────────────────────────────┐
│  console_server.py                             │
│  /api/m1/evidence/<pair>                       │
│  /api/m1/scan/<pair>                           │
└────────────────┬────────────────────────────────┘
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
┌─────────┐ ┌──────────┐ ┌──────────────────┐
│ 天眼AI  │ │ 巨量K线  │ │ L5 进化实验室   │
│ M1-M4  │ │ 检测 M3  │ │ 影子规则 L5     │
│ 入场裁决│ │          │ │                  │
└────┬────┘ └────┬─────┘ └────────┬─────────┘
     │           │               │
     ▼           ▼               ▼
┌──────────────────────────────────────────────────┐
│  出山AI risk_engine.py                          │
│  回撤保护 + ATR止损 + 反转猎杀（B3）            │
└──────────────────────────────────────────────────┘
                 │
                 ▼
         Freqtrade Bot Overlay
         (9090-9097, 8081-8084)
```

---

## 3. 统一 Evidence Payload JSON Schema

### 3.1 完整 Payload 结构

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Tianlu V6.5.1 M1-M5 Unified Evidence Payload",
  "version": "6.5.1",
  "type": "object",
  "required": ["pair", "ts", "cached_at", "aggregated", "evidence"],

  "properties": {

    "pair": {
      "type": "string",
      "description": "交易对符号，如 'BTC/USDT'"
    },
    "ts": {
      "type": "integer",
      "description": "Unix 时间戳（秒）"
    },
    "cached_at": {
      "type": "string",
      "format": "date-time",
      "description": "缓存命中时间（ISO 8601）"
    },

    "gate": {
      "description": "Gate.io 永续合约数据（BTC/USDT:USDT）",
      "$ref": "#/definitions/exchange_block"
    },
    "okx": {
      "description": "OKX 永续合约数据（BTC/USDT:USDT）",
      "$ref": "#/definitions/exchange_block"
    },
    "bnb": {
      "description": "Binance 永续合约数据（BTC/USDT:USDT）",
      "$ref": "#/definitions/bnb_block"
    },

    "aggregated": {
      "type": "object",
      "required": ["ratio", "netflow", "score", "signal", "valid_count"],
      "properties": {
        "ratio": {
          "type": "number",
          "description": "三所量比均值（当根成交量 / 过去N根均值）"
        },
        "netflow": {
          "type": "number",
          "description": "三所净流入均值（买入-卖出）/ 总成交量"
        },
        "score": {
          "type": "number",
          "description": "聚合评分（0-100）"
        },
        "signal": {
          "type": "string",
          "enum": ["LONG", "SHORT", "NEUTRAL"],
          "description": "聚合信号方向"
        },
        "valid_count": {
          "type": "integer",
          "minimum": 0,
          "maximum": 3,
          "description": "返回非空数据的交易所数量"
        }
      }
    },

    "evidence": {
      "type": "object",
      "description": "M1 信任证据层（V6.5.1 新增）",
      "required": [
        "m1_signal_trust_level",
        "flow_consensus_score",
        "flow_divergence_score",
        "data_freshness_score",
        "source_count",
        "valid_exchange_count"
      ],
      "properties": {
        "m1_signal_trust_level": {
          "type": "string",
          "enum": ["A", "B", "C", "D", "E"],
          "description": "信号信任等级五档：A=>=85分，B=70-84，C=55-69，D=40-54，E=<40"
        },
        "flow_consensus_score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "三所方向一致率 = agreeing / valid_signals"
        },
        "flow_divergence_score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "三所分歧度 = 1 - consensus，高值表示方向冲突"
        },
        "exchange_outlier": {
          "type": ["string", "null"],
          "enum": ["gate", "okx", "bnb", null],
          "description": "唯一与多数方向冲突的交易所，null=无异常"
        },
        "dominant_exchange": {
          "type": ["string", "null"],
          "enum": ["gate", "okx", "bnb", null],
          "description": "量比最高的主导交易所，用于单所拉偏判断"
        },
        "data_freshness_score": {
          "type": "number",
          "minimum": 0.0,
          "maximum": 1.0,
          "description": "数据新鲜度 = max(0, 1 - age_sec / 600)，低于 0.7 禁止入场"
        },
        "source_count": {
          "type": "integer",
          "minimum": 0,
          "maximum": 3,
          "description": "返回非空数据的交易所数量"
        },
        "valid_exchange_count": {
          "type": "integer",
          "minimum": 0,
          "maximum": 3,
          "description": "信号方向与聚合信号一致的交易所数量"
        },
        "book_taker_alignment": {
          "type": "number",
          "minimum": -1.0,
          "maximum": 1.0,
          "description": "订单簿深度与 Taker 方向对齐度，正=做多主导"
        },
        "taker_oi_alignment": {
          "type": "number",
          "minimum": -1.0,
          "maximum": 1.0,
          "description": "Taker 方向与持仓量变化对齐度"
        },
        "funding_pressure_state": {
          "type": "string",
          "enum": ["POSITIVE", "NEGATIVE", "NEUTRAL"],
          "description": "资金费率压力状态（从 OKX/Binance funding_rate 推断）"
        },
        "trust_flags": {
          "type": "array",
          "items": { "type": "string" },
          "description": "诊断标签数组：NO_DATA / SINGLE_EXCHANGE / SPLIT_HIGH / OUTLIER_* / V2_SHADOW_STALE / GATE_SPOT_MODE / OKX_KEY_MISSING"
        },
        "computed_at": {
          "type": "string",
          "format": "date-time",
          "description": "evidence 计算时间（ISO 8601）"
        }
      }
    },

    "m2_support_resistance": {
      "type": "object",
      "description": "M2 支撑压力数据",
      "properties": {
        "nearest_support":          { "type": "number" },
        "nearest_resistance":       { "type": "number" },
        "support_distance_pct":    { "type": "number" },
        "resistance_distance_pct": { "type": "number" },
        "sr_touch_count":          { "type": "integer" },
        "sr_quality_score":        { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "false_breakout_risk":     { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "structure_alignment":     { "type": "string", "enum": ["BULLISH","BEARISH","NEUTRAL"] }
      }
    },

    "m3_giant_candle": {
      "type": "object",
      "description": "M3 巨量K线数据",
      "properties": {
        "giant_candle_direction":   { "type": "string", "enum": ["UP","DOWN","NONE"] },
        "giant_candle_strength":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "volume_ratio":            { "type": "number" },
        "after_giant_confirm_bars":{ "type": "integer" },
        "reversal_probability":    { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "continuation_probability":{ "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "fake_reversal_risk":      { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      }
    },

    "m4_technical": {
      "type": "object",
      "description": "M4 技术面数据",
      "properties": {
        "trend_direction":    { "type": "string", "enum": ["UP","DOWN","NEUTRAL"] },
        "macd_state":         { "type": "string", "enum": ["BULLISH","BEARISH","NEUTRAL"] },
        "rsi_state":          { "type": "string", "enum": ["OVERBOUGHT","OVERSOLD","NEUTRAL"] },
        "atr_state":          { "type": "string", "enum": ["HIGH_VOL","NORMAL_VOL","LOW_VOL"] },
        "volatility_state":   { "type": "string", "enum": ["EXPANDING","CONTRACTING","STABLE"] },
        "multi_tf_alignment": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "technical_score":    { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      }
    },

    "l5_evolution": {
      "type": "object",
      "description": "L5 进化实验室数据",
      "properties": {
        "shadow_rule_id":            { "type": ["string","null"] },
        "candidate_param_id":        { "type": ["string","null"] },
        "entry_noise_score":         { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "exit_noise_score":          { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "post_exit_continuation_loss": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "missed_profit_after_exit":  { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "promotion_gate_state":     { "type": "string", "enum": ["OPEN","CLOSED","PENDING"] },
        "manual_confirm_required":   { "type": "boolean" },
        "rule_age_bars":            { "type": "integer" },
        "win_rate_historical":      { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "profit_factor_historical": { "type": "number" }
      }
    },

    "v2_shadow": {
      "type": "object",
      "description": "V2 Shadow 元数据（所有 M1-M5 共享）",
      "properties": {
        "db_path":           { "type": "string" },
        "status":            { "type": "string", "enum": ["LIVE","STALE","MISSING"] },
        "last_snap_ts":      { "type": ["integer","null"] },
        "last_snap_age_sec": { "type": ["integer","null"] },
        "snapshots_count":   { "type": "integer" }
      }
    }
  },

  "definitions": {
    "exchange_block": {
      "type": ["object", "null"],
      "description": "Gate/OKX 数据块（包含 whale_ratio）",
      "properties": {
        "ratio":       { "type": "number" },
        "netflow":     { "type": "number" },
        "whale_ratio": { "type": "number" },
        "vol":         { "type": "number" },
        "score":       { "type": "number" },
        "signal":      { "type": "string", "enum": ["LONG","SHORT","NEUTRAL"] }
      }
    },
    "bnb_block": {
      "type": ["object", "null"],
      "description": "Binance 数据块（无 whale_ratio）",
      "properties": {
        "ratio":   { "type": "number" },
        "netflow": { "type": "number" },
        "vol":     { "type": "number" },
        "score":   { "type": "number" },
        "signal":  { "type": "string", "enum": ["LONG","SHORT","NEUTRAL"] }
      }
    }
  }
}
```

### 3.2 Python 类型注解

```python
from dataclasses import dataclass, field
from typing import Literal, Optional

# ── M1 信任等级 ──
TrustLevel = Literal["A", "B", "C", "D", "E"]
Signal     = Literal["LONG", "SHORT", "NEUTRAL"]

# ── Exchange 数据块 ──
@dataclass
class ExchangeBlock:
    ratio:       float
    netflow:     float
    vol:         float
    score:       float
    signal:      Signal
    whale_ratio: Optional[float] = None   # BNB 无此字段

@dataclass
class EvidenceBlock:
    m1_signal_trust_level:   TrustLevel
    flow_consensus_score:    float        # 0.0-1.0
    flow_divergence_score:   float        # 0.0-1.0
    exchange_outlier:        Optional[Literal["gate","okx","bnb"]]
    dominant_exchange:       Optional[Literal["gate","okx","bnb"]]
    data_freshness_score:   float        # 0.0-1.0
    source_count:           int          # 0-3
    valid_exchange_count:   int          # 0-3
    book_taker_alignment:    float = 0.0  # -1.0 to 1.0
    taker_oi_alignment:     float = 0.0  # -1.0 to 1.0
    funding_pressure_state: Literal["POSITIVE","NEGATIVE","NEUTRAL"] = "NEUTRAL"
    trust_flags:            list[str] = field(default_factory=list)
    computed_at:             str = ""

@dataclass
class V2Shadow:
    status:           Literal["LIVE","STALE","MISSING"]
    last_snap_ts:    Optional[int]
    last_snap_age_sec: Optional[int]
    snapshots_count: int = 0

@dataclass
class M1EvidencePayload:
    pair:      str
    ts:        int
    cached_at: str
    gate:      Optional[ExchangeBlock]
    okx:       Optional[ExchangeBlock]
    bnb:       Optional[ExchangeBlock]
    aggregated: dict                        # {ratio, netflow, score, signal, valid_count}
    evidence:  EvidenceBlock
    v2_shadow: Optional[V2Shadow] = None
    m2_support_resistance: Optional[dict] = None
    m3_giant_candle:       Optional[dict] = None
    m4_technical:          Optional[dict] = None
    l5_evolution:          Optional[dict] = None
```

---

## 4. M1 Signal Trust Level 详细规范（V6.5.1）

### 4.1 信任等级判定表

| 等级 | 评分 | 量比 | 净流入 | 共识 | 新鲜度 | 动作 |
|------|------|------|--------|------|--------|------|
| **A** | >= 85 | >= 3.0x | >= 0.8 | 三所全一致 | >= 0.8 | 强势执行（可自动驾驶） |
| **B** | 70-84 | >= 2.0x | >= 0.5 | >= 2所一致 | >= 0.7 | 建议执行（需 AI 二次确认） |
| **C** | 55-69 | 1.5-2.0x | >= 0.4 | >= 2所一致 | >= 0.5 | 谨慎观察（不自动执行） |
| **D** | 40-54 | < 1.5x | 任意 | < 2所一致 | < 0.5 | **禁止入场** |
| **E** | < 40 | 极低/无 | 无 | < 2所 | 任意 | **禁止入场（记录警告）** |

### 4.2 综合评分算法

```python
def compute_trust_score(consensus: float,
                         ratio: float,
                         freshness: float,
                         divergence: float) -> float:
    """
    M1 综合信任评分（0-100）

    权重分配：
      共识贡献    40%  — 三所方向一致性
      量比贡献    30%  — 成交量放大程度（上限 5.0x）
      新鲜度贡献  20%  — 数据时效性（10分钟阈值）
      稳定性贡献  10%  — 分歧越小稳定性越高
    """
    normalized_ratio = min(ratio / 5.0, 1.0) if ratio > 0 else 0.0
    score = (
        consensus          * 40.0 +
        normalized_ratio   * 30.0 +
        freshness          * 20.0 +
        (1.0 - divergence) * 10.0
    )
    return round(score, 1)
```

### 4.3 入场拦截决策表

| 拦截条件 | 拦截代码 | 严重度 |
|---------|---------|--------|
| `data_freshness_score < 0.7` | `STALE_DATA` | **BLOCK** |
| `m1_signal_trust_level == "E"` | `TRUST_LEVEL_E` | **BLOCK** |
| `m1_signal_trust_level == "D"` | `TRUST_LEVEL_D` | **BLOCK** |
| `flow_consensus_score < 0.4` | `EXTREME_DIVERGENCE` | **BLOCK** |
| `volume_ratio < 2.0` 且 `"SPLIT_HIGH"` | `LOW_VOL_HIGH_DIVERGENCE` | **WATCH** |
| Exchange Outlier = 主导交易所 | `DOMINANT_EXCHANGE_OUTLIER` | **WARN + DISCOUNT** |

---

## 5. 三所一致性算法（Three-Exchange Consensus）

### 5.1 方向一致性

```python
def compute_flow_consensus(gate_signal, okx_signal, bnb_signal,
                            aggregated_signal) -> tuple[float, str | None]:
    """
    计算三所方向一致率和 Outlier 交易所。
    返回 (consensus_score, outlier_exchange)
    """
    signals = {"gate": gate_signal, "okx": okx_signal, "bnb": bnb_signal}
    valid = {ex: sig for ex, sig in signals.items() if sig != "NEUTRAL"}

    if not valid:
        return 0.0, None

    agreeing = sum(1 for sig in valid.values() if sig == aggregated_signal)
    consensus = agreeing / len(valid)

    # Outlier：唯一非 NEUTRAL 且与聚合信号冲突的交易所
    outlier = None
    for ex, sig in valid.items():
        if sig != aggregated_signal:
            outlier = ex
            break

    return round(consensus, 3), outlier
```

### 5.2 量比分歧度

```python
def compute_ratio_divergence(gate_r: float, okx_r: float, bnb_r: float) -> float:
    ratios = [r for r in [gate_r, okx_r, bnb_r] if r > 0]
    if len(ratios) < 2:
        return 0.0
    return round((max(ratios) - min(ratios)) / max(ratios), 3)
```

---

## 6. 天眼AI + 出山AI 集成规范

### 6.1 天眼AI 入场裁决集成

```python
# api_autopilot.py — M1 入场门
def m1_entry_gate(pair: str) -> dict:
    data     = calc_fund_flow_for_pair(pair, tf="15m")
    evidence = data.get("evidence", {})

    trust_level = evidence.get("m1_signal_trust_level", "C")
    freshness   = evidence.get("data_freshness_score", 1.0)
    consensus   = evidence.get("flow_consensus_score", 0.0)
    outlier     = evidence.get("exchange_outlier")
    flags       = evidence.get("trust_flags", [])

    # ── BLOCK 层 ──
    if freshness < 0.7:
        return {"action": "BLOCK", "reason": "M1_STALE_DATA", "trust_level": trust_level}
    if trust_level in ("D", "E"):
        return {"action": "BLOCK", "reason": f"M1_TRUST_LEVEL_{trust_level}", "trust_level": trust_level}
    if consensus < 0.4:
        return {"action": "BLOCK", "reason": "M1_EXTREME_DIVERGENCE", "trust_level": trust_level}

    # ── 降权处理 ──
    entry_weight = 1.0
    if outlier and evidence.get("dominant_exchange") == outlier:
        entry_weight *= 0.3
        logger.warning("M1: dominant exchange %s flagged as outlier, weight reduced to 0.3", outlier)

    # ── APPROVE 层 ──
    composite = {
        "pair":           pair,
        "action":        "APPROVE",
        "trust_level":    trust_level,
        "consensus":      consensus,
        "entry_weight":   entry_weight,
        "freshness":      freshness,
        "outlier":        outlier,
        "flags":          flags,
        "m1_signal":      data["aggregated"]["signal"],
        "m1_ratio":       data["aggregated"]["ratio"],
        "m1_netflow":     data["aggregated"]["netflow"],
    }
    return composite
```

### 6.2 出山AI 回撤保护集成

```python
# risk_engine.py — L5 进化 + 回撤保护
def l5_post_entry_guard(pair: str, entry_price: float,
                         current_price: float, position: dict) -> dict:
    l5_state = get_l5_evolution_state(pair)

    # ── L5 晋升门 ──
    if l5_state["promotion_gate_state"] == "CLOSED":
        return {"action": "HOLD", "reason": "L5_GATE_CLOSED"}
    if l5_state["manual_confirm_required"]:
        return {"action": "PENDING_MANUAL", "reason": "L5_LOW_CONFIDENCE"}
    if l5_state["entry_noise_score"] >= 0.6:
        return {"action": "WATCH", "reason": "L5_HIGH_ENTRY_NOISE"}

    # ── ATR 止损（出山AI核心） ──
    atr = get_atr(pair)
    unrealized_pnl_pct = (current_price - entry_price) / entry_price

    if unrealized_pnl_pct <= -2.0 * atr / entry_price:
        return {"action": "EXIT", "reason": "ATR_STOP_LOSS"}

    # ── B3 反转猎杀 ──
    if l5_state.get("post_exit_continuation_loss", 0) >= 0.4:
        # 记录30分钟冷却
        set_cooldown(pair, seconds=1800)
        return {"action": "WATCH", "reason": "L5_B3_CONTINUATION_LOSS_HISTORY"}

    return {"action": "HOLD"}
```

### 6.3 M1-M4 英雄卡综合裁决

```python
def composite_hero_card_verdict(m1_ev, m2_ev=None, m3_ev=None,
                                 m4_ev=None) -> dict:
    """
    合并 M1-M4 信任证据为综合裁决信号。
    用于控制台英雄卡展示。
    """
    grades = {
        "M1": m1_ev.get("m1_signal_trust_level", "C"),
        "M2": m2_ev.get("trust_level", "C") if m2_ev else "C",
        "M3": m3_ev.get("trust_level", "C") if m3_ev else "C",
        "M4": m4_ev.get("trust_level", "C") if m4_ev else "C",
    }
    grade_score = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25, "E": 0.0}
    avg = mean(grade_score[g] for g in grades.values())
    composite = (
        "A" if avg >= 0.875 else
        "B" if avg >= 0.625 else
        "C" if avg >= 0.375 else
        "D"
    )
    return {
        "composite_trust":    composite,
        "per_layer":          grades,
        "composite_score":    round(avg, 3),
        "m1_consensus":      m1_ev.get("flow_consensus_score", 0.0),
        "m1_freshness":      m1_ev.get("data_freshness_score", 0.0),
        "m1_outlier":        m1_ev.get("exchange_outlier"),
        "m1_flags":          m1_ev.get("trust_flags", []),
    }
```

---

## 7. API 端点规范

### 7.1 M1 Evidence 端点

```
GET /api/m1/evidence/<pair>

示例请求：
  curl http://127.0.0.1:9099/api/m1/evidence/BTC-USDT

示例响应：
{
  "ok": true,
  "pair": "BTC/USDT",
  "ts": 1746352800,
  "aggregated": {
    "ratio": 3.45,
    "netflow": 0.72,
    "score": 87.3,
    "signal": "LONG",
    "valid_count": 3
  },
  "evidence": {
    "m1_signal_trust_level": "A",
    "flow_consensus_score": 1.0,
    "flow_divergence_score": 0.0,
    "exchange_outlier": null,
    "dominant_exchange": "gate",
    "data_freshness_score": 0.92,
    "source_count": 3,
    "valid_exchange_count": 3,
    "book_taker_alignment": 0.65,
    "taker_oi_alignment": 0.58,
    "funding_pressure_state": "NEUTRAL",
    "trust_flags": [],
    "computed_at": "2026-05-04T15:00:00Z"
  },
  "v2_shadow": {
    "status": "LIVE",
    "last_snap_ts": 1746352500,
    "last_snap_age_sec": 300,
    "snapshots_count": 847
  }
}
```

---

## 8. 向后兼容性说明

| 字段 | V6.5 存在性 | V6.5.1 变化 | 兼容性处理 |
|------|-----------|------------|---------|
| `aggregated{}` | 原有 | 无变化 | 消费者直接读取，无需修改 |
| `evidence{}` | **新增** | N/A | 消费者使用 `.get("evidence", {})` 兜底 |
| `v2_shadow{}` | **新增** | N/A | 消费者使用 `.get("v2_shadow", {})` 兜底 |
| `m2-m5` 块 | **新增** | N/A | 逐步接入，前端忽略未知 key |
| `ai_evaluate_pair()` | 原有 | 无变化 | 不受影响 |
| Bot overlay configs | 原有 | 无变化 | 不受影响 |
| 数据库 schema | 原有 | 无变化 | 不受影响 |

---

## 9. 已知问题与缓解措施

| 问题 | 文件 | 影响 | V6.5.1 缓解 |
|------|------|------|-----------|
| Binance netflow = 0 | `collector_bnb.py` | `bnb.netflow=0`，聚合 netflow 偏低 | `trust_flags += ["BINANCE_SHADOW_STALE"]`，降权 BNB |
| V2 Shadow 停更 | `fund_flow_v2_collector.py` | `v2_shadow.status = "STALE"` | 新鲜度降级，不阻塞 M1 实时裁决 |
| Gate `defaultType="spot"` | `collector_gate.py:16` | 若旧采集器被调用，读到现货数据 | `trust_flags += ["GATE_SPOT_MODE"]`，降权 Gate |
| OKX Key 池为空 | `api_m1.py:46-72` | OKX 数据全部 null | `trust_flags += ["OKX_KEY_MISSING"]`，valid_count 反映真实情况 |
| L5 影子规则未建立 | `l5_evolution_lab/` | 所有 `l5_evolution_*` 字段为默认值 | 降权执行，依赖 M1-M4 裁决 |

---

## 10. 文件所有权

| 文件 | 角色 | 负责方 |
|------|------|-------|
| `api_m1.py` | M1 资金流采集 + trust evidence 计算 | 户部代理 |
| `collector_gate.py` | M1 Gate 数据源（永续/现货混用风险） | 户部代理 |
| `collector_okx.py` | M1 OKX 数据源 | 户部代理 |
| `collector_bnb.py` | M1 BNB 数据源（netflow=0 待修复） | 户部代理 |
| `m4_m5_shadow_lab.py` | M4-M5 技术面 + 市场结构数据 | 进化署 |
| `l5_evolution_lab/fund_flow_v2_collector.py` | V2 Shadow 数据采集 | 进化署 |
| `l5_evolution_lab/*` | L5 进化实验室（影子规则/候选参数） | 进化署 |
| `console_server.py` | Evidence 消费者 / 英雄卡展示 / API 网关 | 相权殿 |
| `api_autopilot.py` | 天眼AI 入场裁决（置信度 50% 门槛） | 御史台 |
| `risk_engine.py` | 出山AI 回撤保护 + ATR 止损 + B3 反转猎杀 | 御史台 |
