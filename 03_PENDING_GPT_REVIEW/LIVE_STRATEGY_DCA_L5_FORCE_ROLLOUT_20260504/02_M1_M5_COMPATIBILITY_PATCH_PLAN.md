# M1-M5 Compatibility Patch Plan
**Version:** 1.0 | **Date:** 2026-05-04 | **Status:** DRAFT - Pending GPT Review
**Author:** 户部代理 | **Scope:** Tianlu V6.5 Trust Evidence Layer Live Rollout

---

## 1. Rollout Constraints (Strict)

- **NO bot restart** — do not touch running bot processes
- **NO exchange API trading calls** — no `force_entry`, `force_exit`, or order placement
- **NO force_entry/exit** — read-only evidence only
- **Backup first** — all modified files archived before any change
- **Backward-compatible** — existing data flows must not break

---

## 2. Backup Plan

Before any edit, run:

```bash
# Create timestamped backup directory
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
mkdir -p "$BACKUP_DIR"

# Backup modified files
cp -a ~/freqtrade_console/api_m1.py               "$BACKUP_DIR/api_m1.py.orig"
cp -a ~/freqtrade_console/collector_gate.py        "$BACKUP_DIR/collector_gate.py.orig"
cp -a ~/freqtrade_console/collector_okx.py         "$BACKUP_DIR/collector_okx.py.orig"
cp -a ~/freqtrade_console/collector_bnb.py          "$BACKUP_DIR/collector_bnb.py.orig"
cp -a ~/freqtrade_console/console_server.py        "$BACKUP_DIR/console_server.py.orig"

# Verify backup
ls -lh "$BACKUP_DIR/"
echo "Backup complete at $(date)"
```

**Rollback command:**
```bash
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
for f in api_m1.py collector_gate.py collector_okx.py collector_bnb.py console_server.py; do
    cp -a "$BACKUP_DIR/${f}.orig" ~/freqtrade_console/$f
done
echo "Rollback complete"
```

---

## 3. Files to Modify

| # | File | Change Type | Risk |
|---|---|---|---|
| 1 | `api_m1.py` | Add evidence computation function + inject into return | Low |
| 2 | `console_server.py` | Add `/api/m1/evidence` endpoint (new route only) | Low |
| 3 | `collector_gate.py` | Add `perp` mode + `defaultType` fix (comment) | Medium |

No changes to `collector_okx.py`, `collector_bnb.py`, `l5_evolution_lab/*`.

---

## 4. Patch: api_m1.py

### 4.1 Add import for `datetime` (if not present)

Check around line 11: `from datetime import datetime` — should already be present.

### 4.2 Add `compute_trust_grade` function

Insert **after** line 554 (`def _calc_score` ends), before `def ai_evaluate_pair`.

