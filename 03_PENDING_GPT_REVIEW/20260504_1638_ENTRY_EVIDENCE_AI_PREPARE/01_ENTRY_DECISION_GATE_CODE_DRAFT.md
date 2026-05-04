# 01_ENTRY_DECISION_GATE_CODE_DRAFT.md
# 入场决策门草案（EntryDecisionGate）

## 代码引用来源

| 来源 | 文件:行号 |
|------|-----------|
| check_entry_rules() 函数签名 | `bt_tools/v65_autopilot.py:854` |
| L1量比检查 | `bt_tools/v65_autopilot.py:906-920` |
| L2资金流检查 | `bt_tools/v65_autopilot.py:991-1099` |
| L4 S/R支撑压力检查 | `bt_tools/v65_autopilot.py:1100-1180` |
| V6.5量比阈值常量 | `bt_tools/v65_autopilot.py:152` (_VOL_SIGNAL_MULT=5.0) |
| L4 S/R入场容差 | `bt_tools/v65_autopilot.py:510` (_SR_ENTRY_RANGE=1.0) |
| L4触底/触顶次数 | `bt_tools/v65_autopilot.py:485` (_LONG_TOUCH=3) |
| 周末量比阈值 | `bt_tools/v65_autopilot.py:879` (6.0x) |
| check_exit_cooldown() | `bt_tools/v65_autopilot.py:826` |
| _get_capital_flow() | `bt_tools/v65_autopilot.py:3093` |

---

## EntryDecisionGate 草案

