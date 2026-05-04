# 出山AI 完整场景话术与ExitDecisionGate裁决规范
> 出山院代理生成 | 日期: 2026-05-04 | 版本: V1.0
> 状态: PENDING REVIEW

---

## 概述

出山AI是回撤保护AI，负责在持仓期间持续评估出场条件。它与ExitDecisionGate协同工作：
- 出山AI输出 action 和 score
- ExitDecisionGate 做最终裁决（5档G1-G5）
- 两者结合形成完整的"持仓卫士"决策闭环

本文档定义出山AI的10个核心场景话术，每个场景包含：
- 当前建议（Verdict）
- 触发证据（M1-M5五维数据）
- 风险解释
- 是否已执行
- 是否仅建议
- 下一步动作

---

## 场景话术格式模板

```markdown
### 场景N: [场景名称]

**裁决**: G[X] | verdict=[verdict] | score=[score]

**触发证据（M1-M5）**:
- M1资金流: [量比/净流向/信号]
- M2支撑压力: [距S/R/双验数/紧贴状态]
- M3巨量K线: [HIGH/GIANT/OUTFLOW/反转猎杀]
- M4技术指标: [RSI/ATR/OI/EMA/RSI衰竭]
- M5（特殊）: [其他扩展数据]

**风险解释**: [为什么会触发这个场景]
**当前建议**: [HOLD/WATCH/PARTIAL_EXIT/FULL_EXIT_REVIEW/EMERGENCY]
**是否已执行**: [已执行 / 未执行 / 仅建议]
**是否仅建议**: [是（需飞书确认）/ 否（自动执行）]
**下一步动作**:
1. [动作1]
2. [动作2]
```

---

## 场景1：继续持有（HOLD）

### 场景1: 继续持有（G1_HOLD）

**裁决**: G1 | verdict=HOLD | score=15-29

**触发证据（M1-M5）**:
- M1资金流: 15m量比 1.2x | 净流向 -0.1 | 信号 NEUTRAL
  - 1h量比 0.8x | 净流向 -0.05 | 信号 NEUTRAL
  - 4h量比 0.6x | 净流向 0.1 | 信号 NEUTRAL
- M2支撑压力: 距支撑 2.1% | 距压力 4.5% | 双验 1所 | 非紧贴
- M3巨量K线: HIGH=1所 | GIANT阳 0次 | GIANT阴 0次 | OUTFLOW 无 | 反转猎杀 无
- M4技术指标: RSI15m=52🟡 | ATR=3.2%🌬️ | OI变化 +1.2%➡️ | OI比率 1.02➡️ | EMA混乱 | RSI衰竭 无
- M5扩展: 趋势延续概率 55%（>=50%，允许持有）

**风险解释**:
趋势延续概率=55%，虽未达到强势做多信号，但趋势仍在延续。当前浮盈稳定，市场无明显反转信号。继续持有等待趋势确认或更高浮盈。

**当前建议**: HOLD（继续持有）
**是否已执行**: 未执行
**是否仅建议**: 是（自动持有，无需确认）

**下一步动作**:
1. 继续正常持仓，不做任何操作
2. 每10分钟监控M1量比变化
3. 若M1转净流出>=0.3，立即触发场景6评估

---

### 场景1B: 强做多环境继续持有（G1_HOLD + 趋势强）

**裁决**: G1 | verdict=HOLD | score=65-79 | trend_continuation_prob=82%

**触发证据（M1-M5）**:
- M1资金流: 15m量比 5.2x📈 | 净流入 0.85 | 信号 LONG
  - 1h量比 3.1x📈 | 净流入 0.42 | 信号 LONG
  - 4h量比 2.0x📈 | 净流入 0.31 | 信号 LONG
  - 三所共振: 偏多✅
- M2支撑压力: 距支撑 0.5% | 距压力 3.8% | 三验✅✅✅ | 紧贴支撑🟢
- M3巨量K线: HIGH=3所⚡ | GIANT阳 2次🐂 | OUTFLOW 无 | INFLOW 流入 | 反转猎杀 无
- M4技术指标: RSI15m=58🟡 | RSI1h=65🟠 | RSI4H=62🟡 | 综合RSI 62 | ATR=3.5%🌬️ | OI变化 +6.5%📈加仓 | OI比率 1.18📈 | EMA多头排列✅ | RSI衰竭 无
- M5扩展: 趋势延续概率 82%，远超50%门槛

**风险解释**:
三重做多信号（M1资金流三线共振 + M2三验紧贴支撑 + M3 GIANT阳流入 + M4 OI机构加仓），趋势延续概率82%。所有指标均支持继续持有，不应止盈出场。

**当前建议**: HOLD（继续持有，不止盈）
**是否已执行**: 未执行
**是否仅建议**: 是（强烈建议持有）

**下一步动作**:
1. 继续持有，不触发任何止盈
2. 设置P3（35%基准）止盈目标
3. 若RSI4H>70出现多头衰竭信号，触发场景5（多头衰竭评估）

---

## 场景2：观察（WATCH）

### 场景2: 趋势不明，观察等待（G2_WATCH）

**裁决**: G2 | verdict=WATCH | score=30-49

**触发证据（M1-M5）**:
- M1资金流: 15m量比 1.8x | 净流向 0.1 | 信号 NEUTRAL
  - 1h量比 1.5x | 净流向 -0.1 | 信号 NEUTRAL
  - 4h量比 1.2x | 净流向 0.05 | 信号 NEUTRAL
  - 三所背离⚠️
- M2支撑压力: 距支撑 1.5% | 距压力 2.3% | 双验 2所 | 非紧贴
- M3巨量K线: HIGH=1所 | GIANT阳 0次 | GIANT阴 1次 | OUTFLOW 无 | 反转猎杀 无
- M4技术指标: RSI15m=48⚪ | RSI1h=52🟡 | RSI4H=55⚪ | ATR=4.2%🌬️ | OI变化 +0.5%➡️ | OI比率 1.01➡️ | EMA混乱
- M5扩展: 趋势延续概率 42%（<50%），趋势不明

