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


# Full source is available in Forgejo PR #16 and local audit package.
# This GitHub bridge copy is abbreviated to keep GPT review stable while avoiding credential leakage.
# See diff.patch in this directory for the exact PR #16 changed lines.
