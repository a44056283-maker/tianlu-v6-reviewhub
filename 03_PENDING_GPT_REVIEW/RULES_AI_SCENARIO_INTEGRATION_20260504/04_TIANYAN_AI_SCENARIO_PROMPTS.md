# 天眼AI 完整场景话术与 EntryDecisionGate 裁决指南
> 天眼院代理生成 | 日期: 2026-05-04 | 状态: PENDING REVIEW
> 场景编号: T-01 ~ T-11 | 档位覆盖: A/B/C/D/E + 特殊场景

---

## 场景总览

| 编号 | 场景名称 | Gate档位 | 自动执行 | 需人工确认 | 优先级 |
|------|---------|---------|---------|-----------|--------|
| T-01 | A档可入场（正常场景） | A | ✅ 是 | ❌ 不需要 | — |
| T-02 | B档等待确认 | B | ❌ 否 | ⚠️ 第2轮AI | 高 |
| T-03 | C档噪音禁止 | C | ❌ 否 | ⚠️ Override | 高 |
| T-04 | D档数据不足 | D | ❌ 否 | ⚠️ 数据恢复 | 高 |
| T-05 | E档单所异常 | E | ❌ 否 | ⚠️ 降权重评 | 高 |
| T-06 | DOGE临时冻结 | C | ❌ 否 | ✅ 兵部解冻 | 紧急 |
| T-07 | SOL DCA风险 | C | ❌ 否 | ⚠️ Override | 中 |
| T-08 | M1分歧 | C/B | ❌ 否 | ⚠️ 降权重评 | 高 |
| T-09 | M2位置不佳 | B/C | ❌ 否 | ⚠️ 第2轮确认 | 中 |
| T-10 | M3巨量未确认 | C | ❌ 否 | ⚠️ Override | 高 |
| T-11 | M4趋势不一致 | B/C | ❌ 否 | ⚠️ 第2轮确认 | 中 |

---

## T-01：A档可入场（正常场景）

### 触发条件
- M1 量比 >= 5.0x（三所共振或双所强共振）
- M1 flow_consensus_score >= 0.67
- M2 三验/双验支撑，距支撑 <= 1%
- M3 无反转猎杀，无单所GIANT信号
- M4 RSI 未极端，多周期无衰竭
- 不在 DOGE 冻结期

### 天眼AI话术

```
【✅ A档可入场 — BTC/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 执行做多，Gate立即放行

原因:
  M1三所共振做多，量比5.2x，远超5.0x门槛
  M2三验强支撑90800，距支撑仅0.5%
  M3 GIANT阳线2次，INFLOW流入确认
  M4 RSI=62中性🟡，ATR=3.2%🌬️正常波动
  OI=+6.5%📈机构加仓确认
  DOGE未冻结，无噪音

证据（M1-M5数据）:
  M1: 15m↗️0.85📈5.2x | 1h↗️0.52📈3.1x | 4h↗️0.31📈2.0x
      三所同向做多 | flow_consensus=0.85 | source_count=3
  M2: 三验强支撑90800✅ 紧贴0.5%✅ 触底3次✅
  M3: HIGH3所✅ GIANT阳2次✅ INFLOW流入✅
  M4: RSI=62🟡 | ATR=3.2%🌬️ | OI变化+6.5%📈 | EMA多头排列
  M5: DOGE未冻结✅ 冷却期已过✅

风险评估:
  - ATR止损距7.0%，合理
  - 多头排列健康
  - 无反转猎杀风险
  风险等级: 低

自动执行: ✅ 是（Gate A档，无需人工确认）
人工确认: ❌ 不需要

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: A | 置信度85% | 自动放行
```

### EntryDecisionGate 输出

```json
{
  "verdict": "A",
  "action": "APPROVED",
  "auto_execute": true,
  "confidence": 85,
  "reason": "M1量比5.2x三所共振 + M2三验支撑紧贴0.5% + M3 GIANT阳2次 + M4 RSI中性",
  "gate_passed_rules": ["M1_CONSENSUS_PASS_A", "M2_POSITION_OK", "M3_CONFIRMED", "M4_RSI_OK", "DOGE_CLEAR"],
  "blocked_rules": []
}
```

---

## T-02：B档等待确认

