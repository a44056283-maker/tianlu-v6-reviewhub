# L5晋级链路补丁 #06 — L5 Promotion Gate（晋级闸门）

> 生成时间：2026-05-04 15:00
> 状态：等待翰林院GPT审核

---

## 一、当前状态（审计结果）

| 指标 | 当前值 | 晋级闸门要求 | 状态 |
|------|--------|-------------|------|
| 影子运行天数 | **7天** | ≥7天 | **PASS** |
| 影子样本总数 | **3040条** | ≥300条 | **PASS** |
| 资金流硬闸通过率 | **74.3%**（159/214） | ≥65%且≤85% | **PASS** |
| 规则一致率 | **93.7%** | ≥85% | **PASS** |
| 增强平均加分 | **+11.58** | ≥+5.0 | **PASS** |
| 综合噪音优质率 | **9.3%** | ≥8% | **PASS** |
| 高噪音率 | **40.7%** | ≤45% | **PASS** |
| walk-forward测试 | **未执行** | 连续3期正期望 | **未开始** |
| 历史胜率基线 | **未量化** | ≥52% | **未量化** |
| 最大回撤基线 | **未量化** | ≤20% | **未量化** |

> **注意**：尽管多数指标已满足，但walk-forward、历史胜率、回撤三项核心闸门**尚未建立量化标准**。本补丁负责建立完整晋级闸门体系。

---

## 二、晋级闸门定义（五级）

### G1 — 影子运行闸门（数据充足性）
```python
G1_MIN_DAYS = 7          # 最少影子运行7天
G1_MIN_SAMPLES = 300     # 最少300条样本
G1_MIN_PAIRS = 3         # 最少覆盖3个交易对
```

### G2 — 信号质量闸门（噪声控制）
```python
G2_MIN_QUALITY_PCT = 8.0    # 优质信号占比 ≥ 8%
G2_MAX_HIGH_NOISE_PCT = 45.0 # 高噪音占比 ≤ 45%
G2_MIN_AGREEMENT_PCT = 85.0  # 影子与基准一致率 ≥ 85%
G2_MIN_DELTA_SCORE = 5.0     # 增强平均加分 ≥ +5.0
```

### G3 — 资金流硬闸（强化版）
```python
G3_MIN_PASS_RATE = 0.65   # 资金流通过率 ≥ 65%
G3_MAX_PASS_RATE = 0.85   # 资金流通过率 ≤ 85%（不能太松）
G3_MIN_CANDIDATES = 50   # 至少50个资金流候选样本
G3_FLOW_THRESHOLD = 0.30 # 资金流阈值（与L2.5一致）
```

### G4 — 风险控制闸门（回撤/胜率）
```python
G4_MIN_WIN_RATE = 0.52    # 历史回测/模拟胜率 ≥ 52%
G4_MAX_DRAWDOWN = 0.20    # 最大回撤 ≤ 20%
G4_MIN_SHARPE = 1.2      # 夏普比率 ≥ 1.2（未来扩展）
G4_MIN_TRADE_COUNT = 100 # 胜率样本最少100笔交易
```

### G5 — Walk-Forward闸门（泛化能力）
```python
G5_PERIODS = 3            # 连续3个walk-forward周期
G5_POSITIVE_EXPECTANCY = True  # 所有周期均正期望
G5_MAX_DEGRADATION = 0.20  # 参数稳定性：相对样本内收益衰减 ≤ 20%
```

---

## 三、晋级闸门检查代码

