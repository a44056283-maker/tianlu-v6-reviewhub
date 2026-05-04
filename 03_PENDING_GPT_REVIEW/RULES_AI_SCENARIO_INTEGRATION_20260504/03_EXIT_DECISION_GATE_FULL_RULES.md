# ExitDecisionGate 完整规则
> 出山院代理生成 | 日期: 2026-05-04 | 版本: V1.0
> 状态: PENDING REVIEW

---

## 一、设计目标

ExitDecisionGate（出场裁决闸门）是出山AI的核心控制层，所有出场动作必须经过此门控。它的职责是：

1. 防止连续亏损后自动收紧止盈（卖在黎明前）
2. 维护 7 条出场路径的互斥优先级
3. 记录 post_exit_continuation 观察期状态
4. 为每个 exit 请求生成标准化裁决结果

---

## 二、5档裁决定义

| 档位 | 名称 | 含义 | 置信度范围 | 执行动作 |
|------|------|------|-----------|---------|
| **G1** | HOLD | 继续持有 | - | 0% 出场 |
| **G2** | WATCH | 观察（趋势不明） | - | 0% 出场，记录但不执行 |
| **G3** | PARTIAL_EXIT | 建议部分止盈 | 50-79% | 按档位比例出场（30-60%） |
| **G4** | FULL_EXIT_REVIEW | 建议全平，需人工复核 | 80-99% | 100% 出场，但需飞书确认 |
| **G5** | EMERGENCY_REVIEW | 紧急风险复核 | 100% | 立即全平，无需确认 |

### 2.1 档位判断逻辑

```
score >= 90 + 紧急信号     → EMERGENCY_REVIEW（G5）
score >= 80                → FULL_EXIT_REVIEW（G4）
score >= 50                → PARTIAL_EXIT（G3）
score >= 30                → WATCH（G2）
score < 30                 → HOLD（G1）
```

### 2.2 档位与 P1/P2/P3 止盈的关系

| 档位 | P1止盈（基准15%） | P2止盈（基准25%） | P3止盈（基准35%） |
|------|-----------------|-----------------|-----------------|
| HOLD | ❌ 不触发 | ❌ 不触发 | ❌ 不触发 |
| WATCH | ❌ 不触发 | ❌ 不触发 | ❌ 不触发 |
| PARTIAL_EXIT | ✅ 触发（30-60%） | ✅ 触发（30-60%） | ✅ 触发（30-60%） |
| FULL_EXIT_REVIEW | ✅ 触发（100%） | ✅ 触发（100%） | ✅ 触发（100%） |
| EMERGENCY_REVIEW | ✅ 立即全平 | ✅ 立即全平 | ✅ 立即全平 |

---

## 三、7条出场规则

### 规则1：连续亏损后不自动过早止盈

**问题代码**（已修复）：
```python
# v65_autopilot.py:4670-4675（旧版bug）
if consec_losses >= 2 and profit_pct > 5:
    thresh = 10  # 盈利>5%就开始卖（绕过门控）
    _temp_thresh_override[base] = thresh
```

**规则1要求**：
- 连续亏损 >= 2 次时，`_temp_thresh_override[base]` 不得被直接写入
- 必须经过 ExitDecisionGate.evaluate() 裁决
- 观测期内（24小时），auto_profit_tighten 动作被禁止
- 连续亏损收紧请求必须进入 G4/FULL_EXIT_REVIEW 或 G5/EMERGENCY_REVIEW，不能直接执行

**触发条件**：
```python
consec_losses >= _EXIT_GATE_LOSS_THRESHOLD  # 默认=2
```

**执行效果**：
- action = "block": 收紧请求被拦截，`_temp_thresh_override.pop(base, None)`
- observation_active = True: 进入 24 小时观察期
- 观察期内：规则P1/P2/P3 正常触发，但自学习收紧被禁止

---

### 规则2：出场前检查趋势延续概率

**规则2要求**：
- 在执行任何止盈出场前（除 EMERGENCY_REVIEW 外），必须评估趋势延续概率
- 趋势延续概率 < 50% 时，不建议继续持有
- 趋势延续概率 >= 50% 时，允许继续持有（HOLD）

**评估维度**：

| 维度 | 权重 | 延续概率高分标准 |
|------|------|----------------|
| M1资金流 | 30% | 15m/1h/4h 三线同向 + 量比 >= 3x |
| M2支撑压力 | 20% | 紧贴支撑（多单）+ 双验以上 |
| M3巨量K线 | 25% | GIANT阳 + INFLOW 流入（非 OUTFLOW） |
| M4技术指标 | 25% | RSI 未衰竭 + OI 加仓 + EMA 多头排列 |

**计算公式**：
```
trend_continuation_score = M1_score*0.3 + M2_score*0.2 + M3_score*0.25 + M4_score*0.25
trend_continuation_prob = min(trend_continuation_score / 80, 1.0) * 100%
```

---

### 规则3：出场前检查 post_exit_continuation 风险

