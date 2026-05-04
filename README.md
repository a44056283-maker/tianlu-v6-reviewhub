# tianlu-v6-reviewhub

天禄 V6.5 Claude ↔ GPT 审核中转站

## 用途

存放 Claude 交付报告、补丁、测试记录、回滚说明、风险检查，供 GPT 审核。

## 禁止存放

- API Key / Secret / Token / Passphrase
- .env / api_keys.json 原文
- 交易数据库 / 钱包私钥 / 助记词

## 目录结构

| 目录 | 用途 |
|------|------|
| 00_INSTRUCTIONS | Claude 启动说明 |
| 01_CLAUDE_TASKS_PENDING | 待执行任务 |
| 02_CLAUDE_DONE_REPORTS | Claude 交付报告 |
| 03_PENDING_GPT_REVIEW | **GPT 待审核包** |
| 04_GPT_REVIEW_DECISIONS | GPT 审核结论 |
| 05_CLAUDE_FIX_RESULTS | Claude 整改结果 |
| 06_RELEASE_CANDIDATES | 候选版本 |
| 07_DAILY_PROGRESS | 每日进展 |
| 08_ARCHIVE | 历史归档 |

## 审核闭环

1. Claude 完成任务 → 提交到 `03_PENDING_GPT_REVIEW/`
2. GPT 读取仓库审核
3. GPT 输出到 `04_GPT_REVIEW_DECISIONS/`
4. Claude 读取整改 → 提交到 `05_CLAUDE_FIX_RESULTS/`
5. 循环直到通过
