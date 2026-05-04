# 天禄 V6.5.1 · 定时执行进度工作计划

> 生成方：GPT / 架构师审核员  
> 日期：2026-05-04  
> 执行方：Claude Code 多子代理协作  
> 目标：让 Claude 按计划推进 EntryDecisionGate、M1-M5 evidence、天眼AI/出山AI对接、Stage A 验证，并生成定时进度脚本。  
> 重要边界：本计划先推进“准备版 / shadow-only / dry-run / 报告包”，不直接全量实盘上线。

---

## 一、当前状态

当前项目状态：

```text
规则文档生成：已完成
M1-M5 字段规范：已完成候选版
天眼AI/出山AI话术：已完成候选版
Live rollout 补丁草案：已完成候选版
GPT 审核：要求先做 Stage A 验证
实盘全量上线：未批准
```

当前最重要的阻塞点：

```text
1. QA 清单未完全通过；
2. py_compile / JSON 校验没有真实执行；
3. 9091-9097 overlay 备份需要补齐；
4. Mac B 8081-8084 SSH 仍需处理；
5. temporary_pair_freeze / dca_pause_rules 是否被实盘代码读取，需要证明；
6. EntryDecisionGate 和 M1-M5 evidence 仍需代码化；
7. 天眼AI/出山AI调用仍需接入 evidence 与 gate 输出。
```

---

## 二、总体目标

Claude 今日后续目标分成两条线并行：

### A线：Stage A 执行前验证

目标：证明现有候选包具备进入 9090 单机器人灰度的条件。

必须输出：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_RULES_AI_STAGE_A_VALIDATION/
```

包含：

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

### B线：代码化准备包

目标：提前准备 EntryDecisionGate、M1-M5 evidence、天眼AI/出山AI调用对接，但不直接接管实盘。

必须输出：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_ENTRY_EVIDENCE_AI_PREPARE/
```

包含：

```text
00_MASTER_ENTRY_EVIDENCE_AI_PREPARE_SUMMARY.md
01_ENTRY_DECISION_GATE_CODE_DRAFT.md
02_M1_M5_EVIDENCE_API_DRAFT.md
03_TIANYAN_AI_CALL_INTEGRATION_DRAFT.md
04_CHUSHAN_AI_CALL_INTEGRATION_DRAFT.md
05_SHADOW_ONLY_RUNTIME_SWITCH.md
06_DRY_RUN_TEST_PLAN.md
07_ROLLBACK_PLAN.md
08_INTERNAL_QA_CHECKLIST.md
PATCH.diff
REVIEW_PACKAGE.zip
```

---

## 三、多子代理分工

### 1. 中书省 · 总协调代理

职责：

```text
1. 创建两个任务目录；
2. 协调 A线和 B线并行推进；
3. 收集子代理输出；
4. 每 30 分钟生成进度快照；
5. 推送 GitHub；
6. 生成总报告和 REVIEW_PACKAGE。
```

输出：

```text
00_MASTER_PROGRESS_SUMMARY.md
TIMED_PROGRESS_LOG.md
```

### 2. 都察院 · Stage A 验证代理

职责：

```text
1. 完成 QA 清单；
2. 执行 py_compile；
3. 执行 JSON 校验；
4. 检查 overlay 备份完整性；
5. 证明字段读取路径；
6. 明确是否允许进入 9090 单机器人灰度。
```

输出：

```text
01_QA_CHECKLIST_COMPLETED.md
02_PY_COMPILE_RESULT.md
03_JSON_VALIDATE_RESULT.md
04_OVERLAY_BACKUP_COMPLETENESS.md
05_FREEZE_RULE_READ_PATH_PROOF.md
06_DCA_PAUSE_RULE_READ_PATH_PROOF.md
08_STAGE_A_EXECUTION_DECISION.md
```

### 3. 兵部 · 12 机器人与 Mac B 代理

职责：

```text
1. 核查 9090-9097 overlay 备份；
2. 核查 8081-8084 Mac B 连接；
3. 如果 SSH 不通，生成人工执行说明；
4. 不直接修改 Mac B。
```

输出：

```text
07_MACB_8081_8084_VERIFICATION.md
12_BOT_GREY_DEPLOYMENT_SCOPE.md
```

### 4. 户部 · M1-M5 evidence 代理