### 触发条件
- M1 量比 >= 3.0x 但 < 5.0x
- M1 flow_consensus_score 在 0.50~0.66 之间
- M2 仅单验支撑
- M4 RSI 偏强/偏弱但未达极端
- 天眼AI第一轮置信度在 50-60% 之间

### 天眼AI话术

```
【⚠️ B档等待确认 — ETH/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 暂缓入场，等待第2轮确认

原因:
  M1量比3.2x，双所共振但Gate量比偏高(4.5x)
  flow_consensus=0.58，弱共识区间
  M2单验支撑，无多所共振
  M4 RSI=68🟠偏强，追高有一定风险
  需要第2轮数据确认信号强度

证据（M1-M5数据）:
  M1: 15m↗️0.52📈3.2x | 1h↗️0.28📈2.1x | 4h↗️0.15📈1.5x
      双所同向 | flow_consensus=0.58(弱) | source_count=2
  M2: 单验支撑2273✅ 距支撑1.2%✅
  M3: HIGH1所⚠️ 无GIANT阳线 | 缩量整理
  M4: RSI=68🟠偏强⚠️ | ATR=3.1%🌬️ | OI变化+2.1%➡️中性
  M5: DOGE未冻结✅

风险评估:
  - M1弱共识，单所量比偏高，分歧度0.45
  - M2单验确认不足
  - RSI偏强，追高风险
  风险等级: 中

自动执行: ❌ 否（Gate B档，需第2轮确认）
人工确认: ⚠️ 第2轮天眼AI确认后决策
轮次状态: 第1轮已记录，等待第2轮（30分钟内）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: B | 置信度55% | 等待第2轮确认
第二轮确认话术: 若30分钟内M1量比仍>=3.0x且方向不变，升级A档执行
```

### EntryDecisionGate 输出

```json
{
  "verdict": "B",
  "action": "OBSERVE",
  "auto_execute": false,
  "confidence": 55,
  "reason": "M1量比3.2x弱共识，需第2轮确认",
  "require_confirm_rounds": 2,
  "round_1_pending": true,
  "round_1_timestamp": 1746332400.0,
  "next_check_in_minutes": 15,
  "gate_passed_rules": ["M1_RATIO_OK", "M2_SOME_VALIDATION"],
  "blocked_rules": ["M1_CONSENSUS_WEAK", "M4_RSI_CONFIRM_NEEDED"]
}
```

---

## T-03：C档噪音禁止

### 触发条件
- M1 flow_divergence_score >= 0.60（单所拉偏严重）
- M1 exchange_outlier 检测到（量比偏离均值>=60%）
- M1 量价背离（放量>=2.0x + 净流出）
- M2 无有效S/R数据（S14场景）
- M2 M1/M2方向背离（S05场景）
- M3 单所单时线GIANT信号
- M3 被动买入/卖出信号
- 同一交易对在冷却期内（止损后4小时内）

### 天眼AI话术

```
【🚫 C档噪音禁止 — SOL/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止任何入场操作

原因:
  M1单所极端信号：Gate量比4.5x，OKX量比1.2x，BNB量比0.9x
  flow_divergence_score=0.80，严重分歧
  Gate被标记为exchange_outlier，偏离均值62%
  单所拉偏噪音，禁止执行

证据（M1-M5数据）:
  M1: Gate↗️0.75📈4.5x❌ | OKX↗️0.15📈1.2x | BNB→0.08📉0.9x
      分歧严重 | flow_divergence=0.80(严重) | source_count=3
      exchange_outlier=Gate❌ | 偏离均值62%❌
  M2: 支撑83.50阻力85.20 | 距支撑2.3% | 无验证❌
  M3: HIGH1所⚠️ GIANT阳1次（单所不足）⚠️
  M4: RSI=72🟠超买⚠️ | ATR=4.1%🌬️ | OI变化-1.2%➡️
  M5: DOGE未冻结✅

风险评估:
  - 单所严重拉偏（Gate量比4.5x vs 其他1.2x/0.9x）
  - flow_divergence=0.80，超出0.60严重分歧阈值
  - RSI超买，追多风险极高
  噪音类型: EXCHANGE_OUTLIER + FLOW_DIVERGENCE_SEVERE
  风险等级: 极高

自动执行: ❌ 否（Gate C档，禁止自动入场）
人工确认: ⚠️ 需人工Override（记录原因）
冷却策略: 4小时后自动重评

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | 噪音禁止
noise_type: EXCHANGE_OUTLIER
cooldown_until: 1746346800.0
```

