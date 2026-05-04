# 回滚计划 — LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT

> 生成时间：2026-05-04 14:30
> 用途：补丁执行后如出现问题，快速回滚到执行前状态
> 备份目录：`~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/`

---

## 一、配置补丁回滚（P0-1, P0-2）

### 回滚方法

每个overlay配置文件修改前都有备份：

```bash
# 例如 config_9090_overlay.json
BACKUP_DIR="/Users/luxiangnan/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000"

# 回滚 config_9090_overlay.json
cp "$BACKUP_DIR/config_9090_overlay.json.bak_20260504_150000" \
   ~/freqtrade_console/bt_tools/config_9090_overlay.json

# 重复对所有12个overlay配置文件执行
```

### 回滚命令脚本

```bash
#!/bin/bash
# rollback_overlay.sh — 回滚所有overlay配置
BACKUP_DIR="/Users/luxiangnan/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000"
TARGET_DIR="/Users/luxiangnan/freqtrade_console/bt_tools"

for f in config_9090_overlay.json config_9091_overlay.json config_9092_overlay.json \
         config_9093_overlay.json config_9094_overlay.json config_9095_overlay.json \
         config_9096_overlay.json config_9097_overlay.json; do
    BACKUP="$BACKUP_DIR/${f}.bak_20260504_150000"
    if [ -f "$BACKUP" ]; then
        cp "$BACKUP" "$TARGET_DIR/$f"
        echo "✅ 回滚: $f"
    else
        echo "⚠️  未找到备份: $BACKUP"
    fi
done
```

---

## 二、代码补丁回滚（P0-3, P0-4, P0-5, P1-1, P1-2, P1-3）

### 回滚方法

每个Python文件修改前都有备份：

```bash
BACKUP_DIR="/Users/luxiangnan/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000"

# 回滚 v65_autopilot.py
cp "$BACKUP_DIR/v65_autopilot.py.bak_20260504_142502" \
   ~/freqtrade_console/bt_tools/v65_autopilot.py

# 回滚 console_server.py
cp "$BACKUP_DIR/console_server.py.bak_20260504_142502" \
   ~/freqtrade_console/console_server.py
```

### 回滚后重启

代码回滚后需要重启 console_server 使修改生效：

```bash
# 找到 console_server 进程
ps aux | grep console_server | grep -v grep

# 重启（仅重启 console_server，不动机器人）
# 参考命令（需根据实际启动方式调整）
launchctl unload ~/Library/LaunchAgents/com.tianlu.console-server.plist
launchctl load ~/Library/LaunchAgents/com.tianlu.console-server.plist
```

---

## 三、回滚触发条件

| 条件 | 建议操作 |
|------|----------|
| 机器人无法正常入场 | 立即回滚所有overlay配置 |
| 机器人无法正常止损 | 立即回滚 P0-3（DCA清除止损冷却） |
| 出场异常（无法止盈或提前平仓） | 立即回滚 P0-4（ExitDecisionGate） |
| console_server 无法启动 | 立即回滚 console_server.py 并重启 |
| Mac B bot 无响应 | 手动SSH到Mac B执行rollback_overlay.sh |

---

## 四、分阶段回滚顺序

如果需要选择性回滚，按以下顺序：

1. **首先**：回滚 overlay 配置（P0-1 DOGE冻结 + P0-2 SOL DCA暂停）
2. **其次**：回滚 v65_autopilot.py（P0-3~P1-3）
3. **最后**：回滚 console_server.py（P1-1 ForceGuard审计日志）

---

## 五、验证回滚成功

```bash
# 验证 overlay 配置 JSON 语法正确
python3 -c "import json; json.load(open('~/freqtrade_console/bt_tools/config_9090_overlay.json'))"

# 验证 v65_autopilot.py 语法正确
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py

# 验证 console_server.py 语法正确
python3 -m py_compile ~/freqtrade_console/console_server.py

# 确认机器人日志无异常
tail -50 ~/freqtrade_bots/user_data_*/logs/*.log 2>/dev/null | grep -i error
```

---

*兵部存档 | 2026-05-04*
