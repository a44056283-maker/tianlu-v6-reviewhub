# L5晋级链路补丁 #05 — L5 Candidate Registry（候选参数注册表）

> 生成时间：2026-05-04 15:00
> 状态：等待翰林院GPT审核 → 爸确认 → 才写入runtime

---

## 一、设计原则

L5候选参数**绝对禁止**直接写入实盘runtime。
所有L5生成的候选参数必须经过：
1. **候选注册** → 写入本地Registry（SQLite）
2. **自动打分** → Registry内部评分
3. **人工确认** → 爸在控制台点击"批准"
4. **写入runtime** → 仅人工批准后才写入实盘参数

---

## 二、数据库表结构

```sql
-- L5候选参数注册表（沙盒隔离，永远不直接写runtime）
CREATE TABLE IF NOT EXISTS l5_candidates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    TEXT    UNIQUE NOT NULL,   -- UUID
    ts_created      INTEGER NOT NULL,           -- Unix timestamp
    source_bot      TEXT    NOT NULL,           -- 来源bot端口
    pair            TEXT    NOT NULL,           -- 交易对
    direction       TEXT    NOT NULL,           -- LONG / SHORT
    params_json     TEXT    NOT NULL,           -- 候选参数JSON

    -- 评分维度
    shadow_score    REAL    NOT NULL DEFAULT 0,  -- 影子评分
    win_rate_score  REAL    NOT NULL DEFAULT 0,  -- 历史胜率评分
    drawdown_score  REAL    NOT NULL DEFAULT 0,  -- 最大回撤评分
    noise_score     REAL    NOT NULL DEFAULT 0,  -- 噪音评分
    composite_score REAL    NOT NULL DEFAULT 0,  -- 综合评分(加权)

    -- 流程状态
    status          TEXT    NOT NULL DEFAULT 'pending',  -- pending/approved/rejected/expired
    human_approver  TEXT,                               -- 批准人
    ts_approved     INTEGER,                            -- 批准时间戳
    approval_note   TEXT,                               -- 爸的备注
    ts_expires      INTEGER NOT NULL,                   -- 过期时间(14天后)
    runtime_written INTEGER NOT NULL DEFAULT 0,         -- 是否已写runtime
    ts_runtime      INTEGER,                            -- 写runtime时间

    -- 追踪字段
    reject_reason   TEXT,                               -- 拒绝原因
    shadow_run_id   TEXT,                              -- 关联影子实验ID
    applied_to_port  TEXT,                              -- 最终应用的bot端口
    notes           TEXT                                -- 翰林院备注
);

CREATE INDEX IF NOT EXISTS idx_cand_status ON l5_candidates(status);
CREATE INDEX IF NOT EXISTS idx_cand_pair ON l5_candidates(pair);
CREATE INDEX IF NOT EXISTS idx_cand_created ON l5_candidates(ts_created DESC);
CREATE INDEX IF NOT EXISTS idx_cand_expires ON l5_candidates(ts_expires);
```

```sql
-- 候选参数变更记录（审计用）
CREATE TABLE IF NOT EXISTS l5_candidate_audit (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    TEXT    NOT NULL,
    action          TEXT    NOT NULL,  -- registered/scored/approved/rejected/expired/runtime_written
    actor           TEXT    NOT NULL,  -- system / human / bot_name
    ts              INTEGER NOT NULL,
    detail          TEXT
);
```

---

## 三、L5CandidateRegistry 完整代码

