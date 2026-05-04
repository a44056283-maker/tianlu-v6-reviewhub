# GPT 审核建议 · 20260504_112219_FULL_AUDIT

## 审核结论：有条件通过

## 最优先整改项（P0）

| 优先级 | 编号 | 问题 | 建议动作 |
|--------|------|------|---------|
| P0-1 | 🔴 最高 | OpenClaw embedded agent / cron 仍走 /v1/responses 导致 404 | 备份并修复 provider：minimax2-7 → minimax |
| P0-2 | 🔴 最高 | force_entry / force_exit 无统一权限闸 | 生成 FORCE_ACTION_PERMISSION_MAP.md |
| P0-3 | 🔴 最高 | DCA_MAX_LAYER=10 与"封顶2次"注释冲突 | 核查并统一代码与注释 |
| P0-4 | 🟠 重要 | 策略规则无单一真相源文档 | 生成 STRATEGY_SOURCE_OF_TRUTH.md |
| P0-5 | 🟠 重要 | 12 个 bot 配置一致性矩阵缺失 | 生成 12_BOT_CONSISTENCY_MATRIX.md |

## 下一轮 Claude 应执行的清单

- [ ] 备份并修复 OpenClaw provider：minimax2-7 → minimax
- [ ] 验证 Feishu / 微信 / cron 不再调用 /v1/responses
- [ ] 生成 STRATEGY_SOURCE_OF_TRUTH.md
- [ ] 生成 12_BOT_CONSISTENCY_MATRIX.md
- [ ] 生成 FORCE_ACTION_PERMISSION_MAP.md
- [ ] 生成 L5_PROMOTION_GATE_RULES.md

## 核心原则

**现在不建议继续扩功能或直接优化收益。**

先完成：
1. 定源头（STRATEGY_SOURCE_OF_TRUTH）
2. 定权限（FORCE_ACTION_PERMISSION_MAP）
3. 定闸门（L5_PROMOTION_GATE_RULES）
4. 定一致性（12_BOT_CONSISTENCY_MATRIX）
5. 修复 OpenClaw 通讯链路（minimax provider）

---

*GPT 审核结论：有条件通过*
*审核时间：2026-05-04*
*下一轮重点：P0-1 OpenClaw fix → P0-2~P0-5 文档体系建设*
