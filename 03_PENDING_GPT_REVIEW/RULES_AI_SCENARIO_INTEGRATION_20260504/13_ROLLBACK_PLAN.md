# V6.5.1 规则与AI场景接入 - 回滚计划

**文档编号**: 13_ROLLBACK_PLAN
**生成时间**: 2026-05-04 15:00:00
**回滚基准时间**: 2026-05-04 15:00:00
**执行代理**: 都察院（监察与QA）

---

## 一、备份目录

```
~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/
```

## 二、备份文件清单

本次更新涉及的备份文件（发布前由各子代理生成）：

### 2.1 策略代码备份
```
v65_autopilot.py.bak_<TIMESTAMP>
```
- 路径: `~/freqtrade_console/bt_tools/v65_autopilot.py`
- 备份由`02_CODEX_TASKS/策略代码子代理`生成

### 2.2 中控台代码备份
```
console_server.py.bak_<TIMESTAMP>
```
- 路径: `~/freqtrade_console/console_server.py`
- 备份由`03_CODEX_TASKS/中控台子代理`生成

### 2.3 Overlay 配置文件备份
```
config_gate_a63904550_overlay.json.bak_<TIMESTAMP>
config_gate_a15637798222_overlay.json.bak_<TIMESTAMP>
config_gate_b15637798222_overlay.json.bak_<TIMESTAMP>
config_gate_c15637798222_overlay.json.bak_<TIMESTAMP>
config_okx_xxx_overlay.json.bak_<TIMESTAMP>   (9093-9097各账号)
```
- 路径: `~/freqtrade_bots/user_data_<EXCHANGE>_<ACCOUNT>/`
- 备份由`04_CONFIG_PATCH子代理`生成

### 2.4 备份完整性验证命令
```bash
# 验证备份文件是否存在
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
ls -lh ${BACKUP_DIR}/v65_autopilot.py.bak_* \
        ${BACKUP_DIR}/console_server.py.bak_* \
        ${BACKUP_DIR}/*_overlay.json.bak_*
```

---

## 三、配置补丁回滚方法（Overlay JSON）

### 3.1 Overlay 文件路径（Mac A - 本地）
```
~/freqtrade_bots/user_data_gate_a63904550/config_gate_a63904550_overlay.json
~/freqtrade_bots/user_data_gate_a15637798222/config_gate_a15637798222_overlay.json
~/freqtrade_bots/user_data_gate_b15637798222/config_gate_b15637798222_overlay.json
~/freqtrade_bots/user_data_gate_c15637798222/config_gate_c15637798222_overlay.json
~/freqtrade_bots/user_data_okx_xxx/config_okx_xxx_overlay.json  (各账号)
```

### 3.2 Overlay 文件路径（Mac B - 远程，需SSH）
```
192.168.13.104:~/freqtrade_bots/user_data_gate_a63904550/config_gate_a63904550_overlay.json
192.168.13.104:~/freqtrade_bots/user_data_gate_a15637798222/config_a15637798222_overlay.json
192.168.13.104:~/freqtrade_bots/user_data_gate_b15637798222/config_b15637798222_overlay.json
192.168.13.104:~/freqtrade_bots/user_data_gate_c15637798222/config_c15637798222_overlay.json
```

### 3.3 回滚命令
```bash
# Mac A (本地) - 逐个回滚
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000

# Gate overlay (以 a63904550 为例，其他账号同理)
cp ${BACKUP_DIR}/config_gate_a63904550_overlay.json.bak_<TIMESTAMP> \
   ~/freqtrade_bots/user_data_gate_a63904550/config_gate_a63904550_overlay.json

# OKX overlay (各账号同理)
cp ${BACKUP_DIR}/config_okx_xxx_overlay.json.bak_<TIMESTAMP> \
   ~/freqtrade_bots/user_data_okx_xxx/config_okx_xxx_overlay.json

# Mac B (远程) - SSH执行
sshpass -p '613822' scp ${BACKUP_DIR}/config_gate_a63904550_overlay.json.bak_<TIMESTAMP> \
    luxiangnan@192.168.13.104:~/freqtrade_bots/user_data_gate_a63904550/config_gate_a63904550_overlay.json
```

---

## 四、代码补丁回滚方法

### 4.1 v65_autopilot.py 回滚
```bash
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
FREQTRADE_CONSOLE=~/freqtrade_console/bt_tools

# 查找最新备份
BAK_FILE=$(ls ${BACKUP_DIR}/v65_autopilot.py.bak_* | tail -1)

# 执行回滚
cp ${BAK_FILE} ${FREQTRADE_CONSOLE}/v65_autopilot.py

# 验证
md5sum ${BAK_FILE} ${FREQTRADE_CONSOLE}/v65_autopilot.py
```

### 4.2 console_server.py 回滚
```bash
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
FREQTRADE_CONSOLE=~/freqtrade_console

# 查找最新备份
BAK_FILE=$(ls ${BACKUP_DIR}/console_server.py.bak_* | tail -1)

# 执行回滚
cp ${BAK_FILE} ${FREQTRADE_CONSOLE}/console_server.py

# 验证
md5sum ${BAK_FILE} ${FREQTRADE_CONSOLE}/console_server.py
```

---

## 五、回滚后重启步骤

### 5.1 核心原则
> **只重启 console_server，不动机器人。**

