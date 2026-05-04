# 天禄 V6.5 当前亏损归因与 M1 资金流重建升级报告

> 生成方：GPT / 架构师审核员
> 日期：2026-05-04
> 状态：待 Claude 多子代理协作执行
> 任务性质：只读审计、归因、止血建议、资金流证据链重建；暂不直接修改实盘策略

---

## 一、总判断

交易系统升级计划可以继续执行，但当前不应直接进入实盘规则升级。用户反馈“现在交易全部亏损”，因此阶段目标必须从“继续增强策略”调整为：

1. 亏损归因；
2. 暂停盲目扩大风险；
3. 重建 M1 资金流准确性；
4. 审核 DCA 与杠杆是否放大亏损；
5. 审核出场是否存在提前平仓；
6. 通过 L5 影子实验验证新参数；
7. 经 GPT 审核后再进入小范围实盘改造。

当前可以继续推进：OpenClaw、备份、缓存、UI、数据采集、L5 回测、M1 资金流重建。

当前暂不建议推进：实盘入场规则升级、自动加仓策略优化、自动晋级实盘参数、提高杠杆、扩大仓位。

---

## 二、当前最可能的问题链路

### 1. M1 资金流信号失真

M1 是入场证据链的第一层。如果 Gate / OKX / Binance 数据不同步，或 OHLCV、盘口、主动买卖、OI、资金费率存在延迟或缺失，后续天眼AI、api_autopilot 和 L5 回测都会基于错误证据做判断。

需要重点检查：

- 三所数据更新时间；
- 三所方向是否一致；
- 是否存在单交易所异常拉偏；
- 是否存在旧缓存；
- 是否存在数据源缺失；
- M1 信号是否直接影响入场或 DCA。

### 2. DCA 与杠杆放大错误方向

前序审计已经发现 DCA 层数、资金流触发、S/R 检查、强中弱杠杆等参数需要核查。尤其 DCA_MAX_LAYER 与注释存在冲突，必须先查清真实意图，再决定是否调整。

### 3. 出场链路可能造成误判

系统中存在 L5 动态止盈、S/R 出场、部分平仓、紧急退出、冷却和交易所止损等多个出场路径。如果缺少统一出场裁决，可能出现该持有时提前平、该止损时没止损、或多路径重复触发。

### 4. 控制面过多

当前存在 9099 控制台、7891 edict、OpenClaw、飞书、微信、cron、LaunchAgents、策略内部逻辑等多个影响系统行为的路径。必须明确哪些只能看，哪些只能建议，哪些能进入执行链路。

---

## 三、立即执行原则

### 可执行

- 当前亏损归因；
- M1 资金流准确性审计；
- 12 机器人亏损矩阵；
- 入场噪音路径分析；
- DCA 风险审计；
- 出场误判审计；
- L5 影子实验与回测；
- 缓存、备份、OpenClaw、UI 等基础设施修复。

### 暂不执行

- 不直接改实盘策略；
- 不直接改 12 个机器人配置；
- 不直接扩大仓位；
- 不直接提高杠杆；
- 不直接上线新入场规则；
- 不让 L5 候选参数自动进入实盘。

---

## 四、建议 Claude 采用多子代理协作

### 1. 中书省：总协调代理

职责：创建任务目录、分配任务、收集报告、生成总报告、打包交付、推送 GitHub。

输出：

- CURRENT_LOSS_AND_M1_AUDIT_SUMMARY.md
- GPT_REVIEW_PACKAGE.zip

### 2. 户部：数据与资金流代理

职责：审计 M1 数据源，检查 Gate / OKX / Binance 数据，检查 M1 缓存更新时间，判断是否存在数据延迟、缺失、单所异常，并提出 M1 重建参数。

输出：

- M1_FUND_FLOW_ACCURACY_AUDIT.md
- M1_DATA_SOURCE_HEALTH_MATRIX.md
- M1_REBUILD_PARAMETERS.md

### 3. 兵部：机器人与亏损矩阵代理

职责：覆盖 12 个机器人，统计每个机器人当前持仓、盈亏、交易所、策略、user_data，判断亏损是否集中在某些机器人、币种或交易所。

输出：

- BOT_LOSS_MATRIX_12_NODES.md
- CURRENT_POSITIONS_RISK_SNAPSHOT.md
- BOT_CONFIG_DIFF_CANDIDATES.md

### 4. 刑部：风控与高风险动作代理

职责：审计高风险交易动作入口、DCA 层数冲突、杠杆、仓位、最大持仓、退出路径，输出暂停/保留/人工确认建议。

输出：

- FORCE_ACTION_PERMISSION_MAP.md
- DCA_RISK_AUDIT_REPORT.md
- LEVERAGE_AND_EXPOSURE_RISK_REPORT.md

### 5. 工部：缓存与备份基础设施代理

职责：接续缓存与备份链路审计，验证每日交易参数备份，草拟 OpenClaw 每日备份脚本，执行 cache copy 方法探针，但不直接安装 LaunchAgent。

