# 08_INTERNAL_QA_CHECKLIST.md
# 内部 QA 清单

## 概述

本文档是 EntryDecisionGate + M1-M5 Evidence + AI 接入草案的内部 QA 检查清单。
每个检查项必须在 GPT 评审前完成。

---

## 代码引用检查

- [ ] `01_ENTRY_DECISION_GATE_CODE_DRAFT.md` 中所有引用已标注文件:行号
- [ ] 引用了 `v65_autopilot.py:854` 的 `check_entry_rules()` 函数签名
- [ ] 引用了 `v65_autopilot.py:1100-1180` 的 L4 S/R 检查逻辑
- [ ] 引用了 `v65_autopilot.py:152` 的 `_VOL_SIGNAL_MULT` 常量
- [ ] 引用了 `console_server.py:26832` 的 `/api/m1/hero_card` 端点
- [ ] 引用了 `console_server.py:14389` 的 `TianyanAgent` 类
- [ ] 引用了 `console_server.py:15457` 的 `ExitAIAgent` 类
- [ ] 引用了 `console_server.py:25692` 的 `/api/bt2/sr_levels` 端点
- [ ] 引用了 `console_server.py:13837` 的天眼AI `ENTRY_PROMPT`
- [ ] 引用了 `console_server.py:15475` 的出山AI `SYSTEM_PROMPT`

---

## Evidence API 检查

### M1 Evidence
- [ ] `02_M1_M5_EVIDENCE_API_DRAFT.md` 包含完整 payload 示例
- [ ] M1 payload 包含 `ratio`, `netflow`, `signal`, `gate_ratio`, `okx_ratio`, `bnb_ratio`
- [ ] M1 payload 包含 `tf_15m`, `tf_1h`, `tf_4h` 多时线数据
- [ ] 数据来源标注为 `console_server.py:26832`
- [ ] TTL 标注为 60 秒

### M2 Evidence
- [ ] M2 payload 包含 `has_sr`, `sr_type`, `sr_price`, `sr_touches`
- [ ] M2 payload 包含 `support` 和 `resistance` 两个对象
- [ ] 数据来源标注为 `console_server.py:25692`
- [ ] TTL 标注为 5 分钟

### M3 Evidence
- [ ] M3 payload 包含 `atr_15m`, `atr_1h`, `atr_4h`
- [ ] M3 payload 包含 `giant_count`, `squeeze_count`
- [ ] M3 payload 包含 `volatility_level`

### M4 Evidence
- [ ] M4 payload 包含 `rsi_15m`, `rsi_1h`, `rsi_4h`
- [ ] M4 payload 包含 `oi_current`, `oi_change_pct`, `oi_signal`

### L5 Evidence
- [ ] L5 payload 包含 `scene_type`, `trend_direction`
- [ ] L5 payload 包含 `dot_blacklist_level`, `liquidation_wave`
- [ ] L5 payload 包含 `l5_verdict`, `data_gaps`

---

## 天眼AI接入检查

- [ ] `03_TIANYAN_AI_INTEGRATION_DRAFT.md` 包含完整 MiniMax API 调用代码
- [ ] **无硬编码 API key**：使用 `os.environ.get("MINIMAX_API_KEY", "")`
- [ ] API URL 标注为 `https://api.minimaxi.com/v1/chat/completions`
- [ ] Model 标注为 `MiniMax-M2.7-highspeed`
- [ ] 包含 JSON 解析逻辑（处理 MiniMax 可能追加的文本）
- [ ] **包含 shadow 模式**：只记录，不执行
- [ ] 输入 payload 包含 M1-M4 evidence JSON 示例
- [ ] 输出包含 `verdict`, `confidence`, `reason`, `speech` 字段
- [ ] **包含调用频率限制**：每 pair 每 60 秒最多 1 次
- [ ] Verdict 枚举值完整：`EXECUTE_LONG`, `EXECUTE_SHORT`, `OBSERVE`, `FORBIDDEN`, `UNKNOWN`
- [ ] 对接点已标注为 `console_server.py:14419` `TianyanAgent.analyze()`

---

## 出山AI接入检查

