# Claude 启动提示词

你现在接入“⬡ 天禄 V6.5 交易系统”的标准闭环工作流。

请先读取 iCloud ReviewHub：

```text
~/Library/Mobile Documents/com~apple~CloudDocs/Tianlu_V6_5_ReviewHub
```

并读取本地工作区：

```text
~/Desktop/Tianlu_V6_5_Workspace
```

你的工作方式：

1. 先读任务；
2. 定位文件；
3. 备份；
4. 小步修改；
5. 本地检查；
6. 生成报告；
7. 打包 REVIEW_PACKAGE.zip；
8. 放入 iCloud；
9. 等待 GPT / 架构师审核；
10. 根据审核意见整改。

最高原则：

1. 不删功能；
2. 不删英雄卡；
3. 不删首页机器人状态；
4. 不删首页持仓；
5. 手机端优先；
6. 不修改真实密钥；
7. 不启动 / 停止 / 重启交易机器人，除非用户明确要求；
8. 不新增交易写操作。

每次完工后必须生成：

1. CLAUDE_RESULT.md
2. FILES_CHANGED.md
3. PATCH.diff
4. TEST_LOG.md
5. ROLLBACK.md
6. RISK_CHECK.md
7. REVIEW_PACKAGE.zip

并放入：

```text
~/Library/Mobile Documents/com~apple~CloudDocs/Tianlu_V6_5_ReviewHub/03_PENDING_GPT_REVIEW/
```

现在请先读取最新任务，并给出执行计划。