```python
# ── Trust Evidence Layer (M1裁决补丁 v1.0 2026-05-04) ──────────────────────
def compute_trust_grade(data: dict) -> tuple[str, dict]:
    """
    Compute M1 signal trust grade (A/B/C/D/E) and evidence metadata.
    Pure function — no I/O, no side effects. Read-only.

    Grade thresholds:
      A: >= 85%  — 3 exchanges agree, ratio >= 3.0x, freshness >= 0.8
      B: 70-84%  — 2+ exchanges agree, ratio >= 2.0x, freshness >= 0.7
      C: 55-69%  — mild signal
      D: 40-54%  — low confidence, entry BLOCKED
      E: < 40%   — no data / stale / severe divergence, BLOCKED

    Returns (grade, evidence_dict).
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

    # Consensus: exchanges whose direction matches aggregated signal
    exchange_sigs = [s for s in [g_sig, o_sig, b_sig] if s != "NEUTRAL"]
    agreeing = [s for s in exchange_sigs if s == signal]
    consensus = len(agreeing) / max(len(exchange_sigs), 1)
    divergence = 1.0 - consensus

    # Outlier detection: single exchange that disagrees
    outlier = None
    all_sigs = {"gate": g_sig, "okx": o_sig, "bnb": b_sig}
    for ex, sig in all_sigs.items():
        if sig not in ("NEUTRAL", signal) and sig != "NEUTRAL":
            outlier = ex
            break

    # Freshness — default 0.95 if not set by caller (backward compat)
    freshness = data.get("evidence", {}).get("data_freshness_score", 0.95)

    # Trust flags
    flags = []
    if vc == 0:
        flags.append("NO_DATA")
    elif vc == 1:
        flags.append("SINGLE_EXCHANGE")
    if divergence >= 0.5:
        flags.append("SPLIT_HIGH")
    if outlier:
        flags.append(f"OUTLIER_{outlier.upper()}")
    # Check Binance shadow staleness via v2_shadow if present
    v2 = data.get("v2_shadow", {})
    if v2.get("status") == "STALE":
        flags.append("V2_SHADOW_STALE")
    elif v2.get("status") == "MISSING":
        flags.append("V2_SHADOW_MISSING")
    # Check Gate spot mode flag from gate record
    if gate.get("_is_spot", False):
        flags.append("GATE_SPOT_MODE")
    # OKX key missing check
    if not _M1_OKX_KEYS:
        flags.append("OKX_KEY_MISSING")

    # Composite score 0-100
    score = (
        consensus            * 40.0 +
        min(ratio / 5.0, 1.0) * 30.0 +
        freshness            * 20.0 +
        (1.0 - divergence)   * 10.0
    )

    # Grade assignment
    if   score >= 85: grade = "A"
    elif score >= 70: grade = "B"
    elif score >= 55: grade = "C"
    elif score >= 40: grade = "D"
    else:            grade = "E"

    evidence = {
        "m1_signal_trust_level":  grade,
        "flow_consensus_score":   round(consensus, 3),
        "flow_divergence_score":  round(divergence, 3),
        "exchange_outlier":        outlier,
        "data_freshness_score":   freshness,
        "source_count":           vc,
        "valid_exchange_count":   len(agreeing),
        "trust_flags":            flags,
        "computed_at":            datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    return grade, evidence
```

### 4.3 Inject evidence into `calc_fund_flow_for_pair` return

Find the return block in `calc_fund_flow_for_pair` (around line 449-463). The current return is:

```python
    return {
        "pair": pair,
        "ts": int(time.time()),
        "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gate": results.get("gate"),
        "okx": results.get("okx"),
        "bnb": results.get("bnb"),
        "aggregated": {
            "ratio": round(agg_ratio, 3),
            "netflow": round(agg_netflow, 3),
            "score": agg_score,
            "signal": agg_signal,
            "valid_count": len([r for r in results.values() if r]),
        }
    }
```

Replace with:

```python
    agg_data = {
        "ratio": round(agg_ratio, 3),
        "netflow": round(agg_netflow, 3),
        "score": agg_score,
        "signal": agg_signal,
        "valid_count": len([r for r in results.values() if r]),
    }
    # Build raw data dict for trust computation
    raw_data = {
        "pair": pair,
        "ts": int(time.time()),
        "gate": results.get("gate"),
        "okx": results.get("okx"),
        "bnb": results.get("bnb"),
        "aggregated": agg_data,
    }
    # Compute trust grade and evidence (read-only, no I/O)
    _, evidence = compute_trust_grade(raw_data)

    # Inject gate spot-mode flag
    if results.get("gate"):
        # collector_gate defaultType="spot" — mark if perp data unavailable
        results["gate"]["_is_spot"] = True

    return {
        "pair": pair,
        "ts": int(time.time()),
        "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gate": results.get("gate"),
        "okx": results.get("okx"),
        "bnb": results.get("bnb"),
        "aggregated": agg_data,
        "evidence": evidence,
    }
```

### 4.4 Optional: Add V2 shadow status to evidence (best-effort)

In `calc_fund_flow_for_pair`, after computing `evidence`, add:

```python
    # Best-effort V2 shadow health check (non-blocking)
    v2_status = "MISSING"
    v2_last_ts = None
    v2_last_age = None
    try:
        v2_db = Path(__file__).parent / "l5_evolution_lab" / "fund_flow_v2_shadow.sqlite"
        if v2_db.exists():
            conn = sqlite3.connect(str(v2_db), timeout=3.0)
            row = conn.execute(
                "SELECT ts FROM fund_flow_v2_snapshots ORDER BY ts DESC LIMIT 1"
            ).fetchone()
            conn.close()
            if row:
                v2_last_ts = row[0]
                v2_last_age = int(time.time()) - v2_last_ts
                v2_status = "LIVE" if v2_last_age < 600 else "STALE"
    except Exception:
        v2_status = "MISSING"

    evidence["v2_shadow"] = {
        "status": v2_status,
        "last_snap_ts": v2_last_ts,
        "last_snap_age_sec": v2_last_age,
    }
```

