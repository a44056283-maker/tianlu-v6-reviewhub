# GPT_审核建议 · 20260504_143000_LOSS_AND_M1_AUDIT

## 审核结论

**有条件通过。**

本轮 13 个文件已完成亏损归因、M1 资金流审计、DCA 风险、出场误判、权限矩阵、L5 晋级规则等基础分析。当前可以进入“止血 + 资金流证据链重建 + 影子实验对接”阶段。

但不批准一次性直接执行所有实盘策略修改、DCA/杠杆调整、L5 自动晋级。原因是当前报告已经明确：系统存在 DOGE 批量止损循环、SOL SHORT DCA 满层、DCA 清除止损冷却、止盈过度收紧、高风险动作无认证等紧急风险。此时如果直接改实盘策略，可能放大亏损或引入新控制风险。

---

## 一、当前已确认的紧急风险

### P0-1：DOGE/USDT 批量止损循环

现象：8 个机器人同步做空 DOGE/USDT，批量止损后立即重新入场，形成循环损耗。

处理原则：

- 冻结 DOGE/USDT 自动新增入场 24 小时；
- DOGE 只能进入只读监控与 L5 影子实验；
- 禁止继续自动 DCA；
- 不删除已有仓位，不强制平仓，由风险出场策略单独审。

### P0-2：SOL/USDT SHORT DCA 满层

现象：SOL/USDT SHORT DCA 已满层，ROE 约 -27.9%。

处理原则：

- 暂停 SOL SHORT 的新增 DCA；
- 保留风险监控；
- 出场必须走出山AI / ExitDecisionGate / 人工确认，不允许自动扩大仓位。

### P0-3：DCA 触发时清除止损冷却

现象：`v65_autopilot.py` 中存在 DCA 触发后清除止损冷却的逻辑。

处理原则：

- 不允许直接修改代码；
- 先生成补丁草案；
- 补丁必须经过回测与 GPT 审核；
- 必须避免“刚止损 → 马上重新 DCA/入场”的循环。

### P0-4：连续亏损后止盈收紧到 10%

现象：自学习逻辑在连续亏损时可能把止盈阈值收紧到 10%。

处理原则：

- 连续亏损时不应自动提前平仓；
- 应增加出场后延续损失检测；
- 该逻辑先进入 L5 影子实验，不直接写实盘。

### P0-5：高风险动作缺少统一认证

现象：force_entry / force_exit 等动作仍缺少统一权限闸。

处理原则：

- 先生成 FORCE_ACTION_PERMISSION_MAP；
- 再设计 ForceActionGuard；
- 任何实际执行前必须人工确认。

---

## 二、允许 Claude 下一步执行的范围

允许执行，但必须分阶段：

### 第一阶段：止血与只读确认

1. 生成 DOGE 自动新增入场冻结方案；
2. 生成 SOL SHORT DCA 暂停方案；
3. 生成当前持仓风险快照；
4. 生成当前 12 机器人入场/DCA 状态矩阵；
5. 不修改实盘配置，只生成补丁草案。

输出：

- `DOGE_AUTO_ENTRY_FREEZE_PLAN.md`
- `SOL_SHORT_DCA_PAUSE_PLAN.md`
- `CURRENT_RISK_POSITION_SNAPSHOT.md`
- `12_BOT_ENTRY_DCA_STATUS_MATRIX.md`

### 第二阶段：M1-M5 参数与交易机器人对接设计

1. 将 M1 输出升级为 A/B/C/D/E 裁决；
2. 新增 flow_consensus_score；
3. 新增 flow_divergence_score；
4. 新增 exchange_outlier；
5. 新增 data_freshness_score；
6. 将 M1-M5 参数定义为证据层，不直接触发交易；
7. 生成与 FOttStrategy / api_autopilot / console_server 兼容的字段映射。

输出：

- `M1_M5_TO_BOT_COMPATIBILITY_SPEC.md`
- `M1_FUND_FLOW_DECISION_SCHEMA.md`
- `ENTRY_DECISION_GATE_SPEC.md`
- `EXIT_DECISION_GATE_SPEC.md`

