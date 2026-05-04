# 02_M1_M5_EVIDENCE_API_DRAFT.md
# M1-M5 Evidence 统一接口草案

## 概述

每个 evidence 接口包含：
- **数据来源**：从哪里读（现有代码位置）
- **payload JSON 格式**：返回字段说明
- **API 端点**：console_server.py 中的现有接口或新建

所有接口均为**只读**（read-only），不得修改任何机器人参数。

---

## M1 Evidence（资金流）

### 数据来源
- 现有API：`console_server.py:26832` `/api/m1/hero_card`
- 数据源：`console_server.py` 内部 `_MTF_CACHE`（内存缓存，与天眼AI/ExitAI同一数据源）
- 读取函数：`console_server.py:26843` `_get_mtf_cache()`

### Payload JSON

```json
{
  "ok": true,
  "ts": 1746345600,
  "primary_tf": "15m",
  "timeframe_policy": "15m_primary_mtf_confirmation",
  "pairs": {
    "btc": {
      "pair": "BTC/USDT",
      "pair_id": "btc",
      "ts": 1746345600,
      "ratio": 5.234,           // 15m量比（15m为主时线）
      "netflow": 1234567.89,    // 15m净流入（USD）
      "score": 85,
      "signal": "LONG",         // LONG / SHORT / NEUTRAL
      "gate_ratio": 4.5,
      "okx_ratio": 5.8,
      "bnb_ratio": 5.2,
      "valid_count": 3,         // 有效交易所数量（3所交叉）
      "grade": "A",
      "action": "做多",
      "urgency": "HIGH",
      "confidence": 0.88,
      "speech": "三所共振做多信号确认...",
      "cached_at": 1746345600,
      "tf_15m": {
        "ratio": 5.234,
        "netflow": 1234567.89,
        "gate_ratio": 4.5,
        "okx_ratio": 5.8,
        "bnb_ratio": 5.2,
        "signal": "LONG",
        "valid_count": 3
      },
      "tf_1h": {
        "ratio": 3.1,
        "netflow": 8901234.56,
        "gate_ratio": 2.8,
        "okx_ratio": 3.4,
        "bnb_ratio": 3.1,
        "signal": "LONG",
        "valid_count": 3
      },
      "tf_4h": {
        "ratio": 2.2,
        "netflow": 34567890.12,
        "gate_ratio": 2.0,
        "okx_ratio": 2.5,
        "bnb_ratio": 2.1,
        "signal": "LONG",
        "valid_count": 3
      },
      "data_status": "live",
      "data_source": "m1_mtf_cache"
    }
  }
}
```

### API 端点（现有）

```python
# console_server.py:26832-26905（已存在，无需新建）
@app.route("/api/m1/hero_card")
def api_m1_hero_card():
    """M1英雄卡只读端点（读取共享内存缓存_MTF_CACHE，毫秒响应）"""
    # GET /api/m1/hero_card
    # 返回: 所有交易对的M1资金流数据
    # TTL: 实时更新（_MTF_CACHE 60秒刷新）
```

### TTL 说明
- 缓存刷新：60秒（`console_server.py` 内 `_MTF_CACHE` 自动刷新）
- 建议前端轮询：60秒

---

## M2 Evidence（S/R 支撑/压力位）

### 数据来源
- 现有API：`console_server.py:25692` `/api/bt2/sr_levels`
- 数据源：三所交叉 S/R 计算结果（`m2_sr_enhanced.py` 或 `_normalize_m2_pair()`）
- 读取函数：`console_server.py:25323` `_normalize_m2_pair()`

### Payload JSON