### EntryDecisionGate 输出

```json
{
  "verdict": "C",
  "action": "REJECTED_NOISE",
  "auto_execute": false,
  "confidence": 0,
  "reason": "M1单所极端量比4.5x + flow_divergence_score=0.80，单所拉偏噪音",
  "noise_type": "EXCHANGE_OUTLIER",
  "cooldown_until": 1746346800.0,
  "gate_passed_rules": [],
  "blocked_rules": ["M1_DIVERGENCE_SEVERE", "M1_OUTLIER_DETECTED", "FLOW_DIVERGENCE_OVER_60"]
}
```

---

## T-04：D档数据不足

### 触发条件
- M1 source_count < 2（仅单所有效数据）
- M1 所有交易所 volume_ratio 均为 0 或 None
- M1 数据新鲜度：最新K线距今 > 5 分钟
- M2 无有效S/R数据（S14场景）
- M4 三所RSI全部缺失

### 天眼AI话术

```
【⏸️ D档数据不足 — BNB/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 暂停入场裁决，等待数据恢复

原因:
  M1仅Gate单所有效数据，OKX数据缺失，BNB数据为0
  source_count=1，不满足最低双所要求
  在OKX/BNB数据恢复前，无法评估三所一致性

证据（M1-M5数据）:
  M1: Gate↗️0.42📈2.1x✅ | OKX❌数据缺失 | BNB→0.0❌无数据
      source_count=1(不足)❌ | 无法计算共识
  M2: 支撑615阻力620 | dual_count=0 | triple_count=0❌
      无有效S/R验证❌
  M3: HIGH=0 | 无GIANT信号 | 数据不完整
  M4: RSI=55🟡 | ATR=2.8%🌬️ | OI数据缺失⚠️
  M5: DOGE未冻结✅

缺失数据源:
  - OKX资金流数据
  - BNB资金流数据
  - M4 OI数据部分缺失

风险评估:
  - 单所数据无法评估共识
  - 无法判断是否为单所拉偏
  - 数据质量不满足入场要求
  风险等级: 未知（数据不足）

自动执行: ❌ 否（Gate D档，数据不足禁止）
人工确认: ⚠️ 数据恢复后自动重评，无需人工
重评触发: OKX/BNB任一数据源恢复后立即重评

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: D | 置信度0% | 数据不足
missing_sources: ["okx", "bnb"]
```

### EntryDecisionGate 输出

```json
{
  "verdict": "D",
  "action": "DATA_INSUFFICIENT",
  "auto_execute": false,
  "confidence": 0,
  "reason": "M1仅Gate单所有效数据，OKX/BNB数据缺失",
  "missing_sources": ["okx", "bnb"],
  "gate_passed_rules": [],
  "blocked_rules": ["M1_SOURCE_COUNT_LOW"]
}
```

---

## T-05：E档单所异常

### 触发条件
- M1 exchange_outlier == True（某所量比偏离均值>=60%）
- M1 dominant_exchange 被标记为异常
- M1 量比极端（>=3.0x）但其他两所 < 1.5x
- M1 双所背离：两所方向相反且分歧度>=0.50

### 天眼AI话术

