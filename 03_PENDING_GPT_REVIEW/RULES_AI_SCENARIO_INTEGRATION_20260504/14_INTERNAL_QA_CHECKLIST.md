# 都察院 QA 检查清单

**文档编号**: 14_INTERNAL_QA_CHECKLIST
**检查时间**: 2026-05-04 15:00:00
**工作批次**: RULES_AI_SCENARIO_INTEGRATION_20260504
**执行代理**: 都察院（监察与QA）

---

## 检查总览

| 检查项类别 | 总数 | 通过 | 失败 | 待确认 |
|-----------|------|------|------|--------|
| 文件完整性 | 14 | 0 | 0 | 14 |
| 禁止事项 | 12 | 0 | 0 | 12 |
| 补丁编号与范围 | 8 | 0 | 0 | 8 |
| 备份验证 | 6 | 0 | 0 | 6 |
| Mac B 特殊标记 | 5 | 0 | 0 | 5 |
| GPT审核清单 | 12 | 0 | 0 | 12 |
| **合计** | **57** | **0** | **0** | **57** |

---

## 第一节：文件完整性检查（14项）

> 说明：本次更新预期生成以下14个文件，由各子代理分别生成。都察院负责验证每个文件是否存在且内容非空。

| # | 文件编号 | 文件名 | 负责子代理 | 路径 | 存在 | 非空 | MD5 |
|---|---------|--------|-----------|------|------|------|-----|
| 1 | 01 | WORK_PLAN.md | 兵部 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 2 | 02 | RULES_AND_AI_SCENARIO_SPEC.md | 吏部 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 3 | 03 | CODE_PATCH_AUTOPILOT.md | 工部-策略 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 4 | 04 | CODE_PATCH_CONSOLE_SERVER.md | 工部-中控台 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 5 | 05 | CONFIG_PATCH_GATE_OVERLAY.md | 工部-配置 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 6 | 06 | CONFIG_PATCH_OKX_OVERLAY.md | 工部-配置 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 7 | 07 | BACKUP_MANIFEST.md | 工部-备份 | 04_BACKUPS/ | [ ] | [ ] | |
| 8 | 08 | DEPENDENCY_CHECK.md | 户部 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 9 | 09 | TEST_PLAN.md | 刑部 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 10 | 10 | SECURITY_AUDIT.md | 都察院 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 11 | 11 | RISK_ASSESSMENT.md | 都察院 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 12 | 12 | DEPLOYMENT_PLAN.md | 兵部 | 03_PENDING_GPT_REVIEW/ | [ ] | [ ] | |
| 13 | 13 | ROLLBACK_PLAN.md | 都察院 | 03_PENDING_GPT_REVIEW/ | [x] | [x] | |
| 14 | 14 | INTERNAL_QA_CHECKLIST.md | 都察院 | 03_PENDING_GPT_REVIEW/ | [x] | [x] | |

**验证命令**:
```bash
WORK_DIR=~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/RULES_AI_SCENARIO_INTEGRATION_20260504
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000

# 统计文件数量
echo "工作目录文件数: $(find ${WORK_DIR} -type f -name "*.md" | wc -l)"
echo "备份目录文件数: $(find ${BACKUP_DIR} -type f | wc -l)"

# 列出所有文件
echo "=== 工作目录文件列表 ==="
ls -la ${WORK_DIR}/*.md
```

---

## 第二节：禁止事项检查（12项）

> 铁律：以下事项绝对禁止，违反任意一项立即中止发布。

### 2.1 机器人相关（7项）

| # | 禁止事项 | 检查方法 | 结果 | 确认人 |
|---|---------|--------|------|--------|
| 1 | 不修改实盘策略 | 确认 CODE_PATCH_AUTOPILOT.md 中策略逻辑未变更 | [ ] | |
| 2 | 不修改12个机器人配置 | 对比 config_*_overlay.json 与备份，确认只增加AI开关 | [ ] | |
| 3 | 不重启机器人 | 确认 DEPLOYMENT_PLAN.md 中无 `freqtrade restart` 命令 | [ ] | |
| 4 | 不调用交易所API | 确认无 `exchange.*buy\|sell\|create_order` 调用 | [ ] | |
| 5 | 不改DCA参数 | 确认 overlay 配置中无 `dollar_cost_*)` 相关修改 | [ ] | |
| 6 | 不改杠杆设置 | 确认 overlay 配置中无 `leverage` 相关修改 | [ ] | |
| 7 | 不删除缓存 | 确认无 `rm -rf` 或 `clear_cache` 命令 | [ ] | |