```json
{
  "ok": true,
  "pairs": {
    "BTC/USDT": {
      "pair": "BTC/USDT",
      "support": {
        "price": 95234.56,         // 支撑位价格
        "touches": 4,              // 触底次数（≥3才有效）
        "strength": 0.85,          // 强度 0-1
        "source": "triple_exchange",
        "dist_to_price": -0.45     // 当前价距支撑位百分比（负数=在支撑上方）
      },
      "resistance": {
        "price": 97890.12,
        "touches": 3,
        "strength": 0.72,
        "source": "triple_exchange",
        "dist_to_price": 2.34      // 当前价距压力位百分比
      },
      "has_sr": true,
      "sr_type": "support",        // 当前主要S/R: support / resistance
      "sr_price": 95234.56,
      "sr_touches": 4,
      "data_source": "m2_triple_exchange"
    }
  }
}
```

### API 端点（现有）

```python
# console_server.py:25692-25750（已存在）
@app.route("/api/bt2/sr_levels")
def api_bt2_sr_levels_default():
    """返回S/R Levels数据（三所交叉验证）"""
    # GET /api/bt2/sr_levels?pair=BTC/USDT
    # TTL: 5分钟（S/R Levels变化不频繁）
```

### TTL 说明
- S/R 变化频率：低（通常几分钟~几十分钟变化一次）
- 建议缓存：5分钟
- 重要：入场评估时需**实时**读取最新S/R

---

## M3 Evidence（波动率：ATR + GIANT K线）

### 数据来源
- 数据源：`v65_autopilot.py:3093` `_get_capital_flow()` 的返回值
- 备选：`console_server.py` 内 OHLCV 计算逻辑
- 计算：需要 ATR(14) 和 GIANT K线识别

### Payload JSON（草案）

```json
{
  "pair": "BTC/USDT",
  "ts": 1746345600,
  "atr_15m": 45.67,           // ATR(14) on 15m
  "atr_1h": 98.23,            // ATR(14) on 1h
  "atr_4h": 234.56,           // ATR(14) on 4h
  "giant_count": 2,            // GIANT阳/阴K线数量（最近20根）
  "squeeze_count": 1,          // SQZ压缩次数
  "volatility_level": "HIGH",  // LOW / MEDIUM / HIGH
  "atr_percentile": 0.78,      // ATR在历史分位数
  "m3_verdict": "EXECUTE_LONG", // 自适应置信度算法输出
  "m3_confidence": 0.85,
  "data_source": "ohlcv_calculated"
}
```

### API 端点（新建草案）

```python
# console_server.py（新建端点，草案）
@app.route("/api/m3/evidence", methods=["GET"])
def api_m3_evidence():
    """
    M3波动率Evidence只读端点（草案）
    GET /api/m3/evidence?pair=BTC/USDT

    返回: ATR + GIANT K线 + 波动率
    TTL: 60秒（与M1同步刷新）
    """
    pair = request.args.get("pair", "BTC/USDT")
    # TODO: 实现ATR计算和GIANT K线识别
    # 数据来源可复用 console_server.py 内的 OHLCV 计算
    return jsonify({...})
```

### TTL 说明
- 建议刷新：60秒
- ATR为滞后指标，无需高频刷新

---

## M4 Evidence（技术指标：RSI / OBV / OI）

### 数据来源
- RSI：`console_server.py` 内 RSI 计算（`ta-lib` 或 pandas）
- OI（持仓量）：`_get_m1_m4_data_flow_cached()` 或 `_build_live_ff_for_ai()`
- OBV：需新增计算逻辑

### Payload JSON（草案）

```json
{
  "pair": "BTC/USDT",
  "ts": 1746345600,
  "rsi_15m": 68.5,
  "rsi_1h": 62.3,
  "rsi_4h": 71.8,
  "obv_15m": 123456789.0,
  "obv_trend": "LONG",         // OBV趋势方向
  "oi_current": 1234567890.0, // 持仓量（USD）
  "oi_change_pct": 5.2,       // OI变化百分比
  "oi_signal": "INCREASING",  // INCREASING / DECREASING / STABLE
  "m4_verdict": "OBSERVE",
  "m4_confidence": 0.65,
  "urgency": "MEDIUM",
  "data_source": "technical_indicators"
}
```

### API 端点（新建草案）

