# M1-M5 到交易机器人字段映射表
**Version:** 1.0 | **Date:** 2026-05-04 | **Status:** DRAFT - Pending GPT Review
**Author:** 户部代理 | **Scope:** Tianlu V6.5 M1-M5 Evidence Layer to Bot Parameter Interface

---

## 1. 概述

本文档定义 M1-M5 五个证据层到交易机器人（Freqtrade overlay config / api_autopilot / risk_engine）的完整字段映射表。

**设计原则：**
- 所有字段只读，不触发交易所 API 交易操作
- 字段名遵循 `snake_case` 命名规范
- 取值范围明确，类型安全
- 向后兼容：新增字段不影响已有数据流

---

## 2. 映射总览

```
M1 资金流裁决 ──────→ bot.fund_flow_signal / api_autopilot.entry_gate
M2 支撑压力 ────────→ bot.sr_zone / api_autopilot.entry_confirmation
M3 巨量K线 ─────────→ bot.whale_signal / api_autopilot.entry_refinement
M4 技术面 ──────────→ bot.technical_filter / api_autopilot.exit_trigger
M5/L5 进化层 ───────→ bot.evolution_state / risk_engine.post_entry_gaurd
```

---

## 3. M1 资金流字段（M 层核心）

**来源文件：** `api_m1.py` → `calc_fund_flow_for_pair()` / `compute_trust_grade()`
**数据层：** 三所（Gate / OKX / Binance）永续合约资金流聚合

### 3.1 信任裁决字段

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `m1_signal_trust_level` | string | `A` / `B` / `C` / `D` / `E` | 信号信任等级五档制，A最高E最低，D/E强制禁止入场 | M1 |
| `flow_consensus_score` | float | 0.0 - 1.0 | 三所方向一致率：`agreeing_exchanges / total_non_neutral_exchanges` | M1 |
| `flow_divergence_score` | float | 0.0 - 1.0 | 三所分歧度：`1 - flow_consensus_score`，高值表示方向冲突 | M1 |
| `exchange_outlier` | string \| null | `gate` / `okx` / `bnb` / `null` | 唯一与多数方向冲突的交易所，`null` 表示无异常 | M1 |
| `dominant_exchange` | string \| null | `gate` / `okx` / `bnb` / `null` | 量比最高的主导交易所，用于单所拉偏判断 | M1 |
| `data_freshness_score` | float | 0.0 - 1.0 | 数据新鲜度：`max(0, 1 - age_sec / 600)`，低于 0.7 禁止入场 | M1 |
| `source_count` | int | 0 - 3 | 返回非空数据的交易所数量 | M1 |
| `valid_exchange_count` | int | 0 - 3 | 信号方向与聚合信号一致的交易所数量 | M1 |

### 3.2 信任标志字段

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `trust_flags` | list[string] | 见下方 | 诊断性标签数组，触发对应保护逻辑 | M1 |
| `book_taker_alignment` | float | -1.0 - 1.0 | 订单簿深度与 Taker 方向对齐度，正=做多主导，负=做空主导 | M1 |
| `taker_oi_alignment` | float | -1.0 - 1.0 | Taker 方向与持仓量变化对齐度 | M1 |
| `funding_pressure_state` | string | `POSITIVE` / `NEGATIVE` / `NEUTRAL` | 资金费率压力状态（从 OKX / Binance funding_rate 推断） | M1 |
| `trust_flags` 枚举值 | 说明 | 触发条件 |
| `NO_DATA` | 无有效数据 | `valid_count == 0` |
| `SINGLE_EXCHANGE` | 仅单所有效 | `valid_count == 1` |
| `SPLIT_HIGH` | 高度分歧 | `divergence >= 0.5` |
| `OUTLIER_GATE` | Gate 数据异常 | Gate 方向与聚合信号冲突 |
| `OUTLIER_OKX` | OKX 数据异常 | OKX 方向与聚合信号冲突 |
| `OUTLIER_BNB` | Binance 数据异常 | BNB 方向与聚合信号冲突 |
| `V2_SHADOW_STALE` | V2 Shadow 数据陈旧 | V2 shadow DB 超过 10 分钟未更新 |
| `V2_SHADOW_MISSING` | V2 Shadow 数据库缺失 | V2 shadow DB 不存在 |
| `GATE_SPOT_MODE` | Gate 使用现货数据 | `collector_gate.py` 误用 `defaultType="spot"` |
| `OKX_KEY_MISSING` | OKX API Key 未配置 | `_M1_OKX_KEYS` 池为空 |

