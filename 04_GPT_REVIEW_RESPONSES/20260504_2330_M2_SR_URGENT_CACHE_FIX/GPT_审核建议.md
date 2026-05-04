# GPT_审核建议 · 20260504_2330_M2_SR_URGENT_CACHE_FIX

## 审核结论

**有条件通过。**

Claude 本轮定位正确：M2/S/R 页面长期像旧数据，并不是 Triple S/R 三所数据完全坏掉，而是 `realtime_prices` 缓存约 7 小时未刷新、前端不展示数据年龄、实时价格覆盖后没有重算 S/R 距离。

本轮已执行的缓存归档、旧缓存清理、即时刷新可以认可；但 `console_server.py` 与 `m2_sr.html` 补丁仍是草案，不允许未修正就直接应用到生产控制台。

---

## 已确认通过

1. 未修改实盘交易策略。
2. 未重启 9090-9097 / 8081-8084。
3. 未调用交易所下单 API。
4. 未执行 force_entry / force_exit。
5. 旧 realtime price 缓存先归档到 TianLu_Archive，再逐文件清理。
6. 刷新后 BTC/ETH/SOL/BNB/DOGE realtime prices 均小于 1 分钟。
7. `console_server.py` 与 `m2_sr_enhanced.py` 当前基线 py_compile 通过。

---

## 补丁应用前必须整改

### P0-1：修复 `_rt_th` 作用域风险

PATCH.diff 中 `_schedule_rt_price_refresh()` 使用 `_rt_th.Timer()`，但 `_rt_th` 只在启动块中条件导入。如果启动块未执行，函数会出现未定义风险。

要求：在文件顶部或函数内部稳定导入：

```python
import threading as _rt_th
```

不要依赖条件块里的 import。

### P0-2：防止定时器重复启动

如果 console_server 热重载、重复 import 或初始化流程重复执行，可能启动多个 Timer。

要求：启动前判断 `_rt_price_refresh_timer is None`，并记录“只启动一次”。

### P0-3：确认刷新函数真实存在

PATCH.diff 调用了：

```python
from m2_sr_enhanced import prewarm_realtime_prices_parallel
```

但当前测试只证明 `m2_sr_enhanced.py` 编译通过，没有证明该函数存在。

要求执行并写入报告：

```bash
grep -n "def prewarm_realtime_prices_parallel" ~/freqtrade_console/bt_tools/backtest_core/m2_sr_enhanced.py
```

如果不存在，改用已有 `_prewarm_realtime_prices()`，或在补丁中新增并验证。

### P0-4：确认 `sys` / `_Path` 依赖

force_live 分支使用 `sys.path.insert()` 和 `_Path`，必须确认作用域内已导入。

建议显式使用：

```python
import sys
from pathlib import Path as _Path
```

### P0-5：前端插入位置需做 JS 语法验证

`_recomputeSRDistances()` 插入位置必须确认不破坏 `_loadBlock2_AI()` 的作用域和括号结构。

要求应用前执行：

```bash
node --check <抽取后的 m2_sr.js>
```

若无法抽取，至少在浏览器控制台验证无 JS 语法错误。

### P0-6：确认 `_m2Data` 作用域

补丁中 `_updateCacheIndicator()` 使用 `window._m2Data`，但原页面可能只使用局部 `_m2Data`。

要求确认 `_m2Data` 定义方式。若是局部变量，应直接读 `_m2Data`，或在加载后同步：

```javascript
window._m2Data = _m2Data
```

### P0-7：timestamp 兼容秒级 Unix 时间

当前补丁主要处理字符串和毫秒级数字。如果后端返回秒级 timestamp，例如 `1746345600`，age 不会计算。

必须补：

```javascript
else if (typeof ts === 'number' && ts > 1e9) ageMs = Date.now() - ts * 1000;
```

---

## 下一步批准范围

允许 Claude 进入：

```text
M2 S/R Urgent Fix V2：补丁草案修订 + 语法验证 + 重启计划
```

输出目录：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_URGENT_FIX_V2/
```

必须包含：

```text
00_M2_SR_FIX_V2_SUMMARY.md
01_BACKEND_TIMER_PATCH_V2.md
02_FRONTEND_CACHE_INDICATOR_PATCH_V2.md
03_TIMESTAMP_COMPATIBILITY_TEST.md
04_JS_SYNTAX_TEST.md
05_FORCE_LIVE_FUNCTION_EXISTENCE_PROOF.md
06_APPLY_AND_RESTART_CONSOLE_SERVER_PLAN.md
07_ROLLBACK_PLAN.md
PATCH.diff
TEST_LOG.md
REVIEW_PACKAGE.zip
```

---

## 允许真正应用补丁的条件

只有以下全部满足，才允许应用补丁并重启 console_server：

1. `py_compile console_server.py` 通过；
2. `m2_sr_enhanced.py` 中实时价格刷新函数存在，或补丁中新增并验证；
3. 前端 JS 语法检查通过；
4. timestamp 秒/毫秒/字符串三种格式均能计算 age；
5. `_m2Data` 作用域确认；
6. 回滚文件存在；
7. 用户明确允许重启 console_server；
8. 明确不重启 9090-9097 / 8081-8084。

---

## 最终评价

已执行的归档、清理、即时刷新：**通过。**

补丁草案：**有条件通过，需要 V2 修订。**

当前可以认为：M2 页面旧价格问题的直接症状已临时缓解；长期修复还需要应用 console_server 定时刷新与前端 cache indicator / S/R 距离重算补丁。补丁应用前必须先修正以上 P0 风险点。