**规则3要求**：
- 执行 PARTIAL_EXIT（G3）及以上裁决前，必须检查 post_exit_continuation 状态
- 观测期（observation_period）激活时，禁止执行 auto_profit_tighten
- 但 ATR 止损、P0 舆情、持仓卫士（出山AI）强制出场不受观察期限制

**检查逻辑**：
```python
post_state = _post_exit_continuation.get(pair)
if post_state and post_state.get("observation_active"):
    if time.time() < post_state.get("observation_end_ts"):
        # 仍在观测期
        if action == "auto_profit_tighten":
            return { "action": "observe", "blocked_reason": "observation_period_blocks_auto_tighten" }
```

**不受观察期限制的动作**：

| 动作 | 说明 |
|------|------|
| ATR止损 | 硬风控，不可绕过 |
| P0舆情强制出场 | 突发事件优先 |
| 出山AI持仓卫士 | 决策层，不受限制 |
| 规则P1/P2/P3 | 正常止盈规则，不经自学习 |

---

### 规则4：force_exit 默认进入人工确认

**规则4要求**：
- 用户手动触发的 force_exit 不得直接全平
- 必须先评估风险级别，再推送飞书通知
- 连续亏损观察期内，force_exit 需要双重确认

**force_exit 流程**：
```
用户触发 force_exit
  → ExitDecisionGate.evaluate(force_exit=True)
  → 评估持仓风险级别（G1-G5）
  → 推送飞书通知（兵部）
  → 等待人工确认（若有风险）
  → 执行全平（仅当 G4/G5 或用户明确确认）
```

**飞书通知格式**：
```
【force_exit 确认请求】
pair: {pair}
方向: {direction}
浮盈: {pnl_pct}%
当前裁决: G{tier} {verdict}
连续亏损: {consec_losses}次
观察期: {observation_active ? "激活中(" + remaining_hours + "h)" : "无"}
请回复【确认全平】以继续执行
```

---

### 规则5：L5动态止盈不得直接无确认全平

**规则5要求**：
- L5 动态止盈的 P3 档（100% 全平）不得直接执行
- 必须经过 ExitDecisionGate.evaluate() 裁决
- 裁决结果为 G4/FULL_EXIT_REVIEW 时，推送飞书确认后再执行
- 裁决结果为 G5/EMERGENCY_REVIEW 时，立即执行并通知

**L5 P3 档位处理**：
```python
if l5_tier == "P3" and exit_pct == 100:
    gate_result = gate.evaluate(position, ..., force_exit=False)
    if gate_result["action"] in ("full_exit_review", "emergency_review"):
        if gate_result["action"] == "emergency_review":
            _execute_full_exit(trade_id)
            _send_feishu_emergency(trade_id, gate_result)
        else:  # full_exit_review
            _send_feishu_confirm(trade_id, gate_result)
            # 等待人工确认后再执行
    else:
        # G1-G3：不允许 P3 全平执行
        _log(f"[Gate] L5 P3 blocked: {gate_result['action']}")
```

---

### 规则6：S/R exit 不得单独触发强制出场

**规则6要求**：
- L2 时线止盈（S/R 触及 + 放量确认）不得单独触发强制全平
- 必须结合 M1/M4 综合裁决
- S/R exit 只能作为 PARTIAL_EXIT（G3）的辅助条件

**S/R exit 综合评估**：

| 条件 | S/R exit 效果 |
|------|--------------|
| S/R + M1同向量比 >= 3x + RSI未衰竭 | PARTIAL_EXIT 50% |
| S/R + M1同向量比 < 2x | WATCH（观察） |
| S/R + M1反向量比 | HOLD（继续持有） |
| S/R + M4 RSI衰竭 | FULL_EXIT_REVIEW 复核 |

---

### 规则7：P0-4 bug修复 — 连续亏损收紧必须经过门控

**规则7（P0 bug修复）**：
- 原代码（v65_autopilot.py:4670-4675）直接写入 `_temp_thresh_override`，绕过门控
- 修复后：所有连续亏损收紧请求必须经过 ExitDecisionGate.evaluate()
- 门控返回 action = "block" 时，清除 `_temp_thresh_override[base]`，不下发收紧阈值

**P0 修复代码**：
```python
# 替换 v65_autopilot.py:4670-4675
gate = ExitDecisionGate()
gate_result = gate.evaluate(
    position={"pair": pair, "direction": direction,
              "profit_pct": profit_pct, "leverage": leverage},
    m1_payload=None, l5_payload=None)

# blocked → 清除待下发阈值，观察期保护生效
if gate_result.get("action") in ("block", "observe"):
    _temp_thresh_override.pop(base, None)
    _log(f"[Gate] AUTO-TIGHTEN BLOCKED: consec_losses={consec_losses}")
```

**验证清单**：
- [ ] `_post_exit_continuation` 全局变量已声明
- [ ] `ExitDecisionGate` 类已插入 `check_exit_conditions()` 函数之前
- [ ] 原 4670-4675 行已被门控调用替换
- [ ] 连续亏损 >= 2 时，`_temp_thresh_override[base]` 不再被写入
- [ ] 观察期结束后，`_post_exit_continuation[pair]` 被正确清除

