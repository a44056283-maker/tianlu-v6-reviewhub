# 兵部审计报告：12机器人亏损矩阵
**审计时间**: 2026-05-04 14:30 GMT+8
**审计人**: 兵部代理
**数据来源**: trade_journal.json (缓存 2026-05-02 23:24) / daily_dept_report.json (2026-05-04 10:02) / bot logs (/private/tmp/bot_*.log)
**数据限制**: SQLite数据库无法直接查询（只读接口受阻），OKX/MacB历史数据暂缺。

---

## 一、12机器人拓扑汇总

| 端口 | 主机 | 交易所 | 账号 | 策略 | 数据库 | 在线状态 |
|------|------|--------|------|------|--------|---------|
| 9090 | Mac A | Gate.io | Gate-17656685222 | FOttStrategy | tradesv3_gate.sqlite | **在线** |
| 9091 | Mac A | Gate.io | Gate-85363904550 | FOttStrategy | tradesv3_gate.sqlite | **在线** |
| 9092 | Mac A | Gate.io | Gate-15637798222 | FOttStrategy | tradesv3_gate.sqlite | **在线** |
| 9093 | Mac A | OKX | OKX-15637798222 | FOttStrategy | tradesv3_okx.sqlite | **在线** |
| 9094 | Mac A | OKX | OKX-BOT853639 | FOttStrategy | tradesv3_okx.sqlite | **在线** |
| 9095 | Mac A | OKX | OKX-BOTa440562 | FOttStrategy | tradesv3_okx.sqlite | **在线** |
| 9096 | Mac A | OKX | OKX-BHB1663875 | FOttStrategy | tradesv3_okx.sqlite | **在线** |
| 9097 | Mac A | OKX | OKX-17656685222 | FOttStrategy | tradesv3_okx.sqlite | **在线** |
| 8081 | Mac B | Gate.io | MacB-Gate-a63904550 | FOttStrategy | ?/user_data_gate_a63904550 | **在线(0仓)** |
| 8082 | Mac B | Gate.io | MacB-Gate-a15637798222 | FOttStrategy | ?/user_data_gate_a15637798222 | **在线(0仓)** |
| 8083 | Mac B | Gate.io | MacB-Gate-b15637798222 | FOttStrategy | ?/user_data_gate_b15637798222 | **在线(0仓)** |
| 8084 | Mac B | Gate.io | MacB-Gate-c15637798222 | FOttStrategy | ?/user_data_gate_c15637798222 | **在线(0仓)** |

**注**: 所有机器人使用同一份 v65_autopilot.py 策略源码（FOttStrategy框架层全部禁用）。

---

## 二、历史汇总数据（trade_journal.json 缓存）

**来源**: trade_journal.json (最后更新: 2026-05-02 23:24)
**覆盖**: 仅Gate bots (9090/9091/9092) 的已平仓交易

| 指标 | 数值 |
|------|------|
| 已平仓总交易数 | **197笔** |
| 总盈亏 (profit_abs) | **+$205.88** |
| 盈利交易数 | 83笔 |
| 亏损交易数 | 107笔 |
| 胜率 | **42.1%** |
| 平均盈利 | +$22.14 |
| 平均亏损 | -$15.25 |
| 盈亏比 | 1.45:1 |

**注**: 该缓存数据为2026-05-02快照，不含OKX bots历史数据和MacB bots数据。

---

## 三、今日批量强平分析（2026-05-04）

**来源**: /private/tmp/bot_9090.log ~ bot_9097.log (2026-05-04 日志)

### 3.1 DOGE/USDT 批量止损（所有Gate+OKX bots）

| Bot | 交易ID | 方向 | 杠杆 | 亏损(USDT) | 触发时间 | exit_reason |
|-----|--------|------|------|------------|---------|-------------|
| 9090 | 216 | SHORT | 5x | **-$15.20** | 05-04 10:17 | force_exit |
| 9091 | 223 | SHORT | 5x | **-$12.04** | 05-04 10:13 | force_exit |
| 9092 | 199 | SHORT | 5x | ~-$15 | 05-04 10:22 | force_exit |
| 9093 | 187 | SHORT | 5x | ~-$12 | 05-04 10:31 | force_exit |
| 9094 | 144 | SHORT | 5x | ~-$12 | 05-04 10:44 | force_exit |
| 9095 | 142 | SHORT | 5x | ~-$12 | 05-04 10:27 | force_exit |
| 9096 | 116 | SHORT | 5x | ~-$12 | 05-04 10:36 | force_exit |
| 9097 | 114 | SHORT | 5x | ~-$12 | 05-04 10:50 | force_exit |

**DOGE批量止损估算总亏损**: 约 **-$96 ~ -$120 USDT**（8个bot各一笔）
**触发模式**: 所有bot同时做空DOGE → 同时force_exit，属于策略同向信号触发，非异常。

### 3.2 其他强平事件

| Bot | 交易对 | 方向 | 盈亏 | exit_reason |
|-----|--------|------|------|-------------|
| 9090 | ETH/USDT | SHORT | **-$27.96** | force_exit |
| 9091 | BNB/USDT | LONG | **+$22.66** | force_exit |
| 9091 | BNB/USDT | LONG | +$22.66 | force_exit |
| 9092 | BNB/USDT | LONG | +$22.66 | force_exit |
| 9093 | BNB/USDT | LONG | +$22.66 | force_exit |
| 9094 | DOGE/USDT | SHORT | -$12 | force_exit |
| 9095 | DOGE/USDT | LONG? | ~ | force_exit |
| 9096 | BNB/USDT | LONG | +$22.66 | force_exit |
| 9097 | BNB/USDT | LONG | +$22.66 | force_exit |