### 3.3 M1 → Bot 参数注入

```python
# 示例：api_autopilot.py 消费 M1 evidence
evidence = calc_fund_flow_for_pair(pair, tf="15m").get("evidence", {})

trust_level = evidence.get("m1_signal_trust_level", "C")
freshness   = evidence.get("data_freshness_score", 1.0)
consensus   = evidence.get("flow_consensus_score", 0.0)
outlier     = evidence.get("exchange_outlier")
flags       = evidence.get("trust_flags", [])

# 入场拦截门
if freshness < 0.7:
    return {"action": "BLOCK", "reason": "M1_STALE_DATA"}
if trust_level in ("D", "E"):
    return {"action": "BLOCK", "reason": f"M1_TRUST_LEVEL_{trust_level}"}
if consensus < 0.4:
    return {"action": "BLOCK", "reason": "M1_EXTREME_DIVERGENCE"}
if outlier and outlier == evidence.get("dominant_exchange"):
    # 主导交易所异常，降权 30%
    entry_weight *= 0.3
```

---

## 4. M2 支撑压力字段

**来源文件：** `m4_m5_shadow_lab.py` / `console_server.py` 支撑压力计算
**数据层：** 近期高低点 + 订单簿深度 + 成交量分布

### 4.1 M2 字段定义

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `nearest_support` | float | >= 0 | 最近支撑位价格（USDT） | M2 |
| `nearest_resistance` | float | >= 0 | 最近阻力位价格（USDT） | M2 |
| `support_distance_pct` | float | 0.0 - 100.0 | 当前价格到支撑位的距离百分比 | M2 |
| `resistance_distance_pct` | float | 0.0 - 100.0 | 当前价格到阻力位的距离百分比 | M2 |
| `sr_touch_count` | int | >= 0 | 该支撑/压力位被触及次数（用于判断质量） | M2 |
| `sr_quality_score` | float | 0.0 - 1.0 | 支撑压力位质量分：触及次数越多/成交量越大越可信 | M2 |
| `false_breakout_risk` | float | 0.0 - 1.0 | 假突破风险（触及次数多+成交量萎缩=高风险） | M2 |
| `structure_alignment` | string | `BULLISH` / `BEARISH` / `NEUTRAL` | 价格结构与 M1 信号的对齐方向 | M2 |

### 4.2 M2 → Bot 参数注入

```python
# V6.5 入场规则：价格需在支撑位 ±1% 范围内，且 sr_touch_count >= 3
sr_evidence = get_m2_sr_evidence(pair)

in_support_zone = abs(current_price - sr_evidence["nearest_support"]) / current_price <= 0.01
high_quality_sr = sr_evidence["sr_touch_count"] >= 3
low_false_breakout = sr_evidence["false_breakout_risk"] < 0.5

if not (in_support_zone and high_quality_sr):
    return {"action": "BLOCK", "reason": "M2_SR_ZONE_NOT_HIT"}
```

---

## 5. M3 巨量K线字段

**来源文件：** `m4_m5_shadow_lab.py` 巨量K线检测逻辑
**数据层：** 成交量突增超过历史均值 N 倍的 K 线检测

### 5.1 M3 字段定义

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `giant_candle_direction` | string | `UP` / `DOWN` / `NONE` | 巨量K线方向（UP=大阳线，DOWN=大阴线，NONE=无） | M3 |
| `giant_candle_strength` | float | 0.0 - 1.0 | 巨量K线强度：实体比例 + 成交量倍数 | M3 |
| `volume_ratio` | float | >= 0 | 当根K线成交量 / 过去 N 根均值（量比） | M3 |
| `after_giant_confirm_bars` | int | >= 0 | 巨量K线后连续同向 K 线数量（确认计数） | M3 |
| `reversal_probability` | float | 0.0 - 1.0 | 巨量K线后反转概率（高量比+长影线=高反转风险） | M3 |
| `continuation_probability` | float | 0.0 - 1.0 | 巨量K线后延续概率（高量比+短影线+方向确认=高延续） | M3 |
| `fake_reversal_risk` | float | 0.0 - 1.0 | 假反转风险（M3量比>=5x但M1分歧>=0.5=高风险） | M3 |

