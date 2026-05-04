# 06_ROLLBACK_PLAN.md

## 回滚方案

**草案文件** | **Stage C 灰度失败时执行**

---

## 1. 回滚触发条件

以下任一情况发生时，执行回滚：

| 条件 | 严重程度 |
|------|----------|
| py_compile 失败 | 🔴 阻断 |
| 9090 bot 掉线 | 🔴 阻断 |
| 意外阻断正常交易（非测试币对）| 🔴 阻断 |
| Shadow 模式日志出现错误堆栈 | 🟠 高 |
| 内存/CPU 异常增长 | 🟠 高 |
|爸手动要求回滚 | 🔴 阻断 |

---

## 2. 回滚层级

### Level 1：Shadow 模式回滚（最快）

如果补丁处于 Shadow 模式，只需将 `_SHADOW_MODE = True` 改回：

```bash
# 编辑代码
sed -i '' 's/_SHADOW_MODE = False/_SHADOW_MODE = True/' \
    ~/freqtrade_console/bt_tools/v65_autopilot.py

# py_compile
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py

# 重启 console_server
pkill -f "console_server.py" && sleep 2
cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &

# 验证
sleep 5
curl -s http://127.0.0.1:9099/api/health | grep ok && echo "✅ console_server OK"
```

### Level 2：完全回滚补丁（补丁应用后）

```bash
# 从 git 回滚 v65_autopilot.py
cd ~/freqtrade_console
git checkout HEAD -- bt_tools/v65_autopilot.py

# 验证
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo "✅ 回滚后 py_compile OK"

# 重启 console_server
pkill -f "console_server.py" && sleep 2
cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &

# 验证 bot 存活
for port in 9090 9091 9092; do
    result=$(curl -s --max-time 5 "http://127.0.0.1:${port}/api/v1/status" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trade_mode', 'ERR'))" 2>/dev/null)
    echo "9090 bot trade_mode: $result"
done
```

### Level 3：回滚 overlay 配置（如果已写入 freeze/pause 规则）

```bash
# 恢复 9090 overlay
cp ~/freqtrade/config_9090_overlay.json.bak.20260504 \
   ~/freqtrade/config_9090_overlay.json

# 验证
python3 -m json.tool ~/freqtrade/config_9090_overlay.json >/dev/null && echo "✅ overlay JSON OK"

# 不需要重启 bot（overlay 只在下次启动生效）
```

---

## 3. 回滚检查清单

| 检查项 | 命令 | 预期结果 |
|--------|------|----------|
| console_server 运行 | `curl -s http://127.0.0.1:9099/api/health` | `{"ok": true}` |
| 9090 bot 存活 | `curl -s --max-time 5 http://127.0.0.1:9090/api/v1/status` | HTTP 200 |
| py_compile 通过 | `python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py` | 无错误 |
| git status | `cd ~/freqtrade_console && git status bt_tools/v65_autopilot.py` | 无变更（Level 2）或已回滚 |
| 日志无 Freeze/DCA-Pause 异常 | `grep -i "error\|exception\|traceback" ~/.console_server.log \| tail -10` | 无异常堆栈 |

---

## 4. 回滚后报告

回滚完成后必须：
1. 在 `TEST_LOG.md` 中记录回滚时间和原因
2. 通知爸（通过飞书 webhook 或直接告知）
3. 分析根因，更新补丁后重新提交 Stage B

---

## 5. 回滚命令速查表

```bash
# Level 1: Shadow 关闭
sed -i '' 's/_SHADOW_MODE = False/_SHADOW_MODE = True/' ~/freqtrade_console/bt_tools/v65_autopilot.py
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo OK
pkill -f "console_server.py"; sleep 2; cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &

# Level 2: 补丁完全回滚
cd ~/freqtrade_console && git checkout HEAD -- bt_tools/v65_autopilot.py
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo OK
pkill -f "console_server.py"; sleep 2; cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &

# Level 3: overlay 配置恢复
cp ~/freqtrade/config_9090_overlay.json.bak.20260504 ~/freqtrade/config_9090_overlay.json
python3 -m json.tool ~/freqtrade/config_9090_overlay.json >/dev/null && echo OK
```

---

## 6. 恢复测试计划

回滚后 30 分钟内：
- [ ] 检查 9090-9097 所有 bot 状态正常
- [ ] 检查 Mac B 8081-8084 所有 bot 状态正常
- [ ] 检查 console_server 日志无异常
- [ ] 确认正常交易未受影响
- [ ] 通知爸回滚已完成
