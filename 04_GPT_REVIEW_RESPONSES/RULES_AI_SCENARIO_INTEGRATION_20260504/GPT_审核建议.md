# GPT_审核建议 · RULES_AI_SCENARIO_INTEGRATION_20260504

## 审核结论

**有条件通过，但不得直接进入实盘执行。**

本轮交付的方向正确，已经完成 V6.5.1 规则与 AI 场景接入候选版的主要设计材料，包括 M1-M5 字段映射、EntryDecisionGate、ExitDecisionGate、天眼AI话术、出山AI话术、12机器人兼容性、DOGE/SOL止血、DCA/杠杆保护、ForceActionGuard、L5 Shadow Promotion、dry-run 和回滚包。

但是，当前交付包仍存在明显的执行前阻断项：

1. QA 清单显示 57 项检查中仅 4 项确认，53 项仍待确认；
2. dry-run 日志显示无法实际执行 `py_compile` 和 JSON 校验，属于人工审查，不等于通过；
3. 9091-9097 overlay 备份缺失；
4. Mac B 8081-8084 仍未实际验证；
5. 当前包偏向规则与设计，尚不能作为直接实盘上线依据。

因此，本轮只能批准进入“Stage A：只读补验证 + 配置级灰度准备”，不能直接上线全部规则。

---

## 一、已确认有效的内容

### 1. 总体交付范围完整

总报告说明本轮目标是完成 V6.5.1 接入候选版，覆盖 M1-M5 字段映射、入场闸门、出场闸门、天眼AI/出山AI话术、12机器人兼容性、DOGE/SOL止血、DCA/杠杆保护、ForceActionGuard、L5影子实验、dry-run、回滚计划等内容。

### 2. EntryDecisionGate 设计方向正确

EntryDecisionGate 明确所有入场信号必须经过统一门控，只有 A 档允许自动驾驶入场，B 档等待确认，C/D/E 禁止入场或降权，这个方向符合“减少入场噪音”的目标。

### 3. M1/M2/M3/M4/L5 的证据层设计方向正确

M1 资金流、M2 支撑压力、M3 巨量K线、M4 技术面、L5 影子实验被统一为 evidence payload，而不是直接下单，这个方向正确。

### 4. 天眼AI/出山AI话术作为解释层是必要的

本轮将 AI 话术纳入交易解释链，有助于用户在手机端和飞书/微信端理解“为什么允许入场、为什么禁止入场、为什么建议持有、为什么建议出场复核”。

---

## 二、执行前阻断项

### 阻断项 1：QA 未完成

`14_INTERNAL_QA_CHECKLIST.md` 中显示：

- 文件完整性 14 项：0 通过，14 待确认；
- 禁止事项 12 项：0 通过，12 待确认；
- 补丁编号与范围 8 项：0 通过，8 待确认；
- 备份验证 6 项：0 通过，6 待确认；
- Mac B 特殊标记 5 项：0 通过，5 待确认；
- GPT审核清单 12 项：0 通过，12 待确认；
- 合计 57 项：0 通过，57 待确认。

同文件后续又出现 4/57 已确认的统计，但整体仍未达到可执行标准。

结论：QA 不能算通过。

### 阻断项 2：dry-run 不是真正通过

`12_DRY_RUN_TEST_LOG.md` 明确说明：

- `python3 -m py_compile` 因权限限制无法执行；
- JSON 校验无法执行；
- Python 和 JSON 均基于人工审查；
- 9091-9097 overlay 备份缺失；
- Mac B 8081-8084 状态为 SSH pending。

结论：当前 dry-run 只能算“人工预审”，不能算真正验证通过。

### 阻断项 3：Mac B 未打通

本轮多处显示 Mac B 8081-8084 仍需手动验证。任何涉及 12 机器人配置一致性的执行，都必须将 Mac B 单独作为执行包处理，不能用 Mac A 代替。

### 阻断项 4：规则和代码落地之间仍缺少读取证明