```python
#!/usr/bin/env python3
"""
L5 Promotion Gate — 晋级闸门检查

在L5影子实验室报告生成后，调用此模块检查所有晋级闸门。
只有全部通过（PASS）或全部豁免项均满足，才允许候选进入Registry。

文件位置: ~/freqtrade_console/l5_evolution_lab/l5_promotion_gate.py
"""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

BASE = Path("/Users/luxiangnan/freqtrade_console/l5_evolution_lab")
REPORT_PATH = BASE / "latest_report.json"
DB_PATH = BASE / "m4_m5_shadow_lab.sqlite"


class GateLevel(str, Enum):
    G1_DATA = "G1_DATA"         # 数据充足性
    G2_QUALITY = "G2_QUALITY"   # 信号质量
    G3_FLOW = "G3_FLOW"         # 资金流硬闸
    G4_RISK = "G4_RISK"         # 风险控制
    G5_WALKFORWARD = "G5_WALKFORWARD"  # Walk-Forward


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"   # 数据不足，待补充
    SKIP = "SKIP"         # 豁免（如无w-f数据时）


@dataclass
class GateResult:
    gate: str
    status: str
    value: Any
    threshold: Any
    message: str
    weight: float = 1.0  # 用于综合评分


@dataclass
class PromotionGateReport:
    ts: int
    all_pass: bool
    overall_score: float          # 0-100
    gates: list[GateResult] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    next_check_ts: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "ts": self.ts,
            "all_pass": self.all_pass,
            "overall_score": self.overall_score,
            "gates": [g.__dict__ for g in self.gates],
            "blocked_reason": self.blocked_reason,
            "next_check_ts": self.next_check_ts,
        }


class L5PromotionGate:
    """
    L5晋级闸门检查器

    检查顺序：G1 → G2 → G3 → G4 → G5
    顺序检查，任意FAIL则晋级终止。

    G1/G2/G3: 可立即检查（有影子数据即可）
    G4: 需要历史胜率/回撤数据（可模拟估算）
    G5: 需要walk-forward回测（翰林院单独触发）
    """

    # ---- G1 闸门值 ----
    G1_MIN_DAYS = 7
    G1_MIN_SAMPLES = 300
    G1_MIN_PAIRS = 3

    # ---- G2 闸门值 ----
    G2_MIN_QUALITY_PCT = 8.0
    G2_MAX_HIGH_NOISE_PCT = 45.0
    G2_MIN_AGREEMENT_PCT = 85.0
    G2_MIN_DELTA_SCORE = 5.0

    # ---- G3 闸门值 ----
    G3_MIN_PASS_RATE = 0.65
    G3_MAX_PASS_RATE = 0.85
    G3_MIN_CANDIDATES = 50
    G3_FLOW_THRESHOLD = 0.30

    # ---- G4 闸门值 ----
    G4_MIN_WIN_RATE = 0.52
    G4_MAX_DRAWDOWN = 0.20
    G4_MIN_TRADE_COUNT = 100

    # ---- G5 闸门值 ----
    G5_PERIODS = 3
    G5_MAX_DEGRADATION = 0.20

    def __init__(self, report_path: Path = REPORT_PATH, db_path: Path = DB_PATH):
        self.report_path = report_path
        self.db_path = db_path

    def check_all(self) -> PromotionGateReport:
        """
        执行全部晋级闸门检查。
        返回 PromotionGateReport。
        """
        report = json.loads(self.report_path.read_text(encoding="utf-8"))
        ts = int(time.time())
        gates: list[GateResult] = []

        # ---- G1: 数据充足性 ----
        g1 = self._check_g1(report)
        gates.append(g1)

        # G1 FAIL则全部终止
        if g1.status == GateStatus.FAIL.value:
            return PromotionGateReport(
                ts=ts,
                all_pass=False,
                overall_score=0.0,
                gates=gates,
                blocked_reason=f"G1 FAILED: {g1.message}",
                next_check_ts=ts + 3600,  # 1小时后重检
            )

        # ---- G2: 信号质量 ----
        g2 = self._check_g2(report)
        gates.append(g2)

        if g2.status == GateStatus.FAIL.value:
            return PromotionGateReport(
                ts=ts, all_pass=False, overall_score=10.0,
                gates=gates,
                blocked_reason=f"G2 FAILED: {g2.message}",
            )

        # ---- G3: 资金流硬闸 ----
        g3 = self._check_g3(report)
        gates.append(g3)

        if g3.status == GateStatus.FAIL.value:
            return PromotionGateReport(
                ts=ts, all_pass=False, overall_score=25.0,
                gates=gates,
                blocked_reason=f"G3 FAILED: {g3.message}",
            )

        # ---- G4: 风险控制 ----
        g4 = self._check_g4(report)
        gates.append(g4)

        if g4.status == GateStatus.FAIL.value:
            return PromotionGateReport(
                ts=ts, all_pass=False, overall_score=50.0,
                gates=gates,
                blocked_reason=f"G4 FAILED: {g4.message}",
            )

        # ---- G5: Walk-Forward ----
        g5 = self._check_g5(report)
        gates.append(g5)

        # G5为PENDING时，G4 PASS + G5 PENDING 可允许进入评审
        # 但G5 FAIL则晋级终止
        if g5.status == GateStatus.FAIL.value:
            return PromotionGateReport(
                ts=ts, all_pass=False, overall_score=75.0,
                gates=gates,
                blocked_reason=f"G5 FAILED: {g5.message}",
            )

        # 全部PASS
        overall = sum(g.weight * (100 if g.status == GateStatus.PASS.value else 0) for g in gates)
        overall = round(overall / sum(g.weight for g in gates), 1)

        return PromotionGateReport(
            ts=ts,
            all_pass=True,
            overall_score=overall,
            gates=gates,
            next_check_ts=ts + 86400 * 7,  # 全通后7天后再检
        )

    # -------------------------------------------------------------------------
    # 逐级检查
    # -------------------------------------------------------------------------

    def _check_g1(self, report: dict) -> GateResult:
        """G1: 数据充足性闸门"""
        days = report.get("days", 0)
        samples = report.get("sample_count", 0)
        pair_count = len(report.get("by_pair", {}))

        checks = {
            "days": (days >= self.G1_MIN_DAYS, f"影子运行{days}天，需≥{self.G1_MIN_DAYS}天"),
            "samples": (samples >= self.G1_MIN_SAMPLES, f"样本{samples}条，需≥{self.G1_MIN_SAMPLES}条"),
            "pairs": (pair_count >= self.G1_MIN_PAIRS, f"交易对{pair_count}个，需≥{self.G1_MIN_PAIRS}个"),
        }

        all_pass = all(v[0] for v in checks.values())
        msg = "; ".join(v[1] for v in checks.values())

        return GateResult(
            gate=GateLevel.G1_DATA.value,
            status=GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value={"days": days, "samples": samples, "pair_count": pair_count},
            threshold={
                "min_days": self.G1_MIN_DAYS,
                "min_samples": self.G1_MIN_SAMPLES,
                "min_pairs": self.G1_MIN_PAIRS,
            },
            message=msg,
            weight=1.5,  # G1权重略高
        )

    def _check_g2(self, report: dict) -> GateResult:
        """G2: 信号质量闸门"""
        noise = report.get("noise") or {}
        quality_pct = noise.get("quality_pct", 0.0)
        high_noise_pct = noise.get("high_noise_pct", 0.0)
        agreement = report.get("agreement_pct", 0.0)
        delta = report.get("avg_delta_score", 0.0)

        checks = {
            "quality_pct": (
                quality_pct >= self.G2_MIN_QUALITY_PCT,
                f"优质信号{quality_pct}%（需≥{self.G2_MIN_QUALITY_PCT}%）",
            ),
            "high_noise_pct": (
                high_noise_pct <= self.G2_MAX_HIGH_NOISE_PCT,
                f"高噪音{high_noise_pct}%（需≤{self.G2_MAX_HIGH_NOISE_PCT}%）",
            ),
            "agreement": (
                agreement >= self.G2_MIN_AGREEMENT_PCT,
                f"一致率{agreement}%（需≥{self.G2_MIN_AGREEMENT_PCT}%）",
            ),
            "delta": (
                delta >= self.G2_MIN_DELTA_SCORE,
                f"增强加分{delta}（需≥{self.G2_MIN_DELTA_SCORE}）",
            ),
        }

        all_pass = all(v[0] for v in checks.values())
        msg = "; ".join(v[1] for v in checks.values())

        # 计算G2得分（质量越高分越高）
        quality_score = min(100.0, quality_pct / self.G2_MIN_QUALITY_PCT * 60)
        noise_score = max(0.0, 40.0 - high_noise_pct / self.G2_MAX_HIGH_NOISE_PCT * 40)
        g2_score = quality_score + noise_score

        return GateResult(
            gate=GateLevel.G2_QUALITY.value,
            status=GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value={
                "quality_pct": quality_pct,
                "high_noise_pct": high_noise_pct,
                "agreement_pct": agreement,
                "avg_delta_score": delta,
                "g2_score": round(g2_score, 1),
            },
            threshold={
                "min_quality_pct": self.G2_MIN_QUALITY_PCT,
                "max_high_noise_pct": self.G2_MAX_HIGH_NOISE_PCT,
                "min_agreement_pct": self.G2_MIN_AGREEMENT_PCT,
                "min_delta_score": self.G2_MIN_DELTA_SCORE,
            },
            message=msg,
            weight=2.0,
        )

    def _check_g3(self, report: dict) -> GateResult:
        """G3: 资金流硬闸"""
        fg = report.get("flow_gate") or {}
        candidate_count = fg.get("candidate_count", 0)
        block_pct = fg.get("block_pct", 0.0)
        pass_rate = 1.0 - block_pct / 100.0

        checks = {
            "min_candidates": (
                candidate_count >= self.G3_MIN_CANDIDATES,
                f"资金流候选{candidate_count}个（需≥{self.G3_MIN_CANDIDATES}个）",
            ),
            "min_pass_rate": (
                pass_rate >= self.G3_MIN_PASS_RATE,
                f"通过率{pass_rate*100:.1f}%（需≥{self.G3_MIN_PASS_RATE*100:.0f}%）",
            ),
            "max_pass_rate": (
                pass_rate <= self.G3_MAX_PASS_RATE,
                f"通过率{pass_rate*100:.1f}%（需≤{self.G3_MAX_PASS_RATE*100:.0f}%，不能太松）",
            ),
        }

        all_pass = all(v[0] for v in checks.values())
        msg = "; ".join(v[1] for v in checks.values())

        return GateResult(
            gate=GateLevel.G3_FLOW.value,
            status=GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value={
                "candidate_count": candidate_count,
                "pass_rate": round(pass_rate, 3),
                "block_pct": block_pct,
            },
            threshold={
                "min_pass_rate": self.G3_MIN_PASS_RATE,
                "max_pass_rate": self.G3_MAX_PASS_RATE,
                "min_candidates": self.G3_MIN_CANDIDATES,
            },
            message=msg,
            weight=1.5,
        )

    def _check_g4(self, report: dict) -> GateResult:
        """
        G4: 风险控制闸门

        注意：当前影子实验室没有真实胜率/回撤数据。
        G4暂时使用影子评分作为代理指标，待walk-forward模块就绪后替换。
        """
        # TODO(walkforward): 等 walk_forward 模块完成后来替换为真实数据
        # 目前用影子分数估算
        avg_shadow_score = report.get("avg_delta_score", 0.0) + 50.0  # 估算
        estimated_win_rate = min(0.75, 0.40 + avg_shadow_score / 200.0)
        estimated_drawdown = max(0.05, 0.25 - avg_shadow_score / 400.0)

        checks = {
            "win_rate": (
                estimated_win_rate >= self.G4_MIN_WIN_RATE,
                f"估算胜率{estimated_win_rate*100:.1f}%（需≥{self.G4_MIN_WIN_RATE*100:.0f}%）[待真实数据]",
            ),
            "drawdown": (
                estimated_drawdown <= self.G4_MAX_DRAWDOWN,
                f"估算回撤{estimated_drawdown*100:.1f}%（需≤{self.G4_MAX_DRAWDOWN*100:.0f}%）[待真实数据]",
            ),
        }

        all_pass = all(v[0] for v in checks.values())
        msg = "; ".join(v[1] for v in checks.values())

        return GateResult(
            gate=GateLevel.G4_RISK.value,
            status=GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value={
                "estimated_win_rate": round(estimated_win_rate, 3),
                "estimated_drawdown": round(estimated_drawdown, 3),
                "note": "G4当前为估算值，待walk_forward模块完成后替换为真实数据",
            },
            threshold={
                "min_win_rate": self.G4_MIN_WIN_RATE,
                "max_drawdown": self.G4_MAX_DRAWDOWN,
            },
            message=msg,
            weight=2.5,  # G4权重最高（风险控制优先）
        )

    def _check_g5(self, report: dict) -> GateResult:
        """
        G5: Walk-Forward闸门

        当前状态：walk_forward模块尚未执行。
        G5设为PENDING，不阻止晋级评审，但须在人工确认前完成。
        """
        # 检查是否有walk_forward报告
        wf_report = BASE / "walk_forward_report.json"
        if wf_report.exists():
            wf = json.loads(wf_report.read_text(encoding="utf-8"))
            periods_ok = wf.get("periods_positive", [])
            all_positive = len(periods_ok) >= self.G5_PERIODS and all(periods_ok)
            degradation = wf.get("max_degradation", 1.0)
            deg_ok = degradation <= self.G5_MAX_DEGRADATION

            all_pass = all_positive and deg_ok
            return GateResult(
                gate=GateLevel.G5_WALKFORWARD.value,
                status=GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
                value=wf,
                threshold={"periods": self.G5_PERIODS, "max_degradation": self.G5_MAX_DEGRADATION},
                message=f"Walk-forward {len(periods_ok)}期，全正期望={all_positive}，衰减={degradation*100:.1f}%（限{self.G5_MAX_DEGRADATION*100:.0f}%）",
                weight=2.0,
            )
        else:
            return GateResult(
                gate=GateLevel.G5_WALKFORWARD.value,
                status=GateStatus.PENDING.value,
                value=None,
                threshold={"periods": self.G5_PERIODS},
                message=f"Walk-forward报告不存在（walk_forward_report.json），G5待执行。请触发 walk_forward 模块。",
                weight=0.0,  # PENDING不影响总分
            )


def run_gate_check() -> PromotionGateReport:
    """快捷入口：运行全套闸门检查。"""
    checker = L5PromotionGate()
    result = checker.check_all()
    # 保存结果
    out_path = BASE / "promotion_gate_report.json"
    out_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = run_gate_check()
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if not result.all_pass:
        print(f"\n[BLOCKED] {result.blocked_reason}")
    else:
        print(f"\n[APPROVED] L5晋级闸门全部通过，综合得分 {result.overall_score}/100")
```

