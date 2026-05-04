# 天禄 V6.5 今日实盘改造执行方案 · 多子代理协作版

> 生成方：GPT / 架构师审核员  
> 日期：2026-05-04  
> 状态：给 Claude Code 执行  
> 目标：今天推进实盘策略修改、DCA/杠杆调整、L5 晋级链路、force_entry/force_exit 权限闸、12 机器人配置一致性。  
> 核心原则：今天可以完成“代码与配置落地”，但必须分阶段、可回滚、先备份、先验证、先小范围灰度。

---

## 0. 总判断

用户要求今天完成以下内容：

1. 实盘策略修改；
2. DCA / 杠杆实盘调整；
3. L5 自动晋级链路；
4. 自动 force_entry / force_exit；
5. 直接改 12 个机器人配置。

GPT 审核后允许 Claude 推进，但执行方式必须变成：

```text
先止血 → 再建统一闸门 → 再改配置 → 再小范围灰度 → 再全量同步 → 最后输出回滚包
```

禁止直接“一次性全量改 12 个机器人并立即放开自动交易”。

今天可以完成的定义是：

```text
1. 完成代码补丁；
2. 完成配置补丁；
3. 完成 12 机器人配置一致性更新；
4. 完成本地检查；
5. 完成灰度执行方案；
6. 完成回滚包；
7. 完成 REVIEW_PACKAGE；
8. 等用户确认后再执行重启/全量生效。
```

---

## 1. 今日 P0 实盘止血目标

根据亏损归因报告，当前优先处理：

### P0-1 DOGE/USDT 批量止损循环

目标：冻结 DOGE/USDT 自动新增入场 24 小时。

要求：

- 不强平已有仓位；
- 不删除 DOGE 数据；
- 只禁止新增自动入场和自动 DCA；
- 允许只读监控和人工确认出场。

### P0-2 SOL/USDT SHORT DCA 满层

目标：暂停 SOL/USDT SHORT 继续 DCA。

要求：

- 不直接平仓；
- 不继续加仓；
- 保持风险监控；
- 出场走 ExitDecisionGate 或人工确认。

### P0-3 DCA 清除止损冷却

目标：修复 DCA 触发后清除止损冷却的风险。

要求：

- 禁止刚止损后立即重新入场或 DCA；
- 加入 cooldown lock；
- 保留日志；
- 补丁必须可回滚。

### P0-4 自学习止盈收紧到 10%

目标：连续亏损时不自动提前收紧止盈。

要求：

- 连续亏损后进入观察，而不是提前平仓；
- 引入 post_exit_continuation 观察指标；
- 新逻辑先进入 L5 shadow。

### P0-5 force_entry / force_exit 无统一确认

目标：所有高风险动作统一经过 ForceActionGuard。

要求：

- force_entry 默认禁止自动执行；
- force_exit 默认要求人工确认；
- 紧急风险出场可进入 pending queue，但不直接执行；
- 每次高风险动作必须写 audit log。

---

## 2. 多子代理分工

Claude 必须使用多子代理协作，禁止一个代理乱改全部文件。

### 2.1 中书省 · 总控代理

职责：

1. 创建今日任务目录；
2. 创建统一备份目录；
3. 分配子代理任务；
4. 收集所有补丁；
5. 统一执行本地检查；
6. 输出总报告；
7. 打包 REVIEW_PACKAGE；
8. 推送 GitHub。

输出：

```text
00_MASTER_LIVE_ROLLOUT_SUMMARY.md
REVIEW_PACKAGE.zip
```

### 2.2 兵部 · 12 机器人配置代理

职责：

1. 读取 9090-9097 与 8081-8084 配置；
2. 生成 12_BOT_CONFIG_BEFORE_AFTER_MATRIX.md；
3. 生成统一配置补丁；
4. 不直接重启机器人；
5. 检查配置 JSON。

输出：