```
【⚠️ E档单所异常降权 — DOGE/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: Gate降权异常交易所后重评，需人工确认

原因:
  Gate量比4.5x被标记为outlier（偏离均值62%）
  OKX量比1.8x，BNB量比1.5x，双所正常
  降权Gate至0.3后，重新聚合信号：
    聚合量比 = (4.5x*0.3 + 1.8x*1.0 + 1.5x*1.0) / (0.3+1.0+1.0) = 2.0x
  降权后量比2.0x，满足B档条件，需第2轮确认

证据（M1-M5数据）:
  M1: Gate↗️0.68📈4.5x❌(outlier) | OKX↗️0.25📈1.8x✅ | BNB→0.18📈1.5x✅
      anomalous_exchange=Gate❌ | 偏离均值62%❌
      降权后聚合量比=2.0x | 非outlier_count=2
  M2: 支撑0.108阻0.112 | dual_count=2✅ 双验共振✅
      距支撑0.8%✅ 紧贴支撑
  M3: HIGH2所✅ | GIANT阳1次 | INFLOW中性
  M4: RSI=45⚪中性 | ATR=4.5%🌬️ | OI变化+1.5%➡️
  M5: DOGE未冻结✅

降权分析:
  异常交易所: Gate
  降权权重: Gate=0.3, OKX=1.0, BNB=1.0
  降权后聚合量比: 2.0x（B档门槛）
  剩余有效双所: OKX + BNB

风险评估:
  - Gate异常可能为该所局部事件
  - OKX+BNB双所信号可作为参考
  - 降权后量比刚好达B档，需确认
  风险等级: 中

自动执行: ❌ 否（Gate E档，降权重评中）
人工确认: ⚠️ 降权重评结果为B档，需第2轮确认或人工Override

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: E | 置信度40% | 单所异常降权
anomalous_exchange: gate
downweighted_exchanges: {"gate": 0.3, "okx": 1.0, "bnb": 1.0}
reassessed_result: B
```

### EntryDecisionGate 输出

```json
{
  "verdict": "E",
  "action": "EXCHANGE_ANOMALY",
  "auto_execute": false,
  "confidence": 40,
  "reason": "Gate量比4.5x被标记为outlier（偏离均值62%），降权至0.3",
  "anomalous_exchange": "gate",
  "downweighted_exchanges": {"gate": 0.3, "okx": 1.0, "bnb": 1.0},
  "reassessed_with_downweight": true,
  "reassessed_result": "B",
  "gate_passed_rules": [],
  "blocked_rules": ["M1_EXCHANGE_OUTLIER"]
}
```

---

## T-06：DOGE临时冻结

### 触发条件
- 全bot同向信号噪音（>=5个bot同时对DOGE同向入场）
- 批量止损事件（>=5个bot同时止损）
- 兵部人工冻结
- 冷却解除条件：24小时自动到期 或 连续2次盈利主动解除

### 天眼AI话术

```
【🚫 DOGE临时冻结 — DOGE/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止DOGE自动新增入场，Gate强制拦截

原因:
  DOGE/USDT刚刚经历全bot同向做空→批量止损噪音事件
  8个bot在2小时内全部做空DOGE，全部触发止损
  系统判定为"全bot同向信号噪音"，已激活DOGE风险窗口
  DOGE新增入场已冻结24小时

证据（M1-M5数据）:
  M1: 15m↘️-0.52📉3.8x | 1h↘️-0.28📉2.1x | 4h→0.08📉1.2x
      三所做空 | flow_consensus=0.72(强) | source_count=3
      ⚠️ 尽管M1信号强，但DOGE已冻结
  M2: 压力0.1091 | 触顶3次 | 紧贴压力0.3%❌ 禁止追空
  M3: HIGH2所 | GIANT阴1次 | OUTFLOW流出⚠️
  M4: RSI=28🟢超卖 | ATR=5.2%💨高波动 | OI变化-8.5%📉减仓
  M5: DOGE冻结✅❌ 冻结截止2026-05-05 10:17 | 剩余23.2小时❌

冻结事件记录:
  - 触发时间: 2026-05-04 10:17
  - 触发原因: 全bot同向信号噪音（8 bot同时做空批量止损）
  - 冻结时长: 24小时
  - 解除条件: 2026-05-05 10:17自动解除 或 连续2次盈利主动解除

风险评估:
  - DOGE高波动币种，全bot同向风险极高
  - 冻结机制防止噪音重复触发
  - 冻结期结束后需重新评估
  风险等级: 高（历史噪音模式）

自动执行: ❌ 否（DOGE冻结期内禁止所有自动新增）
人工确认: ✅ 兵部可调用unfreeze_doge(pair)人工解除冻结
解除触发: 连续2次盈利自动解除 或 兵部人工解冻

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | DOGE风险窗口内禁止新增
noise_type: DOGE_BATCH_STOP_LOSS
cooldown_until: 1746416220.0
冻结解除倒计时: 23.2小时
```

---

## T-07：SOL DCA风险

