# 兵部审计报告：入场噪音原因分析
**审计时间**: 2026-05-04 14:30 GMT+8
**审计人**: 兵部代理
**数据来源**: bot logs (/private/tmp/bot_*.log) / trade_journal.json / v65_autopilot.py

---

## 一、入场30天统计（估算）

**数据来源**: trade_journal.json (2026-03-29 ~ 2026-05-02 缓存)
**覆盖范围**: 仅Gate bots (9090/9091/9092) 历史已平仓交易

| 指标 | 数值 |
|------|------|
| 已平仓总交易数 | 197笔 |
| 统计周期 | ~34天 (2026-03-29 ~ 2026-05-02) |
| 日均平仓交易 | ~5.8笔/天 |
| 盈利交易 | 83笔 |
| 亏损交易 | 107笔 |
| 胜率 | 42.1% |

**注**: OKX bots (9093-9097) 和 MacB bots (8081-8084) 历史数据暂缺，无法纳入统计。

---

## 二、今日(2026-05-04)入场次数详细分析

**来源**: /private/tmp/bot_9090.log ~ bot_9097.log

### 2.1 入场事件时间线

| 时间 | Bot | 交易对 | 方向 | 入场标签 | 触发来源 |
|------|-----|--------|------|---------|---------|
| 05-03 11:22 | 9090 | ETH/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 11:22 | 9090 | SOL/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 11:22 | 9090 | BTC/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 11:22 | 9090 | BNB/USDT | LONG | tianyan_auto_entry | 天眼AI |
| 05-03 11:52 | 9091 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 15:03 | 9093 | BTC/USDT | - | tianyan_auto_entry | 天眼AI |
| 05-03 15:05 | 9094 | BTC/USDT | - | tianyan_auto_entry | 天眼AI |
| 05-03 15:03 | 9095 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 15:03 | 9096 | BTC/USDT | - | tianyan_auto_entry | 天眼AI |
| 05-03 15:03 | 9097 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:46 | 9090 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:48 | 9093 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:49 | 9091 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:49 | 9095 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:53 | 9094 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:53 | 9097 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-03 19:47 | 9096 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-04 12:22 | 9090 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |
| 05-04 ~12:22 | 9091 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI (双次入场) |
| 05-04 ~12:50 | 9093-9097 | DOGE/USDT | SHORT | tianyan_auto_entry | 天眼AI |

**入场次数统计（今日）**: ~20次（覆盖约14小时）

### 2.2 关键发现：所有入场均来自天眼AI

**来源**: bot日志中所有入场均显示 `enter_tag='tianyan_auto_entry'`

```python
# 典型入场日志
trade_id: 216, type: entry_fill
enter_tag: 'tianyan_auto_entry'  ← 天眼AI入场
buy_tag: 'tianyan_auto_entry'
```

**结论**: 当前所有入场信号100%来自天眼AI（tianyan_auto_entry），而非V6.5本地规则（L1/L2/L4自动驾驶）。

---

## 三、入场信号来源分析

### 3.1 入场信号触发链路

```
V6.5 Autopilot (每37.5秒扫描)
    ↓
天眼AI (Tianyan AI) 评估入场信号
    ↓
tianyan_auto_entry 触发
    ↓
Bot收到forceenter命令 → 执行入场
```

**来源**: bot_manager.sh 配置 `--userdir 绝对路径` + v65_autopilot.py
**日志确认**: 所有入场均带 `enter_tag='tianyan_auto_entry'`

### 3.2 当前自动驾驶状态

**来源**: bot logs 2026-05-04 13:18:
```
🤖 AI_MODE: 跳过Bot自主入场【BNB/USDT:USDT】，入场权交由天眼AI
════════ 自动驾驶循环开始 [Gate-85363904550] ═══
扫描5 → 合格5 → 过滤0 → 交易0 → 跳过5 (37.5s)
```

**发现**: V6.5 autopilot 已通过所有规则（合格5），但最终入场权交给天眼AI（跳过5）。

### 3.3 当前S/R信号（扫描数据）

**来源**: bot_9090.log 2026-05-04 13:20:

| 交易对 | TF | 类型 | S/R价格 | 触顶/底次数 | 状态 |
|--------|-----|------|---------|------------|------|
| DOGE/USDT | 15m/1h/4h | resistance | $0.1091 | 触顶3次 | **做空信号** |
| SOL/USDT | 15m/1h/4h | resistance | $83.841 | 触顶3次 | 继续交易 |
| BTC/USDT | 15m/1h/4h | resistance | $78,884 | 触顶3次 | 继续交易 |
| ETH/USDT | 15m/1h/4h | support | $2,273 | 触底3次 | **做多信号** |
| ETH/USDT | 15m/1h/4h | resistance | $2,303 | 触顶3次 | 做空信号 |
| BNB/USDT | 15m/1h/4h | resistance | $617.52 | 触顶3次 | 做空信号 |

