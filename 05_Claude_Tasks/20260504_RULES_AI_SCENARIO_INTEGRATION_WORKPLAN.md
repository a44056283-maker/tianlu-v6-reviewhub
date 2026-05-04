# 天禄 V6.5 · M1-M5 数据规则接入交易机器人 + 天眼AI/出山AI场景话术工作计划

> 生成方：GPT / 架构师审核员  
> 日期：2026-05-04  
> 执行方：Claude Code 多子代理协作  
> 目标版本：V6.5.1 接入候选版  
> 当前原则：今天完成规则、字段、话术、补丁草案、dry-run、回滚包；不建议今天全量实盘上线。

---

## 一、总目标

本计划用于指导 Claude Code 继续推进天禄 V6.5 交易系统升级。

当前系统已经完成：

1. OpenClaw 飞书 / 微信 / 子代理恢复；
2. GitHub ReviewHub 审核闭环打通；
3. 缓存与备份链路审计；
4. 亏损归因与 M1 资金流审计；
5. DOGE 批量止损循环、SOL SHORT DCA 满层、DCA 清除止损冷却、止盈过早收紧、force 动作无认证等问题定位。

接下来重点不是继续盲目优化收益，而是完成：

```text
M1-M5 数据 → 规则证据层 → 天眼AI入场裁决 → 出山AI出场裁决 → 交易机器人兼容字段 → L5影子实验 → GPT审核 → 小范围灰度
```

---

## 二、时间判断

### 今天可完成

今天目标是完成 **V6.5.1 接入候选版**，包括：

1. M1-M5 到交易机器人字段映射；
2. EntryDecisionGate 入场统一裁决规则；
3. ExitDecisionGate 出场统一裁决规则；
4. 天眼AI入场场景话术；
5. 出山AI出场场景话术；
6. DOGE/SOL 止血规则草案；
7. DCA/杠杆保护规则草案；
8. ForceActionGuard 权限闸草案；
9. L5 Shadow Promotion 规则；
10. dry-run 检查；
11. 回滚包；
12. REVIEW_PACKAGE.zip。

### 2-3 天内完成

单机器人灰度与小范围实盘验证。

### 5-7 天内完成

全量 12 机器人稳定版。

---

## 三、今日不允许直接完成的事项

以下内容今天不能直接全量上线：

1. 12 个机器人全量重启；
2. 直接全量应用新入场规则；
3. 直接全量应用 DCA/杠杆修改；
4. L5 自动写入 live runtime；
5. 自动 force_entry / force_exit；
6. 未经 GPT 审核直接修改 12 个机器人配置；
7. 删除旧策略、旧缓存、旧备份；
8. 调用交易所 API 或执行真实下单动作。

今天只允许形成：

```text
规则完整版 + 话术完整版 + 补丁草案 + dry-run + 回滚包 + GPT审核包
```

---

## 四、Claude 多子代理分工

Claude 必须通过多子代理协作完成，不允许一个代理同时乱改全部模块。

### 1. 中书省 · 总协调代理

职责：

1. 创建任务目录；
2. 读取本计划；
3. 分发任务给各子代理；
4. 收集所有产物；
5. 生成总报告；
6. 打包 REVIEW_PACKAGE；
7. push 到 GitHub。

输出：

```text
00_MASTER_RULES_INTEGRATION_SUMMARY.md
REVIEW_PACKAGE.zip
```

### 2. 户部 · M1-M5 数据规则代理

职责：

1. 整理 M1-M5 所有可用字段；
2. 定义 M1-M5 统一 evidence payload；
3. 定义 M1 A/B/C/D/E 裁决等级；
4. 定义资金流一致性与异常交易所参数；
5. 保证 M1-M5 只作为证据层，不直接触发交易。

输出：

```text
01_M1_M5_TO_BOT_FIELD_MAPPING.md
01_M1_FUND_FLOW_DECISION_SCHEMA.md
01_M1_M5_EVIDENCE_PAYLOAD_SPEC.md
```

### 3. 天眼院 · 入场AI话术与入场裁决代理

职责：

1. 设计天眼AI入场场景话术；
2. 设计 EntryDecisionGate 完整规则；
3. 输出 A/B/C/D/E 五档入场裁决；
4. 明确禁止入场原因；
5. 将 M1-M5 证据转成天眼AI可解释语言。

输出：

```text
02_ENTRY_DECISION_GATE_FULL_RULES.md
04_TIANYAN_AI_SCENARIO_PROMPTS.md
```

### 4. 出山院 · 出场AI话术与出场裁决代理

