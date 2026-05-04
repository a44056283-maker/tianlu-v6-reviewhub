# GPT_审核建议 · 20260505_0030_M2_SR_URGENT_FIX_V3

## 审核结论

**有条件通过，批准应用补丁，但必须按“受控应用 + 正确重启 console_server + 验证后留观”的方式执行。**

V3 已修正 V2 的 3 个关键阻断点：

1. timestamp 秒级数字被 `new Date()` 当成毫秒的问题；
2. `window._m2Data` 可能不存在的问题；
3. 初始 300 秒 Timer 未设置 daemon 的问题。

V3 报告显示：`console_server.py` 临时副本 py_compile 通过，AST 解析成功，m2_sr.html JS 11 项检查通过，函数定义在 `<script>` 标签内。可以进入受控应用阶段。

---

## 一、批准范围

允许应用以下补丁：

1. `console_server.py`：实时价格 30 分钟定时刷新器；
2. `console_server.py`：`_prewarm_realtime_prices_parallel()`；
3. `console_server.py`：`/api/bt2/sr_levels?force_live=1` 并行刷新优化；
4. `m2_sr.html`：缓存年龄指示器；
5. `m2_sr.html`：timestamp 秒/毫秒/ISO 兼容；
6. `m2_sr.html`：实时价格覆盖后重算 S/R 距离。

---

## 二、应用前必须做的最后检查

### 1. 备份

执行前必须再次备份：

```bash
cd ~/freqtrade_console
TS=$(date +%Y%m%d_%H%M%S)
cp console_server.py ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/console_server.py.bak.$TS
cp static/tabs/m2_sr.html ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/m2_sr.html.bak.$TS
```

### 2. 确认 console_server 启动方式

当前系统历史上存在 LaunchAgent 启动 `console_server.py` 的情况。不要直接使用 `pkill + nohup` 造成重复进程。

执行前先检查：

```bash
launchctl list | grep -i tianlu | grep -i console || true
ps aux | grep console_server.py | grep -v grep
lsof -iTCP:9099 -sTCP:LISTEN -n -P
```

如果 `com.tianlu.console-server` 存在，应优先使用 LaunchAgent 管理；如果没有，再使用手动启动。

### 3. py_compile

应用补丁后必须执行：

```bash
cd ~/freqtrade_console
python3 -m py_compile console_server.py
```

### 4. 前端语法/浏览器验证

应用后至少做一次：

```text
刷新 M2 页面；
打开浏览器控制台；
确认无 JS SyntaxError；
确认 m2-cache-indicator 出现。
```

---

## 三、重启 console_server 的批准方式

批准重启：**仅限 console_server。**

不允许重启：

```text
9090-9097
8081-8084
OpenClaw gateway
freqtrade bots
```

推荐重启顺序：

### 如果 LaunchAgent 存在

```bash
launchctl kickstart -k gui/$UID/com.tianlu.console-server
sleep 5
curl -s --max-time 8 http://127.0.0.1:9099/api/health
```

如果 label 名称不同，按实际 `launchctl list` 结果使用。

### 如果无 LaunchAgent

```bash
pkill -f "console_server.py" || true
sleep 2
cd ~/freqtrade_console
nohup python3 console_server.py >> ~/.console_server.log 2>&1 &
sleep 5
curl -s --max-time 8 http://127.0.0.1:9099/api/health
```

---

## 四、应用后必须验证

### 后端验证

```bash
curl -s --max-time 8 "http://127.0.0.1:9099/api/bt2/sr_levels" | head
curl -s --max-time 20 "http://127.0.0.1:9099/api/bt2/sr_levels?force_live=1" | head
```

检查日志：

```bash
grep -E "RT-Price-Refresh|实时价格定期刷新|force_live|RT-Price-Parallel" ~/.console_server.log | tail -20
```

### 前端验证

1. 打开 M2 页面；
2. 确认顶部出现 `m2-cache-indicator`；
3. 点击“强制刷新”；
4. 确认页面不再长期显示旧价格；
5. 确认当前价格变化后支撑/压力距离同步变化。

### 机器人验证

只读验证，不重启：

```bash
ps aux | grep freqtrade | grep -v grep | wc -l
```

确保机器人进程数量没有异常变化。

---

## 五、留观要求

应用后至少留观 30 分钟。

重点观察：

1. console_server 是否稳定；
2. 9099 是否持续可访问；
3. M2 页面 cache indicator 是否显示；
4. force_live 是否仍超时；
5. 日志是否出现反复异常；
6. 交易机器人是否未受影响。

---

## 六、仍需后续优化但不阻塞本次应用

以下问题不阻塞 V3 应用，但后续 Codex 需要继续优化：

1. `_prewarm_realtime_prices_parallel()` 中 TimeoutError 处理可以更细；
2. `_recomputeSRDistances()` 后续应兼容无 `levels`、仅有 `support/resistance` 的结构；
3. cacheStale 目前主要看第一对交易对，后续应改为所有交易对 max age；
4. M2 S/R 三所交叉校验和 7 天热缓存归档仍需进入下一阶段系统化修复。

---

## 七、回滚要求

如果出现以下任一情况，立即回滚：

1. `console_server.py` py_compile 失败；
2. 9099 无法启动；
3. M2 页面 JS 报错；
4. `/api/bt2/sr_levels` 无法返回；
5. 机器人进程异常变化；
6. 用户要求回滚。

回滚必须优先恢复备份文件，不要仅依赖 `git checkout`，因为本地目录未必是干净 Git 工作树。

---

## 八、最终批准

**批准执行 V3 应用。**

执行顺序：

```text
备份 → 应用补丁 → py_compile → 重启 console_server → API验证 → 前端验证 → 30分钟留观 → 写执行报告 → push GitHub
```

执行报告输出到：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_FIX_V3_APPLIED_RESULT/
```

必须包含：

```text
00_APPLY_RESULT_SUMMARY.md
01_CONSOLE_SERVER_RESTART_LOG.md
02_API_VERIFY_RESULT.md
03_FRONTEND_VERIFY_RESULT.md
04_ROBOT_UNAFFECTED_CHECK.md
05_ROLLBACK_STATUS.md
TEST_LOG.md
REVIEW_PACKAGE.zip
```
