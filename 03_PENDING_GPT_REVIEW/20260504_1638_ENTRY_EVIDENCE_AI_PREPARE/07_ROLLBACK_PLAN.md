# 07_ROLLBACK_PLAN.md
# 回滚方案

## 概述

本文件描述如何安全回滚 EntryDecisionGate 相关代码。所有草案均为**非侵入式**设计，回滚操作简单安全。

---

## 回滚原则

1. **删除即回滚**：如果 EntryDecisionGate 代码未写入实盘文件，则无需回滚
2. **环境变量优先**：改变量即可立即停止 AI 介入
3. **不改配置文件**：无需修改 robot config 或 database

---

## 回滚场景

### 场景A：草案文件未接入实盘（当前状态）

**当前状态**：所有文件都在 `20260504_1638_ENTRY_EVIDENCE_AI_PREPARE/` 目录，未写入 `~/freqtrade_console/`

**无需任何操作**

---

### 场景B：草案已接入 console_server.py，但需回滚

**操作步骤**：

```bash
# 1. 立即停止 AI 介入（无需重启进程）
export TIANLU_ENTRY_GATE_MODE=dry
export TIANLU_EXIT_GATE_MODE=dry

# 2. 确认已停止
curl http://127.0.0.1:9099/api/gate/status
# 预期: {"entry_mode":"dry","exit_mode":"dry","is_shadow":false}

# 3. 找到接入点并删除（引用: 01_ENTRY_DECISION_GATE_CODE_DRAFT.md 集成点）
#    在 v65_autopilot.py:1257 附近删除:
#    gate_result = evaluate(pair, direction, current_price)
#    _log(f"[EntryGate] ...")

# 4. 删除新建文件（如果已创建）
rm -f ~/freqtrade_console/bt_tools/entry_decision_gate.py
rm -f ~/freqtrade_console/bt_tools/runtime_switch.py

# 5. 重启 console_server（仅此操作需要重启）
pkill -f "console_server.py" && sleep 2 && cd ~/freqtrade_console && \
  SSL_CERT_FILE=... PYTHONPATH=... python console_server.py &

# 6. 验证回滚成功
curl http://127.0.0.1:9099/api/gate/status
# 预期: 404 或错误（因为API已删除）
```

---

### 场景C：只需暂停 AI 介入（不删除代码）

**操作步骤**：

```bash
# 方法1: 环境变量（立即生效，无需重启）
export TIANLU_ENTRY_GATE_MODE=dry
export TIANLU_EXIT_GATE_MODE=dry

# 方法2: API动态切换（需console_server支持 05_SHADOW_MODE_RUNTIME_SWITCH.md）
curl -X POST http://127.0.0.1:9099/api/gate/mode \
  -H "Content-Type: application/json" \
  -d '{"entry_mode": "dry", "exit_mode": "dry"}'

# 验证
curl http://127.0.0.1:9099/api/gate/status
```

---

### 场景D：恢复到特定版本

```bash
# 1. 找到最近一次接入前的 git commit
cd ~/freqtrade_console
git log --oneline -10

# 2. 恢复到接入前版本（不影响 bot 数据）
git checkout <commit_hash> -- console_server.py bt_tools/v65_autopilot.py

# 3. 删除新建文件（如有）
rm -f bt_tools/entry_decision_gate.py
rm -f bt_tools/runtime_switch.py

# 4. 重启 console_server
pkill -f "console_server.py"
cd ~/freqtrade_console && python console_server.py &
```

---

## 回滚验证清单

回滚完成后执行：

- [ ] `curl http://127.0.0.1:9099/api/gate/status` 返回 404 或错误
- [ ] Bot 日志中无 `[EntryGate]` 字样
- [ ] Bot 日志中无 `[天眼AI][SHADOW]` 字样
- [ ] Bot 日志中无 `[出山AI][SHADOW]` 字样
- [ ] 机器人正常接收交易信号（无 EntryGate 拦截）
- [ ] `/api/m1/hero_card` 正常返回
- [ ] `/api/bt2/sr_levels` 正常返回
- [ ] V6.5 自动驾驶正常（不受影响）

---

## 快速回滚命令

```bash
# 一键回滚（需在 ~/freqtrade_console 目录下执行）
# 1. 停止 AI 介入
export TIANLU_ENTRY_GATE_MODE=dry
export TIANLU_EXIT_GATE_MODE=dry

# 2. 删除新建文件
rm -f bt_tools/entry_decision_gate.py bt_tools/runtime_switch.py 2>/dev/null

# 3. 确认无新增代码（检查关键字）
grep -n "EntryDecisionGate\|entry_decision_gate\|_log_gate\|call_tianyan_ai\|call_chushan" \
  bt_tools/v65_autopilot.py console_server.py
# 预期: 无匹配（或仅有注释）

# 4. 重启 console_server（如有代码被修改）
pkill -f "console_server.py" 2>/dev/null
sleep 2
cd ~/freqtrade_console && python console_server.py > /dev/null 2>&1 &
echo "回滚完成"
```

---

## Bot 隔离性确认

**关键保证**：EntryDecisionGate 设计为**只读**模块，不修改任何机器人参数：

- [ ] 不修改 `balance` 或 `stake_amount`
- [ ] 不调用 `force_entry` 或 `force_exit`
- [ ] 不修改 `leverage` 或 `position_pct`
- [ ] 只读取 M1-M5 evidence（read-only）
- [ ] 只写日志文件

因此回滚不会影响正在运行的机器人。

---

## 紧急联系人

如回滚后仍有问题：
1. 检查机器人状态：`~/freqtrade_console/bot_manager.sh status`
2. 检查 console_server 日志：`tail -f ~/.freqtrade_console.log`
3. 如需完全恢复：使用 git 回滚（见场景D）