### 5.2 M3 裁决逻辑

```python
# 巨量K线入场标准（L1 量比修正为 5.0x，非 2.5x）
if m3["volume_ratio"] >= 5.0:
    if m3["giant_candle_direction"] == "UP" and m1["signal"] == "LONG":
        return {"action": "APPROVE", "confidence": m3["continuation_probability"] * 0.8}
    if m3["giant_candle_direction"] == "DOWN" and m1["signal"] == "SHORT":
        return {"action": "APPROVE", "confidence": m3["continuation_probability"] * 0.8}
    if m3["reversal_probability"] >= 0.6:
        return {"action": "BLOCK", "reason": "M3_HIGH_REVERSAL_RISK"}
    if m3["fake_reversal_risk"] >= 0.5:
        return {"action": "WATCH", "reason": "M3_FAKE_REVERSAL_SUSPECTED"}
```

---

## 6. M4 技术面字段

**来源文件：** `m4_m5_shadow_lab.py` / `console_server.py` 技术指标计算
**数据层：** MACD / RSI / ATR / 布林带 / 多时线对齐

### 6.1 M4 字段定义

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `trend_direction` | string | `UP` / `DOWN` / `NEUTRAL` | 主趋势方向（EMA/均线族判定） | M4 |
| `macd_state` | string | `BULLISH` / `BEARISH` / `NEUTRAL` | MACD 状态（macd_line vs signal_line 交叉） | M4 |
| `rsi_state` | string | `OVERBOUGHT` / `OVERSOLD` / `NEUTRAL` | RSI-14 状态，>70 超买，<30 超卖 | M4 |
| `atr_state` | string | `HIGH_VOL` / `NORMAL_VOL` / `LOW_VOL` | ATR 波动率状态（相对历史均值） | M4 |
| `volatility_state` | string | `EXPANDING` / `CONTRACTING` / `STABLE` | 波动率变化方向（布林带宽度） | M4 |
| `multi_tf_alignment` | float | 0.0 - 1.0 | 多时线（15m/1h/4h/1d）对齐度，全部同向=1.0 | M4 |
| `technical_score` | float | 0.0 - 1.0 | 技术面综合分（各指标加权：趋势40%+MACD25%+RSI20%+ATR15%） | M4 |

### 6.2 M4 → Bot 参数注入

```python
# 技术面对齐检查
if m4["multi_tf_alignment"] >= 0.75:
    if m4["technical_score"] >= 0.6:
        entry_weight *= 1.2   # 技术面确认，增强权重
elif m4["technical_score"] < 0.4:
    entry_weight *= 0.7       # 技术面分歧，降低权重

# ATR 止损设置（由出山AI处理）
# bot overlay: stop_loss = current_price - 2 * atr_14
```

---

## 7. M5/L5 进化层字段

**来源文件：** `l5_evolution_lab/` 进化实验室
**数据层：** 历史表现统计 / 影子规则 / 候选参数回测结果

> **注意：** L5（Level 5）为本系统中进化层的正式编号，M5（Module 5）为架构命名，两者等价。本文档统一使用 **L5**。

### 7.1 L5 字段定义

| 字段名 | 类型 | 取值范围 | 说明 | 来源 |
|--------|------|---------|------|------|
| `shadow_rule_id` | string \| null | UUID / `null` | 当前命中的影子规则 ID（`l5_shadow_rules` 表主键） | L5 |
| `candidate_param_id` | string \| null | UUID / `null` | 候选参数组 ID（`l5_candidate_params` 表主键） | L5 |
| `entry_noise_score` | float | 0.0 - 1.0 | 入场噪音评分（历史假突破率统计），越高=越容易触发错误入场 | L5 |
| `exit_noise_score` | float | 0.0 - 1.0 | 出场噪音评分（过早/过晚出场比例），越高=出场信号越不可靠 | L5 |
| `post_exit_continuation_loss` | float | 0.0 - 1.0 | 出场后趋势延续损失率（出场后 N 根K线内反向移动的比例） | L5 |
| `missed_profit_after_exit` | float | 0.0 - 1.0 | 出场后错过利润比例（出场过早导致踏空的比例） | L5 |
| `promotion_gate_state` | string | `OPEN` / `CLOSED` / `PENDING` | 规则晋升门状态：`OPEN`=可执行，`CLOSED`=禁止，`PENDING`=待确认 | L5 |
| `manual_confirm_required` | bool | `true` / `false` | 是否需要人工二次确认（L5 低置信时触发） | L5 |
| `rule_age_bars` | int | >= 0 | 影子规则存活K线数（<60 根=新规则，降权） | L5 |
| `win_rate_historical` | float | 0.0 - 1.0 | 该影子规则历史胜率（历史样本） | L5 |
| `profit_factor_historical` | float | >= 0 | 该影子规则历史盈亏比 | L5 |