```text
01_12_BOT_CONFIG_BEFORE_AFTER_MATRIX.md
01_12_BOT_CONFIG_PATCH_PLAN.md
```

### 2.3 户部 · M1-M5 资金流与参数代理

职责：

1. 实现 M1 A/B/C/D/E 裁决字段；
2. 增加 flow_consensus_score、flow_divergence_score、exchange_outlier、data_freshness_score；
3. 将 M1-M5 输出转成统一 evidence payload；
4. 保持 M1-M5 为证据层，不直接下单。

输出：

```text
02_M1_M5_EVIDENCE_PAYLOAD_SPEC.md
02_M1_M5_COMPATIBILITY_PATCH_PLAN.md
```

### 2.4 刑部 · DCA / 杠杆 / force 动作代理

职责：

1. 修改 DCA Guard；
2. 修复 DCA 清除止损冷却；
3. 限制 DOGE 自动新增和 DCA；
4. 限制 SOL SHORT 继续 DCA；
5. 建立 ForceActionGuard。

输出：

```text
03_DCA_LEVERAGE_GUARD_PATCH.md
03_FORCE_ACTION_GUARD_PATCH.md
03_RISK_ACTION_AUDIT_LOG_SPEC.md
```

### 2.5 出山院 · 出场策略代理

职责：

1. 审查 P1/P2/P3；
2. 暂停连续亏损后自动止盈收紧；
3. 增加 post_exit_continuation 观测字段；
4. 不直接触发自动 force_exit。

输出：

```text
04_EXIT_DECISION_GATE_PATCH.md
04_POST_EXIT_CONTINUATION_SPEC.md
```

### 2.6 翰林院 · L5 进化代理

职责：

1. 建立 L5 Candidate Registry；
2. 允许 L5 生成候选参数；
3. 默认禁止 auto_apply_to_live；
4. 如果用户要求“自动晋级”，必须设计成“自动提交候选 + 人工确认应用”；
5. 不允许 L5 直接写实盘 runtime。

输出：

```text
05_L5_CANDIDATE_REGISTRY_PATCH.md
05_L5_PROMOTION_GATE_PATCH.md
05_L5_NO_AUTO_LIVE_APPLY_POLICY.md
```

### 2.7 都察院 · QA 代理

职责：

1. 检查是否改了密钥；
2. 检查是否误触发交易；
3. 检查 JSON / Python 语法；
4. 检查 12 机器人配置一致性；
5. 检查回滚包。

输出：

```text
06_INTERNAL_QA_CHECKLIST.md
06_ROLLBACK_PLAN.md
```

---

## 3. 任务目录