### 5.2 重启步骤
```bash
# 1. 确认 console_server 进程PID
ps aux | grep console_server | grep -v grep

# 2. 停止 console_server
pkill -f "python.*console_server.py"   # 或用 launchctl / systemctl

# 3. 等待3秒确认进程退出
sleep 3

# 4. 确认机器人仍在运行（不应被影响）
ps aux | grep freqtrade | grep -v grep | wc -l

# 5. 重启 console_server（必须包含 SSL_CERT_FILE + PYTHONPATH）
cd ~/freqtrade_console
PYTHONPATH=/Users/luxiangnan/freqtrade \
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
python console_server.py &

# 6. 验证 console_server 启动成功
sleep 5
curl -s https://console.tianlu2026.org/api/health | head -1
```

---

## 六、分阶段回滚顺序

### Phase 1: 立即止血（0-5分钟）
1. 停止所有计划外的交易所API调用
2. 暂停 AI 场景评测功能（通过配置开关）
3. 确认 12 个机器人进程未被修改

### Phase 2: 配置回滚（5-15分钟）
1. 回滚 Mac A 所有 overlay 配置文件
2. 通过 SSH 回滚 Mac B 所有 overlay 配置文件
3. 验证 overlay 配置生效

### Phase 3: 代码回滚（15-30分钟）
1. 回滚 v65_autopilot.py
2. 回滚 console_server.py
3. 重启 console_server

### Phase 4: 验证（30-45分钟）
1. 确认 dashboard 可访问
2. 确认机器人状态正常
3. 确认英雄卡显示正常
4. 确认 pending_approvals.json 无异常积压

---

## 七、验证回滚成功的检查步骤

```bash
# === Phase 4 验证命令 ===

# 1. 确认 console_server 进程存活
ps aux | grep "python.*console_server.py" | grep -v grep

# 2. 确认 12 个机器人进程存活
ps aux | grep "freqtrade" | grep -v grep | wc -l
# 预期: 至少 12 个进程

# 3. 确认 dashboard 可访问
curl -s -o /dev/null -w "%{http_code}" https://console.tianlu2026.org/

# 4. 确认 v65_autopilot.py 内容正确
grep -c "V6.5" ~/freqtrade_console/bt_tools/v65_autopilot.py

# 5. 确认 console_server.py 版本正确
grep "ROLLBACK_MARKER\|VERSION" ~/freqtrade_console/console_server.py | head -5

# 6. 确认 overlay 配置未被修改（对比 checksum）
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
md5sum ${BACKUP_DIR}/config_*_overlay.json.bak_* | head -5
md5sum ~/freqtrade_bots/user_data_*/config_*_overlay.json | head -5

# 7. 确认 pending_approvals.json 无异常积压
cat ~/freqtrade_console/pending_approvals.json | python -c "import json,sys; d=json.load(sys.stdin); print(f'Pending: {len(d)}')"

# 8. 确认飞书通知正常
tail -5 ~/freqtrade_console.log | grep -i "feishu\|error\|alert"
```

---

## 八、回滚触发条件

### 8.1 立即回滚条件（任意一条满足即触发）
| 触发条件 | 严重程度 | 说明 |
|---------|---------|------|
| 机器人意外平仓 | P0 | 任何非计划内的平仓事件 |
| 账户资金异常 | P0 | 余额与预期差异 > 1% |
| API调用超限 | P0 | 触发交易所API限制 |
| console_server 崩溃 | P1 | 无法重启或反复崩溃 |
| Dashboard 无法访问 | P1 | 持续 > 5分钟 |
| Hero Card 显示异常 | P1 | 关键字段缺失或错误 |
| pending_approvals 积压 > 100 | P2 | 超过正常处理能力 |

### 8.2 评估后回滚条件（满足任意3条触发）
| 触发条件 | 说明 |
|---------|------|
| AI评测结果异常 | 置信度 > 95% 但方向错误 |
| 入场信号过于频繁 | 5分钟内 > 10个信号 |
| 策略规则不匹配 | 代码与文档描述不一致 |
| 备份文件损坏 | md5sum 不一致 |
| 关键功能失效 | 原功能无法正常使用 |

---

## 九、联系信息

| 角色 | 职责 | 联系方式 |
|-----|------|---------|
| 都察院 | 回滚决策与执行 | 本次执行 |
| 尚书省 | 紧急通知 | 飞书Webhook |
| 爸 | 最终决策者 | 手动确认 |

---

## 十、附录：快速回滚命令汇总

```bash
#!/bin/bash
# === 一键回滚脚本 ===
BACKUP_DIR=~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000
set -e

echo "[1/4] 回滚 v65_autopilot.py..."
cp $(ls ${BACKUP_DIR}/v65_autopilot.py.bak_* | tail -1) ~/freqtrade_console/bt_tools/v65_autopilot.py

echo "[2/4] 回滚 console_server.py..."
cp $(ls ${BACKUP_DIR}/console_server.py.bak_* | tail -1) ~/freqtrade_console/console_server.py

echo "[3/4] 回滚 overlay 配置（Mac A）..."
for f in ${BACKUP_DIR}/*_overlay.json.bak_*; do
  OVERLAY_NAME=$(basename $f .bak_*)
  TARGET_DIR=$(echo $OVERLAY_NAME | sed 's/config_\(.*\)_overlay/\1/' | sed 's/gate_/gate_/' | sed 's/okx_/okx_/')
  # 根据实际命名规则调整目标路径
  echo "  回滚: $OVERLAY_NAME"
done

echo "[4/4] 重启 console_server..."
pkill -f "python.*console_server.py" || true
sleep 3
cd ~/freqtrade_console && \
PYTHONPATH=/Users/luxiangnan/freqtrade \
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \
nohup python console_server.py > /dev/null 2>&1 &

echo "回滚完成！验证: curl https://console.tianlu2026.org/"
```

---

**文档状态**: 已生成
**下次审查**: 发布前由尚书省复核