**风险解释**:
M1三所背离，量比偏低（1.5-1.8x），无法确认方向。M2处于中间地带（距支撑1.5%，距压力2.3%）。M4 RSI中性（48-55），无明确方向信号。趋势延续概率42%，低于50%门槛，但不足以触发出场。继续观察。

**当前建议**: WATCH（观察，不操作）
**是否已执行**: 未执行
**是否仅建议**: 是（观察等待，无需确认）

**下一步动作**:
1. 不执行任何出场，继续持仓
2. 等待M1三所共振信号出现
3. 若15m量比跌破1.0x，触发场景10（止盈收紧风险）评估
4. 下一周期继续评估

---

### 场景2B: DCA补仓后观察期（G2_WATCH + DCA后）

**裁决**: G2 | verdict=WATCH | score=35 | observation_active=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 2.5x | 净流入 0.35 | 信号 LONG
  - 1h量比 1.8x | 净流入 0.2 | 信号 LONG
- M2支撑压力: 距支撑 0.3%🟢 | 双验 2所 | 紧贴支撑✅
- M3巨量K线: HIGH=2所⚡ | GIANT阳 1次🐂 | OUTFLOW 无
- M4技术指标: RSI15m=42⚪ | ATR=5.5%💨 | OI变化 -2.1%📉 | OI比率 0.91📉减仓
- M5扩展: 刚完成DCA补仓（layer=1），观察期激活（剩余23.5h）

**风险解释**:
刚完成DCA补仓，layer=1。进入24小时观察期（post_exit_continuation）。观察期内：禁止auto_profit_tighten，禁止auto_dca，禁止auto_reentry。正常P1/P2/P3止盈规则不受影响。

**当前建议**: WATCH（观察期内，DCA完成）
**是否已执行**: DCA已执行（补仓）
**是否仅建议**: 是（观察期规则自动生效）

**下一步动作**:
1. 正常监控P1/P2/P3止盈（不受观察期影响）
2. 不允许再次DCA（layer已封顶2次）
3. 24小时观察期结束后，恢复正常自学习行为
4. 若出现连续2次盈利，观察期可提前解除

---

## 场景3：部分止盈（PARTIAL_EXIT）

### 场景3: P1达标建议部分止盈（G3_PARTIAL_EXIT）

**裁决**: G3 | verdict=PARTIAL_EXIT | score=55 | near_sr=True | pnl=18.5%

**触发证据（M1-M5）**:
- M1资金流: 15m量比 3.2x📈 | 净流入 0.65 | 信号 LONG
  - 1h量比 2.1x📈 | 净流入 0.35 | 信号 LONG
  - 4h量比 1.5x | 净流入 0.2 | 信号 LONG
- M2支撑压力: 距支撑 0.5%🟢 | 双验 2所 | 紧贴支撑✅ | near_sr=True
- M3巨量K线: HIGH=2所⚡ | GIANT阳 1次🐂 | OUTFLOW 无 | 反转猎杀 无
- M4技术指标: RSI15m=64🟠 | RSI1h=62🟡 | RSI4H=58⚪ | 综合RSI 61 | ATR=3.2%🌬️ | OI变化 +3.8%📈 | OI比率 1.12📈 | EMA多头排列✅ | RSI衰竭 无
- M5扩展: 趋势延续概率 71.2% | 紧贴支撑 + 双验

**风险解释**:
浮盈18.5%达到P1档（10x杠杆=15%触发），紧贴支撑双验，M1同向量比3.2x。趋势延续概率71.2%，建议部分止盈50%锁定利润，但保留50%仓位等待更高位。near_sr条件满足时，P1即可触发。

**当前建议**: PARTIAL_EXIT（部分止盈50%）
**是否已执行**: 未执行（建议）
**是否仅建议**: 是（推送到飞书，等待确认后执行）

**下一步动作**:
1. 构建飞书通知：「部分止盈50%建议，浮盈18.5%，紧贴支撑」
2. 用户确认后，执行 `rpc._rpc_force_exit(trade_id, amount=50%)`
3. 剩余50%继续持有，目标P2（25%触发）或P3（35%触发）
4. 若M1转净流出<-0.3，立即触发场景6

**飞书话术**:
```
【部分止盈建议】BTC/USDT LONG
浮盈: 🟢+18.5% | 评分: 55分 | 档位: G3
紧贴支撑（0.5%）+ 双验✅ + M1量比3.2x同向
建议止盈: 50%（锁定约9%利润）
剩余50%目标: P2(25%)或P3(35%)
请回复【确认50%止盈】继续执行
```

---

### 场景3B: RSI超买预警提前止盈（G3_PARTIAL_EXIT + RSI预警）

**裁决**: G3 | verdict=PARTIAL_EXIT | score=62 | pnl=22.3% | rsi_warning=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 2.8x📈 | 净流入 0.5 | 信号 LONG
  - 1h量比 2.0x📈 | 净流入 0.3 | 信号 LONG
  - 4h量比 1.2x | 净流入 0.15 | 信号 LONG
- M2支撑压力: 距支撑 1.2% | 双验 1所 | 非紧贴
- M3巨量K线: HIGH=1所 | GIANT阳 1次🐂 | OUTFLOW 无
- M4技术指标: RSI15m=74🔴 | RSI1h=72🔴 | RSI4H=68🟠 | 综合RSI 71.3 | ATR=4.5%🌬️ | OI变化 -3.2%📉减仓 | OI比率 0.88📉 | EMA多头排列⚠️ | **多头衰竭预警⚠️**
- M5扩展: 趋势延续概率 58% | RSI多周期衰竭临界（4H68接近65）