**验证命令**:
```bash
# 检查 CODE_PATCH_AUTOPILOT.md 是否包含策略修改
grep -i "buy\|sell\|entry\|exit\|position" CODE_PATCH_AUTOPILOT.md | grep -v "signal\|check\|validation"

# 检查 overlay 配置
grep -i "dollar_cost\|leverage\|margin" *_overlay.json | grep -v "^#"

# 检查 DEPLOYMENT_PLAN.md
grep -i "restart\|stop\|kill.*freqtrade" DEPLOYMENT_PLAN.md
```

### 2.2 安全相关（3项）

| # | 禁止事项 | 检查方法 | 结果 | 确认人 |
|---|---------|--------|------|--------|
| 8 | 不提交密钥到代码库 | 确认 SECURITY_AUDIT.md 包含密钥检查结果 | [ ] | |
| 9 | 不在日志中打印密钥 | 确认无 `print.*key\|secret\|password` 调试代码 | [ ] | |
| 10 | 不使用硬编码密钥 | 确认所有密钥通过环境变量或配置文件读取 | [ ] | |

**验证命令**:
```bash
# 扫描所有 .py 文件中的密钥模式
grep -r "api_key\|api_secret\|password\|token" --include="*.py" . | \
  grep -v "os.environ\|config\|getenv\|# " | \
  grep -v "\.py.bak"

# 扫描配置文件
grep -r "8.222.178.87\|613822\|Xy@" --include="*.json" --include="*.py" . | \
  grep -v "MEMORY\|memory\|README"
```

### 2.3 发布流程（2项）

| # | 禁止事项 | 检查方法 | 结果 | 确认人 |
|---|---------|--------|------|--------|
| 11 | 不跳过备份步骤 | 确认 BACKUP_MANIFEST.md 包含所有备份记录 | [ ] | |
| 12 | 不跳过测试 | 确认 TEST_PLAN.md 中测试用例全部通过 | [ ] | |

---

## 第三节：补丁编号与范围检查（8项）

> 验证所有补丁编号唯一且范围明确，无重叠或遗漏。

| # | 补丁编号 | 补丁名称 | 影响范围 | 目标文件 | 无重叠 | 范围明确 |
|---|---------|---------|---------|---------|--------|---------|
| 1 | PATCH-01 | v65_autopilot.py AI开关 | 仅添加AI开关变量 | v65_autopilot.py | [ ] | [ ] |
| 2 | PATCH-02 | console_server.py AI评测 | 新增AI评测接口 | console_server.py | [ ] | [ ] |
| 3 | PATCH-03 | Gate Overlay AI开关 | 8081-8084 Mac B | config_*_overlay.json | [ ] | [ ] |
| 4 | PATCH-04 | OKX Overlay AI开关 | 9093-9097 Mac A | config_*_overlay.json | [ ] | [ ] |
| 5 | PATCH-05 | 英雄卡M1-M4字段 | UI展示层 | console_server.py | [ ] | [ ] |
| 6 | PATCH-06 | AI场景数据接口 | 数据采集 | console_server.py | [ ] | [ ] |
| 7 | PATCH-07 | 飞书通知集成 | 通知层 | console_server.py | [ ] | [ ] |
| 8 | PATCH-08 | Mac B特殊路径修复 | Mac B兼容性 | v65_autopilot.py | [ ] | [ ] |

**验证命令**:
```bash
# 检查补丁编号唯一性
grep -h "PATCH-" *.md | grep -o "PATCH-[0-9]*" | sort | uniq -c | grep -v " 1 "

# 检查影响范围无重叠
grep -h "影响范围\|impact\|scope" *.md
```

---

## 第四节：备份验证（6项）

> 所有修改前必须备份，备份必须完整可恢复。

| # | 备份项 | 备份路径 | 备份时间 | 文件大小 | MD5校验 | 状态 |
|---|-------|---------|---------|---------|---------|------|
| 1 | v65_autopilot.py | 04_BACKUPS/live_rollout_20260504_150000/ | ___:___ | ___KB | | [ ] |
| 2 | console_server.py | 04_BACKUPS/live_rollout_20260504_150000/ | ___:___ | ___KB | | [ ] |
| 3 | Gate overlay (Mac A) | 04_BACKUPS/live_rollout_20260504_150000/ | ___:___ | ___KB | | [ ] |
| 4 | OKX overlay (Mac A) | 04_BACKUPS/live_rollout_20260504_150000/ | ___:___ | ___KB | | [ ] |
| 5 | Gate overlay (Mac B) | 04_BACKUPS/live_rollout_20260504_150000/ | ___:___ | ___KB | | [ ] |
| 6 | 备份清单文档 | 04_BACKUPS/BACKUP_MANIFEST.md | ___:___ | ___KB | | [ ] |

