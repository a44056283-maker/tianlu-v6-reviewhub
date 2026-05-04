# 都察院 QA 检查清单

> 审计时间：2026-05-04 13:25
> 审计员：都察院

---

## 一、文件完整性检查

| 编号 | 文件 | 状态 | 大小 |
|------|------|------|------|
| 01 | M1_FUND_FLOW_ACCURACY_AUDIT.md | ✅ | 7.6KB |
| 02 | M1_DATA_SOURCE_HEALTH_MATRIX.md | ✅ | 3.2KB |
| 03 | M1_REBUILD_PARAMETERS.md | ✅ | 8.9KB |
| 03 | BOT_LOSS_MATRIX_12_NODES.md | ✅ | 7.9KB |
| 04 | CURRENT_POSITIONS_RISK_SNAPSHOT.md | ✅ | 8.9KB |
| 05 | ENTRY_NOISE_CAUSE_REPORT.md | ✅ | 8.0KB |
| 06 | DCA_RISK_AUDIT_REPORT.md | ✅ | 5.4KB |
| 07 | EXIT_MISJUDGMENT_AUDIT_REPORT.md | ✅ | 7.8KB |
| 08 | FORCE_ACTION_PERMISSION_MAP.md | ✅ | 7.4KB |
| 09 | L5_PROMOTION_GATE_RULES.md | ✅ | 6.3KB |
| 10 | L5_SHADOW_BACKTEST_PLAN.md | ✅ | 6.7KB |
| 11 | BACKUP_CACHE_INFRA_NEXT_ACTIONS.md | ✅ | 6.0KB |

**结果：12/12 文件全部生成 ✅**

---

## 二、必须回答的问题检查

| 问题 | 来源 | 状态 | 摘要 |
|------|------|------|------|
| 当前是否建议暂停自动新增入场 | 05_ENTRY_NOISE | ✅ | **建议冻结 DOGE/USDT 24小时** |
| 当前是否建议暂停自动 DCA | 06_DCA_RISK | ✅ | 建议暂停（SOL DCA满层ROE -27.9%） |
| 哪些机器人亏损最多 | 03_BOT_LOSS_MATRIX | ✅ | DOGE批量止损-$96~$120 |
| M1三所数据是否一致 | 01_M1_FUND_FLOW | ✅ | 三所有覆盖，Binance净流入缺失 |
| M1是否存在数据延迟或缺失 | 01_M1_FUND_FLOW | ✅ | V2 Shadow停更2天 |
| DCA是否放大亏损 | 06_DCA_RISK | ✅ | 是（SOL SHORT DCA满层） |
| 出场是否存在提前平仓 | 07_EXIT_MISJUDGMENT | ✅ | 存在（连续亏损收紧止盈至10%） |
| L5数据是否可用于影子回测 | 09_L5_PROMOTION | ✅ | 可用，但candidate仅21个样本 |
| 是否可以恢复实盘入场 | 05_ENTRY_NOISE | ⚠️ | DOGE除外，其他建议观察 |
| 哪些参数必须先入L5影子实验 | 10_L5_SHADOW | ✅ | 见L5_SHADOW_BACKTEST_PLAN |
| 哪些操作必须等待GPT审核 | 全部 | ✅ | 见总报告 |

---

## 三、禁止事项检查

| 禁止项 | 执行情况 |
|--------|---------|
| 不修改实盘策略 | ✅ 未执行 |
| 不修改12个机器人配置 | ✅ 未执行 |
| 不停止/重启机器人 | ✅ 未执行 |
| 不调用交易所下单API | ✅ 未执行 |
| 不改DCA参数 | ✅ 未执行 |
| 不改杠杆 | ✅ 未执行 |
| 不安装新LaunchAgent | ✅ 未执行 |
| 不删除缓存 | ✅ 未执行 |
| 不把密钥推送到GitHub | ✅ 脱敏处理 |

---

## 四、数据质量评估

| 数据源 | 时效 | 评估 |
|--------|------|------|
| trade_journal.json | 2026-05-02 | ⚠️ 缓存，非实时 |
| daily_dept_report.json | 2026-05-04 10:02 | ✅ 实时 |
| m1_cache.db | 2026-05-04 13:10 | ✅ 实时 |
| m4_cache.db | 2026-05-04 09:37 | ✅ 实时 |
| L5 shadow lab | 2026-05-04 12:34 | ✅ 实时 |
| bot logs | 2026-05-04 | ✅ 实时 |
| M4_cache.db | 仅12KB | ⚠️ 严重偏小 |

---

## 五、关键风险标记

| 风险 | 等级 | 描述 |
|------|------|------|
| SOL/USDT SHORT DCA满层 | 🔴 紧急 | ROE -27.9%，需立即关注 |
| DOGE/USDT 批量止损循环 | 🔴 紧急 | 8 bots同步做空→止损→重新入场 |
| DCA触发清除止损冷却 | 🔴 紧急 | v65_autopilot.py:6269-6272 |
| M4_cache.db 仅12KB | 🟡 可疑 | 可能数据采集异常 |
| 自学习收紧止盈10% | 🟡 中风险 | 连续亏损时提前平仓 |
| 高风险动作无认证 | 🟡 中风险 | force_entry/exit无任何确认 |

---

## 六、结论

**本轮审计完成，可以交付 GPT 审核。**

无文件缺失，无禁止动作执行，数据质量基本可靠（trade_journal.json 为缓存是已知限制）。

**止血建议：** 立即冻结 DOGE/USDT 自动新增入场24小时；监控 SOL/USDT SHORT DCA仓位。