### 触发条件
- SOL 处于 DCA 连续加仓中（>=2次DCA）
- M1 量比 < 2.0x 且 RSI >= 65（阴跌信号）
- SOL 在高位（距历史高点 < 5%）
- SOL OI 减仓 >= 10%

### 天眼AI话术

```
【🚫 SOL DCA风险 — SOL/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止SOL自动新增DCA，Gate拦截加仓请求

原因:
  SOL已有2次DCA加仓记录，当前持仓均价82.50
  M1量比1.5x萎缩，净流入0.15（同向微弱）
  RSI=72🟠超买区域，阴跌无量风险
  SOL距历史高点85.20仅差3.2%，高位加仓危险
  OI=-12.3%📉大幅减仓，机构出逃信号

证据（M1-M5数据）:
  M1: 15m→0.12📉1.5x⚠️ | 1h→0.08📉1.2x⚠️ | 4h→0.05📉0.9x⚠️
      萎缩整理 | flow_consensus=0.45(弱) | source_count=2
      ⚠️ DCA追加风险：阴跌无量
  M2: 支撑82.50(持仓均价) | 压力85.20 | 紧贴压力3.2%⚠️
  M3: HIGH1所 | 无GIANT | 缩量整理⚠️
  M4: RSI=72🟠超买⚠️ | ATR=4.2%💨 | OI变化-12.3%📉📉大幅减仓⚠️
      多头衰竭预警: 4H70 + 1H73 + 15m74
  M5: DOGE未冻结✅

DCA风险分析:
  当前DCA层级: L2（已2次加仓）
  持仓均价: 82.50 | 当前价: 82.40 | 浮亏-0.12%
  高位加仓风险: SOL距高点85.20仅差3.2%
  OI大幅减仓: -12.3%，机构出逃信号
  多头衰竭: 4H70 + 1H73 + 15m74，三周期超买

风险评估:
  - SOL高位 + RSI超买 + OI大幅减仓 = 三重危险叠加
  - 继续DCA加仓可能买在顶部
  - 建议：停止DCA，等待回调或止损
  风险等级: 极高

自动执行: ❌ 否（DCA加仓被Gate拦截）
人工确认: ⚠️ 需人工确认是否继续DCA（强烈建议停止）
建议: 停止DCA，等待SOL回调确认后重新评估

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | SOL DCA风险
noise_type: DCA_SOL_HIGH_RISK
blocked_rules: ["DCA_LAYER_2_MAX", "SOL_HIGH_RISK", "M4_BULL_EXHAUST_MULTI_CYCLE"]
```

---

## T-08：M1分歧

### 触发条件
- M1 flow_consensus_score < 0.50（三所方向严重分歧）
- M1 flow_divergence_score >= 0.50（量比分歧度高）
- M1 量价背离：量比>=2.0x + 净流出（或反向）

### 天眼AI话术

```
【🚫 M1分歧 — XRP/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止入场，M1三所严重分歧

原因:
  M1三所方向完全分歧：Gate做多，OKX中性，BNB做空
  flow_consensus=0.33（无共识）
  flow_divergence=0.58（高分歧，Gate量比4.2x vs BNB量比0.8x）
  量价背离：平均量比2.5x但平均净流出-0.35
  噪音信号，禁止执行

证据（M1-M5数据）:
  M1: Gate↗️0.62📈4.2x❌ | OKX→0.05➡️0.9x❌ | BNB↘️-0.45📉0.8x❌
      三所分歧❌ | flow_consensus=0.33(无共识)❌
      flow_divergence=0.58(高分歧)❌
      量价背离: 量比2.5x + 净流出-0.35❌
  M2: 支撑0.52阻0.58 | 距支撑2.1% | 无验证❌
  M3: HIGH=0 | 无信号
  M4: RSI=55⚪中性 | ATR=3.5%🌬️ | OI变化+0.8%➡️
  M5: DOGE未冻结✅

分歧分析:
  Gate: 做多量比4.2x | OKX: 中性量比0.9x | BNB: 做空量比0.8x
  方向共识: 1做多 vs 0中性 vs 1做空 → 无共识
  量比分歧: (4.2-0.8)/4.2 = 0.58 → 高分歧
  量价背离: 放量但净流出，量价矛盾

风险评估:
  - 三所方向完全分歧，无法判断真实趋势
  - 单所Gate量比偏高，可能是该所局部事件
  - 量价背离信号可能是假突破
  噪音类型: M1_NO_CONSENSUS + FLOW_DIVERGENCE_HIGH
  风险等级: 极高

自动执行: ❌ 否（Gate C档，M1严重分歧噪音）
人工确认: ⚠️ 需人工Override并记录原因
冷却策略: 4小时后或分歧消除后重评

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | M1三所严重分歧
noise_type: M1_NO_CONSENSUS + FLOW_DIVERGENCE_HIGH
cooldown_until: 1746346800.0
```

