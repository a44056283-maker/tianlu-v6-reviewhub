# EntryDecisionGate + M1-M5 Evidence + AI接入草案 —— 总览

**生成时间**: 2026/05/04
**输出目录**: `20260504_1638_ENTRY_EVIDENCE_AI_PREPARE/`
**状态**: 草案（DRAFT）—— 禁止直接写入实盘文件

---

## 目录清单

| 文件 | 标题 | 关键引用 |
|------|------|----------|
| `01_ENTRY_DECISION_GATE_CODE_DRAFT.md` | 入场决策门草案 | `v65_autopilot.py:854` |
| `02_M1_M5_EVIDENCE_API_DRAFT.md` | M1-M5 Evidence统一接口草案 | `console_server.py:26832` |
| `03_TIANYAN_AI_INTEGRATION_DRAFT.md` | 天眼AI调用接入草案 | `console_server.py:14389` |
| `04_CHUSHAN_AI_INTEGRATION_DRAFT.md` | 出山AI调用接入草案 | `console_server.py:15457` |
| `05_SHADOW_MODE_RUNTIME_SWITCH.md` | Shadow模式运行时开关草案 | 新建 |
| `06_DRY_RUN_TEST_PLAN.md` | Dry-run测试计划 | 新建 |
| `07_ROLLBACK_PLAN.md` | 回滚方案 | 新建 |
| `08_INTERNAL_QA_CHECKLIST.md` | 内部QA清单 | 新建 |

---

## 执行边界说明（铁律）

1. **禁止写入实盘文件** —— 所有草案文件仅用于 GPT 评审，不得直接 cp 到 ~/freqtrade_console/
2. **禁止硬编码 API key** —— 所有 key 使用环境变量占位符 "${MINIMAX_API_KEY}"
3. **禁止写实际执行的交易代码** —— 只写草案（draft），不写可执行代码
4. **Shadow模式优先** —— 默认 shadow，不阻止任何实盘交易
5. **引用现有代码位置** —— 草案中所有引用须标注 文件:行号

---

## 现有代码关键引用

| 功能 | 文件 | 行号 |
|------|------|------|
| check_entry_rules() 函数 | bt_tools/v65_autopilot.py | 854-1263 |
| V6.5量比阈值常量 | bt_tools/v65_autopilot.py | 152 |
| L4 S/R检查 | bt_tools/v65_autopilot.py | 1100-1180 |
| M1英雄卡只读API | console_server.py | 26832-26905 |
| TianyanAgent类（天眼AI） | console_server.py | 13830-15200 |
| ExitAIAgent类（出山AI） | console_server.py | 15457-16000 |
| MiniMax API Key加载 | console_server.py | 13607-13623 |
| M2 S/R Levels API | console_server.py | 25692-25750 |
| 天眼英雄卡页面 | console_server.py | 2835-2839 |
| 出山AI页面 | console_server.py | 2855-2863 |
| /api/m1/ai_summary | console_server.py | 26908-26949 |

---

## 关键设计决策（爸确认，2026-04-27）

- 置信度门槛: 50%（入场/出场统一）
- 自动驾驶量比: 5.0x（维持）
- Shadow模式: 默认启用，只记录日志不执行
- AI verdict 只展示，不直接驱动机器人