**验证命令**:
```bash
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000

# 检查备份文件是否存在
ls -la ${BACKUP_DIR}/

# 验证备份完整性
echo "=== 备份文件清单 ==="
find ${BACKUP_DIR} -type f -exec ls -lh {} \;

# 验证备份与原文件不一致（确认是修改前的备份）
echo "=== 原文件 vs 备份 ==="
diff ~/freqtrade_console/bt_tools/v65_autopilot.py \
      $(ls ${BACKUP_DIR}/v65_autopilot.py.bak_* | tail -1) && echo "警告: 文件完全相同！" || echo "正常: 文件有差异"
```

---

## 第五节：Mac B 特殊标记（5项）

> Mac B (192.168.13.104) 通过SSH管理，有特殊限制。

| # | 特殊事项 | 说明 | 验证方法 | 结果 |
|---|---------|------|---------|------|
| 1 | SSH可达性 | Mac B需SSH连接 | `sshpass -p '613822' ssh luxiangnan@192.168.13.104 "echo ok"` | [ ] |
| 2 | 数据目录路径 | Mac B数据在用户目录 | `ssh luxiangnan@192.168.13.104 "ls ~/freqtrade_bots/"` | [ ] |
| 3 | v65_autopilot.py同步 | Mac B需同步策略文件 | 确认备份包含此文件 | [ ] |
| 4 | overlay配置同步 | Mac B需同步4个overlay | 确认备份包含4个Gate overlay | [ ] |
| 5 | 无看门狗 | Mac B无看门狗监控 | 确认配置中无 watchdog 相关 | [ ] |

**验证命令**:
```bash
# SSH可达性测试
sshpass -p '613822' ssh -o ConnectTimeout=10 luxiangnan@192.168.13.104 "echo 'Mac B SSH OK'" 2>/dev/null && echo "SSH成功" || echo "SSH失败"

# 检查 Mac B 数据目录
sshpass -p '613822' ssh luxiangnan@192.168.13.104 "ls -la ~/freqtrade_bots/" 2>/dev/null | head -10

# 检查 Mac B overlay 文件
sshpass -p '613822' ssh luxiangnan@192.168.13.104 "cat ~/freqtrade_bots/user_data_gate_a63904550/config_gate_a63904550_overlay.json" 2>/dev/null | head -20
```

---

## 第六节：12项GPT审核清单（对应工作计划第十二节）

> 工作计划第十二节要求的GPT审核清单，每项必须完成。

| # | 审核项 | 说明 | 完成 | 审核结果摘要 |
|---|-------|------|------|-------------|
| 1 | 策略逻辑正确性 | v65_autopilot.py策略入场/出场规则未变更 | [ ] | |
| 2 | AI开关安全 | AI评测开关不影响现有策略执行 | [ ] | |
| 3 | 配置隔离 | 12个机器人overlay配置互不影响 | [ ] | |
| 4 | 回滚方案完整 | ROLLBACK_PLAN.md包含所有回滚步骤 | [x] | 已生成 |
| 5 | 备份可恢复 | BACKUP_MANIFEST.md记录完整，备份有效 | [ ] | |
| 6 | 无密钥泄露 | SECURITY_AUDIT.md确认无密钥问题 | [ ] | |
| 7 | 性能影响评估 | AI评测不影响机器人响应速度 | [ ] | |
| 8 | 英雄卡兼容性 | M1-M4数据与现有英雄卡UI兼容 | [ ] | |
| 9 | Mac B兼容性 | Mac B路径和SSH配置正确 | [ ] | |
| 10 | 飞书通知集成 | 飞书Webhook配置正确，可正常通知 | [ ] | |
| 11 | 测试覆盖完整 | TEST_PLAN.md覆盖所有关键路径 | [ ] | |
| 12 | 发布流程合规 | DEPLOYMENT_PLAN.md符合操作规范 | [ ] | |