职责：

```text
1. 准备 M1-M5 evidence API 草案；
2. 统一 evidence payload JSON；
3. 确保只读输出，不触发交易；
4. 输出 api_m1/api_m2/api_m3/api_m4/l5 的接口草案。
```

输出：

```text
02_M1_M5_EVIDENCE_API_DRAFT.md
```

### 5. 天眼院 · EntryDecisionGate 与天眼AI代理

职责：

```text
1. 准备 EntryDecisionGate 代码草案；
2. 准备天眼AI调用接入草案；
3. 所有逻辑默认 shadow-only；
4. 不接管实盘入场。
```

输出：

```text
01_ENTRY_DECISION_GATE_CODE_DRAFT.md
03_TIANYAN_AI_CALL_INTEGRATION_DRAFT.md
```

### 6. 出山院 · 出山AI与 Exit 对接代理

职责：

```text
1. 准备出山AI调用接入草案；
2. 确认出场话术只展示建议；
3. 不直接执行 force_exit；
4. 与 ExitDecisionGate 文档保持兼容。
```

输出：

```text
04_CHUSHAN_AI_CALL_INTEGRATION_DRAFT.md
```

### 7. 工部 · 定时进度脚本代理

职责：

```text
1. 生成定时进度脚本；
2. 生成 LaunchAgent 草案；
3. 定时扫描 GitHub 工作区和本地任务输出；
4. 生成本地进度日志；
5. 可选推送进度到 GitHub；
6. 不安装 LaunchAgent，等待用户确认。
```

输出：

```text
06_MAINTENANCE/tianlu_progress_tick.sh
06_MAINTENANCE/com.tianlu.progress-tick.plist.draft
07_TEST_LOGS/tianlu_progress_tick.log
05_Claude_Tasks/TIMED_PROGRESS_SCRIPT_PLAN.md
```

---

## 四、定时进度脚本要求

Claude 必须生成脚本：

```text
~/Desktop/Tianlu_V6_5_Workspace/06_MAINTENANCE/tianlu_progress_tick.sh
```

脚本功能：

```text
1. 每次运行生成当前任务进度快照；
2. 检查 03_PENDING_GPT_REVIEW 最新目录；
3. 检查 04_GPT_REVIEW_RESPONSES 最新审核建议；
4. 检查 05_Claude_Tasks 最新任务；
5. 检查是否存在 REVIEW_PACKAGE.zip；
6. 检查是否有 TEST_LOG.md；
7. 检查是否有 PATCH.diff；
8. 输出进度百分比；
9. 写入本地日志；
10. 不执行任何交易命令；
11. 不修改实盘文件；
12. 不重启任何服务。
```

日志路径：

```text
~/Desktop/Tianlu_V6_5_Workspace/07_TEST_LOGS/tianlu_progress_tick.log
```

进度快照路径：

```text
~/Desktop/Tianlu_V6_5_Workspace/07_TEST_LOGS/TIANLU_PROGRESS_SNAPSHOT.md
```

脚本建议内容：

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK="$HOME/Desktop/Tianlu_V6_5_Workspace"
REPO="$HOME/Desktop/tianlu-v6-reviewhub"
LOG="$WORK/07_TEST_LOGS/tianlu_progress_tick.log"
SNAP="$WORK/07_TEST_LOGS/TIANLU_PROGRESS_SNAPSHOT.md"
TS="$(date '+%Y-%m-%d %H:%M:%S')"

mkdir -p "$WORK/07_TEST_LOGS"

echo "[$TS] Tianlu progress tick start" >> "$LOG"

LATEST_PENDING="$(find "$REPO/03_PENDING_GPT_REVIEW" -maxdepth 2 -type d 2>/dev/null | sort | tail -1 || true)"
LATEST_REVIEW="$(find "$REPO/04_GPT_REVIEW_RESPONSES" -name 'GPT_*.md' -type f 2>/dev/null | sort | tail -1 || true)"
LATEST_TASK="$(find "$REPO/05_Claude_Tasks" -type f -name '*.md' 2>/dev/null | sort | tail -1 || true)"