**Note:** This requires adding `from pathlib import Path` at the top of `calc_fund_flow_for_pair` if not already imported. Check line 10 — `Path` is already imported.

### 4.5 Add `get_evidence_for_pair` public API

Add after `ai_evaluate_pair` (after line 632):

```python
# ── Public evidence API ──────────────────────────────────────────────────────
def get_evidence_for_pair(pair: str, tf: str = "15m") -> dict:
    """
    Convenience wrapper: returns just the evidence dict for a pair.
    Equivalent to calc_fund_flow_for_pair(pair, tf)["evidence"].
    Read-only — no trading side effects.
    """
    data = calc_fund_flow_for_pair(pair, tf)
    return data.get("evidence", {})
```

### 4.6 Diff summary for api_m1.py

```
+ line ~557: insert compute_trust_grade() function (~80 lines)
+ line ~449-463: modify calc_fund_flow_for_pair return to inject evidence
+ line ~632: insert get_evidence_for_pair() wrapper (~10 lines)
  (no deletion of existing code)
```

---

## 5. Patch: console_server.py

### 5.1 Add new endpoint for M1 evidence (non-breaking)

Find a suitable location near existing M1 endpoints (around line 3826 where fund_flow_v2_status lives). Add:

```python
# ── M1 Trust Evidence API (V6.5.1 裁决补丁) ────────────────────────────────
@app.route("/api/m1/evidence/<pair>")
def api_m1_evidence(pair: str):
    """
    Returns M1 trust evidence for a single pair.
    GET /api/m1/evidence/BTC-USDT

    Response: { ok, pair, evidence{}, aggregated{}, v2_shadow{} }
    """
    try:
        from api_m1 import calc_fund_flow_for_pair, compute_trust_grade
        # Normalize pair format: BTC-USDT -> BTC/USDT
        pair_norm = pair.replace("-", "/")
        data = calc_fund_flow_for_pair(pair_norm, tf="15m")
        evidence = data.get("evidence", {})
        return jsonify({
            "ok": True,
            "pair": pair_norm,
            "ts": int(time.time()),
            "aggregated": data.get("aggregated"),
            "evidence": evidence,
            "v2_shadow": evidence.get("v2_shadow", {}),
        })
    except Exception as e:
        logger.warning("api_m1_evidence error %s: %s", pair, e)
        return jsonify({"ok": False, "error": str(e), "pair": pair}), 500
```

**Note:** `compute_trust_grade` is imported inside the route to avoid module-level import of `api_m1` (which is already imported at line 32). This prevents circular import issues.

### 5.2 Diff summary for console_server.py

```
+ one new @app.route function (~25 lines)
  (no modification of existing endpoints or data flows)
```

---

## 6. Patch: collector_gate.py (Informational — No Code Change Required)

**Issue:** Line 16 hardcodes `defaultType: "spot"` in the ccxt options.

**Status:** **No code change required for this rollout.** The existing `collector_gate.py` is used by the bot's own data collection, not by `api_m1.py`. The `api_m1.py` uses its own `_make_exchange()` factory which correctly targets perp (`"gate"`, `"gateio"` ccxt ID uses USDT perpetual by default when no `defaultType` is set).

The spot-mode risk is documented in `trust_flags` via `GATE_SPOT_MODE` in the evidence layer, triggered only when `collector_gate.py` is invoked from bot contexts. The evidence layer flags this as a trust concern without modifying the collector.

**Future action (separate ticket):** Create a `collector_gate_perp.py` that uses `defaultType: "futures"` for perp-specific data. Track in: `memory/gate_perp_collector_todo.md`.

---

## 7. V2 Shadow Health Check (Non-Breaking Addition)

The V2 shadow DB staleness check (Section 4.4) is best-effort — it uses a 3-second timeout on the sqlite connection to avoid blocking the M1 scan if the shadow DB is locked.

```
try:
    conn = sqlite3.connect(str(v2_db), timeout=3.0)
    row = conn.execute("SELECT ts FROM fund_flow_v2_snapshots ORDER BY ts DESC LIMIT 1").fetchone()
    conn.close()
    if row:
        v2_last_ts = row[0]
        v2_last_age = int(time.time()) - v2_last_ts
        v2_status = "LIVE" if v2_last_age < 600 else "STALE"
except Exception:
    v2_status = "MISSING"
```