输出：

- TRADING_PARAMS_BACKUP_VERIFY_REPORT.md
- OPENCLAW_DAILY_BACKUP_PLAN.md
- CACHE_COPY_METHOD_PROBE.md
- L5_DATA_COLLECTOR_RECOVERY_PLAN.md

### 6. 翰林院：L5 与回测代理

职责：审计 L5 影子实验状态，检查 candidate/runtime 是否可能写入实盘，建立晋级闸门，设计误入场/误出场回测指标。

输出：

- L5_PROMOTION_GATE_RULES.md
- L5_SHADOW_BACKTEST_PLAN.md
- NOISE_REDUCTION_BACKTEST_SPEC.md

### 7. 都察院：复核代理

职责：检查所有子报告是否齐全，是否误修改真实系统，是否包含密钥，是否覆盖 12 个机器人，是否有回滚方案。

输出：

- INTERNAL_QA_CHECKLIST.md
- REVIEW_PACKAGE_INDEX.md

---

## 五、Claude 本轮任务目录

Claude 应创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_LOSS_AND_M1_AUDIT/
```

建议文件清单：

```text
00_CURRENT_LOSS_AND_M1_AUDIT_SUMMARY.md
01_M1_FUND_FLOW_ACCURACY_AUDIT.md
02_M1_DATA_SOURCE_HEALTH_MATRIX.md
03_BOT_LOSS_MATRIX_12_NODES.md
04_CURRENT_POSITIONS_RISK_SNAPSHOT.md
05_ENTRY_NOISE_CAUSE_REPORT.md
06_DCA_RISK_AUDIT_REPORT.md
07_EXIT_MISJUDGMENT_AUDIT_REPORT.md
08_FORCE_ACTION_PERMISSION_MAP.md
09_L5_PROMOTION_GATE_RULES.md
10_L5_SHADOW_BACKTEST_PLAN.md
11_BACKUP_CACHE_INFRA_NEXT_ACTIONS.md
12_INTERNAL_QA_CHECKLIST.md
REVIEW_PACKAGE.zip
```

完成后 push 到 GitHub，等待 GPT 审核。

---

## 六、必须回答的问题

Claude 总报告必须回答：

1. 当前是否建议暂停自动新增入场；
2. 当前是否建议暂停自动 DCA；
3. 哪些机器人亏损最多；
4. 哪些币种亏损最多；
5. 亏损是否集中在某个交易所；
6. M1 三所数据是否一致；
7. M1 是否存在数据延迟或缺失；
8. M1 是否存在单交易所异常拉偏；
9. DCA 是否放大亏损；
10. 杠杆是否放大亏损；
11. 出场是否存在提前平仓；
12. L5 数据是否可以用于影子回测；
13. 是否可以恢复实盘入场；
14. 哪些参数必须先进入 L5 影子实验；
15. 哪些操作必须等待 GPT 审核。

---

## 七、M1 资金流重建参数建议

户部代理需要设计并检查以下参数：

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

M1 最终不应只输出 long/short，而应输出：

```text
A：可作为入场证据
B：只能观察
C：分歧过高，禁止入场
D：数据不足，禁止判断
E：单所异常，降权处理
```

---

## 八、止血建议草案

在报告完成前，不直接修改实盘。

如果审计确认以下任一情况，应建议用户进入止血模式：

1. M1 数据明显延迟；
2. 三所资金流分歧高于阈值；
3. 单交易所异常拉偏；
4. DCA 触发来源不可靠；
5. 亏损集中在 DCA 订单；
6. 亏损集中在高杠杆仓位；
7. 出场后延续损失明显；
8. 某个机器人持续亏损。

止血模式建议：

```text
禁止自动新增入场；
禁止自动 DCA；
允许只读监控；
允许人工确认风险处理；
允许 L5 影子实验；
不允许 L5 自动晋级。
```

---

## 九、禁止 Claude 本轮执行的动作

1. 不修改实盘策略；
2. 不修改 12 个机器人配置；
3. 不停止机器人；
4. 不重启机器人；
5. 不调用交易所下单 API；
6. 不改 DCA 参数；
7. 不改杠杆；
8. 不安装新 LaunchAgent；
9. 不删除缓存；
10. 不把密钥、数据库、日志原文推送 GitHub。

---

## 十、GPT 审核后才允许进入的阶段

只有 GPT 审核通过后，才允许执行：

1. 修改 M1 资金流裁决算法；
2. 修改 DCA 触发条件；
3. 修改入场规则；
4. 修改出场规则；
5. 安装每日备份 LaunchAgent；
6. 修改 tianlu_cache_maintenance.py；
7. 恢复 L5 清算数据采集调度；
8. 小范围恢复自动入场。

---

## 十一、最终目标

本轮不是为了直接盈利优化，而是为了建立：

```text
真实亏损归因
准确 M1 资金流
入场噪音过滤
DCA 风险收口
出场误判识别
L5 影子回测
GPT 审核闭环
```

只有这些完成后，才进入实盘策略升级。