### 7.2 L5 → Bot 参数注入

```python
# L5 进化裁决
l5 = get_l5_evolution_state(pair)

if l5["manual_confirm_required"]:
    return {"action": "PENDING_MANUAL", "reason": "L5_LOW_CONFIDENCE"}
if l5["promotion_gate_state"] == "CLOSED":
    return {"action": "BLOCK", "reason": "L5_GATE_CLOSED"}
if l5["promotion_gate_state"] == "PENDING":
    return {"action": "WATCH", "reason": "L5_GATE_PENDING"}

# 噪音惩罚
entry_weight *= (1.0 - l5["entry_noise_score"] * 0.3)

# 规则成熟度降权（新规则 age_bars < 60）
if l5["rule_age_bars"] < 60:
    entry_weight *= 0.7
```

---

## 8. 统一证据 Payload（完整 JSON Schema）

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Tianlu V6.5 M1-M5 Evidence Payload",
  "version": "6.5.1",
  "type": "object",
  "properties": {
    "pair":            { "type": "string" },
    "ts":              { "type": "integer" },
    "cached_at":       { "type": "string", "format": "date-time" },

    "gate":            { "$ref": "#/definitions/exchange_data" },
    "okx":             { "$ref": "#/definitions/exchange_data" },
    "bnb":             { "$ref": "#/definitions/exchange_data" },

    "aggregated": {
      "type": "object",
      "properties": {
        "ratio":       { "type": "number" },
        "netflow":     { "type": "number" },
        "score":       { "type": "number" },
        "signal":      { "type": "string", "enum": ["LONG","SHORT","NEUTRAL"] },
        "valid_count": { "type": "integer", "minimum": 0, "maximum": 3 }
      }
    },

    "evidence": {
      "type": "object",
      "properties": {
        "m1_signal_trust_level":  { "type": "string", "enum": ["A","B","C","D","E"] },
        "flow_consensus_score":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "flow_divergence_score":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "exchange_outlier":        { "type": ["string","null"], "enum": ["gate","okx","bnb",null] },
        "dominant_exchange":       { "type": ["string","null"], "enum": ["gate","okx","bnb",null] },
        "data_freshness_score":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "source_count":           { "type": "integer", "minimum": 0, "maximum": 3 },
        "valid_exchange_count":   { "type": "integer", "minimum": 0, "maximum": 3 },
        "book_taker_alignment":   { "type": "number", "minimum": -1.0, "maximum": 1.0 },
        "taker_oi_alignment":     { "type": "number", "minimum": -1.0, "maximum": 1.0 },
        "funding_pressure_state": { "type": "string", "enum": ["POSITIVE","NEGATIVE","NEUTRAL"] },
        "trust_flags":            { "type": "array", "items": { "type": "string" } },
        "computed_at":            { "type": "string", "format": "date-time" }
      }
    },

    "m2_support_resistance": {
      "nearest_support":         { "type": "number" },
      "nearest_resistance":      { "type": "number" },
      "support_distance_pct":   { "type": "number" },
      "resistance_distance_pct":{ "type": "number" },
      "sr_touch_count":         { "type": "integer" },
      "sr_quality_score":        { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "false_breakout_risk":     { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "structure_alignment":     { "type": "string", "enum": ["BULLISH","BEARISH","NEUTRAL"] }
    },

    "m3_giant_candle": {
      "giant_candle_direction":  { "type": "string", "enum": ["UP","DOWN","NONE"] },
      "giant_candle_strength":   { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "volume_ratio":            { "type": "number" },
      "after_giant_confirm_bars":{ "type": "integer" },
      "reversal_probability":    { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "continuation_probability":{ "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "fake_reversal_risk":      { "type": "number", "minimum": 0.0, "maximum": 1.0 }
    },

    "m4_technical": {
      "trend_direction":         { "type": "string", "enum": ["UP","DOWN","NEUTRAL"] },
      "macd_state":              { "type": "string", "enum": ["BULLISH","BEARISH","NEUTRAL"] },
      "rsi_state":               { "type": "string", "enum": ["OVERBOUGHT","OVERSOLD","NEUTRAL"] },
      "atr_state":               { "type": "string", "enum": ["HIGH_VOL","NORMAL_VOL","LOW_VOL"] },
      "volatility_state":        { "type": "string", "enum": ["EXPANDING","CONTRACTING","STABLE"] },
      "multi_tf_alignment":      { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "technical_score":         { "type": "number", "minimum": 0.0, "maximum": 1.0 }
    },

    "l5_evolution": {
      "shadow_rule_id":           { "type": ["string","null"] },
      "candidate_param_id":       { "type": ["string","null"] },
      "entry_noise_score":        { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "exit_noise_score":         { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "post_exit_continuation_loss": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "missed_profit_after_exit": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "promotion_gate_state":     { "type": "string", "enum": ["OPEN","CLOSED","PENDING"] },
      "manual_confirm_required":  { "type": "boolean" },
      "rule_age_bars":           { "type": "integer" },
      "win_rate_historical":      { "type": "number", "minimum": 0.0, "maximum": 1.0 },
      "profit_factor_historical": { "type": "number" }
    },

    "v2_shadow": {
      "db_path":             { "type": "string" },
      "status":              { "type": "string", "enum": ["LIVE","STALE","MISSING"] },
      "last_snap_ts":        { "type": ["integer","null"] },
      "last_snap_age_sec":   { "type": ["integer","null"] },
      "snapshots_count":     { "type": "integer" }
    }
  },
  "definitions": {
    "exchange_data": {
      "type": ["object","null"],
      "properties": {
        "ratio":        { "type": "number" },
        "netflow":      { "type": "number" },
        "whale_ratio":  { "type": "number" },
        "vol":          { "type": "number" },
        "score":        { "type": "number" },
        "signal":       { "type": "string", "enum": ["LONG","SHORT","NEUTRAL"] }
      }
    }
  }
}
```

---

## 9. 层级优先级矩阵

| 场景 | M1 优先级 | M2 优先级 | M3 优先级 | M4 优先级 | L5 优先级 |
|------|----------|----------|----------|----------|----------|
| 入场确认 | **最高**（一票拦截） | 高（支撑验证） | 中（量能确认） | 中（趋势对齐） | 低（噪音过滤） |
| 出场触发 | 低 | 低 | 中 | **最高**（技术面主导） | 中（进化修正） |
| 回撤保护 | 高（资金流反转） | 低 | 低 | 中（RSI超买） | **最高**（出山AI） |
| 反转猎杀 | **最高**（M1做空信号） | 中 | 高（巨量阴线） | 中 | 中 |

---

## 10. 已知限制与数据缺失

| 限制项 | 受影响字段 | 当前处理方式 |
|--------|----------|------------|
| Binance `netflow = 0`（无法从公开数据估算） | `bnb.netflow`, `aggregated.netflow` 偏低 | `trust_flags += ["BINANCE_SHADOW_STALE"]`，降权 BNB |
| V2 Shadow 数据库停更（5月2日后无数据） | `v2_shadow.status = "STALE"` | 新鲜度降级，不阻塞入场 |
| `collector_gate.py` `defaultType="spot"` | 若旧采集器被调用，读到现货数据 | `trust_flags += ["GATE_SPOT_MODE"]` |
| OKX API Key 池为空 | `okx` 数据全部 `null` | `trust_flags += ["OKX_KEY_MISSING"]` |
| L5 影子规则数据库未建立 | 所有 `l5_evolution_*` 字段为默认值 | 降权执行，依赖 M1-M4 裁决 |
