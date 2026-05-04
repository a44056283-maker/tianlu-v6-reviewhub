# M1-M5 Evidence Payload Specification
**Version:** 1.0 | **Date:** 2026-05-04 | **Status:** DRAFT - Pending GPT Review
**Author:** 户部代理 | **Scope:** Tianlu V6.5 M1-M5 Capital Flow Evidence Layer

---

## 1. Overview

This document defines the unified evidence payload structure for the M1-M5 capital flow evidence layer in Tianlu V6.5. All five modules (M1: Volume Ratio, M2: Netflow Direction, M3: Whale Ratio, M4: Technical Confirmation, M5: Market Structure) share a common wrapper envelope and expose trust signals consumed by the 天眼AI (api_autopilot) and 出山AI (risk_engine) decision pipelines.

---

## 2. Design Principles

1. **Backward-compatible envelope** — Existing `aggregated{}` fields (ratio, netflow, score, signal, valid_count) are preserved unchanged. Trust-layer fields are added as new top-level keys.
2. **Explicit provenance** — Every payload carries its source file, data age, and exchange coverage so consumers can reject stale data without guessing.
3. **No trading-side effects** — All evidence computation is read-only: no `force_entry/exit`, no exchange API writes, no bot config changes.
4. **A/B/C/D/E trust levels** — Human-readable signal quality gate used by both autopilot and human review.

---

## 3. M1 Evidence Payload Structure

### 3.1 Top-Level Envelope

```python
{
    "pair": str,              # e.g. "BTC/USDT"
    "ts": int,                # Unix timestamp of scan
    "cached_at": str,         # ISO datetime string of cache hit

    # ── Per-exchange raw data (unchanged) ──
    "gate": { ratio, netflow, whale_ratio, vol, score, signal } | None,
    "okx":  { ratio, netflow, whale_ratio, vol, score, signal } | None,
    "bnb":  { ratio, netflow, vol, score, signal }              | None,

    # ── Aggregated raw data (unchanged) ──
    "aggregated": {
        "ratio": float,
        "netflow": float,
        "score": float,
        "signal": str,          # "LONG" | "SHORT" | "NEUTRAL"
        "valid_count": int,     # 0-3
    },

    # ── NEW: Trust evidence layer ──
    "evidence": {
        "m1_signal_trust_level": str,   # "A" | "B" | "C" | "D" | "E"
        "flow_consensus_score": float,   # 0.0 - 1.0
        "flow_divergence_score": float,  # 0.0 - 1.0
        "exchange_outlier": str | None,  # None | "binance" | "gate" | "okx"
        "data_freshness_score": float,  # 0.0 - 1.0  (<0.7 → block entry)
        "source_count": int,             # 3 = all three exchanges
        "valid_exchange_count": int,    # exchanges agreeing on direction
        "outlier_exchange": str | None, # which exchange is the outlier
        "trust_flags": [str],           # e.g. ["BINANCE_SHADOW_STALE", "SPLIT_HIGH"]
        "computed_at": str,             # ISO datetime
    },

    # ── NEW: V2 shadow metadata ──
    "v2_shadow": {
        "db_path": str,
        "last_snap_ts": int | None,
        "last_snap_age_sec": int | None,
        "shadow_confidence": float | None,
        "shadow_direction": str | None,
        "status": str,  # "LIVE" | "STALE" | "MISSING"
    },
}
```

### 3.2 Field Definitions