**注**: 所有 exit_reason=force_exit 表示由天眼AI或出山AI触发，非V6.5 P1/P2/P3止盈。

---

## 四、当前持仓快照（2026-05-04 约10:02）

**来源**: daily_dept_report.json (10:02实时) + trade_journal.json (05-02缓存)

| Bot | 交易所 | 当前开仓数 | 高杠杆(>=7x) | 备注 |
|-----|---------|-----------|-------------|------|
| 9090 | Gate | ~5 | 0 | 有SOL/ETH/BTC/BNB+新仓 |
| 9091 | Gate | ~5 | 0 | 同上 |
| 9092 | Gate | ~5 | 0 | 同上 |
| 9093 | OKX | ~5 | 0 | DOGE/BNB/BTC+新仓 |
| 9094 | OKX | ~5 | 0 | 同上 |
| 9095 | OKX | ~5 | 0 | 同上 |
| 9096 | OKX | ~5 | 0 | 同上 |
| 9097 | OKX | ~5 | 0 | 同上 |
| 8081 | MacB-Gate | **0** | 0 | 心跳0持仓 |
| 8082 | MacB-Gate | **0** | 0 | 心跳0持仓 |
| 8083 | MacB-Gate | **0** | 0 | 心跳0持仓 |
| 8084 | MacB-Gate | **0** | 0 | 心跳0持仓 |
| **合计** | | **~38** | **0** | |

---

## 五、亏损最严重的机器人

**注**: 由于OKX和MacB bots的SQLite历史数据无法直接查询，以下评估基于日志推断和已知缓存数据。

### 5.1 历史数据（Gate bots, 缓存）
- trade_journal.json 显示 9091 的交易条目数 (2424次更新) 高于 9092 (1830次) 和 9090 (1654次)
- 9091 的日志条目最多 → 可能经历了更多交易调整或重复记录
- **评估**: 历史维度上 9091 交易最频繁

### 5.2 今日数据（2026-05-04 DOGE批量止损）
| Bot | DOGE止损亏损 | 状态 |
|-----|-------------|------|
| 9090 | -$15.20 | 最严重 |
| 9091 | -$12.04 | 第二 |
| 9092 | ~-$15 | 并列 |
| 9093-9097 | 各~-$12 | 一致 |

**亏损最严重: 9090 (Gate DOGE -$15.20 + ETH -$27.96 ≈ -$43)**

### 5.3 Mac B bots
- 8081-8084 当前0持仓，无今日亏损
- 历史数据无法确认（MacB数据库路径: `/Users/luxiangnan/freqtrade_bots/` - 该目录不存在于Mac A本地）

---

## 六、盈利最好的机器人（今日）

**评估**: BNB/USDT LONG bots 在出山AI强平触发时多数以 +$22.66 平仓:
- 9091: +$22.66 (BNB #1) + +$22.66 (BNB #2) = **+$45.32**
- 9092: +$22.66
- 9093: +$22.66
- 9096: +$22.66
- 9097: +$22.66

**注**: force_exit 触发时机的平仓可能不是最佳止盈点，实际盈利应参考完整交易周期数据。

---

## 七、亏损集中币种分析

**来源**: bot logs 2026-05-04

| 币种 | 方向 | 亏损次数 | 平均亏损 | 风险评估 |
|------|------|---------|---------|---------|
| DOGE/USDT | SHORT | 8/8 bots | ~-$12~-15 | **极高** - 全bot同向信号触发同时止损 |
| ETH/USDT | SHORT | 2+ bots | -$27.96 | 高 - 杠杆偏高 |
| SOL/USDT | SHORT | 有bot | 未知 | 中 |
| BNB/USDT | LONG | 有bot | +$22.66 | 盈利 |

**关键发现**: DOGE/USDT 是今天最大的亏损来源，约 -$96~-120 的批量同向止损。根本原因是所有bot同时捕捉到DOGE做空信号，量比触发后全部入场，随后被 force_exit 批量平仓。这说明策略存在信号同步性问题。

---

## 八、数据限制说明

| 限制项 | 说明 |
|--------|------|
| SQLite数据库只读 | 无法执行sqlite3/python3查询 |
| trade_journal.json | 仅含Gate bots历史数据（197笔），OKX/MacB数据缺失 |
| Mac B bots | SSH不可达，Mac A本地无freqtrade_bots目录 |
| 缓存时效 | trade_journal.json为2026-05-02快照，OKX今日数据未收录 |

---

## 九、审计结论

1. **总亏损**: 历史缓存显示净盈利+$205.88（197笔，42.1%胜率），但OKX bots历史数据缺失无法确认总体盈亏。
2. **今日最大亏损**: DOGE/USDT批量止损约-$96~-120（8个bot），主因是策略信号同步导致全bot同向入场。
3. **Mac B bots**: 8081-8084当前0持仓，疑似全部空仓状态。
4. **高杠杆风险**: 当前无>=7x杠杆持仓，风险可控。
5. **force_exit依赖**: 大量exit_reason=force_exit（天眼/出山AI触发），非V6.5 P1/P2/P3止盈机制，止盈逻辑偏移。