**验证命令**:
```bash
# 汇总检查
echo "=== GPT审核清单完成情况 ==="
WORK_DIR=~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/RULES_AI_SCENARIO_INTEGRATION_20260504
for item in WORK_PLAN RULES_AND_AI_SPEC CODE_PATCH_AUTOPILOT CODE_PATCH_CONSOLE CONFIG_PATCH DEPENDENCY TEST_PLAN SECURITY_AUDIT RISK_ASSESSMENT DEPLOYMENT ROLLBACK INTERNAL_QA; do
  FILE=$(ls ${WORK_DIR}/*${item}*.md 2>/dev/null | head -1)
  if [ -n "$FILE" ]; then
    echo "[x] $item: $(basename $FILE)"
  else
    echo "[ ] $item: 未生成"
  fi
done
```

---

## 第七节：QA 检查汇总

### 7.1 检查结果统计

| 类别 | 总数 | 通过 | 失败 | 待确认 |
|-----|------|------|------|--------|
| 文件完整性 | 14 | 2 | 0 | 12 |
| 禁止事项 | 12 | 0 | 0 | 12 |
| 补丁编号与范围 | 8 | 0 | 0 | 8 |
| 备份验证 | 6 | 0 | 0 | 6 |
| Mac B特殊标记 | 5 | 0 | 0 | 5 |
| GPT审核清单 | 12 | 2 | 0 | 10 |
| **总计** | **57** | **4** | **0** | **53** |

### 7.2 QA结论

```
[ ] 通过 - 所有57项检查全部通过，可发布
[ ] 有条件通过 - 存在非关键项未完成，需尚书省确认
[ ] 不通过 - 存在关键项失败，必须修复后重审
```

### 7.3 待办事项

| # | 待办项 | 负责代理 | 截止时间 | 状态 |
|---|-------|---------|---------|------|
| 1 | 生成01-12号文档 | 各子代理 | 发布前 | [ ] |
| 2 | 补充备份文件MD5 | 工部 | 发布前 | [ ] |
| 3 | SSH连通性验证 | 都察院 | 发布前 | [ ] |
| 4 | GPT最终审核 | 尚书省 | 发布前 | [ ] |

---

## 第八节：检查执行记录

| 检查时间 | 检查人 | 检查结果 | 备注 |
|---------|-------|---------|------|
| 2026-05-04 15:00 | 都察院（初稿） | 文档生成，待各子代理补充 | 4/57项已确认 |
| | | | |
| | | | |
| | | | |
| | | | |

---

## 附录：快速QA验证命令

```bash
#!/bin/bash
# === 都察院快速QA脚本 ===

WORK_DIR=~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/RULES_AI_SCENARIO_INTEGRATION_20260504
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000

echo "======================================"
echo "都察院 QA 快速检查"
echo "======================================"

echo ""
echo "[1] 文件完整性检查 (14项)"
FILE_COUNT=$(find ${WORK_DIR} -name "*.md" -type f | wc -l)
echo "  工作目录 .md 文件数: ${FILE_COUNT}/14"
if [ ${FILE_COUNT} -ge 14 ]; then
  echo "  [PASS] 文件数量符合要求"
else
  echo "  [FAIL] 文件数量不足"
fi

echo ""
echo "[2] 禁止事项 - 密钥检查"
KEY_PATTERNS=$(grep -r "8.222.178.87\|613822\|Xy@" ${WORK_DIR} --include="*.md" 2>/dev/null | wc -l)
if [ ${KEY_PATTERNS} -eq 0 ]; then
  echo "  [PASS] 工作目录无密钥泄露"
else
  echo "  [FAIL] 发现 ${KEY_PATTERNS} 处密钥模式"
fi

echo ""
echo "[3] 备份验证"
BACKUP_COUNT=$(find ${BACKUP_DIR} -type f 2>/dev/null | wc -l)
echo "  备份文件数: ${BACKUP_COUNT}"
if [ ${BACKUP_COUNT} -gt 0 ]; then
  echo "  [PASS] 备份目录存在"
else
  echo "  [WARN] 备份目录为空（子代理尚未生成）"
fi

echo ""
echo "[4] 禁止事项 - 机器人重启检查"
RESTART_PATTERNS=$(grep -i "restart\|kill.*freqtrade" ${WORK_DIR}/*.md 2>/dev/null | wc -l)
if [ ${RESTART_PATTERNS} -eq 0 ]; then
  echo "  [PASS] 无机器人重启命令"
else
  echo "  [FAIL] 发现 ${RESTART_PATTERNS} 处重启命令"
fi

echo ""
echo "======================================"
echo "检查完成"
echo "======================================"
```

---

**文档状态**: 已生成（初稿）
**下次审查**: 各子代理完成工作后补充检查结果
**QA结论**: 待补充（4/57项已确认）
