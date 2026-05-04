# 06_APPLY_AND_RESTART_CONSOLE_SERVER_PLAN.md
# V3 应用与重启 console_server 计划

**⚠️ 前提条件：GPT 审核批准后方可执行**
**⚠️ 本次操作仅重启 console_server，不动任何机器人**

---

## 执行前检查清单

- [ ] GPT 审核批准 V3
- [ ] py_compile 已通过（本文档附件）
- [ ] 机器人状态正常（9090-9097 端口可访问）
- [ ] 备份已创建

---

## 步骤 1：备份当前文件

```bash
cd ~/freqtrade_console
cp console_server.py console_server.py.bak.$(date +%Y%m%d_%H%M%S)
cp static/tabs/m2_sr.html static/tabs/m2_sr.html.bak.$(date +%Y%m%d_%H%M%S)
echo "✅ 备份完成"
```

---

## 步骤 2：应用补丁

### 后端（console_server.py）

在 `print("[Startup] Background pre-warm started: scanner + realtime prices")` 之后插入：

```python
    # ── V2: 实时价格定期刷新定时器（解决启动后数小时不更新问题）────────
    _rt_refresh_scheduled = False
    _RT_PRICE_REFRESH_INTERVAL = int(os.environ.get("TIANLU_RT_PRICE_REFRESH_MIN", "30")) * 60
    _rt_price_refresh_timer = None

    def _schedule_rt_price_refresh():
        """每 N 分钟刷新一次实时价格缓存（daemon Thread，不影响主逻辑）"""
        global _rt_price_refresh_timer
        try:
            _prewarm_realtime_prices()
            import logging as _rt_log
            _rt_log.getLogger("console_server").info(
                f"[RT-Price-Refresh] 实时价格缓存刷新完成 (间隔: {_RT_PRICE_REFRESH_INTERVAL//60}分钟)")
        except Exception as e:
            import logging as _rt_log
            _rt_log.getLogger("console_server").warning(f"[RT-Price-Refresh] 刷新失败: {e}")
        _rt_price_refresh_timer = threading.Timer(_RT_PRICE_REFRESH_INTERVAL, _schedule_rt_price_refresh)
        _rt_price_refresh_timer.daemon = True
        _rt_price_refresh_timer.start()

    def _cancel_rt_price_refresh():
        global _rt_price_refresh_timer
        if _rt_price_refresh_timer:
            _rt_price_refresh_timer.cancel()
            _rt_price_refresh_timer = None

    # V3 修复: 初始 Timer 也设置 daemon=True，防止退出时阻塞
    if _startup_autoscans_enabled() and os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") != "1":
        if not _rt_refresh_scheduled:
            _rt_refresh_scheduled = True
            t = threading.Timer(300, _schedule_rt_price_refresh)
            t.daemon = True   # V3 修复: 防止退出时阻塞
            t.start()
            print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

在 `_prewarm_realtime_prices()` 函数之后（或 startup block 之后）插入并行函数（见 PATCH.diff）。

在 `api_bt2_sr_levels_default()` 的 `result_pairs = {}` 之后、`for pair in pairs:` 之前插入 force_live 调用（见 PATCH.diff）。

### 前端（m2_sr.html）

见 PATCH.diff 中的 m2_sr.html 补丁。

---

## 步骤 3：py_compile 验证

```bash
cd ~/freqtrade_console
python3 -m py_compile console_server.py && echo "✅ 后端 OK"
python3 -c "import ast; ast.parse(open('console_server.py').read())" && echo "✅ AST OK"
```

---

## 步骤 4：重启 console_server

```bash
# 停止
pkill -f "console_server.py" && sleep 2

# 启动
cd ~/freqtrade_console
nohup python3 console_server.py >> ~/.console_server.log 2>&1 &
sleep 5

# 验证
curl -s --max-time 8 http://127.0.0.1:9099/api/health && echo "✅ console_server OK"
```

---

## 步骤 5：验证功能

```bash
# 检查日志中是否有定时器启动消息
grep "RT-Price-Refresh\|实时价格定期刷新" ~/.console_server.log | tail -5

# 检查 API 响应
curl -s --max-time 8 "http://127.0.0.1:9099/api/bt2/sr_levels" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'✅ API OK: {d.get(\"_cache\",{}).get(\"state\",\"?\")}')
"

# 检查机器人状态（不动机器人，只读）
curl -s --max-time 5 http://127.0.0.1:9090/api/v1/status | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'✅ Bot 9090: {d.get(\"trade_mode\",\"ERR\")}')
" 2>/dev/null || echo "⚠️ Bot 9090 未启动（可能是其他原因）"
```

---

## 步骤 6：前端验证

1. 打开浏览器，访问 M2 页面
2. 检查 topbar 右侧是否有缓存年龄指示器（🟢/🟡/🟠/🔴）
3. 点击"强制刷新"按钮，确认响应时间 < 15秒
4. 等待5分钟后，检查日志中有无 `[RT-Price-Refresh] 实时价格缓存刷新完成`

---

## 执行后检查清单

- [ ] console_server 重启成功
- [ ] API 响应正常
- [ ] 缓存指示器显示
- [ ] 机器人未受影响（trade_mode 未变）
- [ ] 日志中有 `[RT-Price-Refresh]` 消息