| Field | Type | Unit / Range | Description |
|---|---|---|---|
| `m1_signal_trust_level` | str | A/B/C/D/E | Overall signal quality grade (see Section 4) |
| `flow_consensus_score` | float | 0.0 - 1.0 | Fraction of exchanges agreeing on direction |
| `flow_divergence_score` | float | 0.0 - 1.0 | `1 - consensus`; high value = directional conflict |
| `exchange_outlier` | str\|None | exchange id | The single exchange whose direction conflicts with the majority. Null if no outlier or <2 valid exchanges |
| `data_freshness_score` | float | 0.0 - 1.0 | Age-based freshness: `max(0, 1 - age_sec/600)`. Below 0.7 blocks entry |
| `source_count` | int | 0-3 | Count of exchanges returning non-null data |
| `valid_exchange_count` | int | 0-3 | Exchanges whose signal matches `aggregated.signal` |
| `trust_flags` | list[str] | - | Diagnostic tags: `BINANCE_SHADOW_STALE`, `GATE_SPOT_MODE`, `SPLIT_HIGH`, `SINGLE_EXCHANGE`, `V2_SHADOW_DEAD`, `OKX_KEY_MISSING` |
| `v2_shadow.status` | str | LIVE/STALE/MISSING | V2 shadow DB health status |

---

## 4. M1 Signal Trust Levels (A/B/C/D/E)

### 4.1 Grade Table

| Grade | Threshold | Conditions | Entry Permission |
|---|---|---|---|
| **A** | >= 85% | 3 exchanges agree, ratio >= 3.0x, freshness >= 0.8 | Full evidence; autopilot may act |
| **B** | 70-84% | 2+ exchanges agree, ratio >= 2.0x, freshness >= 0.7 | Cautious entry; requires secondary confirmation |
| **C** | 55-69% | Mild consensus, ratio 1.5-2.0x | Watch only; no entry |
| **D** | 40-54% | Low confidence signals | Entry blocked regardless of other signals |
| **E** | < 40% | No data / all stale / severe divergence | Entry blocked; log warning |

### 4.2 Grade Computation Algorithm

```python
def compute_trust_grade(data: dict) -> tuple[str, dict]:
    """
    Returns (grade, evidence_dict) for the given calc_fund_flow_for_pair output.
    Pure function — no I/O, no side effects.
    """
    agg     = data.get("aggregated", {})
    ratio   = agg.get("ratio", 0) or 0
    netflow = agg.get("netflow", 0) or 0
    signal  = agg.get("signal", "NEUTRAL")
    vc      = agg.get("valid_count", 0)

    gate = data.get("gate") or {}
    okx  = data.get("okx")  or {}
    bnb   = data.get("bnb")   or {}

    g_sig = gate.get("signal", "NEUTRAL")
    o_sig = okx.get("signal",  "NEUTRAL")
    b_sig = bnb.get("signal",  "NEUTRAL")

    # ── Consensus: exchanges whose direction matches aggregated signal ──
    exchange_sigs = [s for s in [g_sig, o_sig, b_sig] if s != "NEUTRAL"]
    agreeing = [s for s in exchange_sigs if s == signal]
    consensus = len(agreeing) / max(len(exchange_sigs), 1)
    divergence = 1.0 - consensus

    # ── Outlier detection ──
    outlier = None
    all_sigs = {"gate": g_sig, "okx": o_sig, "bnb": b_sig}
    for ex, sig in all_sigs.items():
        if sig != "NEUTRAL" and sig != signal:
            outlier = ex
            break

    # ── Freshness (placeholder — updated by caller with real cache age) ──
    freshness = data.get("evidence", {}).get("data_freshness_score", 0.95)

    # ── Trust flags ──
    flags = []
    if vc < 2:
        flags.append("SINGLE_EXCHANGE" if vc == 1 else "NO_DATA")
    if divergence >= 0.5:
        flags.append("SPLIT_HIGH")
    if outlier:
        flags.append(f"OUTLIER_{outlier.upper()}")

    # ── Composite score (0-100) ──
    score = (
        consensus    * 40 +   # consensus contribution
        min(ratio / 5.0, 1.0) * 30 +  # volume ratio (cap at 5x)
        freshness    * 20 +   # data freshness
        (1.0 - divergence) * 10   # direction stability
    )

    # ── Grade assignment ──
    if   score >= 85: grade = "A"
    elif score >= 70: grade = "B"
    elif score >= 55: grade = "C"
    elif score >= 40: grade = "D"
    else:            grade = "E"

    evidence = {
        "m1_signal_trust_level":    grade,
        "flow_consensus_score":    round(consensus, 3),
        "flow_divergence_score":   round(divergence, 3),
        "exchange_outlier":        outlier,
        "data_freshness_score":    freshness,
        "source_count":            vc,
        "valid_exchange_count":    len(agreeing),
        "trust_flags":             flags,
        "computed_at":            datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return grade, evidence
```