- [ ] `04_CHUSHAN_AI_INTEGRATION_DRAFT.md` 包含完整 MiniMax API 调用代码
- [ ] **无硬编码 API key**：使用环境变量占位符
- [ ] **包含 shadow 模式**：只展示，不执行
- [ ] 输入 payload 包含持仓数据 + M2/M3/M4 evidence
- [ ] 输出包含 `action`, `confidence`, `reason`, `speech` 字段
- [ ] Action 枚举值完整：`EXIT_FULL`, `EXIT_HALF`, `REDUCE_HALF`, `OBSERVE`, `HOLD`, `ATR_STOP`, `HUNT_REVERSE`
- [ ] **反转猎杀场景处理**：包含30分钟冷却记录
- [ ] 对接点已标注为 `console_server.py:15920` `ExitAIAgent.analyze()`
- [ ] **禁止事项**包含：不执行平仓、不修改参数、不直接反手

---

## Shadow模式检查

- [ ] `05_SHADOW_MODE_RUNTIME_SWITCH.md` 包含完整 `runtime_switch.py` 草案
- [ ] 包含三个模式：`shadow`（默认）、`live`、`dry`
- [ ] `is_shadow_mode()` 函数正确实现
- [ ] 日志写入 `/tmp/tianlu_gate_logs/` 目录
- [ ] `get_gate_status()` API 端点草案完整
- [ ] 环境变量配置说明清晰：`TIANLU_ENTRY_GATE_MODE` 和 `TIANLU_EXIT_GATE_MODE`
- [ ] 模式切换决策树清晰

---

## 测试计划检查

- [ ] `06_DRY_RUN_TEST_PLAN.md` 包含 S/R 场景矩阵（6个场景）
- [ ] 包含量比场景矩阵（4个场景）
- [ ] 包含综合场景矩阵（5个场景）
- [ ] 包含 TC-01 到 TC-06 详细测试用例
- [ ] 每个测试用例包含：输入、预期输出、验证方法
- [ ] 包含日志格式示例
- [ ] 包含自动化测试脚本草案
- [ ] 包含验证检查清单

---

## 回滚方案检查

- [ ] `07_ROLLBACK_PLAN.md` 包含4个场景的完整回滚步骤
- [ ] 环境变量切换为 `dry` 模式可立即停止 AI 介入
- [ ] 包含 git 回滚命令
- [ ] 包含回滚验证清单
- [ ] 包含快速回滚一键命令
- [ ] 确认 Bot 隔离性（只读，不修改参数）

---

## 安全检查

- [ ] **无硬编码 API key**：所有文件均无实际 key
- [ ] API key 使用环境变量或占位符 `${MINIMAX_API_KEY}`
- [ ] `tianyan_keys.json` 未在任何草案中被引用为实际文件
- [ ] 无实际交易执行代码（只有草案注释）
- [ ] shadow 模式明确禁止执行交易操作
- [ ] 禁止事项清单完整

---

## 格式检查

- [ ] 所有文件使用 Markdown 格式
- [ ] 所有代码块有语言标注（`python` / `bash` / `json`）
- [ ] 文件路径使用绝对路径或明确标注
- [ ] 关键引用使用 `文件:行号` 格式
- [ ] 禁止事项使用加粗或列表明确标注

---

## 文档完整性检查

- [ ] `00_MASTER_SUMMARY.md` 包含完整目录清单
- [ ] 所有子文件引用主文件中的决策
- [ ] 爸确认的置信度门槛（50%）在所有文件中一致
- [ ] 自动驾驶量比（5.0x）在所有文件中一致
- [ ] 执行边界说明在主文件中清晰列出

---

## 禁止事项清单（所有文件）

- [ ] 禁止写入实盘文件
- [ ] 禁止硬编码 API key
- [ ] 禁止写实际执行的交易代码
- [ ] 禁止在 shadow 模式下执行交易
- [ ] 禁止出山AI直接平仓
- [ ] 禁止出山AI直接反手
- [ ] 禁止修改机器人参数

---

## 签署确认

完成所有检查项后，由以下人员确认：

| 角色 | 确认人 | 日期 | 签字 |
|------|--------|------|------|
| 代码代理（天禄） | _________ | 2026/05/04 | _________ |
| GPT 评审 | _________ | _________ | _________ |
| 爸确认 | _________ | _________ | _________ |

---

## 检查结果汇总

| 检查类别 | 通过项 | 未通过项 | 备注 |
|---------|--------|---------|------|
| 代码引用 | /11 | /11 | |
| Evidence API | /14 | /14 | |
| 天眼AI接入 | /11 | /11 | |
| 出山AI接入 | /9 | /9 | |
| Shadow模式 | /8 | /8 | |
| 测试计划 | /8 | /8 | |
| 回滚方案 | /6 | /6 | |
| 安全检查 | /7 | /7 | |
| 格式检查 | /5 | /5 | |
| 文档完整性 | /4 | /4 | |
| **总计** | **/83** | **/83** | |
