#!/bin/bash
# Mac B GitHub Review Hub 配置脚本
# 来源: tianlu-v6-reviewhub/04_MacB_SETUP/

set -e

REPO_DIR="$HOME/Desktop/tianlu-v6-reviewhub"
SCRIPT_DIR="$REPO_DIR/04_MacB_SETUP"

echo "===== Mac B GitHub Review Hub 配置 ====="

# 1. SSH 密钥验证
echo "[1/5] 验证 GitHub SSH 访问..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "  ✓ SSH key 已授权"
else
    echo "  ✗ SSH key 未授权，请到 GitHub 添加 Mac-Mini-B 公钥"
    exit 1
fi

# 2. Git 配置
echo "[2/5] Git 用户配置..."
git config --global user.name "天禄MacB" || true
git config --global user.email "a44056283@gmail.com" || true
echo "  ✓ Git 已配置"

# 3. 确认 repo 存在
echo "[3/5] 检查 repo..."
if [ -d "$REPO_DIR" ]; then
    echo "  ✓ Repo 已存在: $REPO_DIR"
else
    echo "[3/5] 克隆 repo..."
    mkdir -p "$(dirname $REPO_DIR)"
    git clone git@github.com:a44056283-maker/tianlu-v6-reviewhub.git "$REPO_DIR"
    echo "  ✓ Repo 克隆成功"
fi

# 4. 检查最新待审核任务
echo "[4/5] 待审核任务..."
LATEST=$(ls -t "$REPO_DIR/03_PENDING_GPT_REVIEW/" 2>/dev/null | head -1)
if [ -n "$LATEST" ]; then
    echo "  ✓ 最新审核包: $LATEST"
    echo "  内容: $(ls "$REPO_DIR/03_PENDING_GPT_REVIEW/$LATEST/" | head -5)"
else
    echo "  - 暂无待审核任务"
fi

# 5. 推送测试
echo "[5/5] 测试推送权限..."
cd "$REPO_DIR"
echo "# Mac B test $(date)" >> README.md
git add README.md
git commit -m "Mac B 配置完成 - $(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
git push origin main 2>/dev/null && echo "  ✓ 推送成功" || echo "  - 无变化或推送失败"

echo ""
echo "===== Mac B 配置完成 ====="
echo ""
echo "使用流程："
echo "1. 将审核材料放入 03_PENDING_GPT_REVIEW/YYYYMMDD_HHMMSS_任务名/"
echo "2. 运行 ./scripts/pack_review_package.sh 构建审核包"
echo "3. 运行 ./scripts/push_to_github.sh 推送到 GitHub"
echo "4. 让 GPT 读取 GitHub 上的审核材料并给出建议"
echo "5. 将 GPT 建议放入 04_GPT_REVIEW_RESPONSES/ 对应日期文件夹"
echo ""