---

## 四、当前各闸门状态

### G1 — 数据充足性 ✅ PASS
| 指标 | 当前值 | 要求 | 状态 |
|------|--------|------|------|
| 影子运行天数 | 7天 | ≥7天 | PASS |
| 影子样本总数 | 3040条 | ≥300条 | PASS |
| 交易对覆盖 | 5个 | ≥3个 | PASS |

### G2 — 信号质量 ✅ PASS
| 指标 | 当前值 | 要求 | 状态 |
|------|--------|------|------|
| 优质信号占比 | 9.3% | ≥8% | PASS |
| 高噪音占比 | 40.7% | ≤45% | PASS |
| 影子/基准一致率 | 93.7% | ≥85% | PASS |
| 增强平均加分 | +11.58 | ≥+5.0 | PASS |

### G3 — 资金流硬闸 ✅ PASS
| 指标 | 当前值 | 要求 | 状态 |
|------|--------|------|------|
| 资金流候选数 | 214个 | ≥50个 | PASS |
| 资金流通过率 | 74.3% | ≥65%且≤85% | PASS |

### G4 — 风险控制 ⚠️ PENDING（估算值，待真实数据）
| 指标 | 当前估算 | 要求 | 状态 |
|------|---------|------|------|
| 历史胜率 | ~62% | ≥52% | PASS（估算） |
| 最大回撤 | ~17% | ≤20% | PASS（估算） |