```python
# bt_tools/entry_decision_gate.py  (草案文件，禁止直接写入实盘)
# 引用: v65_autopilot.py:854-1263

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timezone, timedelta
import os

# ── 运行时模式开关（默认shadow）──────────────────────────────
ENTRY_GATE_MODE = os.environ.get("TIANLU_ENTRY_GATE_MODE", "shadow")
#   shadow  - 只记录日志，不阻止（默认）
#   live    - 拒绝时真正阻止入场
#   dry     - 完全不调用AI，只规则检查

# ── 爸确认的置信度门槛 ──────────────────────────────────────
COMPOSITE_SCORE_THRESHOLD = 50  # 2026-04-27爸确认

# ── 关键常量引用（v65_autopilot.py:152, 510）────────────────
_VOL_SIGNAL_MULT     = 5.0    # v65_autopilot.py:152 平时量比门槛
_VOL_SIGNAL_WEEKEND  = 6.0    # v65_autopilot.py:879 周末门槛
_SR_ENTRY_RANGE      = 1.0    # v65_autopilot.py:510 S/R入场范围±1%
_LONG_TOUCH          = 3      # v65_autopilot.py:485 触底次数要求


class EntryVerdictType(Enum):
    ALLOW  = "ALLOW"    # 通过
    BLOCK  = "BLOCK"    # 拒绝
    SHADOW = "SHADOW"   # shadow模式：记录但不阻止


@dataclass
class EntryVerdict:
    """入场决策结果"""
    verdict: EntryVerdictType
    pair: str
    direction: str
    score: int = 0                    # 综合评分 0-100
    confidence: float = 0.0           # 天眼AI置信度 0.0-1.0
    reason: str = ""
    sources: list[str] = field(default_factory=list)  # 通过的层级: ["L1","L2","L4","tianyan_ai"]
    rejected_layers: list[str] = field(default_factory=list)  # 拒绝的层级
    ai_verdict: str = ""             # 天眼AI原始verdict
    ai_speech: str = ""              # 天眼AI话术
    shadow_mode: bool = True         # 是否shadow模式

    @staticmethod
    def allow(pair, direction, score=0, sources=None, **kwargs) -> "EntryVerdict":
        return EntryVerdict(EntryVerdictType.ALLOW, pair, direction,
                            score=score, sources=sources or [], **kwargs)

    @staticmethod
    def block(pair, direction, reason, rejected_layers=None, **kwargs) -> "EntryVerdict":
        return EntryVerdict(EntryVerdictType.BLOCK, pair, direction,
                            reason=reason, rejected_layers=rejected_layers or [], **kwargs)

    @staticmethod
    def shadow(pair, direction, reason, score=0, **kwargs) -> "EntryVerdict":
        return EntryVerdict(EntryVerdictType.SHADOW, pair, direction,
                            score=score, reason=reason, shadow_mode=True, **kwargs)


def _log_gate(msg: str, level: str = "INFO"):
    """EntryDecisionGate专用日志"""
    ts = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} [EntryGate][{level}] {msg}")


# ── M1 Evidence 接口（详见 02_M1_M5_EVIDENCE_API_DRAFT.md） ──
def get_m1_evidence(pair: str) -> dict:
    """
    M1资金流Evidence读取
    数据源: console_server.py:26832 /api/m1/hero_card
    返回: {ratio, netflow, signal, gate_ratio, okx_ratio, bnb_ratio, ...}
    """
    # TODO: 调用 console_server.py:26832 的 /api/m1/hero_card 端点
    raise NotImplementedError("get_m1_evidence() 需对接 /api/m1/hero_card")


def get_m2_sr_evidence(pair: str, direction: str, current_price: float) -> dict:
    """
    M2 S/R Evidence读取
    数据源: console_server.py:25692 /api/bt2/sr_levels
    返回: {has_sr, sr_type, sr_price, sr_touches, data_source, ...}
    """
    raise NotImplementedError("get_m2_sr_evidence() 需对接 /api/bt2/sr_levels")


def get_m3_ohlcv_evidence(pair: str) -> dict:
    """
    M3波动率Evidence读取（ATR + GIANT K线）
    数据源: v65_autopilot.py 内 _get_capital_flow() 或 console_server.py OHLCV计算
    返回: {atr, giant_count, squeeze_count, ...}
    """
    raise NotImplementedError("get_m3_ohlcv_evidence() 需对接现有 OHLCV 计算")


def get_m4_technical_evidence(pair: str) -> dict:
    """
    M4技术指标Evidence读取（RSI/OBV/OI）
    数据源: console_server.py 中的 RSI/OI 计算逻辑
    返回: {rsi_15m, rsi_1h, oi_change, ...}
    """
    raise NotImplementedError("get_m4_technical_evidence() 需对接现有技术指标计算")


def get_l5_scenario_evidence(pair: str) -> dict:
    """
    L5场景Evidence读取
    数据源: console_server.py 中的 L5 模块（爆仓流/订单薄/点差）
    返回: {scene_type, dot_blacklist, spread, ...}
    """
    raise NotImplementedError("get_l5_scenario_evidence() 需对接现有 L5 模块")


# ── 天眼AI调用（详见 03_TIANYAN_AI_INTEGRATION_DRAFT.md） ──
def call_tianyan_ai(m1: dict, m2: dict, m3: dict, m4: dict) -> dict:
    """
    调用天眼AI V5.3 进行入场质量评估
    数据源: console_server.py:13830 TianyanAgent
    返回: {verdict, confidence, reason, speech}
    """
    raise NotImplementedError("call_tianyan_ai() 需对接 TianyanAgent.analyze()")


# ── 综合评分计算 ─────────────────────────────────────────────
def compute_composite_score(
    m1: dict, m2: dict, m3: dict, m4: dict, m5: dict, tianyan: dict
) -> int:
    """
    综合评分（0-100），基于自适应置信度算法
    引用: console_server.py:13901 自适应置信度算法

    评分构成:
      M1共振强度×0.4 + M2强度×0.3 + M3强度×0.3 (×三所一致率)
      M1: 3所同向=1.0, 2所=0.7, 单所=0.3
      M2: 三验=1.0, 双验=0.8, 单验=0.4
      M3: GIANT+双所=1.0, 单所=0.5, 无信号=0.0
    """
    raise NotImplementedError("compute_composite_score() 需实现")


# ═══════════════════════════════════════════════════════════════
#  EntryDecisionGate.evaluate() —— 核心评估函数
# ═══════════════════════════════════════════════════════════════

def evaluate(pair: str, direction: str, current_price: float) -> EntryVerdict:
    """
    入场决策门评估

    评估流程:
      1. S/R检查（L4）—— v65_autopilot.py:1100-1180
      2. M1-M5 evidence收集
      3. 天眼AI评估（shadow模式）
      4. 综合评分 >= 50 → ALLOW/SHADOW
      5. 综合评分 < 50  → BLOCK/SHADOW

    重要: shadow模式下，BLOCK只记录日志，不阻止机器人入场
          禁止在shadow模式下修改机器人参数或调用交易API
    """
    mode = ENTRY_GATE_MODE
    signals_passed = []
    rejected_layers = []

    _log_gate(f"评估开始: {pair} {direction} @ {current_price} (mode={mode})")

    # ── 1. S/R检查（L4）引用: v65_autopilot.py:1100-1180 ─────
    try:
        sr = get_m2_sr_evidence(pair, direction, current_price)
        has_sr = sr.get("has_sr", False)
        sr_type = sr.get("sr_type", "unknown")
        sr_touches = sr.get("sr_touches", 0)
        sr_price = sr.get("sr_price", 0)

        sr_type_match = (
            (direction == "LONG" and sr_type == "support") or
            (direction == "SHORT" and sr_type == "resistance")
        )

        dist_to_sr = 0
        if sr_price > 0 and current_price > 0:
            dist_to_sr = (current_price - sr_price) / sr_price * 100

        l4_passed = (
            has_sr and sr_type_match and
            sr_touches >= _LONG_TOUCH and
            abs(dist_to_sr) < _SR_ENTRY_RANGE
        )

        if not l4_passed:
            reason = (f"S/R拒绝: has_sr={has_sr}, type_match={sr_type_match}, "
                      f"touches={sr_touches}/{_LONG_TOUCH}, dist={dist_to_sr:+.2f}%")
            rejected_layers.append("L4")
            _log_gate(f"  L4拒绝: {reason}")
            if mode == "live":
                return EntryVerdict.block(pair, direction, reason=f"S/R拒绝: {reason}",
                                          rejected_layers=["L4"])
            return EntryVerdict.shadow(pair, direction, reason=f"S/R待确认: {reason}",
                                       rejected_layers=["L4"])

        signals_passed.append("L4")
        _log_gate(f"  L4通过: {sr_type} @ {sr_price:.4f}, touches={sr_touches}, dist={dist_to_sr:+.2f}%")

    except Exception as e:
        _log_gate(f"  L4检查异常: {e}", "WARNING")

    # ── 2. M1-M5 Evidence收集 ───────────────────────────────
    try:
        m1_evidence = get_m1_evidence(pair)
        m2_evidence = sr
        m3_evidence = get_m3_ohlcv_evidence(pair)
        m4_evidence = get_m4_technical_evidence(pair)
        m5_evidence = get_l5_scenario_evidence(pair)
        signals_passed.extend(["M1", "M2", "M3", "M4", "L5"])
    except Exception as e:
        _log_gate(f"  Evidence收集异常: {e}", "WARNING")

    # ── 3. 天眼AI评估（shadow模式）───────────────────────────
    tianyan_result = {"verdict": "UNKNOWN", "confidence": 0.0, "reason": "", "speech": ""}
    try:
        if mode != "dry":
            tianyan_result = call_tianyan_ai(m1_evidence, m2_evidence, m3_evidence, m4_evidence)
            _log_gate(f"  天眼AI: verdict={tianyan_result.get('verdict')}, "
                      f"confidence={tianyan_result.get('confidence', 0):.2f}")
    except Exception as e:
        _log_gate(f"  天眼AI调用异常: {e}", "WARNING")

    # ── 4. 综合评分 ─────────────────────────────────────────
    score = 0
    try:
        if mode != "dry":
            score = compute_composite_score(m1_evidence, m2_evidence, m3_evidence,
                                             m4_evidence, m5_evidence, tianyan_result)
        _log_gate(f"  综合评分: {score}/{COMPOSITE_SCORE_THRESHOLD}")
    except Exception as e:
        _log_gate(f"  综合评分异常: {e}", "WARNING")

    # ── 5. 最终判决 ─────────────────────────────────────────
    if score >= COMPOSITE_SCORE_THRESHOLD and tianyan_result.get("confidence", 0) >= 0.50:
        verdict_type = EntryVerdictType.SHADOW if mode == "shadow" else EntryVerdictType.ALLOW
        _log_gate(f"  → {verdict_type.value}: score={score}, "
                  f"confidence={tianyan_result.get('confidence', 0):.2f}")
        return EntryVerdict(
            verdict=verdict_type, pair=pair, direction=direction, score=score,
            confidence=tianyan_result.get("confidence", 0),
            sources=signals_passed, rejected_layers=rejected_layers,
            ai_verdict=tianyan_result.get("verdict", ""),
            ai_speech=tianyan_result.get("speech", ""),
            shadow_mode=(mode == "shadow")
        )
    else:
        reason = f"综合评分{score} < {COMPOSITE_SCORE_THRESHOLD} 或置信度不足"
        if mode == "live":
            return EntryVerdict.block(pair, direction, reason=reason,
                                      score=score, rejected_layers=rejected_layers)
        _log_gate(f"  → SHADOW (score={score}): {reason}")
        return EntryVerdict.shadow(pair, direction, reason=reason, score=score,
                                    rejected_layers=rejected_layers,
                                    ai_verdict=tianyan_result.get("verdict", ""),
                                    ai_speech=tianyan_result.get("speech", ""))


# ═══════════════════════════════════════════════════════════════
#  集成点: 与 v65_autopilot.py 的 check_entry_rules() 对接
# ═══════════════════════════════════════════════════════════════
#
# 在 check_entry_rules() 末尾（v65_autopilot.py:1257附近）增加:
#
#   gate_result = evaluate(pair, direction, current_price)
#   _log(f"[EntryGate] {pair} {direction} → {gate_result.verdict.value} (score={gate_result.score})")
#   if gate_result.verdict == EntryVerdictType.BLOCK and mode == "live":
#       can_entry = False
#       reasons.append(f"EntryGate拒绝: {gate_result.reason}")
#
# 注意: 此草案不得直接写入 v65_autopilot.py
#       需 GPT 评审 → 爸确认后才可接入实盘
