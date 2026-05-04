#!/bin/bash
# 补丁应用脚本 - Mac A (本地执行)
# 用途: 将PENDING_PATCH目录下的已验证补丁文件复制到实际配置位置
# 前提: 已执行validate_json_syntax.py确认所有文件通过JSON验证
#
# 使用方法:
#   cd ~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/20260504_150000_LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT/PENDING_PATCH
#   ./apply_patches_mac_a.sh
#
# 回滚:
#   cd ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
#   for f in *.bak_20260504_150000; do cp "$f" "${f%.bak_20260504_150000}" ; done

set -e

PENDING_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_DIR="$(cd "$PENDING_DIR/../.." && pwd)/04_BACKUPS/live_rollout_20260504_150000"
FREQTRADE_DIR="$HOME/freqtrade"

echo "============================================"
echo "补丁应用脚本 - Mac A bots (9090-9097)"
echo "============================================"
echo "备份目录: $BACKUP_DIR"
echo "Freqtrade目录: $FREQTRADE_DIR"
echo ""

# Step 1: 验证JSON语法
echo "[1/4] 验证JSON语法..."
python3 "$PENDING_DIR/validate_json_syntax.py"
if [ $? -ne 0 ]; then
    echo "JSON验证失败，退出!"
    exit 1
fi
echo "JSON验证通过"
echo ""

# Step 2: 备份现有配置文件
echo "[2/4] 备份现有配置文件..."

# 9090特殊: FOttStrategy基础配置在bt_tools目录
bt_tools_src="$HOME/freqtrade_console/bt_tools/config_9090_overlay.json"
if [ -f "$bt_tools_src" ]; then
    cp "$bt_tools_src" "$BACKUP_DIR/config_9090_overlay.json.bak_20260504_150000"
    echo "  BACKUP: bt_tools/config_9090_overlay.json (FOttStrategy base)"
else
    echo "  SKIP (不存在): bt_tools/config_9090_overlay.json"
fi

# 9091-9097 exchange overlays in freqtrade directory
for port in 9091 9092 9093 9094 9095 9096 9097; do
    src="$FREQTRADE_DIR/config_${port}_overlay.json"
    if [ -f "$src" ]; then
        cp "$src" "$BACKUP_DIR/config_${port}_overlay.json.bak_20260504_150000"
        echo "  BACKUP: config_${port}_overlay.json"
    else
        echo "  SKIP (不存在): config_${port}_overlay.json"
    fi
done
echo ""

# Step 3: 备份基础策略配置 (9090 base strategy)
echo "[3/4] 备份基础策略配置..."
# 注意: 9090的base strategy位于bt_tools目录,但实际部署时已被上面的覆盖
# 如果bt_tools/config_9090_overlay.json也需要补丁,单独处理
echo "  SKIP: 基础策略在overlay合并后不再单独读取"
echo ""

# Step 4: 应用补丁 (复制PATCHED文件到实际位置)
echo "[4/4] 应用补丁..."

# 9090: bt_tools FOttStrategy base config
bt_tools_dst="$HOME/freqtrade_console/bt_tools/config_9090_overlay.json"
bt_tools_patch="$PENDING_DIR/config_9090_overlay_PATCHED.json"
if [ -f "$bt_tools_patch" ]; then
    cp "$bt_tools_patch" "$bt_tools_dst"
    echo "  APPLIED: config_9090_overlay_PATCHED.json -> bt_tools/config_9090_overlay.json"
fi

# 9091-9097: exchange overlays
for port in 9091 9092 9093 9094 9095 9096 9097; do
    src="$PENDING_DIR/config_${port}_overlay_PATCHED.json"
    dst="$FREQTRADE_DIR/config_${port}_overlay.json"
    if [ -f "$src" ]; then
        cp "$src" "$dst"
        echo "  APPLIED: config_${port}_overlay_PATCHED.json -> config_${port}_overlay.json"
    else
        echo "  SKIP (不存在): config_${port}_overlay_PATCHED.json"
    fi
done

echo ""
echo "============================================"
echo "补丁应用完成!"
echo "============================================"
echo ""
echo "下一步:"
echo "1. 重启需要应用补丁的bot (overlay在启动时加载)"
echo "2. 验证: curl http://127.0.0.1:9090/api/v1/show_config | python3 -m json.tool | grep -E 'temporary_pair_freeze|dca_pause_rules'"
echo "3. 如需回滚: $BACKUP_DIR/*.bak_20260504_150000"
echo ""