---

## 四、ExitDecisionGate 类完整代码

```python
# ══════════════════════════════════════════════════════════════════════════════
# ExitDecisionGate — 出场裁决闸门
# 版本: V1.0 | 日期: 2026-05-04 | 出山院代理
# ══════════════════════════════════════════════════════════════════════════════

import time
from dataclasses import dataclass, field
from typing import Optional

# ── 全局状态（由 v65_autopilot.py 提供）───────────────────────────────
# _post_exit_continuation: dict   # pair → PostExitContinuation
# _temp_thresh_override: dict      # pair_base → float（临时止盈阈值）
# _get_consecutive_losses(pair)   # 函数：获取连续亏损次数
# _v65_profit_exit_allowed(...)    # 函数：v65内部止盈允许判断
# _BASE_EXIT_P1_PROFIT = 15.0     # 基准P1止盈涨幅
# _SELF_LEARNING_ENABLED = True   # 自学习开关

# ── 配置常量 ──────────────────────────────────────────────────────────
_EXIT_GATE_LOSS_THRESHOLD: int = 2           # 连续亏损N次后进入观察期
_EXIT_GATE_OBSERVATION_HOURS: int = 24       # 观察期时长（小时）
_EXIT_GATE_TIGHTEN_THRESHOLD: float = 10.0    # 连续亏损后收紧止盈阈值（%）
_EXIT_GATE_BLOCKED_ACTIONS: list[str] = [     # 观察期内被禁止的动作
    "auto_profit_tighten",    # 自学习自动收紧止盈
    "auto_dca",               # 自动DCA加仓
    "auto_reentry",           # 自动反向入场
]


@dataclass
class PostExitContinuation:
    """出场后延续观测状态"""
    observation_active: bool = False
    consecutive_losses: int = 0
    observation_start_ts: float = 0.0
    observation_end_ts: float = 0.0
    loss_threshold: int = 2
    observation_period_hours: int = 24
    actions_blocked: list[str] = field(
        default_factory=lambda: _EXIT_GATE_BLOCKED_ACTIONS.copy()
    )
    last_loss_pair: str = ""
    unlock_trigger: Optional[str] = None


@dataclass
class ExitVerdict:
    """出场裁决结果"""
    verdict: str          # G1/HOLD | G2/WATCH | G3/PARTIAL_EXIT | G4/FULL_EXIT_REVIEW | G5/EMERGENCY_REVIEW
    approved: bool        # 是否批准执行
    action: str           # "exit" | "observe" | "block" | "pass" | "confirm"
    reason: str           # 决策原因
    exit_pct: float       # 出场比例（0-100）
    tier: str             # 触发档位 P0/P1/P2/P3/P4/P5/P6
    override_thresh: Optional[float]   # 临时阈值（仅自学习收紧场景）
    blocked_reason: Optional[str]       # 被拦截原因
    trend_continuation_prob: float     # 趋势延续概率（0-100%）
    score: int            # 综合评分（0-100）
    feishu_msg: str       # 飞书通知内容


class ExitDecisionGate:
    """
    出场裁决闸门

    所有出场动作必须经过此门控，确保：
    1. 连续亏损后不自动过早止盈（规则1）
    2. 出场前检查趋势延续概率（规则2）
    3. 出场前检查 post_exit_continuation 风险（规则3）
    4. force_exit 默认进入人工确认（规则4）
    5. L5动态止盈不得直接无确认全平（规则5）
    6. S/R exit 不得单独触发强制出场（规则6）
    7. P0-4 bug修复：连续亏损收紧必须经过门控（规则7）

    用法：
        gate = ExitDecisionGate()
        verdict = gate.evaluate(
            position={"pair": "BTC/USDT", "direction": "LONG",
                      "profit_pct": 18.5, "leverage": 10, ...},
            m1_payload={"netflow_15m": 0.85, "ratio_15m": 3.2, ...},
            l5_payload={"tier_idx": 1, "trigger_pct": 20.0, "exit_pct": 50, ...},
            force_exit=False
        )
    """

    # ── 档位阈值常量 ──────────────────────────────────────────────────
    SCORE_EMERGENCY = 90    # G5: 紧急风险复核
    SCORE_FULL_EXIT = 80    # G4: 建议全平复核
    SCORE_PARTIAL = 50      # G3: 建议部分止盈
    SCORE_WATCH = 30        # G2: 观察

    def __init__(self):
        pass

    # ════════════════════════════════════════════════════════════════════
    # 核心评估方法
    # ════════════════════════════════════════════════════════════════════

    def evaluate(
        self,
        position: dict,
        m1_payload: Optional[dict] = None,
        l5_payload: Optional[dict] = None,
        force_exit: bool = False
    ) -> ExitVerdict:
        """
        出场裁决主入口

        流程:
        1. 检查 post_exit_continuation 观察期
        2. 计算综合评分（M1+M2+M3+M4）
        3. 评估趋势延续概率
        4. 判断档位（G1-G5）
        5. 规则保护检查（规则1-7）
        6. 生成标准化裁决结果
        """
        pair = position.get("pair", "")
        direction = position.get("direction", "LONG")
        profit_pct = position.get("profit_pct", 0.0)
        leverage = position.get("leverage", 10)
        consec_losses = self._get_consecutive_losses(pair)
        base = pair.split("/")[0]

        # ── Step 1: 观察期检查（规则1 + 规则3）─────────────────────
        post_state = self._get_post_exit_continuation(pair)
        in_observation = self._is_in_observation(post_state)

        if in_observation and "auto_profit_tighten" in _EXIT_GATE_BLOCKED_ACTIONS:
            # 观测期内：拦截自学习收紧
            _temp_thresh_override.pop(base, None)  # 清除待下发阈值
            remaining_h = self._remaining_obs_hours(post_state)
            return ExitVerdict(
                verdict="G2_WATCH",
                approved=False,
                action="observe",
                reason=f"post_exit_continuation_active (剩余{remaining_h:.1f}h)",
                exit_pct=0.0,
                tier="OBSERVATION",
                override_thresh=None,
                blocked_reason="auto_profit_tighten_blocked_in_observation",
                trend_continuation_prob=0.0,
                score=0,
                feishu_msg=self._build_feishu(
                    pair, direction, profit_pct, "G2/WATCH",
                    f"观测期激活中（剩余{remaining_h:.1f}h），拦截自学习收紧"
                )
            )

        # ── Step 2: 连续亏损 >= 2 必须经过门控（规则7/P0修复）─────
        if consec_losses >= _EXIT_GATE_LOSS_THRESHOLD:
            # 收紧请求被拦截，等待人工确认或观察期结束
            gate_action = "block"
            if in_observation:
                gate_action = "observe"

            return ExitVerdict(
                verdict="G4_FULL_EXIT_REVIEW",
                approved=False,
                action=gate_action,
                reason=f"consecutive_losses={consec_losses} >= {_EXIT_GATE_LOSS_THRESHOLD}, "
                       f"tighten_request_requires_manual_confirm",
                exit_pct=0.0,
                tier="AUTO_TIGHTEN_BLOCKED",
                override_thresh=_EXIT_GATE_TIGHTEN_THRESHOLD,
                blocked_reason="auto_tighten_blocked_require_observation",
                trend_continuation_prob=0.0,
                score=0,
                feishu_msg=self._build_feishu(
                    pair, direction, profit_pct, "G4/FULL_EXIT_REVIEW",
                    f"连续亏损{consec_losses}次，止盈收紧请求需人工确认"
                )
            )

        # ── Step 3: force_exit 必须人工确认（规则4）─────────────────
        if force_exit:
            gate_action = "confirm"
            if consec_losses >= _EXIT_GATE_LOSS_THRESHOLD:
                gate_action = "double_confirm"

            return ExitVerdict(
                verdict="G4_FULL_EXIT_REVIEW",
                approved=False,
                action=gate_action,
                reason="force_exit_requires_manual_confirm",
                exit_pct=100.0,
                tier="FORCE_EXIT",
                override_thresh=None,
                blocked_reason=None,
                trend_continuation_prob=0.0,
                score=80 if gate_action == "confirm" else 60,
                feishu_msg=self._build_feishu(
                    pair, direction, profit_pct, "G4/FORCE_EXIT确认",
                    f"force_exit请求，{'连续亏损观察期内需双重确认' if gate_action == 'double_confirm' else '需人工确认'}"
                )
            )

        # ── Step 4: 计算综合评分 ──────────────────────────────────
        score = self._calc_comprehensive_score(
            position, m1_payload, l5_payload
        )
        trend_prob = self._calc_trend_continuation_prob(
            position, m1_payload, l5_payload
        )

        # ── Step 5: L5 P3 全平必须复核（规则5）────────────────────
        if l5_payload:
            tier_idx = l5_payload.get("tier_idx", -1)
            exit_pct = l5_payload.get("exit_pct", 0)
            trigger_pct = l5_payload.get("trigger_pct", 0)

            if tier_idx == 2 and exit_pct == 100:  # P3 档 100% 全平
                if score >= self.SCORE_EMERGENCY:
                    return self._build_verdict(
                        "G5_EMERGENCY_REVIEW", True, "exit",
                        f"L5_P3_100%_TRIGGERED (score={score})",
                        100.0, f"P4_L5_T{tier_idx+1}", None, None,
                        trend_prob, score
                    )
                else:
                    # 推送复核通知，不直接执行
                    return ExitVerdict(
                        verdict="G4_FULL_EXIT_REVIEW",
                        approved=False,
                        action="confirm",
                        reason=f"L5 P3 全平需复核 (score={score})",
                        exit_pct=100.0,
                        tier=f"P4_L5_T{tier_idx+1}",
                        override_thresh=None,
                        blocked_reason=None,
                        trend_continuation_prob=trend_prob,
                        score=score,
                        feishu_msg=self._build_feishu(
                            pair, direction, profit_pct, "G4/L5_P3复核",
                            f"L5 P3档位全平请求(score={score})，需人工确认"
                        )
                    )

        # ── Step 6: S/R exit 不得单独触发强制全平（规则6）─────────
        sr_payload = position.get("sr_exit_payload", None)
        if sr_payload and sr_payload.get("should_exit"):
            sr_alone = (m1_payload is None or m1_payload.get("ratio_15m", 0) < 2.0)
            if sr_alone:
                # S/R 单独触发 → 只建议部分止盈，不建议全平
                return ExitVerdict(
                    verdict="G3_PARTIAL_EXIT",
                    approved=True,
                    action="exit",
                    reason=f"SR_EXIT_ALONE_NO_FULL (score={score})",
                    exit_pct=30.0,
                    tier="P5_L2_SR",
                    override_thresh=None,
                    blocked_reason=None,
                    trend_continuation_prob=trend_prob,
                    score=score,
                    feishu_msg=self._build_feishu(
                        pair, direction, profit_pct, "G3/S/R触发",
                        f"S/R单独触发(score={score})，建议部分止盈30%"
                    )
                )

        # ── Step 7: 正常裁决 ──────────────────────────────────────
        verdict, approved, exit_pct_val, tier_val = self._determine_verdict_and_action(
            score, trend_prob, profit_pct, leverage, l5_payload
        )

        return ExitVerdict(
            verdict=verdict,
            approved=approved,
            action="exit" if approved else "pass",
            reason=f"normal_evaluation (score={score}, trend_prob={trend_prob:.1f}%)",
            exit_pct=exit_pct_val,
            tier=tier_val,
            override_thresh=None,
            blocked_reason=None,
            trend_continuation_prob=trend_prob,
            score=score,
            feishu_msg=self._build_feishu(
                pair, direction, profit_pct, verdict,
                f"综合评分={score}，趋势延续概率={trend_prob:.1f}%"
            )
        )

    # ════════════════════════════════════════════════════════════════════
    # 辅助方法
    # ════════════════════════════════════════════════════════════════════

    def _calc_comprehensive_score(
        self,
        position: dict,
        m1_payload: Optional[dict],
        l5_payload: Optional[dict]
    ) -> int:
        """
        计算综合评分（0-100）

        M1资金流:  0-25分
        M2 S/R:    0-25分
        M3巨量K线: 0-25分
        M4技术指标: 0-25分
        """
        pair = position.get("pair", "")
        direction = position.get("direction", "LONG")
        profit_pct = position.get("profit_pct", 0.0)
        leverage = position.get("leverage", 10)

        # M1资金流评分（0-25）
        m1_score = self._score_m1(m1_payload, direction)

        # M2支撑压力评分（0-25）
        m2_score = self._score_m2(position)

        # M3巨量K线评分（0-25）
        m3_score = self._score_m3(position)

        # M4技术指标评分（0-25）
        m4_score = self._score_m4(position)

        total = m1_score + m2_score + m3_score + m4_score
        return min(max(total, 0), 100)

    def _score_m1(self, m1_payload: Optional[dict], direction: str) -> int:
        """M1资金流评分（0-25）"""
        if not m1_payload:
            return 0

        score = 0
        ratio_15m = m1_payload.get("ratio_15m", 0.0)
        ratio_1h = m1_payload.get("ratio_1h", 0.0)
        ratio_4h = m1_payload.get("ratio_4h", 0.0)
        netflow_15m = m1_payload.get("netflow_15m", 0.0)
        signal = m1_payload.get("signal_15m", "NEUTRAL")

        # 量比评分
        if direction == "LONG":
            if ratio_15m >= 5.0:   score += 10
            elif ratio_15m >= 3.0: score += 7
            elif ratio_15m >= 2.0: score += 4
            elif ratio_15m >= 1.0: score += 1

            if signal == "LONG" and netflow_15m > 0.3: score += 8
            elif signal == "LONG": score += 4
            elif signal == "NEUTRAL": score += 1
        else:  # SHORT
            if ratio_15m >= 5.0:   score += 10
            elif ratio_15m >= 3.0: score += 7
            elif ratio_15m >= 2.0: score += 4

            if signal == "SHORT" and netflow_15m < -0.3: score += 8
            elif signal == "SHORT": score += 4

        # 三线共振加分
        if ratio_15m >= 3.0 and ratio_1h >= 2.0 and ratio_4h >= 1.5:
            score += 7

        return min(score, 25)

    def _score_m2(self, position: dict) -> int:
        """M2支撑压力评分（0-25）"""
        score = 0
        direction = position.get("direction", "LONG")

        # 紧贴支撑/压力（±1%内）加分
        near_sr = position.get("near_sr", False)
        dual_count = position.get("dual_count", 0)
        dist_support = position.get("dist_support_pct", 999)
        dist_resistance = position.get("dist_resistance_pct", 999)

        if near_sr:
            if direction == "LONG":
                if dist_support <= 0.5:   score += 15
                elif dist_support <= 1.0:  score += 10
                else:                      score += 5
            else:  # SHORT
                if dist_resistance <= 0.5:   score += 15
                elif dist_resistance <= 1.0:  score += 10
                else:                         score += 5

        # 双验/三验加分
        if dual_count >= 3:  score += 10
        elif dual_count >= 2: score += 7
        elif dual_count >= 1: score += 3

        return min(score, 25)

    def _score_m3(self, position: dict) -> int:
        """M3巨量K线评分（0-25）"""
        score = 0
        direction = position.get("direction", "LONG")

        high_count = position.get("high_count", 0)
        giant_bull = position.get("giant_bull", 0)
        giant_bear = position.get("giant_bear", 0)
        reversal_hunt = position.get("reversal_hunt", False)
        outflow_present = position.get("outflow_present", False)
        max_vol_ratio = position.get("max_vol_ratio", 0.0)

        # HIGH数量评分
        if high_count >= 3:    score += 10
        elif high_count >= 2:  score += 7
        elif high_count >= 1:  score += 4

        # GIANT K线评分
        if direction == "LONG":
            if giant_bull >= 2:    score += 10
            elif giant_bull >= 1:  score += 6
            if giant_bear >= 1:   score -= 8  # 机构空头信号
        else:
            if giant_bear >= 2:   score += 10
            elif giant_bear >= 1: score += 6
            if giant_bull >= 1:   score -= 8

        # 放量加分
        if max_vol_ratio >= 5.0: score += 5
        elif max_vol_ratio >= 3.0: score += 3

        # 反转猎杀：立即高分
        if reversal_hunt:
            score = 25  # 直接满分
        # OUTFLOW流出：减分
        if outflow_present:
            score = max(score - 10, 0)

        return min(max(score, 0), 25)

    def _score_m4(self, position: dict) -> int:
        """M4技术指标评分（0-25）"""
        score = 0
        direction = position.get("direction", "LONG")

        rsi_15m = position.get("rsi_15m", 50.0)
        rsi_exhaust = position.get("rsi_exhaust", "none")  # bull_exhaust | bear_exhaust | none
        oi_ratio = position.get("oi_ratio", 1.0)
        atr_pct = position.get("atr_pct", 3.0)
        ema_alignment = position.get("ema_alignment", "混乱")  # 多头排列 | 空头排列 | 混乱
        oi_change_pct = position.get("oi_change_pct", 0.0)

        # RSI评分
        if direction == "LONG":
            if rsi_exhaust == "bull_exhaust":  return 0  # 多头衰竭，立即建议出场
            if rsi_15m < 40:    score += 8
            elif rsi_15m < 50:  score += 5
            elif rsi_15m < 60:  score += 3
            elif rsi_15m < 70:  score += 1
            else:               score -= 5  # RSI偏强，可能过热
        else:  # SHORT
            if rsi_exhaust == "bear_exhaust":  return 0  # 空头衰竭，立即建议出场
            if rsi_15m > 60:    score += 8
            elif rsi_15m > 50:  score += 5
            elif rsi_15m > 40:  score += 3
            else:               score -= 5

        # OI评分
        if oi_ratio >= 1.15:   score += 8
        elif oi_ratio <= 0.85: score -= 8
        if oi_change_pct > 5.0:  score += 4
        if oi_change_pct < -5.0: score -= 6

        # ATR评分
        if atr_pct < 2.0:    score += 3  # 低波动，可持有
        elif atr_pct > 5.0: score -= 5  # 高波动，风险加大

        # EMA排列评分
        if direction == "LONG" and ema_alignment == "多头排列":   score += 4
        elif direction == "SHORT" and ema_alignment == "空头排列": score += 4

        return min(max(score, 0), 25)

    def _calc_trend_continuation_prob(
        self,
        position: dict,
        m1_payload: Optional[dict],
        l5_payload: Optional[dict]
    ) -> float:
        """
        计算趋势延续概率（0-100%）

        公式: weighted_sum / 80 * 100%
        """
        pair = position.get("pair", "")
        direction = position.get("direction", "LONG")

        # M1（30%权重）
        m1_s = self._score_m1(m1_payload, direction)
        m1_contrib = m1_s * 0.30

        # M2（20%权重）
        m2_s = self._score_m2(position)
        m2_contrib = m2_s * 0.20

        # M3（25%权重）
        m3_s = self._score_m3(position)
        m3_contrib = m3_s * 0.25

        # M4（25%权重）
        m4_s = self._score_m4(position)
        m4_contrib = m4_s * 0.25

        total = m1_contrib + m2_contrib + m3_contrib + m4_contrib
        prob = min(total / 80.0, 1.0) * 100.0
        return round(prob, 1)

    def _determine_verdict_and_action(
        self,
        score: int,
        trend_prob: float,
        profit_pct: float,
        leverage: float,
        l5_payload: Optional[dict]
    ) -> tuple[str, bool, float, str]:
        """
        根据评分和趋势延续概率确定档位和动作

        返回: (verdict, approved, exit_pct, tier)
        """
        # 趋势延续概率 < 50% → 不建议继续持有
        if trend_prob < 50.0:
            if score >= self.SCORE_EMERGENCY:
                return "G5_EMERGENCY_REVIEW", True, 100.0, "P0_EMERGENCY"
            elif score >= self.SCORE_FULL_EXIT:
                return "G4_FULL_EXIT_REVIEW", False, 100.0, "P3_L1_30"
            elif score >= self.SCORE_PARTIAL:
                exit_pct = min(50, max(30, score - 20))
                return "G3_PARTIAL_EXIT", True, float(exit_pct), "P3_L1_PROFIT"
            else:
                return "G2_WATCH", False, 0.0, "NONE"

        # 趋势延续概率 >= 50% → 允许继续持有
        if score >= self.SCORE_EMERGENCY:
            return "G5_EMERGENCY_REVIEW", True, 100.0, "P0_EMERGENCY"
        elif score >= self.SCORE_FULL_EXIT:
            return "G4_FULL_EXIT_REVIEW", False, 100.0, "P3_L1_30"
        elif score >= self.SCORE_PARTIAL:
            exit_pct = min(40, max(20, score - 30))
            return "G3_PARTIAL_EXIT", True, float(exit_pct), "P4_L5_DYNAMIC"
        elif score >= self.SCORE_WATCH:
            return "G2_WATCH", False, 0.0, "NONE"
        else:
            return "G1_HOLD", False, 0.0, "NONE"

    # ── 状态管理 ──────────────────────────────────────────────────────

    def _get_post_exit_continuation(self, pair: str) -> Optional[dict]:
        """从全局状态读取 post_exit_continuation"""
        return _post_exit_continuation.get(pair)

    def _is_in_observation(self, post_state: Optional[dict]) -> bool:
        """判断是否在观测期内"""
        if not post_state or not post_state.get("observation_active"):
            return False
        return time.time() < post_state.get("observation_end_ts", 0)

    def _remaining_obs_hours(self, post_state: dict) -> float:
        """计算观测期剩余小时数"""
        remaining = post_state.get("observation_end_ts", 0) - time.time()
        return max(0.0, remaining / 3600.0)

    def _get_consecutive_losses(self, pair: str) -> int:
        """代理到现有 _get_consecutive_losses"""
        try:
            return _get_consecutive_losses(pair)
        except (NameError, AttributeError):
            return 0

    # ── 消息构建 ─────────────────────────────────────────────────────

    def _build_feishu(
        self,
        pair: str,
        direction: str,
        profit_pct: float,
        verdict: str,
        reason: str
    ) -> str:
        """构建飞书通知内容"""
        pnl_icon = "🟢" if profit_pct > 0 else "🔴"
        return (
            f"【{verdict}】{pair} {direction}\n"
            f"{pnl_icon}浮盈: {profit_pct:.2f}%\n"
            f"原因: {reason}"
        )

    def _build_verdict(
        self,
        verdict: str,
        approved: bool,
        action: str,
        reason: str,
        exit_pct: float,
        tier: str,
        override_thresh: Optional[float],
        blocked_reason: Optional[str],
        trend_prob: float,
        score: int
    ) -> ExitVerdict:
        """构建标准裁决结果"""
        return ExitVerdict(
            verdict=verdict,
            approved=approved,
            action=action,
            reason=reason,
            exit_pct=exit_pct,
            tier=tier,
            override_thresh=override_thresh,
            blocked_reason=blocked_reason,
            trend_continuation_prob=trend_prob,
            score=score,
            feishu_msg=""
        )
```

