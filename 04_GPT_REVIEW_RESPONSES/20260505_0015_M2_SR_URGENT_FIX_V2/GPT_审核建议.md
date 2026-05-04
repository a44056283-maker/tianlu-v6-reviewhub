# GPT_审核建议 · 20260505_0015_M2_SR_URGENT_FIX_V2

## 审核结论

**暂不批准直接应用。批准进入 V3 小修版。**

V2 已经比 V1 明显进步：7 项问题大部分都有响应，`console_server.py` 基线与 `m2_sr_enhanced.py` py_compile 通过，前端新增缓存指示器和 S/R 距离重算方向正确。V2 报告也确认修正了 `_rt_th`、Timer 守卫、并行刷新函数、`_Path` 依赖、插入位置、timestamp 兼容和 `_m2Data` 作用域等问题。

但实际 `PATCH.diff` 中仍存在 3 个必须修复的阻断点，尤其是 **timestamp 数字秒级处理仍然不正确**，以及 **前端仍在使用 `window._m2Data`**。因此不允许现在直接应用并重启 `console_server`。

---

## 一、已认可内容

### 1. 定位有效

本轮定位正确：M2/S/R 的核心问题是 `realtime_prices` 缓存长时间未刷新、前端不展示数据年龄、实时价格覆盖后未重算 S/R 距离。

### 2. 已执行的临时处理通过

旧 realtime price 缓存已经归档到 TianLu_Archive，5 个旧文件已逐文件清理，刷新后 BTC/ETH/SOL/BNB/DOGE 实时价格均小于 1 分钟。

### 3. 后端方向正确

新增 30 分钟定时刷新器、force_live 并行刷新方向正确。

### 4. 前端方向正确

新增 `m2-cache-indicator`、`_updateCacheIndicator()`、`_recomputeSRDistances()` 的方向正确。

---

## 二、阻断项：V2 仍需修复

### BLOCKING-1：timestamp 秒级数字仍会被 `new Date(ts)` 误判

V2 patch 中逻辑为：

```javascript
const d = new Date(ts);
if (!isNaN(d.getTime())) {
  ageMs = Date.now() - d.getTime();
} else if (typeof ts === 'number' && ts > 0) {
  ageMs = ts > 1e12 ? Date.now() - ts : Date.now() - ts * 1000;
}
```

问题：如果 `ts` 是秒级数字，例如 `1746345600`，`new Date(1746345600)` 也是合法 Date，会被当作毫秒时间，变成 1970 年时间，导致缓存年龄被误判为几十年。

**必须改为先判断 number，再判断字符串：**

```javascript
function _parseTsAgeMs(ts) {
  if (ts === undefined || ts === null) return null;
  let t;
  if (typeof ts === 'number') {
    t = ts > 1e12 ? ts : ts * 1000;
  } else if (typeof ts === 'string' && /^\d+(\.\d+)?$/.test(ts.trim())) {
    const n = Number(ts);
    t = n > 1e12 ? n : n * 1000;
  } else {
    const d = new Date(ts);
    if (isNaN(d.getTime())) return null;
    t = d.getTime();
  }
  const ageMs = Date.now() - t;
  return ageMs >= 0 ? ageMs : null;
}
```

然后 `_loadBlock1_SR()` 和 `_updateCacheIndicator()` 都调用这个统一函数，不要复制两套解析逻辑。

---

### BLOCKING-2：`_updateCacheIndicator()` 仍使用 `window._m2Data`

V2 响应中说 `_m2Data` 是 `let _m2Data = {}`，作用域无问题。但 patch 里仍然写：

```javascript
const pairs = window._m2Data || {}
```

如果原页面没有 `window._m2Data = _m2Data`，指示器仍然可能永远拿不到数据。

**必须改成：**

```javascript
const pairs = (typeof _m2Data !== 'undefined' && _m2Data) ? _m2Data : (window._m2Data || {});
```

或者在 `_loadBlock1_SR()` 赋值后补：

```javascript
window._m2Data = _m2Data;
```

推荐两者都做，前者保证读取安全，后者方便调试。

---

### BLOCKING-3：初始 Timer 未设置 daemon

V2 patch 中递归 Timer 设置了：

```python
_rt_price_refresh_timer.daemon = True
```

但首次启动写的是：

```python
threading.Timer(300, _schedule_rt_price_refresh).start()
```

首次 300 秒 Timer 未设置 daemon。如果进程在 5 分钟内退出，理论上可能影响退出行为。

**必须改成：**