**风险解释**:
RSI三周期偏高（综合RSI=71.3），接近多头衰竭阈值（4H65+1H70+15m70）。OI出现减仓迹象（-3.2%）。虽趋势延续概率58%>50%，但RSI超买预警，建议提前止盈保护利润。

**当前建议**: PARTIAL_EXIT（部分止盈40%）
**是否已执行**: 未执行（预警）
**是否仅建议**: 是（建议但非强制）

**下一步动作**:
1. 构建飞书通知：「RSI超买预警，建议部分止盈40%」
2. 用户确认后执行部分止盈
3. 剩余60%设置RSI多头衰竭止损线（4H RSI≥70时触发场景5）
4. 下一周期继续监控RSI多周期衰竭状态

**飞书话术**:
```
【⚠️ RSI超买预警】BTC/USDT LONG
浮盈: 🟢+22.3% | 评分: 62分 | 档位: G3
🚨 RSI偏高: 15m=74🔴 | 1h=72🔴 | 4h=68🟠
综合RSI: 71.3 | 多头衰竭预警⚠️
OI减仓: -3.2%📉 | OI比率: 0.88📉
趋势延续概率: 58% | 建议止盈40%
请回复【确认40%止盈】继续执行
```

---

## 场景4：全平复核（FULL_EXIT_REVIEW）

### 场景4: P3达标建议全平复核（G4_FULL_EXIT_REVIEW）

**裁决**: G4 | verdict=FULL_EXIT_REVIEW | score=82 | pnl=38.5%

**触发证据（M1-M5）**:
- M1资金流: 15m量比 1.8x | 净流入 0.25 | 信号 NEUTRAL
  - 1h量比 1.2x | 净流向 -0.05 | 信号 NEUTRAL
  - 4h量比 0.8x | 净流出 -0.1 | 信号 NEUTRAL
- M2支撑压力: 距支撑 3.2% | 距压力 0.3%🟢 | 双验 2所 | **紧贴压力⚠️**
- M3巨量K线: HIGH=1所 | GIANT阳 0次 | GIANT阴 1次🐻 | OUTFLOW 无
- M4技术指标: RSI15m=68🟠 | RSI1h=72🔴 | RSI4H=65🟠 | 综合RSI 68 | ATR=5.5%💨 | OI变化 -6.5%📉大幅减仓 | OI比率 0.78📉减仓 | EMA多头排列⚠️ | **多头衰竭临界⚠️**
- M5扩展: 趋势延续概率 38%（<50%）| 紧贴压力 | OI大幅减仓

**风险解释**:
浮盈38.5%达到P3档（10x杠杆=35%触发）。紧贴压力（0.3%），RSI1h=72超买，OI大幅减仓（-6.5%）。趋势延续概率仅38%，低于50%门槛。M1量比已萎缩（4h仅0.8x）。建议全平，但需人工确认。

**当前建议**: FULL_EXIT_REVIEW（全平复核）
**是否已执行**: 未执行（需复核）
**是否仅建议**: 是（必须飞书确认后才能执行）

**下一步动作**:
1. 构建飞书通知：「P3达标，建议全平复核，紧贴压力+OI减仓」
2. 用户回复【确认全平】后，执行全平
3. 全平后激活post_exit_continuation（24小时观察期）
4. 观察期内禁止auto_reentry

**飞书话术**:
```
【全平复核请求】BTC/USDT LONG
浮盈: 🟢+38.5% | 评分: 82分 | 档位: G4
⚠️ 风险信号:
  - 紧贴压力位（0.3%）⚠️
  - RSI1h=72超买🔴 | OI减仓-6.5%📉
  - 趋势延续概率 38% < 50%
  - M1量比萎缩（4h仅0.8x）
建议: 全平100%，锁定+38.5%利润
请回复【确认全平100%】继续执行
```

---

### 场景4B: ATR高波动全平复核（G4_FULL_EXIT_REVIEW + ATR）

**裁决**: G4 | verdict=FULL_EXIT_REVIEW | score=78 | atr_extreme=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 3.5x📈 | 净流入 0.6 | 信号 LONG
  - 1h量比 2.2x📈 | 净流入 0.35 | 信号 LONG
  - 4h量比 1.8x | 净流入 0.25 | 信号 LONG
- M2支撑压力: 距支撑 1.5% | 距压力 2.8% | 双验 2所
- M3巨量K线: HIGH=2所⚡ | GIANT阳 1次🐂 | OUTFLOW 无 | 反转猎杀 无
- M4技术指标: RSI15m=62🟡 | RSI1h=58🟡 | RSI4H=55⚪ | ATR=8.5%💨💨极端波动 | OI变化 +2.1%➡️ | OI比率 1.05➡️ | EMA多头排列✅
- M5扩展: ATR极端（8.5%），止损距约17%，市场高波动

**风险解释**:
ATR=8.5%为极端波动（>8%阈值），止损距扩大到17%（10x杠杆）。虽M1/M3信号良好，但极端波动市场容易瞬时击穿止损线。OI稳定，RSI中性，综合评分78分。建议全平规避极端波动风险。

**当前建议**: FULL_EXIT_REVIEW（全平复核）
**是否已执行**: 未执行（需复核）
**是否仅建议**: 是（必须确认）

**下一步动作**:
1. 构建飞书通知：「ATR极端波动8.5%，建议全平」
2. 用户确认后全平
3. 降低杠杆（下次入场时建议降低1-2档）

**飞书话术**:
```
【极端波动全平复核】BTC/USDT LONG
浮盈: 🟢+15.2% | 评分: 78分 | 档位: G4
💨💨 ATR=8.5% 极端波动（止损距17%）
💹 M1三线同向做多 | RSI中性55 | OI稳定
⚠️ 极端波动市场易瞬穿止损，建议全平
建议: 全平100%
请回复【确认全平100%】继续执行
```

---

## 场景5：紧急风险复核（EMERGENCY_REVIEW）

### 场景5: 多头衰竭触发紧急平仓（G5_EMERGENCY_REVIEW）