---

## 五、出场裁决结果格式规范

### 5.1 ExitVerdict 数据类

```python
@dataclass
class ExitVerdict:
    verdict: str           # G1_HOLD | G2_WATCH | G3_PARTIAL_EXIT
                          # | G4_FULL_EXIT_REVIEW | G5_EMERGENCY_REVIEW
    approved: bool         # 是否批准执行出场
    action: str            # "exit" | "observe" | "block" | "confirm" | "pass"
    reason: str            # 人类可读的决策原因
    exit_pct: float        # 出场比例（0-100），仅 approved=True 时有效
    tier: str              # 触发档位 P0-P6（对应7条出场路径）
    override_thresh: float | None  # 临时阈值（仅自学习收紧场景）
    blocked_reason: str | None     # 被拦截原因
    trend_continuation_prob: float  # 趋势延续概率（0-100%）
    score: int             # 综合评分（0-100）
    feishu_msg: str        # 飞书通知内容
```

### 5.2 裁决 → 执行映射表

| verdict | approved | action | exit_pct | 飞书通知 |
|---------|----------|--------|----------|---------|
| G1_HOLD | False | pass | 0% | 无 |
| G2_WATCH | False | observe | 0% | 有（观察记录） |
| G3_PARTIAL_EXIT | True | exit | 20-60% | 有（建议） |
| G4_FULL_EXIT_REVIEW | False | confirm | 100% | 有（需确认） |
| G5_EMERGENCY_REVIEW | True | exit | 100% | 有（已执行） |