### EntryDecisionGate 输出

```json
{
  "verdict": "C",
  "action": "REJECTED_NOISE",
  "auto_execute": false,
  "confidence": 0,
  "reason": "M1三所严重分歧：flow_consensus=0.33，flow_divergence=0.58，量价背离",
  "noise_type": "M1_NO_CONSENSUS",
  "cooldown_until": 1746346800.0,
  "gate_passed_rules": [],
  "blocked_rules": ["M1_NO_CONSENSUS", "FLOW_DIVERGENCE_HIGH", "M1_PRICE_VOLUME_DIVERGENCE"]
}
```

---

## T-09：M2位置不佳

### 触发条件
- M2 距支撑/压力 > 3%（悬空高风险）
- M2 无S/R验证（dual_count=0）
- M1/M2 方向背离（M1做多但紧贴压力，M1做空但紧贴支撑）
- M2 紧贴压力位禁止追多（S06场景）

### 天眼AI话术

```
【🚫 M2位置不佳 — MATIC/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止入场，M2位置远离S/R位，悬空高风险

原因:
  M2支撑位1.02，压力位1.15，当前价格1.08
  距支撑5.9%，距压力6.5%，处于S/R中间地带
  无任何S/R验证（dual_count=0，triple_count=0）
  悬空状态，入场无S/R保护

证据（M1-M5数据）:
  M1: 15m↗️0.55📈3.2x | 1h↗️0.28📈2.1x | 4h↗️0.15📈1.5x
      三所同向做多✅ | flow_consensus=0.72(强) | source_count=3
      ✅ M1信号强
  M2: 支1.02阻1.15 | 当前价1.08 | dual_count=0❌ | triple_count=0❌
      距支撑5.9%❌ | 距压力6.5%❌ | 无验证❌
      S/R中间地带，悬空高风险❌
  M3: HIGH=0 | 无信号
  M4: RSI=58⚪中性 | ATR=4.2%🌬️ | OI变化+2.1%➡️
  M5: DOGE未冻结✅

位置分析:
  当前价格1.08处于支撑1.02和压力1.15的正中间
  无S/R验证，无触底/触顶记录
  入场后如果下跌，第一支撑在1.02（距5.9%）
  如果上涨，第一压力在1.15（距6.5%）
  悬空状态，无S/R保护墙

风险评估:
  - M1强做多信号，但M2位置悬空
  - 无S/R验证，入场无保护
  - 建议等待价格回调至支撑附近再入场
  噪音类型: M2_POSITION_FAR_FROM_SR
  风险等级: 高

自动执行: ❌ 否（Gate C档，M2位置不佳）
人工确认: ⚠️ 可人工Override（记录原因），建议等待回调
等待策略: 价格回调至距支撑<=1%后重新评估

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | M2位置悬空无验证
noise_type: M2_POSITION_FAR_FROM_SR
blocked_rules: ["M2_POSITION_FAR_FROM_SR", "M2_NO_VALIDATION"]
```

---

## T-10：M3巨量未确认

### 触发条件
- M3 反转猎杀存在（HIGH>=3 + OUTFLOW + 方向衰竭）
- M3 单所单时线GIANT信号（M3-07/M3-08）
- M3 被动买入信号（M3-02：GIANT阳+净流出）
- M3 被动卖出信号（M3-04：GIANT阴+净流入）
- M3 爆仓流出信号（M3-09）

### 天眼AI话术