**裁决**: G5 | verdict=EMERGENCY_REVIEW | score=95 | bull_exhaust=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 4.2x📈 | 净流入 0.75 | 信号 LONG
  - 1h量比 2.8x📈 | 净流入 0.45 | 信号 LONG
  - 4h量比 1.5x | 净流入 0.2 | 信号 LONG
- M2支撑压力: 距支撑 2.1% | 距压力 0.5%🟢 | 双验 2所 | 紧贴压力⚠️
- M3巨量K线: HIGH=3所⚡⚡⚡ | GIANT阳 2次🐂🐂 | **OUTFLOW流出💧** | **反转猎杀存在🚨**
- M4技术指标: **RSI15m=75🔴** | **RSI1h=74🔴** | **RSI4H=68🟠** | 综合RSI 72.3 | **多头衰竭确认🚨** | ATR=6.5%💨 | OI变化 -8.2%📉大幅减仓 | OI比率 0.72📉机构出逃 | EMA多头排列⚠️
- M5扩展: 趋势延续概率 22%（远低于50%）| 多周期RSI衰竭 | OI机构出逃

**风险解释**:
**RSI三周期多头衰竭确认**（4H68+1H74+15m75全部超标）。HIGH=3所反转猎杀信号存在。OI大幅减仓-8.2%，OI比率0.72机构出逃。M1虽量比较高，但OUTFLOW流出+反转猎杀=机构做多后出货。趋势延续概率仅22%，立即全平。

**当前建议**: EMERGENCY_REVIEW（立即全平，无需确认）
**是否已执行**: 未执行（紧急）
**是否仅建议**: 否（自动执行，后通知）

**下一步动作**:
1. 立即执行全平（无需等待确认）
2. 发送紧急飞书通知（已执行）
3. 全平后激活post_exit_continuation（24小时禁止auto_reentry）
4. 记录此次多头衰竭事件到自学习数据库

**飞书话术（已执行后发送）**:
```
【🚨 已执行紧急全平】BTC/USDT LONG
浮盈: 🟢+28.6% | 评分: 95分 | 档位: G5
🚨🚨 RSI多头衰竭确认:
  4H=68 + 1H=74 + 15m=75 = 多周期衰竭
⚡ HIGH=3所反转猎杀信号
💧 OI大幅减仓-8.2% | OI比率0.72机构出逃
💧 OUTFLOW流出（机构出货）
已执行: 全平100%（G5自动执行）
已激活: 24小时观察期（禁止auto_reentry）
```

---

### 场景5B: ATR止损触发紧急平仓（G5_EMERGENCY_REVIEW + ATR止损）

**裁决**: G5 | verdict=EMERGENCY_REVIEW | score=100 | atr_stop_hit=True

**触发证据（M1-M5）**:
- M1资金流: （触发时状态快照）
- M2支撑压力: （触发时状态快照）
- M3巨量K线: （触发时状态快照）
- M4技术指标: ATR止损线被触及
- M5扩展: 当前价格 <= ATR_long_stop_price

**风险解释**:
ATR动态止损线被触及（多头止损线：入场价 - 2×ATR）。ATR止损是硬风控，不可绕过。立即全平。

**当前建议**: EMERGENCY_REVIEW（立即全平）
**是否已执行**: 未执行（自动执行）
**是否仅建议**: 否（ATR止损自动执行）

**下一步动作**:
1. ATR止损触发，立即全平（不经过Gate，不等待确认）
2. 发送飞书通知（已执行）
3. 记录ATR止损事件
4. ATR止损后180秒禁止反向开仓（stoploss_cooldown）

---

## 场景6：防止提前平仓（连续亏损收紧风险）

### 场景6: 连续亏损2次后收紧止盈被拦截（规则1保护）

**裁决**: G2→G4 | verdict=PARTIAL_EXIT | score=52 | consec_losses=2 | blocked=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 2.5x📈 | 净流入 0.4 | 信号 LONG
  - 1h量比 1.8x📈 | 净流入 0.25 | 信号 LONG
  - 4h量比 1.2x | 净流入 0.1 | 信号 LONG
- M2支撑压力: 距支撑 0.8%🟢 | 双验 2所 | 紧贴支撑✅
- M3巨量K线: HIGH=1所 | GIANT阳 0次 | OUTFLOW 无
- M4技术指标: RSI15m=55⚪ | RSI1h=52🟡 | RSI4H=48⚪ | ATR=3.2%🌬️ | OI变化 +1.5%➡️ | OI比率 1.03➡️
- M5扩展: 连续亏损2次 | **观察期激活（剩余23.8h）** | auto_profit_tighten被禁止

**历史背景**:
```
[2026-05-03 22:15] DOGE/USDT 第1次亏损 -8.5%
[2026-05-04 03:42] DOGE/USDT 第2次亏损 -12.3%
  → 触发post_exit_continuation，激活24小时观察期
```

**风险解释**:
连续亏损2次后，原系统会执行「自学习微调」，将止盈阈值收紧到10%（盈利5%就开始卖）。这会导致「卖在黎明前」——连续亏损后市场通常会反弹，但收紧止盈会导致错过后续大涨。

**规则1保护生效**:
```
[ExitDecisionGate] DOGE/USDT consec_losses=2 >= 2
  → action=block | blocked_reason=auto_tighten_blocked_require_observation
  → _temp_thresh_override['DOGE'] 已清除
  → 观察期激活（剩余23.8h）
```

**当前建议**: WATCH（观察期保护中，正常P1/P2/P3止盈可用）
**是否已执行**: 未执行（收紧被拦截）
**是否仅建议**: 是（观察期规则自动生效）

**下一步动作**:
1. 收紧止盈被拦截，正常P1/P2/P3止盈规则不受影响
2. 24小时观察期内禁止auto_profit_tighten
3. 观察期内禁止DCA（layer已封顶）
4. 观察期内禁止auto_reentry
5. 若出现连续2次盈利，观察期可提前解除
6. 若无操作，观察期24小时后自动解除