### 5.3 action 枚举说明

| action | 含义 | 下一步 |
|--------|------|--------|
| exit | 批准执行出场 | 执行出场并记录日志 |
| observe | 观察（不出场） | 记录当前状态，等待下一周期 |
| block | 拦截（被门控阻止） | 清除临时阈值，触发观察期 |
| confirm | 需要人工确认 | 推送飞书，等待用户回复 |
| pass | 无触发 | 不做任何动作 |

### 5.4 tier 档位编码

| tier | 对应路径 | 优先级 |
|------|---------|--------|
| P0_EMERGENCY | 舆情猎杀 | 最高 |
| P1_ATR | ATR动态止损 | 高 |
| P2_SELF_LEARNING | 自学习防御（方向错误率>50%） | 高 |
| P3_L1_PROFIT | L1盈利分批 | 中 |
| P4_L5_DYNAMIC | L5动态止盈 | 中 |
| P5_L2_SR | L2时线止盈 | 中低 |
| P6_PEAK_DRAWDOWN | 峰值回撤保护 | 低 |
| OBSERVATION | 观察期 | 特殊 |
| AUTO_TIGHTEN_BLOCKED | 自学习收紧被拦截 | 特殊 |
| FORCE_EXIT | 手动平仓 | 特殊 |
| NONE | 无触发 | - |

