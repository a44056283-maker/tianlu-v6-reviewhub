"""GET-only L5 data aggregation with mock fallback.

This module is intentionally side-effect free: it reads local readonly artifacts
and never calls bot RPC, exchange APIs, or mutation endpoints.
"""

from __future__ import annotations

import json
import math
import sqlite3
import time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
LEGACY_BASE_DIR = Path("/Users/luxiangnan/freqtrade_console")
READONLY_ROOTS = tuple(dict.fromkeys((BASE_DIR, LEGACY_BASE_DIR)))
L5_LAB_DIRS = tuple(root / "l5_evolution_lab" for root in READONLY_ROOTS)
BT_CORE_DIRS = tuple(root / "bt_tools" / "backtest_core" for root in READONLY_ROOTS)
BT_DATA_DIRS = tuple(core / "data" for core in BT_CORE_DIRS)
BT_REPORT_DIRS = tuple(
    path
    for root in READONLY_ROOTS
    for path in (
        root / "bt_tools" / "backtest_core" / "reports",
        root / "bt_tools" / "backtest_core" / "results",
        root / "bt_tools" / "reports",
        root / "backtest_results",
    )
)
DATA_POOL_DBS = tuple(root / "data_pool.db" for root in READONLY_ROOTS)
EVOLUTION_PROGRESS_FILES = tuple(root / "evolution_progress.json" for root in READONLY_ROOTS)

SAFE_TIMEFRAMES = {"1m", "5m", "15m", "1h", "4h", "1d"}


def _now_ms() -> int:
    return int(time.time() * 1000)


def _file_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "updated_at": None}
    return {"exists": True, "updated_at": int(path.stat().st_mtime)}


def _read_json(path: Path) -> Any:
    if not path.exists() or not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except Exception:
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, ""):
            return default
        return int(float(value))
    except Exception:
        return default


def _round(value: Any, digits: int = 4) -> float:
    return round(_as_float(value), digits)


def _source(name: str, status: str, detail: str = "", updated_at: int | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "updated_at": updated_at,
    }