```python
# console_server.py（新建端点，草案）
@app.route("/api/m4/evidence", methods=["GET"])
def api_m4_evidence():
    """
    M4技术指标Evidence只读端点（草案）
    GET /api/m4/evidence?pair=BTC/USDT

    返回: RSI + OBV + OI
    TTL: 60秒
    """
    pair = request.args.get("pair", "BTC/USDT")
    # TODO: 实现RSI/OBV/OI计算
    return jsonify({...})
```

---

## M5 / L5 Evidence（场景：市场微结构）

### 数据来源
- 场景类型：`_normalize_m2_payload()` 中的 `scene_type`
- DOT黑名单：`console_server.py:12512` `_get_dot_blacklist_level()`
- 爆仓流：`console_server.py` 内的 `_LIQUIDATION_DATA`
- 点差/订单薄：需对接现有L5模块

### Payload JSON（草案）

```json
{
  "pair": "BTC/USDT",
  "ts": 1746345600,
  "scene_type": "BREAKOUT",    // BREAKOUT / RANGE / REVERSAL / NEUTRAL
  "trend_direction": "LONG",   // 趋势方向
  "dot_blacklist_level": 0,     // DOT黑名单等级（0-3）
  "spread_bps": 2.5,           // 点差（基点）
  "liquidation_wave": "LONG",  // 爆仓流方向
  "liquidation_intensity": 0.3, // 爆仓强度 0-1
  "fear_greed": 65,            // 恐惧贪婪指数（0-100）
  "oi_coverage": 0.8,          // OI覆盖率
  "l5_verdict": "PASS",        // PASS / DOWNGRADE / FORBIDDEN
  "l5_confidence": 0.70,
  "data_gaps": [],             // 数据缺失字段
  "data_source": "l5_scene_module"
}
```

### API 端点（新建草案）

```python
# console_server.py（新建端点，草案）
@app.route("/api/l5/evidence", methods=["GET"])
def api_l5_evidence():
    """
    L5场景Evidence只读端点（草案）
    GET /api/l5/evidence?pair=BTC/USDT

    返回: 场景分类 + 爆仓流 + 点差 + DOT黑名单
    TTL: 60秒
    """
    pair = request.args.get("pair", "BTC/USDT")
    # TODO: 对接现有L5模块
    return jsonify({...})
```

---

## Evidence 汇总 API（草案）

```python
# console_server.py（新建汇总端点，草案）
@app.route("/api/evidence/all", methods=["GET"])
def api_evidence_all():
    """
    M1-M5 Evidence汇总只读端点（草案）
    GET /api/evidence/all?pair=BTC/USDT

    返回: {m1, m2, m3, m4, m5} 全部evidence
    TTL: 60秒

    用途: EntryDecisionGate 一次性获取所有evidence
    """
    pair = request.args.get("pair", "BTC/USDT")
    # 调用各evidence收集函数
    m1 = get_m1_evidence(pair)  # 复用 /api/m1/hero_card
    m2 = get_m2_sr_evidence(pair, direction, current_price)
    m3 = get_m3_evidence(pair)
    m4 = get_m4_evidence(pair)
    m5 = get_l5_evidence(pair)
    return jsonify({
        "ok": True,
        "pair": pair,
        "ts": int(time.time()),
        "m1": m1,
        "m2": m2,
        "m3": m3,
        "m4": m4,
        "m5": m5
    })
```

---

## TTL 汇总表

| Evidence | TTL | 刷新方式 |
|----------|-----|---------|
| M1（资金流） | 60秒 | 60秒cron + K线关闭触发 |
| M2（S/R） | 5分钟 | 变化时触发 |
| M3（波动率） | 60秒 | 与M1同步 |
| M4（技术指标） | 60秒 | 实时计算 |
| L5（场景） | 60秒 | 与M1同步 |

---

## 禁止事项

- **禁止**在 evidence API 中修改任何机器人参数
- **禁止**缓存超过TTL的数据
- **禁止**在 evidence 接口中执行交易