Claude 创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT/
```

必须输出：

```text
00_MASTER_LIVE_ROLLOUT_SUMMARY.md
01_12_BOT_CONFIG_BEFORE_AFTER_MATRIX.md
01_12_BOT_CONFIG_PATCH_PLAN.md
02_M1_M5_EVIDENCE_PAYLOAD_SPEC.md
02_M1_M5_COMPATIBILITY_PATCH_PLAN.md
03_DCA_LEVERAGE_GUARD_PATCH.md
03_FORCE_ACTION_GUARD_PATCH.md
03_RISK_ACTION_AUDIT_LOG_SPEC.md
04_EXIT_DECISION_GATE_PATCH.md
04_POST_EXIT_CONTINUATION_SPEC.md
05_L5_CANDIDATE_REGISTRY_PATCH.md
05_L5_PROMOTION_GATE_PATCH.md
05_L5_NO_AUTO_LIVE_APPLY_POLICY.md
06_INTERNAL_QA_CHECKLIST.md
06_ROLLBACK_PLAN.md
PATCH.diff
TEST_LOG.md
REVIEW_PACKAGE.zip
```

---

## 4. 执行边界

### 允许 Claude 今天完成

1. 代码补丁；
2. 配置补丁；
3. 12 机器人一致性配置准备；
4. 本地语法检查；
5. 不启动机器人情况下的 dry-run 检查；
6. 回滚包；
7. GitHub REVIEW_PACKAGE。

### 需要用户最终确认后才能执行

1. 重启 9090-9097；
2. 重启 8081-8084；
3. 应用实盘配置；
4. 启用自动 force_entry；
5. 启用自动 force_exit；
6. L5 候选参数写入 live runtime。

---

## 5. 具体修改要求

### 5.1 DOGE 自动入场冻结

新增配置项：

```json
{
  "temporary_pair_freeze": {
    "DOGE/USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "allow_manual_exit": true,
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  }
}
```

执行要求：

- 写入统一 runtime 参数或风控配置；
- 不直接删 DOGE；
- 不影响只读监控。

### 5.2 SOL SHORT DCA 暂停

新增配置项：

```json
{
  "dca_pause_rules": {
    "SOL/USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true,
      "allow_exit_review": true
    }
  }
}
```

### 5.3 DCA 冷却锁

新增逻辑：

```text
如果最近一次止损或强制退出发生在 cooldown window 内：
- 禁止自动 DCA；
- 禁止自动重新入场；
- 写入 risk_action_audit_log；
- 进入观察队列。
```

### 5.4 ForceActionGuard

所有高风险动作必须统一检查：

```text
action_type
pair
direction
source
bot_id
risk_level
manual_confirm_required
cooldown_ok
permission_ok
audit_id
```

默认策略：

```text
force_entry：默认禁止自动执行
force_exit：默认人工确认
emergency_exit：只生成 pending action，不直接执行
```

### 5.5 L5 晋级链路

用户要求 L5 自动晋级，但基于风险，今天只能实现：

```text
自动生成候选
自动打分
自动提交晋级建议
人工确认后应用
```

禁止：

```text
L5 直接写 runtime_params
L5 直接改 config overlay
L5 直接改策略源码
```

---

## 6. 验证要求

Claude 必须执行：

```bash
python3 -m py_compile 相关 Python 文件
python3 -m json.tool 相关 JSON 文件
bash -n 相关 shell 文件
```

必须生成：

```text
TEST_LOG.md
```

必须确认：

```text
是否修改密钥：没有
是否调用交易所 API：没有
是否执行 force_entry：没有
是否执行 force_exit：没有
是否重启机器人：没有
是否覆盖旧备份：没有
```

---

## 7. 回滚要求

Claude 必须生成完整回滚包：

```text
04_BACKUPS/live_rollout_时间戳/
```

包含：

1. 修改前文件；
2. 修改后文件清单；
3. 回滚命令；
4. 哪些服务需要重启；
5. 回滚后如何验证。

---

## 8. GPT 最终审核点

完成后 GPT 审核：

1. DOGE freeze 是否只阻止新增，不误伤持仓管理；
2. SOL DCA pause 是否只阻止加仓，不误伤出场；
3. DCA cooldown lock 是否真正阻止止损循环；
4. ForceActionGuard 是否覆盖所有高风险入口；
5. L5 是否仍禁止直接写 live；
6. 12 机器人配置是否一致；
7. 是否有完整回滚方案。

---

## 9. 给 Claude 的直接执行话术

```text
你现在执行天禄 V6.5 今日实盘改造准备任务。

用户要求今天完成实盘策略修改、DCA/杠杆调整、L5 晋级链路、force_entry/force_exit 权限闸、12 机器人配置一致性。

你必须通过多子代理协作完成，但本轮只允许完成代码补丁、配置补丁、dry-run 验证、回滚包和 REVIEW_PACKAGE。

不允许直接重启 9090-9097 / 8081-8084。
不允许直接执行 force_entry / force_exit。
不允许调用交易所 API。
不允许 L5 直接写 live runtime。

请按本文件的七个子代理分工执行，并输出到：
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT/

完成后 push GitHub，等待 GPT 审核。
```