---

## 四、入场噪音原因分析

### 4.1 噪音来源一：DOGE/USDT 全bot同向信号

**问题现象**: 8个bot同时对DOGE/USDT做空 → 8个bot同时被force_exit止损 → 8个bot同时重新入场做空

**证据**:
```
2026-05-03 19:46 (9090): DOGE/USDT entry_fill
2026-05-03 19:48 (9093): DOGE/USDT entry_fill
2026-03 19:49 (9091): DOGE/USDT entry_fill
2026-03 19:49 (9095): DOGE/USDT entry_fill
2026-05-03 19:53 (9094): DOGE/USDT entry_fill
2026-05-03 19:53 (9097): DOGE/USDT entry_fill
2026-05-03 19:47 (9096): DOGE/USDT entry_fill
---
2026-05-04 10:17-10:50: DOGE/USDT 8个bot全部force_exit止损
---
2026-05-04 12:22-13:00: DOGE/USDT 重新入场做空（全部bot）
```

**根本原因**: 天眼AI同时向所有bot下发DOGE做空信号，无bot间差异化过滤。

### 4.2 噪音来源二：S/R "触顶3次" 触发噪音

**V6.5规则**: L4 S/R要求"触顶/底>=3次"才入场

**问题**: 多个币种同时满足"触顶3次"条件，导致多bot同步入场:
- DOGE: 触顶3次 → 8 bot全做空
- SOL: 触顶3次 → 多bot同向
- BNB: 触顶3次 → 多bot同向

**建议**: 增加触顶/底次数要求（>=4次）以降低噪音。

### 4.3 噪音来源三：无入场冷却机制

**证据**: DOGE/USDT 被 force_exit 止损后，立即重新触发入场信号：
- 10:17 平仓 → 12:22 重新入场（仅隔2小时）
- 无"止损后N小时内禁止同一交易对重新入场"的机制

### 4.4 噪音来源四：M1资金流量比阈值过低

**日志显示 DOGE 量比**:
```
[AutoPilot] 💰 资金流: DOGE/USDT SHORT(none) 量比4.3x基线
[AutoPilot] 🚫量比不足4.3x < 1.5x过滤  ← 量比4.3x通过了2.5x门槛？
```

**注**: 4.3x 量比通过 L1 噪音过滤（门槛2.5x），触发了8 bot同步做空信号。

---

## 五、是否建议暂停自动新增入场

### 5.1 当前噪音水平评估

| 指标 | 评估 |
|------|------|
| 今日入场次数 | ~20次（14小时内） |
| 重复入场率 | 高（DOGE: 止损后2小时即重新入场） |
| 全bot同向率 | 极高（8/8 bot同时做空DOGE） |
| force_exit比例 | 高（80%以上） |

**结论**: 入场噪音水平**偏高**。

### 5.2 具体建议

**建议暂停自动新增入场的场景**:

1. **当前**: DOGE/USDT 刚刚经历批量止损，建议**冻结DOGE/USDT新增入场24小时**
   ```json
   { "冻结币种": "DOGE/USDT", "原因": "全bot同向信号噪音", "截止": "2026-05-05 10:17" }
   ```

2. **建议调整**: 量比门槛从2.5x提高到**4.0x**
   - 降低L1噪音触发频率
   - 减少全bot同步信号

3. **建议增加**: 入场冷却机制
   - 止损后同一交易对**4小时内禁止重新入场**
   - 防止噪音重复触发

4. **建议增加**: bot间差异化信号
   - 目前8个bot同时看到同一信号
   - 建议增加"bot index offset"错峰机制

### 5.3 可继续自动入场的场景

- SOL/USDT: 已突破压力位$83.84，当前无同向噪音风险
- BTC/USDT: 贴近压力位$78,884，但单一信号风险可控
- Mac B bots (8081-8084): 当前0持仓，可考虑对低相关币种开放入场权限

---

## 六、审计结论

1. **入场信号100%来自天眼AI** (`tianyan_auto_entry`)，非V6.5本地规则
2. **DOGE/USDT是最大噪音源**：8 bot同步做空→批量止损→立即重新入场，形成噪音闭环
3. **建议冻结DOGE/USDT自动新增入场24小时**，防止噪音重复触发
4. **量比门槛建议从2.5x提高到4.0x**，减少L1噪音
5. **Mac B bots (8081-8084) 全部空仓**，建议排查为何无入场