```python
#!/usr/bin/env python3
"""
L5 Candidate Registry — L5候选参数注册表

核心原则：L5生成的候选参数绝对不直接写入实盘runtime。
所有候选必须：注册 → 打分 → 人工确认 → 才写入runtime。

文件位置: ~/freqtrade_console/l5_evolution_lab/l5_candidate_registry.py
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

BASE = Path("/Users/luxiangnan/freqtrade_console/l5_evolution_lab")
DB_PATH = BASE / "l5_candidate_registry.sqlite"


class CandidateStatus(str, Enum):
    PENDING = "pending"      # 待审核
    APPROVED = "approved"   # 人工批准
    REJECTED = "rejected"   # 人工拒绝
    EXPIRED = "expired"     # 超时过期
    WRITTEN = "runtime_written"  # 已写入runtime


@dataclass
class L5Candidate:
    candidate_id: str
    ts_created: int
    source_bot: str
    pair: str
    direction: str
    params_json: str

    shadow_score: float = 0.0
    win_rate_score: float = 0.0
    drawdown_score: float = 0.0
    noise_score: float = 0.0
    composite_score: float = 0.0

    status: str = CandidateStatus.PENDING.value
    human_approver: Optional[str] = None
    ts_approved: Optional[int] = None
    approval_note: Optional[str] = None
    ts_expires: int = field(default_factory=lambda: int(time.time()) + 14 * 86400)
    runtime_written: int = 0
    ts_runtime: Optional[int] = None

    reject_reason: Optional[str] = None
    shadow_run_id: Optional[str] = None
    applied_to_port: Optional[str] = None
    notes: Optional[str] = None


class L5CandidateRegistry:
    """
    L5候选参数注册表

    职责：
    1. 接收L5影子实验室生成的候选参数
    2. 自动打分（shadow_score / win_rate / drawdown / noise）
    3. 注册到本地SQLite（不写runtime）
    4. 提供人工确认接口
    5. 人工批准后才写入runtime

    绝对禁止：
    - L5候选参数直接写入runtime
    - 任何自动写入（必须人工确认）
    """

    # 综合评分权重（可调）
    WEIGHTS = {
        "shadow_score": 0.35,    # 影子实验评分
        "win_rate_score": 0.25,  # 历史胜率
        "drawdown_score": 0.20,  # 最大回撤
        "noise_score": 0.20,     # 噪音质量
    }

    # 及格门槛
    PASS_THRESHOLDS = {
        "composite_score": 60.0,     # 综合评分 >= 60
        "shadow_score": 55.0,        # 影子评分 >= 55
        "win_rate_score": 50.0,      # 胜率评分 >= 50
        "drawdown_score": 40.0,      # 回撤评分 >= 40
        "noise_score": 0.0,          # 噪音评分无下限
    }

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # -------------------------------------------------------------------------
    # 数据库初始化
    # -------------------------------------------------------------------------

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS l5_candidates (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id    TEXT    UNIQUE NOT NULL,
                    ts_created      INTEGER NOT NULL,
                    source_bot      TEXT    NOT NULL,
                    pair            TEXT    NOT NULL,
                    direction       TEXT    NOT NULL,
                    params_json     TEXT    NOT NULL,

                    shadow_score    REAL    NOT NULL DEFAULT 0,
                    win_rate_score  REAL    NOT NULL DEFAULT 0,
                    drawdown_score  REAL    NOT NULL DEFAULT 0,
                    noise_score     REAL    NOT NULL DEFAULT 0,
                    composite_score REAL    NOT NULL DEFAULT 0,

                    status          TEXT    NOT NULL DEFAULT 'pending',
                    human_approver  TEXT,
                    ts_approved     INTEGER,
                    approval_note   TEXT,
                    ts_expires      INTEGER NOT NULL,
                    runtime_written INTEGER NOT NULL DEFAULT 0,
                    ts_runtime      INTEGER,

                    reject_reason   TEXT,
                    shadow_run_id   TEXT,
                    applied_to_port TEXT,
                    notes           TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_status ON l5_candidates(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_pair ON l5_candidates(pair)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_created ON l5_candidates(ts_created DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_expires ON l5_candidates(ts_expires)")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS l5_candidate_audit (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id TEXT NOT NULL,
                    action      TEXT  NOT NULL,
                    actor       TEXT  NOT NULL,
                    ts          INTEGER NOT NULL,
                    detail      TEXT
                )
            """)

    # -------------------------------------------------------------------------
    # 核心方法
    # -------------------------------------------------------------------------

    def register(
        self,
        candidate_params: dict[str, Any],
        shadow_score: float,
        source_bot: str,
        pair: str,
        direction: str,
        shadow_run_id: Optional[str] = None,
    ) -> str:
        """
        注册一个新L5候选参数。

        Args:
            candidate_params: L5生成的候选参数（如量比阈值、止损系数等）
            shadow_score: 影子实验室给出的评分（0-100）
            source_bot: 来源bot端口
            pair: 交易对
            direction: LONG / SHORT
            shadow_run_id: 关联的影子实验ID

        Returns:
            candidate_id: 新候选的唯一ID

        注意：此方法只写入Registry，不写入runtime。
        """
        candidate_id = str(uuid.uuid4())
        ts = int(time.time())

        # 自动打分
        win_rate_score = self._calc_win_rate_score(candidate_params)
        drawdown_score = self._calc_drawdown_score(candidate_params)
        noise_score = self._calc_noise_score(candidate_params, shadow_score)
        composite_score = self._calc_composite(
            shadow_score, win_rate_score, drawdown_score, noise_score
        )

        params_json = json.dumps(candidate_params, ensure_ascii=False, indent=2)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO l5_candidates (
                    candidate_id, ts_created, source_bot, pair, direction, params_json,
                    shadow_score, win_rate_score, drawdown_score, noise_score, composite_score,
                    status, ts_expires, shadow_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_id, ts, source_bot, pair, direction, params_json,
                shadow_score, win_rate_score, drawdown_score, noise_score, composite_score,
                CandidateStatus.PENDING.value, ts + 14 * 86400, shadow_run_id
            ))
            conn.commit()

        self._audit(candidate_id, "registered", "system", {
            "source_bot": source_bot,
            "pair": pair,
            "shadow_score": shadow_score,
            "composite_score": composite_score,
        })

        return candidate_id

    def score_candidate(self, candidate_id: str) -> dict[str, Any]:
        """
        对候选参数重新评分（可定期重新计算）。
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM l5_candidates WHERE candidate_id = ?", (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}

        cols = [d[0] for d in conn.execute("PRAGMA table_info(l5_candidates)")]
        cand = dict(zip(cols, row)) if 'conn' in dir() else {}
        # 重新计算
        params = json.loads(cand["params_json"])
        new_shadow = cand["shadow_score"]
        new_wr = self._calc_win_rate_score(params)
        new_dd = self._calc_drawdown_score(params)
        new_noise = self._calc_noise_score(params, new_shadow)
        new_composite = self._calc_composite(new_shadow, new_wr, new_dd, new_noise)

        with sqlite3.connect(self.db_path) as conn2:
            conn2.execute("""
                UPDATE l5_candidates SET
                    win_rate_score = ?, drawdown_score = ?, noise_score = ?, composite_score = ?
                WHERE candidate_id = ?
            """, (new_wr, new_dd, new_noise, new_composite, candidate_id))
            conn2.commit()

        return {
            "ok": True,
            "candidate_id": candidate_id,
            "scores": {
                "shadow_score": new_shadow,
                "win_rate_score": new_wr,
                "drawdown_score": new_dd,
                "noise_score": new_noise,
                "composite_score": new_composite,
            },
            "passes": self._check_thresholds(new_shadow, new_wr, new_dd, new_noise, new_composite),
        }

    def approve(
        self,
        candidate_id: str,
        approver: str = "human_father",
        note: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        人工批准候选参数。

        Args:
            candidate_id: 候选ID
            approver: 批准人（固定填 "human_father"）
            note: 爸的批注

        Returns:
            批准结果字典

        注意：批准后仍然需要调用 apply_to_live() 才真正写runtime。
        """
        ts = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status, ts_expires FROM l5_candidates WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}

            status, ts_expires = row
            if status != CandidateStatus.PENDING.value:
                return {
                    "ok": False,
                    "error": f"candidate is {status}, can only approve pending",
                }
            if ts > ts_expires:
                conn.execute(
                    "UPDATE l5_candidates SET status = ? WHERE candidate_id = ?",
                    (CandidateStatus.EXPIRED.value, candidate_id)
                )
                conn.commit()
                return {"ok": False, "error": "candidate expired"}

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE l5_candidates SET
                    status = ?, human_approver = ?, ts_approved = ?, approval_note = ?
                WHERE candidate_id = ?
            """, (CandidateStatus.APPROVED.value, approver, ts, note, candidate_id))
            conn.commit()

        self._audit(candidate_id, "approved", approver, {"note": note})
        return {
            "ok": True,
            "candidate_id": candidate_id,
            "status": CandidateStatus.APPROVED.value,
            "message": "人工批准完成。请调用 apply_to_live() 将候选写入runtime。",
        }

    def reject(
        self,
        candidate_id: str,
        rejector: str = "human_father",
        reason: str = "",
    ) -> dict[str, Any]:
        """
        人工拒绝候选参数。
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status FROM l5_candidates WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}
            if row[0] != CandidateStatus.PENDING.value:
                return {"ok": False, "error": f"candidate is {row[0]}, can only reject pending"}

            conn.execute("""
                UPDATE l5_candidates SET status = ?, reject_reason = ? WHERE candidate_id = ?
            """, (CandidateStatus.REJECTED.value, reason, candidate_id))
            conn.commit()

        self._audit(candidate_id, "rejected", rejector, {"reason": reason})
        return {"ok": True, "candidate_id": candidate_id, "status": CandidateStatus.REJECTED.value}

    def apply_to_live(
        self,
        candidate_id: str,
        target_port: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        将人工批准的候选参数写入实盘runtime。

        这是唯一允许写runtime的方法。
        必须满足：status == 'approved' 且 runtime_written == 0

        Args:
            candidate_id: 候选ID
            target_port: 目标bot端口
            dry_run: True=只检查不写

        Returns:
            写入结果

        Raises:
            PermissionError: 如果status不是approved
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status, runtime_written, params_json FROM l5_candidates WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}
            status, written, params_json = row

        # 安全检查
        if status != CandidateStatus.APPROVED.value:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live denied. candidate_id={candidate_id} "
                f"status={status} (must be approved). "
                f"L5 cannot write to live runtime without human approval."
            )
        if written:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live denied. candidate_id={candidate_id} "
                f"runtime_written={written} (already written). Duplicate write attempt blocked."
            )

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "candidate_id": candidate_id,
                "target_port": target_port,
                "params": json.loads(params_json),
                "message": "dry_run: would write to runtime",
            }

        # 实际写入runtime（通过console_server API）
        from l5_apply_runtime import apply_params_via_api
        ts = int(time.time())
        result = apply_params_via_api(candidate_id, target_port, json.loads(params_json))

        if result.get("ok"):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE l5_candidates SET
                        runtime_written = 1, ts_runtime = ?, applied_to_port = ?
                    WHERE candidate_id = ?
                """, (ts, target_port, candidate_id))
                conn.commit()
            self._audit(candidate_id, "runtime_written", "system", {
                "target_port": target_port,
                "result": result,
            })

        return result

    def list_pending(self, pair: Optional[str] = None, limit: int = 50) -> list[dict]:
        """列出待审核候选（按综合评分倒序）。"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if pair:
                rows = conn.execute("""
                    SELECT * FROM l5_candidates
                    WHERE status = ? AND pair = ?
                    ORDER BY composite_score DESC
                    LIMIT ?
                """, (CandidateStatus.PENDING.value, pair, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM l5_candidates
                    WHERE status = ?
                    ORDER BY composite_score DESC
                    LIMIT ?
                """, (CandidateStatus.PENDING.value, limit)).fetchall()
        return [dict(r) for r in rows]

    def list_approved(self, limit: int = 20) -> list[dict]:
        """列出已批准但未写入runtime的候选。"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM l5_candidates
                WHERE status = ? AND runtime_written = 0
                ORDER BY ts_approved DESC
                LIMIT ?
            """, (CandidateStatus.APPROVED.value, limit)).fetchall()
        return [dict(r) for r in rows]

    def get_status_summary(self) -> dict[str, Any]:
        """获取Registry整体状态摘要。"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM l5_candidates").fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE status = ?",
                (CandidateStatus.PENDING.value,)
            ).fetchone()[0]
            approved = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE status = ?",
                (CandidateStatus.APPROVED.value,)
            ).fetchone()[0]
            written = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE runtime_written = 1"
            ).fetchone()[0]
            avg_score = conn.execute(
                "SELECT AVG(composite_score) FROM l5_candidates"
            ).fetchone()[0] or 0.0
        return {
            "total_candidates": total,
            "pending": pending,
            "approved_not_written": approved - written,
            "runtime_written": written,
            "avg_composite_score": round(avg_score, 2),
        }

    # -------------------------------------------------------------------------
    # 内部评分方法（可扩展/可调参）
    # -------------------------------------------------------------------------

    def _calc_win_rate_score(self, params: dict[str, Any]) -> float:
        """
        基于候选参数计算历史胜率评分（0-100）。
        这里使用参数特征估算，实际应读取历史回测结果。
        """
        score = 50.0
        # 量比越高胜率越高（估算）
        ratio = params.get("l1_volume_ratio", 5.0)
        if ratio >= 8.0:
            score += 15
        elif ratio >= 6.0:
            score += 8
        elif ratio >= 5.0:
            score += 3
        # 止损严格有利于胜率
        stop_loss = params.get("stop_loss_pct", 0.0)
        if stop_loss <= 2.0:
            score += 5
        elif stop_loss >= 4.0:
            score -= 5
        return min(100.0, max(0.0, score))

    def _calc_drawdown_score(self, params: dict[str, Any]) -> float:
        """
        基于候选参数计算最大回撤评分（0-100，越高=回撤越小）。
        """
        score = 50.0
        # 更严格的止损减少回撤
        stop_loss = params.get("stop_loss_pct", 0.0)
        if stop_loss <= 1.5:
            score += 20
        elif stop_loss <= 2.5:
            score += 10
        elif stop_loss >= 5.0:
            score -= 15
        # ATR止损自适应有利于控制回撤
        if params.get("use_atr_stop", False):
            score += 10
        return min(100.0, max(0.0, score))

    def _calc_noise_score(self, params: dict[str, Any], shadow_score: float) -> float:
        """
        噪音评分：基于shadow_score推算信号噪音水平。
        shadow_score高 → 噪音低 → score高
        """
        # shadow_score 已经是 0-100，高分=优质
        return min(100.0, max(0.0, shadow_score))

    def _calc_composite(
        self,
        shadow: float,
        win_rate: float,
        drawdown: float,
        noise: float,
    ) -> float:
        """加权综合评分。"""
        return round(
            shadow * self.WEIGHTS["shadow_score"]
            + win_rate * self.WEIGHTS["win_rate_score"]
            + drawdown * self.WEIGHTS["drawdown_score"]
            + noise * self.WEIGHTS["noise_score"],
            2
        )

    def _check_thresholds(
        self,
        shadow: float,
        win_rate: float,
        drawdown: float,
        noise: float,
        composite: float,
    ) -> dict[str, bool]:
        """检查各维度是否通过门槛。"""
        return {
            "composite_score": composite >= self.PASS_THRESHOLDS["composite_score"],
            "shadow_score": shadow >= self.PASS_THRESHOLDS["shadow_score"],
            "win_rate_score": win_rate >= self.PASS_THRESHOLDS["win_rate_score"],
            "drawdown_score": drawdown >= self.PASS_THRESHOLDS["drawdown_score"],
            "noise_score": True,  # 噪音无硬性门槛
            "all_pass": all([
                composite >= self.PASS_THRESHOLDS["composite_score"],
                shadow >= self.PASS_THRESHOLDS["shadow_score"],
                win_rate >= self.PASS_THRESHOLDS["win_rate_score"],
                drawdown >= self.PASS_THRESHOLDS["drawdown_score"],
            ]),
        }

    def _audit(self, candidate_id: str, action: str, actor: str, detail: Any) -> None:
        """写审计日志。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO l5_candidate_audit (candidate_id, action, actor, ts, detail)
                    VALUES (?, ?, ?, ?, ?)
                """, (candidate_id, action, actor, int(time.time()), json.dumps(detail, ensure_ascii=False)))
                conn.commit()
        except Exception:
            pass  # 审计失败不阻塞主流程


# -------------------------------------------------------------------------
# CLI工具
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    reg = L5CandidateRegistry()

    parser = argparse.ArgumentParser(description="L5 Candidate Registry CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_summary = sub.add_parser("summary", help="查看Registry整体状态")
    p_list = sub.add_parser("list", help="列出待审核候选")
    p_list.add_argument("--pair", "-p", default=None)
    p_list.add_argument("--limit", "-n", type=int, default=50)
    p_approve = sub.add_parser("approve", help="批准候选")
    p_approve.add_argument("candidate_id")
    p_approve.add_argument("--note", "-m", default="")
    p_reject = sub.add_parser("reject", help="拒绝候选")
    p_reject.add_argument("candidate_id")
    p_reject.add_argument("--reason", "-r", default="")
    p_apply = sub.add_parser("apply", help="将批准后的候选写入runtime")
    p_apply.add_argument("candidate_id")
    p_apply.add_argument("--port", required=True, help="目标bot端口")
    p_apply.add_argument("--dry-run", action="store_true")
    p_score = sub.add_parser("score", help="重新评分候选")
    p_score.add_argument("candidate_id")

    args = parser.parse_args()

    if args.cmd == "summary":
        print(json.dumps(reg.get_status_summary(), ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        items = reg.list_pending(pair=args.pair, limit=args.limit)
        print(json.dumps(items, ensure_ascii=False, indent=2))
    elif args.cmd == "approve":
        print(json.dumps(reg.approve(args.candidate_id, note=args.note), ensure_ascii=False, indent=2))
    elif args.cmd == "reject":
        print(json.dumps(reg.reject(args.candidate_id, reason=args.reason), ensure_ascii=False, indent=2))
    elif args.cmd == "apply":
        try:
            result = reg.apply_to_live(args.candidate_id, args.port, dry_run=args.dry_run)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except PermissionError as e:
            print(f"ERROR: {e}")
    elif args.cmd == "score":
        print(json.dumps(reg.score_candidate(args.candidate_id), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
```