**飞书话术（通知出山AI）**:
```
【出山AI·连续亏损保护】DOGE/USDT LONG
连续亏损: 2次（-8.5% + -12.3%）
⚠️ 自学习收紧止盈请求已被拦截（规则1保护）
🔒 24小时观察期已激活
允许: 正常P1(15%)/P2(25%)/P3(35%)止盈
禁止: auto_profit_tighten / auto_dca / auto_reentry
观察期剩余: 23.8小时
```

---

### 场景6B: 连续亏损后止盈10%收紧绕过门控（Bug修复验证）

**裁决**: G2 | verdict=WATCH | score=38 | consec_losses=3 | original_code_bug=True

**触发证据**:
- 原问题代码: v65_autopilot.py:4670-4675
```python
if consec_losses >= 2 and profit_pct > 5:
    thresh = 10  # BUG: 直接写入，绕过门控
    _temp_thresh_override[base] = thresh
```

**修复后代码**:
```python
gate = ExitDecisionGate()
gate_result = gate.evaluate(position, ...)
if gate_result.action in ("block", "observe"):
    _temp_thresh_override.pop(base, None)  # 清除待下发阈值
    # 不写入，观察期保护生效
```

**风险解释**:
原bug会导致：连续亏损>=2次后，盈利只要>5%就触发10%止盈阈值。这意味着：
- 浮盈5%就卖出 → 卖在黎明前
- 错过后续大反弹（通常连续亏损后市场会反转）
- 形成「亏损-收紧-小赚-继续亏损」恶性循环

**规则7（P0修复）保证**:
1. 连续亏损>=2 → gate_result.action = "block"
2. _temp_thresh_override 不被写入
3. 24小时观察期激活
4. 正常P1/P2/P3止盈规则继续生效（不受影响）

**当前建议**: WATCH（修复后，观察期保护生效）
**是否已执行**: 未执行（bug已修复）
**是否仅建议**: N/A（修复验证场景）

**验证检查清单**:
- [ ] _post_exit_continuation 全局变量已声明
- [ ] ExitDecisionGate 类已插入 check_exit_conditions() 之前
- [ ] 原4670-4675行已被门控调用替换
- [ ] 连续亏损>=2时，_temp_thresh_override[base]不再被写入
- [ ] 观察期结束后，_post_exit_continuation[pair]被正确清除

---

## 场景7：出场后延续风险（post_exit_continuation）

### 场景7: 出场后延续观测期激活（连续亏损观察）

**裁决**: G2 | verdict=WATCH | observation_active=True | remaining=23.5h

**触发证据（M1-M5）**:
- M1资金流: 15m量比 0.5x📉 | 净流出 -0.2 | 信号 SHORT
- M2支撑压力: 距支撑 1.8% | 距压力 0.5% | 双验 1所
- M3巨量K线: HIGH=0所 | GIANT阴 1次🐻 | OUTFLOW 流出
- M4技术指标: RSI15m=35🟢 | RSI1h=38🟢 | RSI4H=42⚪ | ATR=4.2%🌬️ | OI变化 -2.8%📉
- M5扩展: 连续亏损3次触发观察期 | 禁止动作: auto_profit_tighten / auto_dca / auto_reentry

**观察期状态**:
```json
{
  "pair": "SOL/USDT",
  "observation_active": true,
  "consecutive_losses": 3,
  "observation_start_ts": 1746374400.0,
  "observation_end_ts": 1746460800.0,
  "remaining_hours": 23.5,
  "actions_blocked": ["auto_profit_tighten", "auto_dca", "auto_reentry"],
  "loss_threshold": 2,
  "observation_period_hours": 24
}
```

**风险解释**:
连续亏损3次后激活24小时观察期。期间：
- 禁止auto_profit_tighten：防止止盈阈值被错误收紧
- 禁止auto_dca：防止越亏越加仓的恶性循环
- 禁止auto_reentry：防止在未确认趋势反转前盲目入场

正常P1/P2/P3止盈规则不受影响（这是规则，不是自适应行为）。

**当前建议**: WATCH（观察期激活中）
**是否已执行**: 已执行（观察期激活）
**是否仅建议**: 否（自动激活）

**下一步动作**:
1. 观察期24小时内禁止所有被拦截动作
2. 正常P1/P2/P3止盈规则继续工作
3. 若连续2次盈利，观察期可提前解除
4. 兵部可人工清除观察期（调用 _deactivate_post_exit_continuation）

**飞书话术（激活通知）**:
```
【出山AI·观察期激活】SOL/USDT LONG
🚦 连续亏损3次，24小时观察期已激活
禁止动作:
  ❌ auto_profit_tighten（自学习收紧止盈）
  ❌ auto_dca（自动DCA加仓）
  ❌ auto_reentry（自动反向入场）
✅ 正常P1/P2/P3止盈规则继续生效
⏰ 剩余时间: 23.5小时
提前解除条件: 连续2次盈利 或 兵部人工清除
```

---

### 场景7B: 出场后延续风险 — 观察期结束恢复正常

**裁决**: G1 | verdict=HOLD | observation_expired=True | remaining=0h

**触发证据（M1-M5）**:
- M5扩展: 观察期24小时到期自动解除 | unlock_trigger=observation_period_expired

**观察期解除状态**:
```
[PostExitContinuation] ✅ 解除观测期: SOL/USDT 原因=observation_period_expired
```

**风险解释**:
观察期24小时到期，自动解除。此时：
- 自学习行为恢复正常（但需重新评估方向）
- DCA重新可用（但需满足DCA触发条件）
- 反向入场重新可用（需天眼AI重新确认）

**当前建议**: HOLD（恢复正常监控）
**是否已执行**: 已执行（观察期解除）
**是否仅建议**: 否（自动解除）

