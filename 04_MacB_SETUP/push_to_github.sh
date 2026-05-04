#!/bin/bash
# Mac B → GitHub 推送脚本
# 用法: ./push_to_github.sh "提交信息"

set -e
REPO_DIR="$HOME/Desktop/tianlu-v6-reviewhub"
cd "$REPO_DIR"

MSG="${1:-Mac B 更新 - $(date +%Y%m%d_%H%M%S)"}"

echo "正在推送..."
git add -A
git commit -m "$MSG"
git push origin main

echo "✓ 推送完成: $MSG"
