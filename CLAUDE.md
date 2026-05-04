# Mac B → GPT 直接审核流程

## 你的任务
你（Mac B）发现了问题或有代码要给 GPT 审核。把文件推到 GitHub，GPT 直接读链接就给建议。

## 极简流程（3步）

### 第1步：把文件放入临时文件夹
```bash
TASK="g2_bridge_问题_$(date +%Y%m%d_%H%M%S)"
mkdir -p ~/Desktop/tianlu-v6-reviewhub/05_MacB_PROJECT_FILES/$TASK
# 把要审核的文件复制进去
cp ~/你的项目文件.py ~/Desktop/tianlu-v6-reviewhub/05_MacB_PROJECT_FILES/$TASK/
```

### 第2步：推送 GitHub
```bash
cd ~/Desktop/tianlu-v6-reviewhub
git add 05_MacB_PROJECT_FILES/$TASK/
git commit -m "Mac B 请 GPT 审核: $TASK"
git push origin main
```

### 第3步：把这个链接发给 GPT
```
请读取这个 GitHub 链接的文件，给我建议：

https://github.com/a44056283-maker/tianlu-v6-reviewhub/tree/main/05_MacB_PROJECT_FILES/[TASK文件夹名]

要审核的内容是：[简述要 GPT 看什么/解决什么问题]
```

## GPT 审核结果获取

GPT 审核后会让你去 `04_GPT_REVIEW_RESPONSES/` 查看建议：
```bash
cd ~/Desktop/tianlu-v6-reviewhub
git pull origin main
# 查看 04_GPT_REVIEW_RESPONSES/ 下的 GPT 回复
```

## 文件夹用途

| 文件夹 | 用途 |
|--------|------|
| `05_MacB_PROJECT_FILES/TASK名/` | 放你要 GPT 审核的项目文件 |
| `03_PENDING_GPT_REVIEW/` | Mac A 的审核任务（不用管） |
| `04_GPT_REVIEW_RESPONSES/` | GPT 审核建议放这里，git pull 后可查看 |

## 禁止
- 不要推 API keys / 密码 / tokens
- 敏感配置推前检查一遍

## SSH 已就绪
Mac B 的 SSH key `Mac-Mini-B` 已配置好，直接 push 即可。