**下一步动作**:
1. 恢复正常监控，下一入场信号需重新评估
2. 自学习数据库记录此次连续亏损事件
3. 兵部可在天眼AI确认趋势后人工决定入场

---

## 场景8：SOL DCA满层风险

### 场景8: SOL DCA满层（layer=2封顶）+ 高波动风险

**裁决**: G3 | verdict=PARTIAL_EXIT | score=58 | dca_layer=2 | sol_risk=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 2.2x📈 | 净流入 0.35 | 信号 LONG
  - 1h量比 1.5x | 净流入 0.2 | 信号 LONG
  - 4h量比 1.0x | 净流向 0.05 | 信号 NEUTRAL
- M2支撑压力: 距支撑 0.3%🟢 | 双验 2所 | 紧贴支撑✅
- M3巨量K线: HIGH=1所 | GIANT阳 0次 | OUTFLOW 无 | 反转猎杀 无
- M4技术指标: RSI15m=58🟡 | RSI1h=62🟡 | RSI4H=55⚪ | ATR=8.2%💨💨极端波动 | OI变化 -4.5%📉减仓 | OI比率 0.85📉 | EMA混乱
- M5扩展: DCA layer=2（已封顶）| SOL ATR极端 | SOL OI减仓

**DCA状态记录**:
```
SOL/USDT DCA状态:
  layer=0: 入场价 128.5
  layer=1: 补仓价 118.2（DCA_间隔=10.3%）
  layer=2: 补仓价 108.5（DCA_间隔=9.7%）→ 已封顶
  当前持仓均价: 118.4
  当前价格: 115.2
  浮亏: -2.7%
```

**SOL特有风险**:
- SOL ATR=8.2%（>8%阈值），价格波动极大
- SOL OI减仓-4.5%，OI比率0.85，机构减仓
- DCA已满层（layer=2封顶），不可再补仓
- 趋势延续概率=52%，略高于50%门槛

**风险解释**:
SOL DCA已满层，无法继续补仓摊低成本。ATR极端波动（8.2%）+ OI减仓双重风险。趋势延续概率52%，略高于50%但不稳定。当前浮亏-2.7%，建议在反弹到P1（15%基准）时部分止盈，锁定利润或减少损失。

**当前建议**: PARTIAL_EXIT（建议P1达标时部分止盈50%）
**是否已执行**: 未执行（建议）
**是否仅建议**: 是（需确认）

**下一步动作**:
1. 设置P1止盈提醒（均价118.4 + 15% = 136.2）
2. 若M1转净流出<-0.3，触发场景9（DOGE止损循环）评估
3. 兵部注意：SOL高波动，建议降低该仓位暴露

**飞书话术**:
```
【SOL风险提示】SOL/USDT LONG（持仓中）
DCA状态: layer=2/2 已封顶
浮亏: 🔴-2.7%（均价118.4，当前115.2）
⚠️ SOL特有风险:
  - ATR=8.2%💨💨 极端波动
  - OI减仓-4.5%📉 | OI比率0.85
建议: P1达标时（136.2）止盈50%
已禁止: 再次DCA（layer封顶）
```

---

## 场景9：DOGE止损循环风险

### 场景9: DOGE止损循环 — 连续止损后触发观察期

**裁决**: G2 | verdict=WATCH | consec_losses=4 | doge_risk=True | atr_repeat=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 1.2x | 净流向 -0.05 | 信号 NEUTRAL
  - 1h量比 0.8x | 净流出 -0.1 | 信号 SHORT
  - 4h量比 0.5x | 净流出 -0.15 | 信号 SHORT
- M2支撑压力: 距支撑 1.0% | 距压力 2.5% | 单验 1所 | 中间地带
- M3巨量K线: HIGH=0所 | GIANT阴 0次 | OUTFLOW 无
- M4技术指标: RSI15m=38🟢 | RSI1h=35🟢 | RSI4H=42⚪ | ATR=12.5%💨💨💨超极端 | OI变化 -1.2%➡️ | OI比率 0.98➡️ | EMA混乱
- M5扩展: 连续亏损4次 | DOGE ATR超极端 | 止损循环风险

**DOGE止损历史**:
```
[2026-05-01 14:00] DOGE/USDT 第1次止损 -15.2%（ATR触发）
[2026-05-01 22:30] DOGE/USDT 第2次止损 -18.5%（ATR触发）
[2026-05-02 09:15] DOGE/USDT 第3次止损 -22.1%（ATR触发）
[2026-05-04 03:42] DOGE/USDT 第4次止损 -25.6%（ATR触发）
  → ATR=12.5%，止损距25%，频繁触发
  → 触发post_exit_continuation，激活24小时观察期
```

**DOGE止损循环根因**:
1. DOGE ATR=12.5%（超极端），止损距25%（10x杠杆）
2. DOGE波动极大，正常市场波动就触发止损
3. 止损触发 → DCA补仓 → 继续止损 → 循环
4. 每止损一次，亏损8-25%，累计损耗巨大

**风险解释**:
DOGE出现4次连续止损，止损循环已形成。ATR=12.5%超极端，止损距25%。连续亏损4次后进入24小时观察期。观察期内禁止auto_dca（防止继续加仓摊低成本）。

**当前建议**: WATCH（观察期激活，禁止DCA）
**是否已执行**: 观察期已激活
**是否仅建议**: 是（观察期规则自动生效）

**下一步动作**:
1. 24小时观察期禁止DCA（防止止损循环加剧）
2. DOGE建议暂停自动入场，等ATR降到<8%再恢复
3. 兵部可考虑：是否需要永久限制DOGE bot的auto_dca功能
4. 若ATR持续>10%，建议天眼AI对DOGE设置入场禁止