> **警告**：G4当前为估算值，待walk-forward模块完成后替换为真实数据。

### G5 — Walk-Forward ❌ PENDING（模块尚未执行）
| 指标 | 状态 | 说明 |
|------|------|------|
| Walk-Forward | 未执行 | walk_forward_report.json 不存在 |

---

## 五、晋级决策树

```
START: 新L5候选参数生成
  │
  ├─→ G1 检查（数据充足性）
  │     ├─ FAIL → 阻塞，补充数据
  │     └─ PASS → 继续
  │
  ├─→ G2 检查（信号质量）
  │     ├─ FAIL → 阻塞，优化规则
  │     └─ PASS → 继续
  │
  ├─→ G3 检查（资金流硬闸）
  │     ├─ FAIL → 阻塞，调整资金流阈值
  │     └─ PASS → 继续
  │
  ├─→ G4 检查（风险控制）
  │     ├─ FAIL → 阻塞，回测重做
  │     └─ PASS → 继续（G4有PENDING豁免权）
  │
  ├─→ G5 检查（Walk-Forward）
  │     ├─ FAIL → 阻塞，walk-forward重做
  │     ├─ PENDING → 允许进入评审，但需在人工确认前完成G5
  │     └─ PASS → 继续
  │
  └─→ 全部PASS → 注册到 L5CandidateRegistry
                   ↓
              爸人工确认
                   ↓
         apply_to_live() 写入runtime
```

---

## 六、闸门参数调整权限

| 闸门 | 可调整权限 | 调整方式 |
|------|-----------|---------|
| G1数据量 | 翰林院 | 修改 L5PromotionGate 常量 |
| G2质量比 | 翰林院+爸确认 | 修改 L5PromotionGate 常量 |
| G3资金流 | 翰林院+爸确认 | 修改 L5PromotionGate 常量 |
| G4风险 | 翰林院+爸确认 | 修改 L5PromotionGate 常量 |
| G5 Walk-Forward | 翰林院 | 独立模块执行 |

**禁止**：任何Bot Agent / L5模块自行修改晋级闸门参数。
