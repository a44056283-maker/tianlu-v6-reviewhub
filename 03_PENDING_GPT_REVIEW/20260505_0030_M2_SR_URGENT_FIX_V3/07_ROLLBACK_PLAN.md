# ROLLBACK_PLAN.md

## 回滚方案

**草案文件** | **补丁应用后发现问题时执行**

---

## 回滚触发条件

| 条件 | 严重程度 |
|------|----------|
| py_compile 失败 | 🔴 阻断 |
| console_server 无法启动 | 🔴 阻断 |
| 前端页面报错 | 🟠 高 |
| 实时价格不刷新 | 🟠 高 |
| 爸手动要求回滚 | 🔴 阻断 |

---

## Level 1: 回滚补丁（最快）

```bash
# 回滚 console_server.py
cd ~/freqtrade_console
git checkout HEAD -- console_server.py

# 回滚 m2_sr.html
git checkout HEAD -- static/tabs/m2_sr.html

# py_compile 验证
python3 -m py_compile ~/freqtrade_console/console_server.py && echo "✅ OK"

# 重启 console_server（不动机器人）
pkill -f "console_server.py" && sleep 2
cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &
sleep 5
curl -s http://127.0.0.1:9099/api/health | grep ok && echo "✅ console_server OK"
```

---

## Level 2: 恢复旧缓存（如果 realtime_prices 被破坏）

```bash
# 从归档恢复
ARCHIVE="/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/stale_cache_archive/20260504_234911"
rsync -a "$ARCHIVE/realtime_prices/" /tmp/tianlu_cache/realtime_prices/
echo "✅ 旧缓存已恢复"

# 验证
ls -lh /tmp/tianlu_cache/realtime_prices/
```

---

## Level 3: 完全回滚（补丁 + 缓存 + 启动器）

```bash
# 停止刷新定时器（重启 console_server 自动停止）
# 1. 回滚补丁
cd ~/freqtrade_console
git checkout HEAD -- console_server.py static/tabs/m2_sr.html

# 2. 重启 console_server
pkill -f "console_server.py" && sleep 2
cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &

# 3. 验证机器人状态
for port in 9090 9091 9092; do
    curl -s --max-time 5 "http://127.0.0.1:${port}/api/v1/status" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'${port}: {d.get(\"trade_mode\", \"ERR\")}')" 2>/dev/null || echo "${port}: 错误"
done
```

---

## 回滚检查清单

| 检查项 | 命令 | 预期 |
|--------|------|------|
| console_server 运行 | `curl -s http://127.0.0.1:9099/api/health` | `{"ok": true}` |
| py_compile | `python3 -m py_compile console_server.py` | 无错误 |
| 机器人存活 | `curl -s --max-time 5 http://127.0.0.1:9090/api/v1/status` | HTTP 200 |
| git status | `cd ~/freqtrade_console && git status` | 无未提交更改 |

---

## 回滚后通知

回滚完成后：
1. 记录回滚时间和原因到 `TEST_LOG.md`
2. 通知爸（飞书或直接告知）
3. 分析根因，更新补丁后重新提交