### 5.5 日志规范

```
[ExitDecisionGate] BTC/USDT LONG pnl=18.5% score=65 trend=71.2%
  → G3_PARTIAL_EXIT | approved=True | action=exit | exit_pct=40% | tier=P4_L5_DYNAMIC
  → reason: normal_evaluation (score=65, trend_prob=71.2%)

[ExitDecisionGate] DOGE/USDT LONG pnl=6.5% consec_losses=2
  → G4_FULL_EXIT_REVIEW | approved=False | action=block | exit_pct=0%
  → reason: consecutive_losses=2 >= 2, tighten_request_requires_manual_confirm
  → blocked: auto_tighten_blocked_require_observation

[ExitDecisionGate] SOL/USDT LONG pnl=12.3% in_observation=True remaining=18.5h
  → G2_WATCH | approved=False | action=observe | exit_pct=0% | tier=OBSERVATION
  → blocked: auto_profit_tighten_blocked_in_observation
```

---

## 六、与现有模块的集成

### 6.1 全局变量声明位置

```python
# v65_autopilot.py 约 1520 行（与 _temp_thresh_override 相邻）
_post_exit_continuation: dict = {}  # pair → PostExitContinuation
```

### 6.2 check_exit_conditions() 中的调用

```python
# 替换 v65_autopilot.py:4670-4675
gate = ExitDecisionGate()
gate_result = gate.evaluate(
    position={"pair": pair, "direction": direction,
              "profit_pct": profit_pct, "leverage": leverage},
    m1_payload=None, l5_payload=None
)

# blocked/observe → 清除待下发阈值，观察期保护生效
if gate_result.action in ("block", "observe"):
    _temp_thresh_override.pop(base, None)
    _log(f"[Gate] AUTO-TIGHTEN BLOCKED: {gate_result.blocked_reason}")
```