职责：

1. 设计出山AI出场场景话术；
2. 设计 ExitDecisionGate 完整规则；
3. 增加出场后延续损失观察；
4. 区分“建议出场”和“已执行出场”；
5. 防止连续亏损时过早止盈。

输出：

```text
03_EXIT_DECISION_GATE_FULL_RULES.md
05_CHUSHAN_AI_SCENARIO_PROMPTS.md
```

### 5. 兵部 · 12 机器人兼容性代理

职责：

1. 覆盖 Mac A 9090-9097；
2. 覆盖 Mac B 8081-8084；
3. 生成 12 机器人兼容性矩阵；
4. 检查哪些机器人可接入新字段；
5. 不直接修改机器人配置。

输出：

```text
06_12_BOT_COMPATIBILITY_MATRIX.md
```

### 6. 刑部 · DCA/杠杆/权限闸代理

职责：

1. 设计 DCA/杠杆保护规则；
2. 设计 DOGE/SOL 紧急规则；
3. 设计 ForceActionGuard；
4. 明确 force_entry / force_exit 的权限、冷却、审计日志；
5. 不直接执行高风险动作。

输出：

```text
07_DOGE_SOL_EMERGENCY_RULES.md
08_DCA_LEVERAGE_GUARD_RULES.md
09_FORCE_ACTION_GUARD_RULES.md
```

### 7. 翰林院 · L5 影子实验与晋级规则代理

职责：

1. 设计 L5 Shadow Promotion 规则；
2. 所有新参数先进入 L5 shadow；
3. 禁止自动写 live runtime；
4. 生成候选参数、回测指标、晋级闸门；
5. 建立人工确认流程。

输出：

```text
10_L5_SHADOW_PROMOTION_RULES.md
```

### 8. 工部 · 补丁索引与dry-run代理

职责：

1. 汇总所有补丁草案；
2. 不直接应用实盘补丁；
3. 生成 proposed patches index；
4. 执行语法检查、JSON检查、dry-run；
5. 生成测试日志。

输出：

```text
11_PROPOSED_PATCHES_INDEX.md
12_DRY_RUN_TEST_LOG.md
```

### 9. 都察院 · QA与回滚代理

职责：

1. 检查是否误修改实盘；
2. 检查是否包含密钥；
3. 检查是否覆盖 12 个机器人；
4. 检查是否有完整回滚方案；
5. 生成回滚计划。

输出：

```text
13_ROLLBACK_PLAN.md
14_INTERNAL_QA_CHECKLIST.md
```

---

## 五、任务输出目录