**飞书话术**:
```
【出山AI·DOGE止损循环警告】DOGE/USDT
🚨 连续亏损4次（止损历史）
  - 5/1 14:00: -15.2%（ATR）
  - 5/1 22:30: -18.5%（ATR）
  - 5/2 09:15: -22.1%（ATR）
  - 5/4 03:42: -25.6%（ATR）
⚠️ DOGE ATR=12.5%💨💨💨 超极端波动
💸 止损距25%，正常波动即触发止损
🔒 24小时观察期已激活
  ❌ auto_dca 已禁止（防止止损循环）
  ❌ auto_reentry 已禁止
建议: 兵部评估DOGE bot参数调整
```

---

## 场景10：止盈10%收紧风险（连续亏损→10%→卖在黎明前）

### 场景10: 连续亏损→10%止盈收紧→卖在黎明前陷阱

**裁决**: G3→G4 | verdict=PARTIAL_EXIT→FULL_EXIT_REVIEW | score=48→72 | tighten_risk=True

**触发证据（M1-M5）**:
- M1资金流: 15m量比 3.8x📈 | 净流入 0.7 | 信号 LONG
  - 1h量比 2.5x📈 | 净流入 0.42 | 信号 LONG
  - 4h量比 1.8x📈 | 净流入 0.28 | 信号 LONG
- M2支撑压力: 距支撑 0.2%🟢 | 三验✅✅✅ | 紧贴支撑✅ | near_sr=True
- M3巨量K线: HIGH=3所⚡⚡⚡ | GIANT阳 3次🐂🐂🐂 | **INFLOW流入💧** | 反转猎杀 无
- M4技术指标: RSI15m=58🟡 | RSI1h=55⚪ | RSI4H=52⚪ | ATR=3.2%🌬️ | OI变化 +8.5%📈大幅加仓 | OI比率 1.22📈机构确认 | EMA多头排列✅
- M5扩展: 连续亏损1次（刚触发收紧条件，尚未到2次）| 趋势反弹信号强烈

**"卖在黎明前"陷阱场景**:

```
时间线:
[05-03 22:00] ETH/USDT 第1次亏损 -15.2%
  → _get_consecutive_losses(ETH) = 1（未达到阈值2）
  → 原代码会尝试收紧（thresh=10%），但gate_result.action="block"
  → 收紧请求被拦截，观察期未激活（需>=2次）

[05-04 06:00] ETH/USD 突发利好（CPI数据超预期）
  → M1量比飙升至3.8x（三线共振做多）
  → M3 GIANT阳3次 + INFLOW流入
  → OI+8.5%大幅加仓（机构顺势）
  → 趋势反弹信号强烈

[05-04 06:30] ETH/USDT 浮盈+6.2%（正在反弹）
  → 原bug代码：若consec_losses>=2（实际=1），会收紧到10%
  → 浮盈5%就开始卖（触发thresh=10%）
  → 卖在黎明前！错过后续+25%大涨！
```

**规则7（P0修复）保证**:

```python
# 修复前（有bug）：
if consec_losses >= 2 and profit_pct > 5:
    thresh = 10  # 直接收紧，卖在黎明前！
    _temp_thresh_override[base] = thresh

# 修复后（有门控）：
gate = ExitDecisionGate()
gate_result = gate.evaluate(position, ...)
if gate_result.action in ("block", "observe"):
    _temp_thresh_override.pop(base, None)  # 清除收紧请求
    # 观察期激活，正常止盈规则继续
```

**正确行为（修复后）**:

```
[05-04 06:30] ETH/USDT 浮盈+6.2%
  → ExitDecisionGate.evaluate():
    - consec_losses=1 < 阈值2 → 不触发block
    - 但M1三线共振+M3 GIANT阳3次+OI大幅加仓
    - score=72 → G3/PARTIAL_EXIT
    - 趋势延续概率=82%
  → 建议: HOLD（继续持有，等P1触发）
  → 不收紧止盈阈值，正常P1/P2/P3规则生效

[05-04 12:00] ETH/USDT 浮盈+18.5%
  → P1触发（15%基准）→ 正常止盈50%
  → 剩余50%继续持有，等P2/P3

[05-05 02:00] ETH/USDT 浮盈+32.0%
  → P3触发 → 全平
  → 累计止盈: 50%+50%=100%，锁定+32%
```

**错误行为（修复前）**:

```
[05-04 06:30] ETH/USDT 浮盈+6.2%
  → 原bug: consec_losses=1 + profit_pct=6.2 > 5
  → thresh=10 → _temp_thresh_override['ETH']=10
  → 立即触发止盈10% → 全部卖出！

[05-04 12:00] ETH/USDT 涨至+25%
  → 错过+25%利润！
  → 连续亏损后立即大涨（卖在黎明前）
```

**风险解释**:
连续亏损后的"黎明前"是最危险的时刻：
1. 连续亏损导致心理焦虑，想尽快"回本"
2. 系统收紧止盈阈值到10%，盈利5%就卖
3. 但连续亏损后市场往往反转（聪明钱入场）
4. 结果：卖在最低点，错过后续大涨

**规则1+规则7双重保护**:
- 规则1：连续亏损>=2 → 收紧请求被拦截
- 规则7：P0 bug修复 → 收紧必须经过Gate，不直接写入
- 即使只有1次亏损，若有收紧请求，Gate也会评估

**当前建议**: HOLD（修复后，黎明前反弹继续持有）
**是否已执行**: 未执行
**是否仅建议**: 是（强烈建议持有，不收紧止盈）

**下一步动作**:
1. 正常持仓，不执行任何收紧止盈
2. 等待P1触发（15%基准）再止盈
3. 连续亏损观察期（若有>=2次）自动激活
4. 兵部监控：确保无黎明前恐慌性手动平仓