### 4.3 Entry Blocking Rules

| Condition | Action |
|---|---|
| `data_freshness_score < 0.7` | **BLOCK** — stale data |
| `m1_signal_trust_level == "E"` | **BLOCK** — no reliable signal |
| `m1_signal_trust_level == "D"` | **BLOCK** — insufficient confidence |
| `flow_consensus_score < 0.4` | **BLOCK** — extreme disagreement |
| `exchange_outlier` == primary exchange | **WARN + DISCOUNT** — outlier exchange weight |

---

## 5. M2-M5 Evidence Payload (Reference)

For completeness, the M2-M5 shadow lab (`m4_m5_shadow_lab.py`) and V2 collector (`fund_flow_v2_collector.py`) share the same envelope pattern:

### 5.1 M2: Netflow Direction

```python
{
    "m2_netflow": {
        "direction": str,      # "LONG" | "SHORT" | "NEUTRAL"
        "score": float,
        "confidence": float,
        "exchange_agreement": float,  # 0.0-1.0
        "taker_delta_ratio": float | None,
        "trust_level": str,    # A/B/C/D/E (same scale as M1)
    }
}
```

### 5.2 M3: Whale Ratio

```python
{
    "m3_whale": {
        "whale_ratio": float,
        "large_trade_count": int,
        "whale_dominance": str,  # "BUYER" | "SELLER" | "BALANCED"
        "trust_level": str,
    }
}
```

### 5.3 M4: Technical Confirmation

```python
{
    "m4_technical": {
        "rsi_14": float | None,
        "atr_14": float | None,
        "oi_change_pct": float | None,
        "funding_rate": float | None,
        "book_imbalance": float | None,
        "m4_score": float,     # weighted composite
        "trust_level": str,
    }
}
```

### 5.4 M5: Market Structure

```python
{
    "m5_structure": {
        "price": float,
        "spread_pct": float | None,
        "bid_depth": float | None,
        "ask_depth": float | None,
        "open_interest": float | None,
        "oi_change_pct": float | None,
        "m5_score": float,
        "trust_level": str,
    }
}
```

### 5.5 V2 Shadow Metadata (All M1-M5)

```python
{
    "v2_shadow": {
        "db_path": str,
        "status": str,       # "LIVE" | "STALE" | "MISSING"
        "last_snap_ts": int | None,
        "last_snap_age_sec": int | None,
        "health_ts": int | None,
        "health_exchanges": dict,  # {exchange: {ok, latency_ms, error}}
        "snapshots_count": int,
    }
}
```

---

## 6. Trust Level Integration with 天眼AI

### 6.1 API Contract

The 天眼AI (`api_autopilot.py`) calls `calc_fund_flow_for_pair()` and expects the returned dict to contain the `evidence{}` top-level key. If `evidence` is absent (backward compatibility), it should treat the signal as `trust_level = "C"` (watch-only).

```python
# api_autopilot.py integration point
data = calc_fund_flow_for_pair(pair, tf="15m")
evidence = data.get("evidence", {})

trust_level = evidence.get("m1_signal_trust_level", "C")
freshness   = evidence.get("data_freshness_score", 1.0)
consensus   = evidence.get("flow_consensus_score", 0.0)

# Blocking gate
if freshness < 0.7:
    return {"action": "BLOCK", "reason": "STALE_DATA"}
if trust_level in ("D", "E"):
    return {"action": "BLOCK", "reason": f"TRUST_LEVEL_{trust_level}"}

# Proceed with full evidence
score  = data["aggregated"]["score"]
signal = data["aggregated"]["signal"]
# ... full AI evaluation
```