### 6.3 L5 动态止盈中的调用

```python
# 在 L5 止盈检测（4736行）前调用
l5_payload = {...}  # 构建L5 payload
gate = ExitDecisionGate()
gate_result = gate.evaluate(position, m1_payload=None, l5_payload=l5_payload)

if gate_result.approved and gate_result.action == "exit":
    _execute_partial_exit(trade_id, gate_result.exit_pct)
elif gate_result.verdict in ("G4_FULL_EXIT_REVIEW", "G5_EMERGENCY_REVIEW"):
    _send_feishu_confirm(trade_id, gate_result.feishu_msg)
```

### 6.4 ATR止损中的集成

```python
# ATR止损不受 ExitDecisionGate 限制（硬风控）
# 但应在执行后记录状态
atr_stop = position.get("atr_stop_price", None)
if atr_stop and direction == "LONG" and current_price <= atr_stop:
    _log(f"[ATR止损] {pair} 触及ATR止损线，立即全平（不经过Gate）")
    rpc._rpc_force_exit(str(trade_id), ordertype="market")
```

---

## 七、验证检查清单

- [ ] `_post_exit_continuation` 全局变量已声明
- [ ] `ExitDecisionGate` 类已完整实现（含5档裁决、7条规则）
- [ ] 原 4670-4675 行已被门控调用替换
- [ ] 连续亏损 >= 2 时，`_temp_thresh_override[base]` 不再被写入
- [ ] 观察期激活后，`_post_exit_continuation[pair]` 状态正确
- [ ] 规则P1/P2/P3 不受观察期限制（仅自学习收紧被禁止）
- [ ] L5 P3 全平进入 G4/G5 复核流程
- [ ] S/R exit 单独触发只建议 G3 部分止盈，不触发全平
- [ ] force_exit 触发飞书确认流程
- [ ] ATR止损硬风控不经过门控
- [ ] `trend_continuation_prob` 计算包含 M1+M2+M3+M4 四维评分
- [ ] `score` 评分包含 M1+M2+M3+M4 四维评分（各25分满分）
