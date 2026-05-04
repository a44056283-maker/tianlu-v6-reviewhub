# 天禄 V6.5 GitHub Review Hub — Mac B 工作台

## 身份
- 机器：Mac Mini (192.168.13.104)
- 角色：GitHub 审核工作台，与 GPT 协作的媒介
- 主人：爸
- Claude：VSCode 内置 Claude 插件

## 核心任务
把本地发生的事件（代码变更、配置调整、问题发现）通过 GitHub 传递给 GPT 审核，再把 GPT 的建议拿回来执行。

## Repo 结构
```
tianlu-v6-reviewhub/
├── 00_INSTRUCTIONS/          # 启动提示 + 风险模板
├── 03_PENDING_GPT_REVIEW/   # ← 放审核材料的地方
├── 04_GPT_REVIEW_RESPONSES/ # ← GPT 回复放这里
└── 04_MacB_SETUP/           # Mac B 配置脚本
```

## 日常工作流

### 场景 A：需要 GPT 审核代码/配置
1. 在 `03_PENDING_GPT_REVIEW/` 下建文件夹
   `YYYYMMDD_HHMMSS_任务名`
2. 把要审核的文件放进去（.py .json .sh .md 都行）
3. 写一个 `README.md` 说明要 GPT 审核什么
4. `git add . && git commit -m "提交信息" && git push origin main`
5. 把下面这个提示词连同 GitHub 链接发给 GPT：

```
请访问 https://github.com/a44056283-maker/tianlu-v6-reviewhub
进入 03_PENDING_GPT_REVIEW/[你建的文件夹名]/
阅读里面的材料并给出审计建议。
```

6. GPT 给出建议后：`git pull origin main`
7. 查看 `04_GPT_REVIEW_RESPONSES/` 下的回复

### 场景 B：收到 GPT 的回复，执行建议
1. 仔细阅读 GPT 回复
2. 在本地执行修改
3. 把修改结果放入新文件夹推送给 GPT 复审

### 场景 C：Mac A 发来任务
1. `git pull origin main`
2. 查看 `03_PENDING_GPT_REVIEW/` 有没有新任务
3. 执行或转发给 GPT

## Git 常用命令
```bash
# 拉取最新
git pull origin main

# 推送
git add .
git commit -m "你的更新说明"
git push origin main

# 查看状态
git status
git log --oneline -5
```

## 禁止事项
- 不要把 API keys / 密码 / secrets 上传到 GitHub
- 不要删除其他机器的提交
- 不要强制覆盖 (`--force`)

## GPT 沟通模板
```
请访问 https://github.com/a44056283-maker/tianlu-v6-reviewhub

仓库里有新的待审核任务：
03_PENDING_GPT_REVIEW/[文件夹名]/

请重点审核：[具体说明要关注什么]

审核完成后，请把回复保存为：
04_GPT_REVIEW_RESPONSES/[文件夹名]/GPT审核建议.md
```

## Mac A & Mac B 分工
| 机器 | IP | 职责 |
|------|-----|------|
| Mac A | 192.168.13.218 | 主控：OpenClaw / Freqtrade / 全部 bot |
| Mac B | 192.168.13.104 | 眼镜采集 + GitHub 审核工作台 |

## 联系方式
- Mac A 有完整天禄系统，可以执行代码修改
- Mac B 负责发现问题、传递问题、接收 GPT 建议
- 两台机器通过 GitHub 同步