---

## 四、候选 → Registry 自动注册集成

在 `m4_m5_shadow_lab.py` 的快照保存逻辑中，当 `enhanced_action == "candidate"` 时，自动调用Registry注册：

```python
# 在 build_report() 或快照保存时调用
from l5_candidate_registry import L5CandidateRegistry

def register_enhanced_candidates(snaps: list[dict]) -> None:
    """自动将影子实验中的增强候选注册到L5CandidateRegistry。"""
    reg = L5CandidateRegistry()
    registered = 0
    for snap in snaps:
        if snap.get("enhanced_action") == "candidate":
            try:
                # 从payload中提取候选参数
                payload = json.loads(snap.get("payload") or "{}")
                params = {
                    "l1_volume_ratio": payload.get("m1_ratio", 5.0),
                    "l2_netflow_threshold": payload.get("m1_netflow", 0.0),
                    "stop_loss_pct": payload.get("stop_loss", 2.5),
                    "entry_score_threshold": payload.get("entry_threshold", 65.0),
                    "flow_gate_threshold": 0.30,
                }
                candidate_id = reg.register(
                    candidate_params=params,
                    shadow_score=snap.get("enhanced_score", 0),
                    source_bot="l5_shadow_lab",
                    pair=snap.get("pair", ""),
                    direction=snap.get("enhanced_direction", "NEUTRAL"),
                    shadow_run_id=f"run_{snap.get('ts')}",
                )
                registered += 1
            except Exception:
                pass  # 注册失败不阻塞主流程
    print(f"[L5 Registry] Auto-registered {registered} candidates from shadow run")
```

---

## 五、人工确认流程

```
L5影子实验
    ↓ 增强候选触发
L5CandidateRegistry.register()
    ↓ 写入pending状态
翰林院审查 pending 列表
    ↓ 爸点击"批准"
L5CandidateRegistry.approve()
    ↓ 状态改为 approved
翰林院点击"应用到实盘"
L5CandidateRegistry.apply_to_live()
    ↓ (PermissionError检查)
    ↓ (必须status==approved)
console_server API 写入runtime
    ↓
runtime_written = 1
```

---

## 六、Registry 状态机

```
pending → approved  (人工批准)
pending → rejected (人工拒绝)
pending → expired  (14天超时)
approved → runtime_written (apply_to_live)
```

**绝对不允许的转换：**
- `pending → runtime_written` (禁止自动跳过人工)
- `rejected → runtime_written` (禁止绕过拒绝)
- `expired → runtime_written` (禁止使用过期候选)