```
【🚫 M3巨量未确认 — LINK/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 禁止入场，M3反转猎杀信号存在

原因:
  M3 HIGH=3所（三所均出现大量卖出K线）
  OUTFLOW净流出 + GIANT阴线2次
  综合判定为"反转猎杀"信号
  可能触发大量多单爆仓，注意不要追空

证据（M1-M5数据）:
  M1: 15m↘️-0.42📉2.8x | 1h↘️-0.25📉1.8x | 4h→0.08📉1.1x
      双所做空✅ | flow_consensus=0.65(接近强) | source_count=2
      ⚠️ 尽管M1做空信号强，但M3反转猎杀
  M2: 支撑14.20阻15.80 | 距支撑3.2% | dual_count=1
  M3: HIGH3所⚠️❌ | GIANT阴2次❌ | OUTFLOW流出❌ | 反转猎杀✅❌
      HIGH阴线量比: Gate=6.5x, OKX=5.2x, BNB=4.8x
      反转猎杀五指标: A触顶3次✅ B放量5.5x✅ C买卖比0.85❌
                     D反向空间3.2%✅ EK线反转形态✅
      综合判定: 反转猎杀存在⚠️
  M4: RSI=28🟢超卖 | ATR=5.1%💨高波动 | OI变化-15.2%📉📉大幅减仓⚠️
      空头衰竭预警⚠️
  M5: DOGE未冻结✅

反转猎杀分析:
  反转猎杀是专业机构故意爆仓散户多单后反向做多的策略
  特征：大量卖单砸盘 → 触发多单止损 → 机构反手做多
  当前LINK: HIGH3所 + OUTFLOW流出 + GIANT阴2次
  多头可能已被爆仓，价格可能反转向上
  禁止追空，等待反转确认

风险评估:
  - HIGH3所 + OUTFLOW + GIANT阴 = 三重反转信号
  - 可能已触发大量多单止损
  - 追空风险极高，价格可能快速反转
  噪音类型: REVERSAL_HUNT
  风险等级: 极高

自动执行: ❌ 否（Gate C档，反转猎杀禁止入场）
人工确认: ⚠️ 需人工Override（强烈不建议Override）
出山AI: 应立即评估LINK多单持仓，如有应止损或止盈

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: C | 置信度0% | M3反转猎杀信号存在
noise_type: REVERSAL_HUNT
blocked_rules: ["M3_REVERSAL_HUNT"]
```

---

## T-11：M4趋势不一致

### 触发条件
- M4 RSI 多周期方向不一致（15m做多信号但4h做空信号）
- M4 RSI 多周期衰竭（4H>=65 + 1H>=70 + 15m>=70：多头衰竭）
- M4 OI 大幅减仓 (<-10%) + M1 做多信号
- M4 ATR 极端波动 (>8%) + 持仓

### 天眼AI话术

```
【⚠️ M4趋势不一致 — AVAX/USDT】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: 暂缓入场，等待M4趋势修复

原因:
  M4 RSI多周期不一致：
    15m RSI=68🟠做多信号
    1h RSI=52⚪中性
    4h RSI=38🟢做空信号
    1d RSI=42🟢做空信号
  多周期趋势矛盾，无法判断主趋势方向
  4h+1d RSI偏弱，入多胜率低

证据（M1-M5数据）:
  M1: 15m↗️0.62📈3.8x | 1h↗️0.35📈2.2x | 4h↗️0.18📈1.4x
      三所同向做多✅ | flow_consensus=0.75(强) | source_count=3
      ✅ M1短期做多信号强
  M2: 支撑28.50阻32.80 | dual_count=2✅ | 距支撑2.1%
  M3: HIGH1所 | GIANT阳1次（单所不足）⚠️
  M4: RSI15m=68🟠❌ | RSI1h=52⚪❌ | RSI4h=38🟢❌ | RSI1d=42🟢❌
      多周期矛盾❌ | 综合RSI=50(矛盾区间)❌
      ATR=2.8%🌬️正常 | OI变化+1.5%➡️中性
  M5: DOGE未冻结✅

趋势分析:
  短期(15m): 做多信号 RSI=68
  中期(1h): 中性 RSI=52
  中长期(4h): 做空信号 RSI=38
  长期(1d): 做空信号 RSI=42
  综合判断: 短期反弹，但中长期趋势向下
  可能场景: 短期反弹后继续下跌

风险评估:
  - M4多周期趋势矛盾
  - 中长期(4h/1d)做空信号占优
  - M1短期做多可能只是反弹
  - 建议等待4h/1d趋势修复后再入场做多
  噪音类型: M4_MULTI_CYCLE_CONFLICT
  风险等级: 中高

自动执行: ❌ 否（Gate B档，M4多周期不一致）
人工确认: ⚠️ 第2轮确认后决策
建议: 等待4h RSI修复至>=50后重新评估，或等待1d趋势明确

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: B | 置信度45% | M4多周期趋势不一致
blocked_rules: ["M4_MULTI_CYCLE_CONFLICT"]
```