REVIEW_PACKAGE_COUNT="$(find "$REPO/03_PENDING_GPT_REVIEW" -name 'REVIEW_PACKAGE.zip' -type f 2>/dev/null | wc -l | tr -d ' ')"
PATCH_COUNT="$(find "$REPO/03_PENDING_GPT_REVIEW" -name 'PATCH.diff' -type f 2>/dev/null | wc -l | tr -d ' ')"
TEST_LOG_COUNT="$(find "$REPO/03_PENDING_GPT_REVIEW" -name '*TEST_LOG*.md' -type f 2>/dev/null | wc -l | tr -d ' ')"

cat > "$SNAP" <<EOF
# 天禄 V6.5 自动进度快照

生成时间：$TS

## 最新待审目录

$LATEST_PENDING

## 最新 GPT 审核意见

$LATEST_REVIEW

## 最新 Claude 任务

$LATEST_TASK

## 交付包统计

- REVIEW_PACKAGE.zip 数量：$REVIEW_PACKAGE_COUNT
- PATCH.diff 数量：$PATCH_COUNT
- TEST_LOG 数量：$TEST_LOG_COUNT

## 状态建议

- 若最新待审目录存在 REVIEW_PACKAGE.zip：等待 GPT 审核。
- 若最新 GPT 审核意见晚于最新待审目录：Claude 应读取审核意见继续整改。
- 若 TEST_LOG 缺失：Claude 需补 dry-run。
- 若 PATCH.diff 缺失：Claude 需补补丁索引。
EOF

echo "[$TS] snapshot written: $SNAP" >> "$LOG"
```

---

## 五、LaunchAgent 草案要求

Claude 可生成草案：

```text
~/Desktop/Tianlu_V6_5_Workspace/06_MAINTENANCE/com.tianlu.progress-tick.plist.draft
```

调度建议：每 30 分钟执行一次。

注意：

```text
只生成草案，不安装。
安装需要用户确认。
```

---

## 六、今日执行节奏

### 0-30 分钟

```text
1. 创建任务目录；
2. 创建进度脚本草案；
3. 生成 LaunchAgent 草案；
4. 生成第一次进度快照。
```

### 30-120 分钟

```text
1. Stage A 验证：py_compile、JSON校验、overlay备份；
2. 字段读取路径证明；
3. Mac B 验证报告。
```

### 2-5 小时

```text
1. EntryDecisionGate 代码草案；
2. M1-M5 evidence API 草案；
3. 天眼AI/出山AI调用对接草案。
```

### 5-8 小时

```text
1. dry-run；
2. 回滚包；
3. REVIEW_PACKAGE；
4. push GitHub；
5. 等 GPT 审核。
```

---

## 七、Claude 本轮禁止事项

```text
1. 不直接应用实盘补丁；
2. 不重启机器人；
3. 不执行 force_entry；
4. 不执行 force_exit；
5. 不调用交易所 API；
6. 不修改 12 机器人配置；
7. 不安装 LaunchAgent；
8. 不删除缓存；
9. 不上传密钥、数据库、日志原文；
10. 不让 L5 写 live runtime。
```

---

## 八、交付标准

Claude 完成后必须推送 GitHub：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_RULES_AI_STAGE_A_VALIDATION/
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_ENTRY_EVIDENCE_AI_PREPARE/
```

并在本地生成：

```text
~/Desktop/Tianlu_V6_5_Workspace/06_MAINTENANCE/tianlu_progress_tick.sh
~/Desktop/Tianlu_V6_5_Workspace/06_MAINTENANCE/com.tianlu.progress-tick.plist.draft
~/Desktop/Tianlu_V6_5_Workspace/07_TEST_LOGS/TIANLU_PROGRESS_SNAPSHOT.md
```

---

## 九、给 Claude 的直接执行话术

```text
你现在执行天禄 V6.5.1 定时推进工作计划。

目标：按 GPT 工作计划并行推进 Stage A 验证和 EntryDecisionGate/M1-M5 evidence/天眼AI/出山AI代码化准备。

你必须通过多子代理协作完成。

第一优先级：生成并运行 tianlu_progress_tick.sh 进度快照脚本。
第二优先级：完成 Stage A 验证包。
第三优先级：完成 EntryDecisionGate + M1-M5 evidence + 天眼AI/出山AI调用准备包。

禁止：不直接应用实盘补丁，不重启机器人，不执行交易动作，不安装 LaunchAgent。

完成后 push GitHub，等待 GPT 审核。
```
