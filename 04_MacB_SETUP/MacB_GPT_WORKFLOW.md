# Mac B 天禄 GPT 审核流程（给 GPT 的说明）

## Mac B 身份
- 机器: Mac Mini (192.168.13.104)
- 主人: 爸
- GitHub: a44056283-maker
- Repo: https://github.com/a44056283-maker/tianlu-v6-reviewhub

## Repo 目录结构
```
tianlu-v6-reviewhub/
├── 00_INSTRUCTIONS/
│   ├── CLAUDE_START_PROMPT.md    ← Claude Code 启动提示
│   └── RISK_CHECK_TEMPLATE.md    ← 风险检查模板
├── 03_PENDING_GPT_REVIEW/        ← 待审核任务（我放这里）
│   └── YYYYMMDD_HHMMSS_任务名/
│       ├── *.md 审核材料
│       └── *_INPUT.zip 打包附件
├── 04_GPT_REVIEW_RESPONSES/       ← GPT 回复放这里
│   └── YYYYMMDD_HHMMSS_任务名/
│       └── GPT_审核建议.md
└── README.md
```

## 日常使用流程

### 步骤 1: 创建审核任务文件夹
日期格式: `YYYYMMDD_HHMMSS_任务简述`
例: `20260504_143000_交易规则优化审查`

### 步骤 2: 放入审核材料
把要 GPT 审核的材料（代码/配置/报告）放入上述文件夹

### 步骤 3: 给 GPT 的提示词
把以下提示词连同 GitHub 链接一起发给 GPT:

```
请访问 https://github.com/a44056283-maker/tianlu-v6-reviewhub
进入 03_PENDING_GPT_REVIEW/20260504_143000_任务名/ 目录
阅读里面的审核材料，给出详细审计建议。

审核维度：
1. 架构设计是否合理
2. 风险控制是否完善
3. 策略逻辑是否正确
4. 代码质量和安全性
5. 是否有遗漏的边界情况

将回复保存为 04_GPT_REVIEW_RESPONSES/20260504_143000_任务名/GPT_审核建议.md
```

### 步骤 4: GPT 审核
GPT 读取 GitHub 上的材料，给出审核建议

### 步骤 5: 本地获取审核结果
```bash
cd ~/Desktop/tianlu-v6-reviewhub
git pull origin main
```

## Mac B 上的常用操作

```bash
# 拉取最新审核结果
cd ~/Desktop/tianlu-v6-reviewhub && git pull origin main

# 查看待审核任务
ls -lt 03_PENDING_GPT_REVIEW/

# 查看 GPT 回复
ls -lt 04_GPT_REVIEW_RESPONSES/

# 推送我的更新到 GitHub
cd ~/Desktop/tianlu-v6-reviewhub
git add -A
git commit -m "Mac B 更新说明"
git push origin main
```

## 注意事项
- Mac B 没有安装 OpenClaw，仅用 GitHub 与 GPT 沟通
- 所有敏感信息（API keys, 密码）不要上传到 GitHub
- 审核材料可以包含代码、配置、截图描述、问题描述
- GPT 需要有 GitHub 账号并获得仓库访问权限（设为 Public 即可）

## 联系
- Mac A (主控): 192.168.13.218, 有 OpenClaw + 完整天禄系统
- Mac B (眼镜): 192.168.13.104, 用于眼镜数据采集 + GitHub 审核