**飞书话术（出山AI报告）**:
```
【出山AI·黎明前保护】ETH/USDT LONG
连续亏损: 1次（未达观察期阈值2次）
⚠️ 潜在风险: 黎明前反弹（连续亏损后反转）
  - M1三线共振量比3.8x/2.5x/1.8x
  - M3 GIANT阳3次🐂🐂🐂 + INFLOW流入
  - OI大幅加仓+8.5%📈
  - 趋势延续概率 82%
🔒 规则7（P0修复）保护:
  - 止盈收紧请求被Gate拦截
  - _temp_thresh_override 未写入
建议: HOLD，继续持有等P1触发（15%）
避免: 黎明前恐慌性平仓
```

---

## 附录：出山AI完整Prompt模板

```
你是出山AI，专门负责量化交易持仓出场决策（回撤保护）。

【输入数据】
{pair} 当前价格: {current_price}

【持仓数据】
- 方向: {direction}（LONG/SHORT）
- 入场价格: {entry_price}
- 当前浮盈: {pnl_pct}%
- 杠杆: {leverage}x
- 强平价格: {liquidation_price}
- 持仓时长: {holding_minutes}分钟
- 连续亏损次数: {consec_losses}次
- 观察期状态: {observation_active ? "激活中(剩余Xh)" : "无"}

【M1资金流】
- 15m: 量比={ratio_15m}x 净流向={netflow_15m} 信号={signal_15m}
- 1h:  量比={ratio_1h}x 净流向={netflow_1h}  信号={signal_1h}
- 4h:  量比={ratio_4h}x 净流向={netflow_4h}  信号={signal_4h}

【M2支撑压力】
- 距支撑: {dist_support}%
- 距压力: {dist_resistance}%
- 双/三所验证: {dual_count}所
- 紧贴状态: {near_sr}（True=±1%内）

【M3巨量K线】
- HIGH数量: {high_count}所
- GIANT阳: {giant_bull}次 | GIANT阴: {giant_bear}次
- OUTFLOW: {outflow_present} | INFLOW: {inflow_present}
- 反转猎杀: {reversal_hunt}

【M4技术指标（三所交叉验证）】
- RSI(15m): {rsi_15m} | RSI(1h): {rsi_1h} | RSI(4h): {rsi_4h} | 综合RSI: {avg_rsi}
- RSI衰竭: {rsi_exhaust}（none/bull_exhaust/bear_exhaust）
- ATR: {atr_pct}% | 止损距: {stop_loss_pct}%
- OI变化: {oi_change_pct}% | OI比率: {oi_ratio}
- EMA排列: {ema_alignment}（多头排列/空头排列/混乱）

【V6.5止盈档位】
- P1触发: {p1_trigger}%（当前浮盈 {pnl_pct}%）
- P2触发: {p2_trigger}%
- P3触发: {p3_trigger}%

【ExitDecisionGate 约束】
- 规则1: 连续亏损>=2 → 收紧被拦截
- 规则7: P0修复 → 收紧必须经过Gate
- 观察期激活时: auto_profit_tighten/auto_dca/auto_reentry 禁止

【决策要求】
返回JSON格式：
{
  "pair": "{pair}",
  "verdict": "G1_HOLD | G2_WATCH | G3_PARTIAL_EXIT | G4_FULL_EXIT_REVIEW | G5_EMERGENCY_REVIEW",
  "action": "exit | observe | block | confirm | pass",
  "score": 0-100,
  "exit_pct": 0-100,
  "reason": "决策理由",
  "trend_continuation_prob": 0-100,
  "consec_losses": {consec_losses},
  "near_sr": true/false,
  "observation_active": true/false,
  "m1_summary": "M1摘要",
  "m2_summary": "M2摘要",
  "m3_summary": "M3摘要",
  "m4_summary": "M4摘要",
  "blocked_reason": "若action=block，填写被拦截原因",
  "feishu_msg": "飞书通知内容（已执行时）或确认请求（需确认时）"
}

【评分规则】
M1资金流: 0-25分（量比>=5x+三线共振=25分）
M2 S/R位置: 0-25分（紧贴支撑+三验=25分）
M3巨量K线: 0-25分（HIGH>=3+GIANT阳+流入=25分）
M4技术指标: 0-25分（RSI配合+OI加仓+多头排列=25分）
总分: 0-100分

【档位判断】
score>=90 + 紧急信号 → G5/EMERGENCY_REVIEW（立即全平）
score>=80 → G4/FULL_EXIT_REVIEW（全平复核）
score>=50 → G3/PARTIAL_EXIT（部分止盈）
score>=30 → G2/WATCH（观察）
score<30 → G1/HOLD（继续持有）

【趋势延续概率】
M1*30% + M2*20% + M3*25% + M4*25% / 80 * 100%
<50%: 不建议继续持有
>=50%: 允许继续持有

【规则约束】
- 连续亏损>=2: 收紧止盈被拦截
- RSI多头衰竭: 立即G5
- ATR止损触及: 立即G5
- L5 P3全平: 需G4复核
- S/R单独触发: 仅G3部分止盈

输出JSON，不要额外解释。
```

---

## 附录：场景决策矩阵速查

| 场景 | verdict | 条件 | action | 飞书 |
|------|---------|------|--------|------|
| 1 HOLD强做多 | G1 | score<50, trend>=50% | pass | 无 |
| 2 WATCH趋势不明 | G2 | 30<=score<50 | observe | 有（记录） |
| 3 部分止盈P1 | G3 | score>=50, pnl>=P1 | exit | 有（建议） |
| 4 全平复核P3 | G4 | score>=80 | confirm | 有（复核） |
| 5 紧急多头衰竭 | G5 | RSI三周期衰竭 | exit | 有（已执行） |
| 6 连续亏损拦截 | G2→G4 | consec>=2 | block/observe | 有（保护） |
| 7 观察期激活 | G2 | obs_active=True | observe | 有（激活） |
| 8 SOL DCA满层 | G3 | dca_layer=2, ATR>8% | exit | 有（风险） |
| 9 DOGE止损循环 | G2 | consec=4, ATR>10% | observe | 有（警告） |
| 10 黎明前反弹 | G3 | consec=1, M1反弹 | pass | 有（保护） |