### 第三阶段：补丁草案，不直接应用

1. DCA 清除止损冷却修复补丁草案；
2. DOGE 噪音过滤补丁草案；
3. SOL DCA 风险保护补丁草案；
4. 自学习止盈收紧逻辑修复草案；
5. ForceActionGuard 草案。

输出：

- `PROPOSED_PATCH_DCA_COOLDOWN_LOCK.md`
- `PROPOSED_PATCH_DOGE_NOISE_FILTER.md`
- `PROPOSED_PATCH_SOL_DCA_GUARD.md`
- `PROPOSED_PATCH_EXIT_TAKE_PROFIT_SELFLEARN.md`
- `PROPOSED_PATCH_FORCE_ACTION_GUARD.md`

### 第四阶段：L5 影子实验

1. 将所有新参数放入 L5 Shadow；
2. 不写 runtime_params；
3. 不改 config overlay；
4. 不自动晋级；
5. 生成 7 天观察指标。

输出：

- `L5_SHADOW_EXPERIMENT_FOR_M1_M5_RULES.md`
- `L5_NO_AUTO_PROMOTION_POLICY.md`
- `BACKTEST_AND_SHADOW_VALIDATION_CHECKLIST.md`

---

## 三、暂不批准的动作

以下动作暂不批准：

1. 直接修改实盘策略；
2. 直接修改 DCA_MAX_LAYER；
3. 直接修改杠杆；
4. 直接改 12 个机器人配置；
5. 直接应用 L5 自动晋级；
6. 直接新增 force_entry / force_exit 自动化；
7. 自动平仓或自动开仓；
8. 不经测试直接安装 LaunchAgent；
9. 把候选规则直接写入 runtime_params。

---

## 四、多子代理协作安排

Claude 应通过多子代理协作完成以下任务：

### 中书省：总协调

- 创建任务目录；
- 分发任务；
- 汇总报告；
- 打包 REVIEW_PACKAGE；
- push GitHub。

### 户部：资金流与 M1-M5 参数

- 设计 M1 A/B/C/D/E 裁决；
- 设计 flow_consensus_score、flow_divergence_score、exchange_outlier；
- 输出 M1-M5 到机器人兼容字段。

### 兵部：12 机器人状态矩阵

- 检查 9090-9097 与 8081-8084；
- 输出每个 bot 当前入场/DCA/风控状态；
- 不改配置。

### 刑部：风控与高风险动作

- 设计 ForceActionGuard；
- 设计 DCA Guard；
- 设计 DOGE/SOL 风险闸。

### 翰林院：L5 影子实验

- 将候选参数纳入 L5 shadow；
- 定义回测指标；
- 禁止自动晋级。

### 都察院：复核

- 检查是否误修改实盘；
- 检查是否包含密钥；
- 检查是否覆盖 12 个机器人；
- 检查是否可回滚。

---

## 五、Claude 下一步任务目录

Claude 应创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M1_M5_BOT_INTEGRATION_PLAN/
```

必须包含：

```text
00_MASTER_IMPLEMENTATION_PLAN.md
01_M1_M5_TO_BOT_COMPATIBILITY_SPEC.md
02_ENTRY_DECISION_GATE_SPEC.md
03_EXIT_DECISION_GATE_SPEC.md
04_DCA_AND_LEVERAGE_GUARD_SPEC.md
05_FORCE_ACTION_PERMISSION_MAP.md
06_L5_SHADOW_EXPERIMENT_PLAN.md
07_PROPOSED_PATCHES_INDEX.md
08_INTERNAL_QA_CHECKLIST.md
REVIEW_PACKAGE.zip
```

---

## 六、最终结论

可以开始实现“对接准备”和“规则补全”，但必须按影子实验和补丁草案方式推进。

当前阶段目标不是直接改实盘，而是：

```text
止血归因 → 资金流重建 → 规则补全 → 兼容性对接 → 补丁草案 → L5影子实验 → GPT审核 → 小范围上线
```

只有 GPT 审核通过后，才允许进入实盘修改阶段。