### 6.2 Composite Signal for M1-M4 Hero Cards

```python
def composite_trust_signal(m1_ev: dict, m2_ev: dict = None,
                           m3_ev: dict = None, m4_ev: dict = None) -> dict:
    """
    Merge M1-M4 trust evidence into a single verdict signal.
    Used by the M1-M4 hero card display in console_server.
    """
    grades = {
        "M1": m1_ev.get("m1_signal_trust_level", "C"),
        "M2": m2_ev.get("trust_level", "C") if m2_ev else "C",
        "M3": m3_ev.get("trust_level", "C") if m3_ev else "C",
        "M4": m4_ev.get("trust_level", "C") if m4_ev else "C",
    }
    grade_score = {"A": 1.0, "B": 0.75, "C": 0.5, "D": 0.25, "E": 0.0}
    avg = mean(grade_score[g] for g in grades.values())
    composite = "A" if avg >= 0.875 \
           else "B" if avg >= 0.625 \
           else "C" if avg >= 0.375 \
           else "D"
    return {
        "composite_trust": composite,
        "per_layer": grades,
        "composite_score": round(avg, 3),
        "consensus": m1_ev.get("flow_consensus_score", 0.0),
        "freshness": m1_ev.get("data_freshness_score", 0.0),
        "outlier":  m1_ev.get("exchange_outlier"),
    }
```

---

## 7. Known Issues Referenced in This Spec

| Issue | File | Impact | Mitigation in This Spec |
|---|---|---|---|
| Binance netflow missing from V2 shadow | `collector_bnb.py` | M1 bnb channel returns 0 netflow | `trust_flags += ["BINANCE_SHADOW_STALE"]`; discount bnb weight |
| V2 shadow DB not updated (stale) | `fund_flow_v2_collector.py` | `v2_shadow.status = "STALE"` | Freshness score drops to 0 on stale; entry blocked |
| `collector_gate.py` defaultType="spot" | `collector_gate.py:16` | Gate spot data mixed with perp bots | Flagged as `GATE_SPOT_MODE`; separate perp collector path |
| OKX key pool empty | `api_m1.py:46-72` | OKX data unavailable | `trust_flags += ["OKX_KEY_MISSING"]`; valid_count reflects reality |

---

## 8. Backward Compatibility Notes

- `calc_fund_flow_for_pair()` return value unchanged except for added `evidence{}` key.
- `ai_evaluate_pair()` unchanged — it continues to use `aggregated{}` fields.
- Existing database schema in `m1_cache.sqlite` unchanged.
- Existing console_server `/api/l5/fund_flow_v2` endpoint unchanged.
- Frontend HTML tabs (`tabs/live-eval.html`, `tabs/l5-m4m5-shadow.html`) require no changes to render the new payload — they simply ignore unknown keys.

---

## 9. File Ownership

| File | Role | Trust Layer Owner |
|---|---|---|
| `api_m1.py` | M1 evidence computation | 户部代理 |
| `collector_gate.py` | M1 Gate data source | 户部代理 |
| `collector_okx.py` | M1 OKX data source | 户部代理 |
| `collector_bnb.py` | M1 BNB data source | 户部代理 |
| `l5_evolution_lab/fund_flow_v2_collector.py` | M2-M5 V2 shadow | 进化署 |
| `l5_evolution_lab/m4_m5_shadow_lab.py` | M4-M5 comparison | 进化署 |
| `console_server.py` | Evidence consumer / autopilot param bridge | 相权殿 |
| `api_autopilot.py` | 天眼AI entry decision | 御史台 |