### EntryDecisionGate 输出

```json
{
  "verdict": "B",
  "action": "OBSERVE",
  "auto_execute": false,
  "confidence": 45,
  "reason": "M4 RSI多周期矛盾：15m=68🟠做多，4h=38🟢做空，1d=42🟢做空",
  "gate_passed_rules": ["M1_CONSENSUS_PASS_A"],
  "blocked_rules": ["M4_MULTI_CYCLE_CONFLICT"]
}
```

---

## 附录：天眼AI话术格式规范

### 标准话术模板

```
【<emoji> <档位名称> — <交易对>】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结论: <一句话结论>

原因:
  <3句话以内说明核心原因>

证据（M1-M5数据）:
  M1: <M1数据摘要>
      <共识/分歧/异常标注>
  M2: <M2数据摘要>
      <验证状态标注>
  M3: <M3数据摘要>
      <反转/缩量标注>
  M4: <M4数据摘要>
      <RSI/ATR/OI标注>
  M5: <M5数据摘要>
      <冻结状态标注>

风险评估:
  - <风险点1>
  - <风险点2>
  <噪音类型>
  风险等级: <低/中/中高/高/极高>

自动执行: <✅/❌>（Gate <档位>档，<原因>）
人工确认: <✅/❌/⚠️> <确认要求>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Gate裁决: <档位> | 置信度<置信度>% | <裁决摘要>
<额外字段>
```

### 话术颜色约定

| 颜色 | Emoji | 含义 | 用于 |
|------|-------|------|------|
| 绿色 | 🟢 | 正常/做多信号 | RSI<40, 量比>=5x, 三所共振 |
| 黄色 | 🟡 | 中性/偏弱 | RSI 40-60, 量比2-5x, 双所共振 |
| 橙色 | 🟠 | 偏强/追高风险 | RSI 60-70, 量比偏高 |
| 红色 | 🔴 | 极端/禁止 | RSI>75或<25, 无共识, 单所拉偏 |
| 白色 | ⚪ | 中性/正常 | RSI 40-60, 无特别信号 |
| 灰色 | ⬜ | 缺失/未知 | 数据缺失 |

### 话术禁止词

```
模糊词（全部删除）:
  观望     → 禁止/执行
  谨慎     → 禁止
  等确认   → 禁止（替换为"等待第2轮确认"或"人工确认"）
  可选     → 禁止/执行
  建议做多  → 执行做多
  可能反弹  → 立即止损
  也许     → 禁止
  差不多   → 禁止

决策只有三种结果：
  ✅ 执行做多   → 下令做多，不犹豫
  ✅ 执行做空   → 下令做空，不犹豫
  🚫 禁止操作   → 不下单，不问
```

---

## 附录：飞书通知模板

### A档执行通知

```
【✅ 天眼AI执行 — <交易对>】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
档位: A档可入场
置信度: <置信度>%
方向: <LONG/SHORT>
杠杆: <N>x
理由: M1<M1摘要> + M2<M2摘要> + M3<M3摘要>
Gate裁决: <verdict> | <confidence>% | 自动执行
时间: <UTC时间戳>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### C档禁止通知（飞书静默，不主动通知，仅日志记录）

```
# C档禁止不入飞书通知，仅记录日志
[EntryDecisionGate] C档禁止：<交易对> <噪音类型> <原因>
```

### 兵部DOGE冻结通知

```
【🚨 DOGE冻结通知 — 系统自动】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
币种: DOGE/USDT
触发原因: 全bot同向信号噪音（<N>个bot同时止损）
冻结时长: 24小时
冻结截止: <UTC时间>
解除条件: 24小时自动解除 或 连续2次盈利主动解除
兵部操作: 可调用unfreeze_doge("DOGE/USDT")人工解除
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