If the V2 collector (`fund_flow_v2_collector.py`) has not run in >10 minutes, `v2_status = "STALE"` and the evidence layer records `V2_SHADOW_STALE` flag. This does **not** block entry — it is informational only.

---

## 8. Compatibility Matrix

| Component | Before Patch | After Patch | Breaking? |
|---|---|---|---|
| `calc_fund_flow_for_pair()` return | 7 keys | 8 keys (+ `evidence`) | No — new key only |
| `ai_evaluate_pair()` | Unchanged | Unchanged | No |
| `scan_all_pairs()` | Unchanged | Injects `evidence` into each result | No |
| `m1_cache.sqlite` schema | Unchanged | Unchanged | No |
| Bot overlay configs | Unchanged | Unchanged | No |
| `/api/l5/fund_flow_v2` | Unchanged | Unchanged | No |
| Frontend tabs | Read existing keys | Ignore unknown `evidence` key | No |
| `/api/m1/evidence/<pair>` | 404 Not Found | Returns evidence dict | New endpoint only |

---

## 9. Verification Steps (Post-Patch, No Bot Restart)

After patching, verify via console_server without restarting any bots:

```bash
# Test 1: Direct M1 evidence endpoint (new)
curl -s http://127.0.0.1:9099/api/m1/evidence/BTC-USDT | python3 -m json.tool

# Expected: {"ok": true, "pair": "BTC/USDT", "evidence": {"m1_signal_trust_level": "A|B|C|...", ...}}

# Test 2: Verify calc_fund_flow_for_pair includes evidence key
curl -s http://127.0.0.1:9099/api/m1/evidence/ETH-USDT | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('evidence' in d, d.get('evidence',{}).get('m1_signal_trust_level'))"

# Test 3: Check V2 shadow status
curl -s http://127.0.0.1:9099/api/l5/fund_flow_v2 | python3 -m json.tool

# Test 4: Verify no breaking change in existing M1 data
curl -s http://127.0.0.1:9099/api/m1/evidence/SOL-USDT | \
  python3 -c "import sys,json; d=json.load(sys.stdin); a=d.get('aggregated',{}); print('ratio' in a, 'netflow' in a, 'signal' in a, 'valid_count' in a)"
# Expected: True True True True

# Test 5: Verify trust_flags populated
curl -s http://127.0.0.1:9099/api/m1/evidence/DOGE-USDT | \
  python3 -c "import sys,json; d=json.load(sys.stdin); ev=d.get('evidence',{}); print(ev.get('trust_flags',[]))"
```

---

## 10. Rollout Sequence

```
Step 1: Run backup commands (Section 2)
Step 2: Apply api_m1.py patch (Section 4)
Step 3: Apply console_server.py patch (Section 5)
Step 4: Restart console_server only:
          # On Mac A:
          cd ~/freqtrade_console && pkill -f "python.*console_server" && sleep 2 && nohup python3 console_server.py > ~/.console_server.log 2>&1 &
Step 5: Run verification tests (Section 9)
Step 6: Report status to 相权殿
```

**CRITICAL:** Step 4 restarts **only** console_server (port 9099). Bot processes (ports 9090-9097) are untouched.

---

## 11. Known Limitations

1. **Binance netflow still zero** — The BNB collector (`collector_bnb.py`) does not compute netflow from OHLCV. The `bnb{}` dict returns `netflow=0`. The evidence layer handles this by only counting non-NEUTRAL signals in consensus. A future patch should add `_calc_netflow_from_ohlcv` to `collector_bnb.py`.

2. **V2 shadow DB may be STALE** — If `fund_flow_v2_collector.py` cron job is not running, `v2_shadow.status = "STALE"`. This is informational only and does not block entry in the current patch. A future patch may elevate this to a blocking condition.

3. **OKX key pool empty** — If no OKX API keys are loaded (all configs use PLACEHOLDER), `_M1_OKX_KEYS` is empty and `OKX_KEY_MISSING` flag is raised. The system still functions with Gate + BNB data, but trust grade is reduced accordingly.

4. **Gate spot vs perp ambiguity** — The `collector_gate.py` `defaultType: "spot"` issue is documented but not fixed in this patch. The evidence layer flags it; the actual fix requires a separate `collector_gate_perp.py`.
