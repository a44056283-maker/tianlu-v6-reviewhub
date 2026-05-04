# Stage B：temporary_pair_freeze / dca_pause_rules 读取逻辑补丁

**生成时间**: 2026/05/04 21:45
**输出目录**: `20260504_2145_STAGE_B_READ_LOGIC_PATCH/`
**状态**: 草案（DRAFT）—— 禁止直接写入实盘文件

---

## 目录清单

| 文件 | 标题 |
|------|------|
| `00_STAGE_B_SUMMARY.md` | Stage B 总览（本文）|
| `01_FREEZE_READ_LOGIC_PATCH.md` | temporary_pair_freeze 读取逻辑补丁 |
| `02_DCA_PAUSE_READ_LOGIC_PATCH.md` | dca_pause_rules 读取逻辑补丁 |
| `03_CONFIG_SCHEMA_AND_EXAMPLE.md` | 配置 schema + DOGE/SOL 示例 |
| `04_9090_GREY_RUN_PLAN.md` | 9090 灰度运行计划 |
| `05_TEST_AND_VERIFY_PLAN.md` | Dry-run 测试与验证计划 |
| `06_ROLLBACK_PLAN.md` | 回滚方案 |
| `07_INTERNAL_QA_CHECKLIST.md` | 内部 QA 清单 |
| `PATCH.diff` | 代码补丁（草案） |
| `TEST_LOG.md` | 测试执行日志 |
| `REVIEW_PACKAGE.zip` | 交付包 |

---

## 执行边界说明（铁律）

1. **禁止写入实盘文件** —— 所有草案文件仅用于 GPT 评审，不得直接 cp 到 ~/freqtrade/
2. **禁止硬编码 API key** —— 不涉及
3. **禁止写实际执行的交易代码** —— 只写草案补丁，不写可执行代码
4. **禁止重启机器人** —— 不重启 9090-9097 / 8081-8084
5. **禁止执行 force_entry / force_exit** —— 不调用交易所 API
6. **引用现有代码位置** —— 所有引用标注 文件:行号

---

## Stage A 阻断点回顾

| 阻断项 | 问题描述 | Stage B 解决方案 |
|--------|----------|----------------|
| temporary_pair_freeze 零读取路径 | overlay 中写了 DOGE freeze，但代码从未读取 | 新增 `is_pair_temporarily_frozen()` 函数 + 接入 check_entry_rules() |
| dca_pause_rules 零读取路径 | overlay 中写了 SOL DCA pause，但代码从未读取 | 新增 `is_dca_paused()` 函数 + 接入 DCA 触发路径 |

---

## 补丁设计原则（GPT 确认）

1. **独立函数** — 不散落逻辑，便于 grep 验证
2. **只读 overlay 字段** — 不修改配置文件
3. **不影响已有仓位** — 不触发平仓/风控出场
4. **不影响人工操作** — 只阻断自动驾驶路径
5. **时间过期自动失效** — 通过 `until_ts` 自动解除

---

## 修改文件清单

| 文件 | 行号范围 | 修改类型 |
|------|----------|----------|
| bt_tools/v65_autopilot.py | ~891-892（新增） | 接入 is_pair_temporarily_frozen() |
| bt_tools/v65_autopilot.py | ~6254-6258（新增） | 接入 is_dca_paused() |
| bt_tools/v65_autopilot.py | ~4131-4132（新增） | 接入 is_dca_paused()（备用路径）|
| bt_tools/v65_autopilot.py | ~1830附近（新增函数） | is_pair_temporarily_frozen() 定义 |
| bt_tools/v65_autopilot.py | ~1843附近（新增函数） | is_dca_paused() 定义 |

---

## 下一步

Stage B 通过 GPT 审核后 → Stage C：9090 单 bot 灰度配置
