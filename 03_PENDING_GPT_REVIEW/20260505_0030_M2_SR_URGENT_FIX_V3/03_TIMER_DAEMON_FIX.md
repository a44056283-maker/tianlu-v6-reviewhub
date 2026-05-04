# 03_TIMER_DAEMON_FIX.md
# V3 修正 #3: 300秒初始 Timer 添加 daemon=True

---

## 根因分析

### V2 代码

```python
# 启动时调度首次刷新（延迟5分钟，防阻塞 Flask 启动）
if _startup_autoscans_enabled() and os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") != "1":
    if not _rt_refresh_scheduled:
        _rt_refresh_scheduled = True
        threading.Timer(300, _schedule_rt_price_refresh).start()  # ← 无 daemon 标志
        print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

### 问题

V2 已正确给 `_rt_price_refresh_timer`（后续的周期性 Timer）设置 `daemon = True`：

```python
_rt_price_refresh_timer = threading.Timer(_RT_PRICE_REFRESH_INTERVAL, _schedule_rt_price_refresh)
_rt_price_refresh_timer.daemon = True  # ✅ 已设置
_rt_price_refresh_timer.start()
```

但 **300秒的初始启动 Timer** 没有设置 `daemon = True`。
Python 进程中若存在非 daemon 线程，进程不会退出。
Flask 正常运行时这不影响，但进程收到退出信号时，
非 daemon Timer 会阻塞退出流程。

### 影响场景

| 场景 | 非 daemon Timer 影响 |
|------|---------------------|
| Flask 正常运行 | 无影响 |
| 进程收到 SIGTERM（`pkill`）| Timer 未触发时可能阻塞退出 |
| Ctrl+C 中断（开发环境）| Timer 未触发时可能阻塞 |
| Restart console_server | 无影响（直接杀进程）|

---

## V3 修正

```python
# 启动时调度首次刷新（延迟5分钟，防阻塞 Flask 启动）
# V3 修复: 添加 daemon=True，确保进程退出时 Timer 自动终止
if _startup_autoscans_enabled() and os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") != "1":
    if not _rt_refresh_scheduled:
        _rt_refresh_scheduled = True
        t = threading.Timer(300, _schedule_rt_price_refresh)
        t.daemon = True   # V3 新增：防止退出时阻塞
        t.start()
        print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

---

## 影响范围

| 位置 | 修正 |
|------|------|
| console_server.py（startup block）| 初始 300s Timer 添加 `daemon=True` |
