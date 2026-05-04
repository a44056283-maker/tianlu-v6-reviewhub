# 都察院 QA 检查清单

> 审计时间：2026-05-04 14:30
> 审计员：都察院

---

## 一、文件完整性检查

| 编号 | 文件 | 状态 |
|------|------|------|
| 01 | 00_MASTER_LIVE_ROLLOUT_SUMMARY.md | ✅ |
| 02 | 01_12_BOT_CONFIG_BEFORE_AFTER_MATRIX.md | ✅ |
| 03 | 01_12_BOT_CONFIG_PATCH_PLAN.md | ✅ |
| 04 | 02_M1_M5_EVIDENCE_PAYLOAD_SPEC.md | ✅ |
| 05 | 02_M1_M5_COMPATIBILITY_PATCH_PLAN.md | ✅ |
| 06 | 03_DCA_LEVERAGE_GUARD_PATCH.md | ✅ |
| 07 | 03_FORCE_ACTION_GUARD_PATCH.md | ✅ |
| 08 | 03_RISK_ACTION_AUDIT_LOG_SPEC.md | ✅ |
| 09 | 04_EXIT_DECISION_GATE_PATCH.md | ✅ |
| 10 | 04_POST_EXIT_CONTINUATION_SPEC.md | ✅ |
| 11 | 05_L5_CANDIDATE_REGISTRY_PATCH.md | ✅ |
| 12 | 05_L5_PROMOTION_GATE_PATCH.md | ✅ |
| 13 | 05_L5_NO_AUTO_LIVE_APPLY_POLICY.md | ✅ |
| 14 | 06_INTERNAL_QA_CHECKLIST.md | ✅ |
| 15 | 06_ROLLBACK_PLAN.md | ✅ |
| 16 | PATCH.diff | ✅ |
| 17 | TEST_LOG.md | ✅ |

**结果：17/17 文件全部生成 ✅**

---

## 二、约束检查

| 禁止项 | 执行情况 |
|--------|---------|
| 不重启任何机器人 | ✅ 未执行 |
| 不调用交易所API | ✅ 未执行 |
| 不执行 force_entry/exit | ✅ 未执行 |
| 不改DCA参数（仅加pause/freeze） | ✅ 仅添加暂停规则 |
| 不改杠杆 | ✅ 未执行 |
| API keys 脱敏 | ✅ 仅显示前8字符 |
| 备份文件保留 | ✅ 4个备份文件已生成 |

---

## 三、补丁编号与范围

| 补丁编号 | 范围 | 优先级 | 状态 |
|----------|------|--------|------|
| P0-1 DOGE冻结 | 12个overlay | P0 紧急 | 待GPT批准 |
| P0-2 SOL DCA暂停 | 12个overlay | P0 紧急 | 待GPT批准 |
| P0-3 DCA清除止损冷却 | v65_autopilot.py | P0 高 | 待GPT批准 |
| P0-4 连续亏损绕过门控 | v65_autopilot.py | P0 高 | 待GPT批准 |
| P0-5 stagger_delay负数 | v65_autopilot.py | P1 低 | 待GPT批准 |
| P1-1 ForceGuard审计日志 | console_server.py | P1 | 待GPT批准 |
| P1-2 PostExitContinuation | v65_autopilot.py | P1 | 待GPT批准 |
| P1-3 L5候选注册表+晋级闸门 | v65_autopilot.py | P1 | 待GPT批准 |
| P1-4 M1-M5证据载荷规范 | api_*.py | P1 | 待GPT批准 |

---

## 四、备份验证

| 文件 | 备份状态 | 行数 |
|------|----------|------|
| v65_autopilot.py | ✅ `v65_autopilot.py.bak_20260504_142502` | 9681 |
| console_server.py | ✅ `console_server.py.bak_20260504_142502` | 32093 |
| config_9090_overlay.json | ✅ `config_9090_overlay.json.bak_20260504_150000` | - |
| config_8081_overlay.json | ✅ `config_8081_overlay.json.bak_20260504_150000_MacA_ref` | - |

---

## 五、Mac B 特殊标记

| 项目 | 状态 |
|------|------|
| Mac B SSH可达性 | ❌ SSH被拒绝（192.168.13.104） |
| 8081-8084 补丁 | ⚠️ 仅占位符，待手动执行 |
| Mac B api_autopilot.py | 未纳入备份（路径分散在多bot目录） |

---

## 六、结论

**本轮审计完成，可以交付 GPT 审核。**

所有约束已遵守，所有文件已生成，备份已就绪。P0-1/P0-2 为配置级修改（不涉及代码），可最先执行；P0-3~P1-4 需代码修改和 console_server 重启。

**下一步：推送 GitHub → 发送链接给 GPT → 等待批准 → 分阶段执行**