P0-1/P0-2 需要确认以下字段是否真的被实盘代码读取：

```json
"temporary_pair_freeze"
"dca_pause_rules"
```

如果当前策略或 api_autopilot 未读取这些字段，仅把它们写入 overlay 不会生效。

---

## 三、允许下一步执行的内容

### Stage A：补齐执行前验证

Claude 下一步只允许先生成并完成：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_RULES_AI_STAGE_A_VALIDATION/
```

必须包含：

```text
01_QA_CHECKLIST_COMPLETED.md
02_PY_COMPILE_RESULT.md
03_JSON_VALIDATE_RESULT.md
04_OVERLAY_BACKUP_COMPLETENESS.md
05_FREEZE_RULE_READ_PATH_PROOF.md
06_DCA_PAUSE_RULE_READ_PATH_PROOF.md
07_MACB_8081_8084_VERIFICATION.md
08_STAGE_A_EXECUTION_DECISION.md
REVIEW_PACKAGE.zip
```

Stage A 目标不是改实盘，而是证明本轮材料具备执行条件。

---

## 四、允许的灰度执行条件

只有满足以下全部条件，才允许进入 P0-1 / P0-2 配置级灰度：

1. `temporary_pair_freeze` 在实盘代码中有读取路径；
2. `dca_pause_rules` 在实盘代码中有读取路径；
3. 9090-9097 overlay 全部备份完成；
4. Mac B 8081-8084 实际路径明确；
5. 所有 JSON 校验通过；
6. 相关 Python 文件 py_compile 通过；
7. 9090 单机器人灰度方案明确；
8. 回滚命令可执行；
9. 用户确认允许执行。

若任一条件不满足，不得进入实盘配置修改。

---

## 五、暂不批准的动作

以下动作仍不批准：

1. 全量修改 12 个机器人配置；
2. 直接应用全部 EntryDecisionGate / ExitDecisionGate 代码；
3. 直接应用 DCA 冷却锁代码；
4. 自动 force_entry / force_exit；
5. L5 自动写入 live runtime；
6. 直接重启 9090-9097 / 8081-8084；
7. 未完成 py_compile / JSON 校验就改实盘；
8. Mac B 使用占位文件代替真实配置；
9. 未经用户确认安装或修改 LaunchAgent。

---

## 六、Claude 必须整改的重点

### 1. 补齐 QA

将 `14_INTERNAL_QA_CHECKLIST.md` 从“待确认”更新为真实检查结果，不允许用空表代表通过。

### 2. 补齐 dry-run

必须实际执行：

```bash
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py
python3 -m py_compile ~/freqtrade_console/console_server.py
python3 -m json.tool config_*.json
```

并把真实输出写入 `02_PY_COMPILE_RESULT.md` 和 `03_JSON_VALIDATE_RESULT.md`。

### 3. 补齐 overlay 备份

必须备份 9090-9097 所有 overlay。Mac B 8081-8084 不能用 Mac A 参考文件代替，必须单独说明真实路径和获取方式。

### 4. 证明配置字段会生效

必须 grep 或代码审计证明：

```text
temporary_pair_freeze
dca_pause_rules
```

确实被实盘策略读取。若没有读取逻辑，先提交读取逻辑补丁草案，不得直接写配置。

### 5. Stage A 只允许 9090 单机器人灰度方案

不要直接全量应用。先 9090，观察 15-30 分钟，再扩展。

---

## 七、最终审核结论

本轮是一个合格的“规则与AI场景接入候选包”，但还不是合格的“可执行实盘发布包”。

结论：**有条件通过。**

允许进入：

```text
Stage A：执行前验证与 9090 配置级灰度准备
```

不允许进入：

```text
全量实盘上线
全量 12 机器人配置修改
自动 force_entry / force_exit
L5 自动写 live
```

Claude 下一步必须先完成 Stage A Validation，再交 GPT 审核。