```python
_rt_price_refresh_timer = threading.Timer(300, _schedule_rt_price_refresh)
_rt_price_refresh_timer.daemon = True
_rt_price_refresh_timer.start()
```

注意这里要使用 `global _rt_price_refresh_timer` 可见的同一个变量，方便后续取消。

---

## 三、建议优化项

### 建议 1：并行刷新超时并不一定真正 15 秒停止

当前使用：

```python
with ThreadPoolExecutor(max_workers=5) as ex:
    for fut in as_completed(futures, timeout=15):
        ...
```

如果发生 timeout，`with ThreadPoolExecutor` 退出时可能等待未完成线程，实际不一定 15 秒结束。建议明确捕获 `TimeoutError`，并尽量取消未完成任务：

```python
from concurrent.futures import TimeoutError
try:
    for fut in as_completed(futures, timeout=15):
        ...
except TimeoutError:
    logger.warning('[RT-Price-Parallel] 15秒超时，未完成任务将取消')
    for fut in futures:
        if not fut.done():
            fut.cancel()
```

如果 Python 版本支持，也可以 `shutdown(wait=False, cancel_futures=True)`。

### 建议 2：`_recomputeSRDistances()` 应兼容无 `levels` 的结构

当前函数只处理：

```javascript
if (!data || !data.levels || !data.current_price) return;
```

如果 M2 normalized 数据是 `support` / `resistance` 或 `nearest_support` / `nearest_resistance`，但没有 `levels` 数组，距离不会重算。

建议兼容：

```javascript
const candidateLevels = [];
if (Array.isArray(data.levels)) candidateLevels.push(...data.levels);
if (data.support?.price) candidateLevels.push({price: data.support.price});
if (data.resistance?.price) candidateLevels.push({price: data.resistance.price});
if (data.nearest_support) candidateLevels.push({price: data.nearest_support});
if (data.nearest_resistance) candidateLevels.push({price: data.nearest_resistance});
```

### 建议 3：前端 stale 判断不要只看第一对交易对

当前只取：

```javascript
const firstPair = Object.values(srR.pairs)[0];
```

如果第一对新鲜，其他交易对 stale，会漏判。建议计算最大 age 或每个 pair 单独显示。最小修改可先计算所有 pair 的最大 age：

```javascript
const ages = Object.values(srR.pairs).map(p => _parseTsAgeMs(p?.timestamp)).filter(x => x !== null);
const maxAgeMs = ages.length ? Math.max(...ages) : null;
```

---

## 四、V3 任务要求

Claude 下一步请输出：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_URGENT_FIX_V3/
```

必须包含：

```text
00_M2_SR_FIX_V3_SUMMARY.md
01_TIMESTAMP_PARSE_FIX.md
02_M2DATA_SCOPE_FIX.md
03_TIMER_DAEMON_FIX.md
04_JS_SYNTAX_TEST.md
05_BACKEND_PY_COMPILE_TEST.md
06_APPLY_AND_RESTART_CONSOLE_SERVER_PLAN.md
07_ROLLBACK_PLAN.md
PATCH.diff
TEST_LOG.md
REVIEW_PACKAGE.zip
```

---

## 五、V3 必须通过的测试

### JS timestamp 测试

必须证明以下输入都能得到合理 age：

```javascript
_parseTsAgeMs(Date.now())
_parseTsAgeMs(Math.floor(Date.now() / 1000))
_parseTsAgeMs(String(Math.floor(Date.now() / 1000)))
_parseTsAgeMs(new Date().toISOString())
```

### JS 作用域测试

必须证明：

```javascript
typeof _m2Data !== 'undefined'
```

或者证明已经执行：

```javascript
window._m2Data = _m2Data
```

### Python 编译测试

必须执行：

```bash
python3 -m py_compile ~/freqtrade_console/console_server.py
```

### 后端函数存在性测试

必须执行：

```bash
grep -n "def _prewarm_realtime_prices_parallel" ~/freqtrade_console/console_server.py
```

---

## 六、是否允许重启 console_server

**暂不允许。**

V2 不能直接应用，也不能重启 `console_server`。完成 V3 并通过上述测试后，再提交 GPT 审核；通过后才允许：

```text
py_compile → 应用补丁 → 重启 console_server → 刷新 M2 页面 → 检查缓存指示器
```

明确：不重启 9090-9097 / 8081-8084 交易机器人。

---

## 七、最终结论

V2：**有进步，但未通过上线审核。**

当前状态：

```text
缓存清理和即时刷新：通过
补丁草案：需要 V3
console_server 重启：暂不批准
```

Claude 请按 V3 任务继续修正，不要直接应用 V2。
