# 01_CONSOLE_SERVER_RESTART_LOG.md
# console_server 重启日志

**重启时间**: 2026-05-05 00:33:20
**旧 PID**: 68800
**新 PID**: 86441
**日志文件**: `/private/tmp/console_server.log`

---

## 重启命令

```bash
kill 68800
launchctl kickstart -k gui/$(id -u)/com.tianlu.console-server
# LaunchAgent 自动重启
```

---

## 启动日志（/private/tmp/console_server.log）

```
00:33:20 [启动] 自动采集系统已就绪
00:33:27 L2指标缓存预热完成，仪表盘将秒级响应
00:34:27 [Startup] Background pre-warm started: scanner + realtime prices
00:34:27 [Startup] 实时价格定期刷新定时器已启动（每30分钟）
```

**注**：新进程日志路径为 `/private/tmp/console_server.log`（LaunchAgent 工作目录），
非 `~/.console_server.log`（旧路径）。

---

## API 健康检查

```json
{"ok": true, "port": 9099, "service": "tianlu-console",
 "entry_loop_counter": 0, "tianyan_running": true,
 "exit_ai_running": true, "ts": 1777912466}
```

---

## 前端文件验证

```bash
$ grep "m2-cache-indicator" static/tabs/m2_sr.html
✅ 存在

$ grep "_updateCacheIndicator" static/tabs/m2_sr.html
✅ 存在

$ grep "_prewarm_realtime_prices_parallel" console_server.py
✅ 存在
```