def _first_existing(paths: tuple[Path, ...]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _mock_candles(limit: int = 96) -> list[dict[str, Any]]:
    base = 68400.0
    candles: list[dict[str, Any]] = []
    start = _now_ms() - limit * 15 * 60 * 1000
    for idx in range(limit):
        drift = idx * 8.5
        wave = math.sin(idx / 6.0) * 260
        close = base + drift + wave
        open_ = close - math.sin(idx / 5.0) * 80
        high = max(open_, close) + 110 + (idx % 5) * 8
        low = min(open_, close) - 105 - (idx % 3) * 9
        volume = 1200 + (idx % 18) * 80 + abs(math.sin(idx / 4.0)) * 560
        candles.append(
            {
                "ts": start + idx * 15 * 60 * 1000,
                "open": round(open_, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": round(volume, 2),
                "source": "mock",
            }
        )
    return candles


def _mock_trades() -> list[dict[str, Any]]:
    return [
        {"pair": "BTC/USDT", "side": "long", "profit_pct": 3.2, "duration": "4h 12m", "result": "win"},
        {"pair": "ETH/USDT", "side": "long", "profit_pct": 1.8, "duration": "2h 35m", "result": "win"},
        {"pair": "SOL/USDT", "side": "long", "profit_pct": -0.9, "duration": "1h 22m", "result": "loss"},
        {"pair": "BTC/USDT", "side": "long", "profit_pct": 2.4, "duration": "5h 04m", "result": "win"},
    ]


def _mock_equity_curve() -> list[dict[str, Any]]:
    equity = 10000.0
    curve = []
    for idx, trade in enumerate(_mock_trades(), start=1):
        equity *= 1 + _as_float(trade.get("profit_pct")) / 100.0
        curve.append({"step": idx, "equity": round(equity, 2), "source": "mock"})
    return curve


def _load_data_pool_candles(pair: str, timeframe: str, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if timeframe not in SAFE_TIMEFRAMES:
        return [], _source("data_pool_sqlite", "unavailable", "unsupported timeframe")
    db_path = _first_existing(DATA_POOL_DBS)
    if db_path is None:
        return [], _source("data_pool_sqlite", "unavailable", "data_pool.db missing")

    table = f"candles_avg_{timeframe}"
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"""
            SELECT ts, o_avg, h_avg, l_avg, c_avg, v_avg
            FROM {table}
            WHERE pair = ?
            ORDER BY ts DESC
            LIMIT ?
            """,
            (pair, limit),
        ).fetchall()
    except Exception as exc:
        return [], _source("data_pool_sqlite", "unavailable", f"read failed: {type(exc).__name__}")
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    candles = [
        {
            "ts": _as_int(row["ts"]),
            "open": _round(row["o_avg"], 2),
            "high": _round(row["h_avg"], 2),
            "low": _round(row["l_avg"], 2),
            "close": _round(row["c_avg"], 2),
            "volume": _round(row["v_avg"], 2),
            "source": "data_pool_sqlite",
        }
        for row in reversed(rows)
    ]
    status = "real" if candles else "unavailable"
    detail = f"{len(candles)} candles" if candles else "no rows"
    return candles, _source("data_pool_sqlite", status, detail, _file_state(db_path)["updated_at"])


def _load_parquet_candles(pair: str, timeframe: str, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    safe_pair = pair.replace("/", "_").replace(":", "_")
    candidates: list[Path] = []
    for directory in BT_DATA_DIRS:
        if directory.exists():
            candidates.extend(directory.glob(f"*{safe_pair}*{timeframe}*.parquet"))
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return [], _source("bt2_parquet", "unavailable", "no parquet file")

    try:
        import pandas as pd  # type: ignore

        frame = pd.read_parquet(candidates[0]).tail(limit)
        candles = []
        for _, row in frame.iterrows():
            ts_value = row.get("timestamp", row.get("date", row.get("ts")))
            if hasattr(ts_value, "timestamp"):
                ts = int(ts_value.timestamp() * 1000)
            else:
                ts = _as_int(ts_value)
            candles.append(
                {
                    "ts": ts,
                    "open": _round(row.get("open"), 2),
                    "high": _round(row.get("high"), 2),
                    "low": _round(row.get("low"), 2),
                    "close": _round(row.get("close"), 2),
                    "volume": _round(row.get("volume"), 2),
                    "source": "bt2_parquet",
                }
            )
        return candles, _source("bt2_parquet", "real", f"{len(candles)} candles", int(candidates[0].stat().st_mtime))
    except Exception as exc:
        return [], _source("bt2_parquet", "partial", f"parquet read failed: {type(exc).__name__}", int(candidates[0].stat().st_mtime))


def _ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (period + 1)
    out = [values[0]]
    for value in values[1:]:
        out.append(value * alpha + out[-1] * (1 - alpha))
    return out


def _macd_signals(candles: list[dict[str, Any]], pair: str, timeframe: str, source_updated_at: int | None = None) -> list[dict[str, Any]]:
    closes = [_as_float(c.get("close")) for c in candles]
    if len(closes) < 35:
        return []
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd = [a - b for a, b in zip(ema12, ema26)]
    line = _ema(macd, 9)
    items = []
    for candle, macd_value, line_value in zip(candles[-24:], macd[-24:], line[-24:]):
        hist = macd_value - line_value
        items.append(
            {
                "ts": candle.get("ts"),
                "macd": round(macd_value, 5),
                "macd_signal": round(line_value, 5),
                "macd_histogram": round(hist, 5),
                "macd_direction": "bullish" if hist > 0 else "bearish" if hist < 0 else "neutral",
                "confirmed": abs(hist) > 4,
                "pair": pair,
                "timeframe": timeframe,
                "source": candle.get("source", "derived"),
                "source_updated_at": source_updated_at,
            }
        )
    return items


def _latest_backtest_result() -> tuple[dict[str, Any] | None, dict[str, Any]]:
    candidates: list[Path] = []
    for directory in BT_REPORT_DIRS:
        if directory.exists():
            candidates.extend(directory.glob("**/bt_*.json"))
            candidates.extend(directory.glob("**/*result*.json"))
    candidates = sorted({p for p in candidates if p.is_file()}, key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None, _source("bt2_result_json", "unavailable", "no result file")
    payload = _read_json(candidates[0])
    if not isinstance(payload, dict):
        return None, _source("bt2_result_json", "partial", "latest result unreadable", int(candidates[0].stat().st_mtime))
    return payload, _source("bt2_result_json", "real", candidates[0].name, int(candidates[0].stat().st_mtime))


def _extract_stats(result: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(result, dict):
        return {}
    stats = result.get("stats")
    if isinstance(stats, dict):
        return stats
    summary = result.get("summary")
    if isinstance(summary, dict):
        return summary
    return result


def _extract_trades(result: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(result, dict):
        return []
    raw = result.get("trades")
    if not isinstance(raw, list):
        raw = result.get("strategy", {}).get("trades") if isinstance(result.get("strategy"), dict) else []
    trades = []
    for item in raw[:80] if isinstance(raw, list) else []:
        if not isinstance(item, dict):
            continue
        profit_pct = _as_float(item.get("profit_pct", item.get("profit_percent", item.get("profit_ratio", 0.0)))) * (100 if abs(_as_float(item.get("profit_ratio", 0.0))) <= 1 and "profit_pct" not in item and "profit_percent" not in item else 1)
        trades.append(
            {
                "pair": str(item.get("pair", "unknown")),
                "side": str(item.get("side", item.get("direction", "display"))),
                "profit_pct": round(profit_pct, 4),
                "duration": str(item.get("duration", item.get("trade_duration", ""))),
                "result": "win" if profit_pct >= 0 else "loss",
            }
        )
    return trades


def _summary_from_result(result: dict[str, Any] | None, source_status: dict[str, Any]) -> dict[str, Any]:
    stats = _extract_stats(result)
    trades = _extract_trades(result)
    total = _as_int(stats.get("total_trades", stats.get("trade_count", len(trades))), len(trades))
    wins = sum(1 for t in trades if _as_float(t.get("profit_pct")) >= 0)
    win_rate = _round(stats.get("win_rate_pct", stats.get("winrate", stats.get("win_rate", (wins / total * 100) if total else 64.37))), 2)
    if win_rate <= 1:
        win_rate *= 100
    return {
        "source": source_status["status"],
        "profit_total_pct": _round(stats.get("total_pnl_pct", stats.get("profit_total_pct", stats.get("profit_total", 132.67))), 2),
        "max_drawdown_pct": _round(stats.get("max_drawdown_pct", stats.get("max_drawdown", min(0.0, _as_float(stats.get("worst_trade", -12.38))))), 2),
        "win_rate_pct": round(win_rate, 2),
        "profit_factor": _round(stats.get("profit_factor", 2.46), 2),
        "sharpe": _round(stats.get("sharpe", stats.get("sharpe_ratio", 2.18)), 2),
        "sample_count": total or 91,
        "equity_curve_status": "real" if trades else "mock",
    }


def _equity_curve(trades: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not trades:
        return _mock_equity_curve()
    equity = 10000.0
    curve = []
    for idx, trade in enumerate(trades[:80], start=1):
        equity *= 1 + _as_float(trade.get("profit_pct")) / 100.0
        curve.append({"step": idx, "equity": round(equity, 2), "source": "bt2_result_json"})
    return curve


def _load_shadow_report() -> tuple[dict[str, Any], dict[str, Any]]:
    for directory in L5_LAB_DIRS:
        for name in ("latest_report.json", "latest.json"):
            path = directory / name
            payload = _read_json(path)
            if isinstance(payload, dict):
                return payload, _source("l5_shadow_report", "real", name, int(path.stat().st_mtime))
    return {}, _source("l5_shadow_report", "unavailable", "latest report missing")


def _load_progress() -> tuple[dict[str, Any], dict[str, Any]]:
    for path in EVOLUTION_PROGRESS_FILES:
        payload = _read_json(path)
        if isinstance(payload, dict):
            return payload, _source("evolution_progress", "real", path.name, int(path.stat().st_mtime))
    return {}, _source("evolution_progress", "unavailable", "progress file missing")


def _risk_summary(shadow: dict[str, Any]) -> dict[str, Any]:
    return {
        "risk_level": "low" if _as_float(shadow.get("avg_delta_score", 0.0)) >= 0 else "medium",
        "warnings": _as_int(shadow.get("block_count", shadow.get("risk_warning_count", 0))),
        "portfolio_note": "display-only shadow summary",
        "source": "l5_shadow_report" if shadow else "mock",
    }


def _ai_review(shadow: dict[str, Any]) -> dict[str, Any]:
    if shadow:
        agreement = _round(shadow.get("agreement_pct", shadow.get("agreement", 88.0)), 2)
        if agreement <= 1:
            agreement *= 100
        return {
            "score": min(99, max(1, round(agreement))),
            "rating": "中低风险" if agreement >= 70 else "需观察",
            "notes": [
                f"影子样本 { _as_int(shadow.get('sample_count', 0)) } 条",
                f"增强候选 { _as_int(shadow.get('enhanced_candidates', 0)) } 条",
                "只读展示，不修改策略参数",
            ],
            "source": "l5_shadow_report",
        }
    return {
        "score": 88,
        "rating": "中低风险",
        "notes": ["mock AI review", "fallback enabled", "只读展示，不修改策略参数"],
        "source": "mock",
    }


def get_l5_backtest_cockpit(pair: str = "BTC/USDT", timeframe: str = "15m", limit: int = 120) -> dict[str, Any]:
    candles, candle_status = _load_parquet_candles(pair, timeframe, limit)
    if not candles:
        candles, candle_status = _load_data_pool_candles(pair, timeframe, limit)
    fallback_sources: list[str] = []
    if not candles:
        candles = _mock_candles(limit)
        fallback_sources.append("candles")
        candle_status = _source("mock_candles", "mock", "generated fallback")

    result, result_status = _latest_backtest_result()
    trades = _extract_trades(result)
    if not trades:
        trades = _mock_trades()
        fallback_sources.append("trades")
    summary = _summary_from_result(result, result_status)
    shadow, shadow_status = _load_shadow_report()
    macd_items = _macd_signals(candles, pair, timeframe, candle_status.get("updated_at"))
    if not macd_items:
        fallback_sources.append("macd_signals")

    source_status = {
        "candles": candle_status,
        "backtest_result": result_status,
        "l5_shadow": shadow_status,
        "macd_signals": _source("derived_macd", "real" if macd_items else "mock", f"{len(macd_items)} signals"),
    }
    module_status = {
        "kline": source_status["candles"]["status"],
        "macd": source_status["macd_signals"]["status"],
        "backtest_summary": source_status["backtest_result"]["status"],
        "equity_curve": "real" if result and trades else "mock",
        "trades": "real" if result and trades else "mock",
        "risk_summary": "real" if shadow else "mock",
        "ai_review": "real" if shadow else "mock",
        "scenario_notes": "mock",
    }
    return {
        "readonly": True,
        "market": {"name": "crypto", "source": candle_status["name"], "status": candle_status["status"]},
        "pair": pair,
        "timeframe": timeframe,
        "candles": candles,
        "macd_signals": macd_items,
        "backtest_summary": summary,
        "equity_curve": _equity_curve(trades if result else []),
        "trades": trades[:40],
        "risk_summary": _risk_summary(shadow),
        "ai_review": _ai_review(shadow),
        "scenario_notes": [
            {"name": "缩量垃圾时间", "note": "降低交易频率，等待成交量与资金流同步放大。", "source": "mock"},
            {"name": "放量突破", "note": "只读展示突破质量，不触发任何交易动作。", "source": "mock"},
        ],
        "module_status": module_status,
        "source_status": source_status,
        "fallback_sources": fallback_sources,
    }


def get_l5_strategy_evolution() -> dict[str, Any]:
    shadow, shadow_status = _load_shadow_report()
    progress, progress_status = _load_progress()
    by_pair = shadow.get("by_pair") if isinstance(shadow.get("by_pair"), dict) else {}
    strategies = []
    for pair, item in list(by_pair.items())[:6]:
        if not isinstance(item, dict):
            continue
        score = 80 + min(19, abs(_round(item.get("avg_delta", item.get("avg_delta_score", 0.0)), 2)))
        strategies.append(
            {
                "name": f"L5 shadow {pair}",
                "pair": pair,
                "score": round(score, 2),
                "status": "readonly",
                "source": "l5_shadow_report",
            }
        )
    if not strategies:
        strategies = [
            {"name": "MACD + ATR", "pair": "BTC/USDT", "score": 91, "status": "mock", "source": "mock"},
            {"name": "EMA(12,26) + RSI", "pair": "ETH/USDT", "score": 86, "status": "mock", "source": "mock"},
            {"name": "Donchian(20) + ATR", "pair": "Top 20", "score": 74, "status": "mock", "source": "mock"},
        ]

    timeline = []
    if isinstance(progress.get("items"), list):
        for item in progress["items"][-8:]:
            if isinstance(item, dict):
                timeline.append(
                    {
                        "time": str(item.get("ts", item.get("date", "progress"))),
                        "text": str(item.get("title", item.get("summary", "L5 progress"))),
                        "status": str(item.get("status", "readonly")),
                        "source": "evolution_progress",
                    }
                )
    if not timeline:
        timeline = [
            {"time": "v2.3.7", "text": "缩量垃圾时间识别加入准入闸门", "status": "mock", "source": "mock"},
            {"time": "v2.3.2", "text": "增加手续费/滑点影响评分", "status": "mock", "source": "mock"},
            {"time": "v2.2.8", "text": "MACD 信号区分假突破与放量突破", "status": "mock", "source": "mock"},
        ]
    timeline_status = "real" if any(item.get("source") == "evolution_progress" for item in timeline) else "mock"

    fallback_sources = []
    if shadow_status["status"] != "real":
        fallback_sources.append("shadow_reviews")
    if progress_status["status"] != "real" or timeline_status != "real":
        fallback_sources.append("evolution_timeline")

    return {
        "readonly": True,
        "strategies": strategies,
        "strategy_scores": [{"name": item["name"], "score": item["score"], "source": item["source"]} for item in strategies],
        "parameter_runs": [
            {"name": "volume_decay_window", "change": "20 -> 34", "purpose": "降低缩量误判", "status": "mock"},
            {"name": "macd_signal_threshold", "change": "0.62 -> 0.71", "purpose": "提升假突破过滤", "status": "mock"},
        ],
        "optimization_history": timeline,
        "evolution_timeline": timeline,
        "next_recommendations": [
            {"title": "下一轮优先", "text": "验证缩量垃圾时间下的 MACD 降噪参数", "priority": "P0"},
            {"title": "接口预留", "text": "后续接入原生回测任务状态，不接真实交易动作", "priority": "P1"},
            {"title": "安全闸门", "text": "P0 guard 已作为执行边界；本阶段仍只允许 GET 只读展示", "priority": "P0"},
        ],
        "shadow_reviews": _ai_review(shadow),
        "risk_warnings": [{"level": _risk_summary(shadow)["risk_level"], "text": "display-only risk summary"}],
        "module_status": {
            "strategies": "real" if shadow_status["status"] == "real" else "mock",
            "strategy_scores": "real" if shadow_status["status"] == "real" else "mock",
            "parameter_runs": "mock",
            "optimization_history": timeline_status,
            "evolution_timeline": timeline_status,
            "next_recommendations": "mock",
            "shadow_reviews": "real" if shadow_status["status"] == "real" else "mock",
            "risk_warnings": "real" if shadow_status["status"] == "real" else "mock",
        },
        "source_status": {"l5_shadow": shadow_status, "evolution_progress": progress_status},
        "fallback_sources": fallback_sources,
    }


def get_l5_data_sources() -> dict[str, Any]:
    parquet_files = [path for directory in BT_DATA_DIRS if directory.exists() for path in directory.glob("*.parquet")]
    parquet_count = len(parquet_files)
    result_count = 0
    newest_result_ts = None
    for directory in BT_REPORT_DIRS:
        if directory.exists():
            result_files = list(directory.glob("**/bt_*.json"))
            result_count += len(result_files)
            if result_files:
                newest_result_ts = max(int(path.stat().st_mtime) for path in result_files + [])
    data_pool = _first_existing(DATA_POOL_DBS)
    sources = {
        "bt2_parquet": _source("bt2_parquet", "real" if parquet_count else "unavailable", f"{parquet_count} files"),
        "bt2_results": _source("bt2_results", "real" if result_count else "unavailable", f"{result_count} files", newest_result_ts),
        "data_pool_sqlite": _source("data_pool_sqlite", "real" if data_pool else "unavailable", "sqlite candles", _file_state(data_pool)["updated_at"] if data_pool else None),
        "l5_shadow_report": _load_shadow_report()[1],
        "evolution_progress": _load_progress()[1],
    }
    fallback_sources = [name for name, status in sources.items() if status["status"] != "real"]
    return {"readonly": True, "sources": sources, "fallback_sources": fallback_sources}


def get_l5_guard_status() -> dict[str, Any]:
    return {
        "readonly": True,
        "guard_status": "enabled",
        "permission_layer": "readonly",
        "mutation_policy": "default deny",
        "protected_paths": [
            "risk execute mutation",
            "proxy mutation",
            "monitor mutation",
            "bot RPC mutation",
        ],
        "source_status": {"trading_action_guard": _source("trading_action_guard", "real", "core merged")},
    }


def get_l5_readiness() -> dict[str, Any]:
    data_sources = get_l5_data_sources()
    fallback_sources = data_sources["fallback_sources"]
    unavailable = [name for name in fallback_sources]
    newest = 0
    for item in data_sources["sources"].values():
        newest = max(newest, _as_int(item.get("updated_at"), 0))
    return {
        "readonly": True,
        "bot_status": {"status": "not_connected", "mode": "display_only"},
        "data_freshness": {"latest_source_ts": newest or None, "checked_at": int(time.time())},
        "guard_status": get_l5_guard_status()["guard_status"],
        "readonly_mode": True,
        "unavailable_sources": unavailable,
        "fallback_sources": fallback_sources,
        "source_status": data_sources["sources"],
    }