Claude 创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_RULES_AI_SCENARIO_INTEGRATION/
```

必须包含：

```text
00_MASTER_RULES_INTEGRATION_SUMMARY.md
01_M1_M5_TO_BOT_FIELD_MAPPING.md
01_M1_FUND_FLOW_DECISION_SCHEMA.md
01_M1_M5_EVIDENCE_PAYLOAD_SPEC.md
02_ENTRY_DECISION_GATE_FULL_RULES.md
03_EXIT_DECISION_GATE_FULL_RULES.md
04_TIANYAN_AI_SCENARIO_PROMPTS.md
05_CHUSHAN_AI_SCENARIO_PROMPTS.md
06_12_BOT_COMPATIBILITY_MATRIX.md
07_DOGE_SOL_EMERGENCY_RULES.md
08_DCA_LEVERAGE_GUARD_RULES.md
09_FORCE_ACTION_GUARD_RULES.md
10_L5_SHADOW_PROMOTION_RULES.md
11_PROPOSED_PATCHES_INDEX.md
12_DRY_RUN_TEST_LOG.md
13_ROLLBACK_PLAN.md
14_INTERNAL_QA_CHECKLIST.md
REVIEW_PACKAGE.zip
```

---

## 六、M1-M5 统一字段规范

Claude 必须在 `01_M1_M5_TO_BOT_FIELD_MAPPING.md` 中定义以下字段：

### M1 资金流字段

```text
flow_consensus_score
flow_divergence_score
dominant_exchange
exchange_outlier
source_count
valid_exchange_count
book_taker_alignment
taker_oi_alignment
funding_pressure_state
data_freshness_score
m1_signal_trust_level
```

### M2 支撑压力字段

```text
nearest_support
nearest_resistance
support_distance_pct
resistance_distance_pct
sr_touch_count
sr_quality_score
false_breakout_risk
structure_alignment
```

### M3 巨量K线字段

```text
giant_candle_direction
giant_candle_strength
volume_ratio
after_giant_confirm_bars
reversal_probability
continuation_probability
fake_reversal_risk
```

### M4 技术面字段

```text
trend_direction
macd_state
rsi_state
atr_state
volatility_state
multi_tf_alignment
technical_score
```

### M5/L5 进化字段

```text
shadow_rule_id
candidate_param_id
entry_noise_score
exit_noise_score
post_exit_continuation_loss
missed_profit_after_exit
promotion_gate_state
manual_confirm_required
```

---

## 七、EntryDecisionGate 入场规则要求

入场裁决必须输出：

```text
A：可入场
B：等待确认
C：噪音禁止
D：数据不足
E：单所异常，降权处理
```

必须满足：

1. M1 三所一致性不足时，禁止 A；
2. M1 数据新鲜度不足时，输出 D；
3. 单所异常拉偏时，输出 E；
4. M2 位置质量不足时，不允许 A；
5. M3 巨量未确认时，不允许直接入场；
6. M4 多周期不一致时，降级；
7. DOGE 风险窗口内禁止自动新增；
8. DCA 不能绕过 EntryDecisionGate。

---

## 八、ExitDecisionGate 出场规则要求

出场裁决必须输出：

```text
HOLD：继续持有
WATCH：观察
PARTIAL_EXIT：建议部分止盈
FULL_EXIT_REVIEW：建议全平复核
EMERGENCY_REVIEW：紧急风险复核
```

必须满足：

1. 连续亏损后不自动过早止盈；
2. 出场前检查趋势延续概率；
3. 出场前检查 post_exit_continuation 风险；
4. force_exit 默认进入人工确认；
5. L5 动态止盈不得直接无确认全平；
6. S/R exit 不得单独触发强制出场。

---

## 九、天眼AI场景话术要求

天眼AI话术必须覆盖：

1. A档可入场；
2. B档等待确认；
3. C档噪音禁止；
4. D档数据不足；
5. E档单所异常；
6. DOGE临时冻结；
7. SOL DCA风险；
8. M1分歧；
9. M2位置不佳；
10. M3巨量未确认；
11. M4趋势不一致。

每条话术必须包含：

```text
结论
原因
证据
风险
是否允许自动执行
是否需要人工确认
```

---

## 十、出山AI场景话术要求

出山AI话术必须覆盖：

1. 继续持有；
2. 观察；
3. 部分止盈；
4. 全平复核；
5. 紧急风险复核；
6. 防止提前平仓；
7. 出场后延续风险；
8. SOL DCA满层风险；
9. DOGE止损循环风险；
10. 止盈10%收紧风险。

每条话术必须包含：

```text
当前建议
触发证据
风险解释
是否已执行
是否仅建议
下一步动作
```

---

## 十一、禁止 Claude 当前执行

本轮禁止：

1. 不直接重启 9090-9097；
2. 不直接重启 8081-8084；
3. 不直接执行 force_entry；
4. 不直接执行 force_exit；
5. 不调用交易所 API；
6. 不把 L5 候选写入 live runtime；
7. 不直接全量修改 12 个机器人配置；
8. 不删除旧策略；
9. 不删除历史缓存；
10. 不提交密钥或数据库。

---

## 十二、今日完成标准

今天 Claude 完成后，GPT 应能审核：

1. M1-M5 字段是否完整；
2. 入场裁决是否完整；
3. 出场裁决是否完整；
4. 天眼AI话术是否能解释入场；
5. 出山AI话术是否能解释出场；
6. 12机器人是否兼容；
7. DOGE/SOL止血规则是否合理；
8. DCA/杠杆保护是否合理；
9. force动作是否被权限闸收口；
10. L5 是否仍保持 shadow，不写实盘；
11. dry-run 是否通过；
12. 是否有回滚方案。

---

## 十三、给 Claude 的直接执行话术

```text
你现在执行天禄 V6.5 规则与AI场景接入工作计划。

目标：今天完成 V6.5.1 接入候选版，包括 M1-M5 到交易机器人字段映射、EntryDecisionGate、ExitDecisionGate、天眼AI场景话术、出山AI场景话术、12机器人兼容性、DOGE/SOL止血规则、DCA/杠杆保护、ForceActionGuard、L5 Shadow Promotion、dry-run 和回滚包。

要求：通过多子代理协作完成。

本轮只生成规则、话术、补丁草案、dry-run 和 REVIEW_PACKAGE，不直接全量实盘上线。

输出到：
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_RULES_AI_SCENARIO_INTEGRATION/

完成后 push GitHub，等待 GPT 审核。
```
