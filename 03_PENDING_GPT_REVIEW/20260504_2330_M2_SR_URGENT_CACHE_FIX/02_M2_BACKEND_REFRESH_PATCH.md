# 工部 · 后端补丁：实时价格定期刷新 + force_live 优化

**草案文件** | **禁止直接写入实盘**

---

## 1. 问题定位

### P0: realtime_prices 仅在启动时刷新一次

**位置**: `console_server.py:124-145`
**根因**: `_prewarm_rt_prices()` 只在 `_async_start_all()` 时调用一次，之后永不触发

**影响**: `/tmp/tianlu_cache/realtime_prices/` 下文件7+小时未更新

**修复**: 新增定时器，每30分钟刷新一次实时价格

### P1: force_live 串行超时

**位置**: `m2_sr_enhanced.py:compute_and_cache_triple()` 串行调用3个交易所
**根因**: 5对 × 3所 × 重试 = 超过20秒
**修复**: 增加并行超时，对每个 pair 用 ThreadPoolExecutor 并行执行

---

## 2. 补丁一：console_server.py — 实时价格定期刷新

### 插入位置: console_server.py 第133行之后

```python
# ── Stage B 新增: 实时价格定期刷新定时器 ────────────────────────
# 每30分钟刷新一次 /tmp/tianlu_cache/realtime_prices/ 缓存
# 解决: _prewarm_rt_prices() 只在启动时运行一次的问题
import threading as _rt_thread

_RT_PRICE_REFRESH_INTERVAL = int(os.environ.get("TIANLU_RT_PRICE_REFRESH_MIN", "30")) * 60
_rt_price_refresh_timer = None

def _schedule_rt_price_refresh():
    """定时刷新实时价格缓存（30分钟间隔）"""
    global _rt_price_refresh_timer
    try:
        sys.path.insert(0, "/Users/luxiangnan/freqtrade_console/bt_tools/backtest_core")
        from m2_sr_enhanced import _prewarm_realtime_prices
        _prewarm_realtime_prices()
        import logging as _rt_log
        _rt_log.getLogger("console_server").info(
            "[RT-Price-Refresh] 实时价格缓存刷新完成 "
            f"(间隔: {_RT_PRICE_REFRESH_INTERVAL//60}分钟)"
        )
    except Exception as e:
        import logging as _rt_log
        _rt_log.getLogger("console_server").warning(
            f"[RT-Price-Refresh] 刷新失败: {e}"
        )
    # 调度下一次
    _rt_price_refresh_timer = _rt_thread.Timer(
        _RT_PRICE_REFRESH_INTERVAL,
        _schedule_rt_price_refresh
    )
    _rt_price_refresh_timer.daemon = True
    _rt_price_refresh_timer.start()

def _cancel_rt_price_refresh():
    global _rt_price_refresh_timer
    if _rt_price_refresh_timer:
        _rt_price_refresh_timer.cancel()
        _rt_price_refresh_timer = None

# 在 _async_start_all() 之后添加:
if os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") == "1" or not _startup_autoscans_enabled():
    pass  # 已在上面的启动块中处理
else:
    _async_start_all()
    # 新增: 启动后等待5分钟，然后开始定期刷新
    _rt_thread.Timer(300, _schedule_rt_price_refresh).start()
    print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

**修改现有 `_async_start_all()` 附近**（在第145行之后添加）:

```python
# 现有代码保持不变，在后面追加:
if not (os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") == "1" or not _startup_autoscans_enabled()):
    import threading as _rt_th
    _rt_th.Timer(300, _schedule_rt_price_refresh).start()
    print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

---

## 3. 补丁二：m2_sr_enhanced.py — force_live 并行优化

### 修改位置: `m2_sr_enhanced.py` `compute_and_cache_triple()` 或新增独立函数

```python
def prewarm_realtime_prices_parallel(pairs: list = None) -> dict:
    """
    并行预热实时价格（解决 force_live 串行超时问题）。
    使用 ThreadPoolExecutor 并行获取多个交易对的价格。
    """
    import concurrent.futures, time as _t

    pairs = pairs or M2_WHITELIST_PAIRS
    results = {}

    def _fetch_pair(pair: str) -> tuple:
        try:
            prices = _fetch_realtime_prices(pair)
            return pair, prices, None
        except Exception as e:
            return pair, {}, str(e)

    start = _t.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(_fetch_pair, p): p for p in pairs}
        for fut in concurrent.futures.as_completed(futures, timeout=15):
            pair, prices, err = fut.result()
            results[pair] = prices
            if err:
                log.warning(f"[RT-Parallel] {pair} fetch error: {err}")

    elapsed = _t.time() - start
    log.info(f"[RT-Parallel] {len(results)}/{len(pairs)} 价格已刷新 ({elapsed:.1f}s)")
    return results
```

### 修改 `/api/bt2/sr_levels` 的 force_live 路径

**位置**: `console_server.py:25764`（`compute_and_cache_triple(pair)` 调用）

```python
# 修改前:
for pair in pairs:
    d = compute_and_cache_triple(pair) if force_live else get_latest_triple(pair)

# 修改后（新增并行选项）:
if force_live:
    # 使用并行预热（15秒超时）
    sys.path.insert(0, str(_Path(__file__).parent / "bt_tools" / "backtest_core"))
    from m2_sr_enhanced import prewarm_realtime_prices_parallel
    prewarm_realtime_prices_parallel(pairs)
    # 再逐个获取最新结果
    for pair in pairs:
        d = get_latest_triple(pair)
        ...
```

---

## 4. PATCH.diff 片段

```diff
diff --git a/console_server.py b/console_server.py
--- a/console_server.py
+++ b/console_server.py
@@ -133,6 +133,38 @@ def _prewarm_rt_prices():
         print(f"[RT Price] Pre-warm skipped: {e}")
 
 # ── Stage B 新增: 实时价格定期刷新定时器 ────────────────────────
+_RT_PRICE_REFRESH_INTERVAL = 1800  # 30分钟
+_rt_price_refresh_timer = None
+
+def _schedule_rt_price_refresh():
+    global _rt_price_refresh_timer
+    try:
+        sys.path.insert(0, "/Users/luxiangnan/freqtrade_console/bt_tools/backtest_core")
+        from m2_sr_enhanced import _prewarm_realtime_prices
+        _prewarm_realtime_prices()
+        import logging as _rt_log
+        _rt_log.getLogger("console_server").info(
+            f"[RT-Price-Refresh] 实时价格缓存刷新完成 (间隔: {_RT_PRICE_REFRESH_INTERVAL//60}分钟)")
+    except Exception as e:
+        import logging as _rt_log
+        _rt_log.getLogger("console_server").warning(f"[RT-Price-Refresh] 刷新失败: {e}")
+    _rt_price_refresh_timer = _rt_th.Timer(_RT_PRICE_REFRESH_INTERVAL, _schedule_rt_price_refresh)
+    _rt_price_refresh_timer.daemon = True
+    _rt_price_refresh_timer.start()
+
+# 在 _async_start_all() 后添加:
+if not (os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") == "1" or not _startup_autoscans_enabled()):
+    import threading as _rt_th
+    _rt_th.Timer(300, _schedule_rt_price_refresh).start()
+    print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")

@@ -25764,6 +25796,16 @@ def api_bt2_sr_levels_default():
             pairs = list(M2_WHITELIST_PAIRS)
         result_pairs = {}
+
+        # ── Stage B 新增: force_live 并行优化 ──────────────────
+        if force_live:
+            sys.path.insert(0, str(_Path(__file__).parent / "bt_tools" / "backtest_core"))
+            try:
+                from m2_sr_enhanced import prewarm_realtime_prices_parallel
+                prewarm_realtime_prices_parallel(pairs)  # 后台并行刷新价格
+            except Exception as e:
+                import logging
+                logging.getLogger("console_server").warning(f"[force_live] 并行刷新失败: {e}")
+
         for pair in pairs:
             d = compute_and_cache_triple(pair) if force_live else get_latest_triple(pair)
```

---

## 5. 测试验证

```bash
# 测试1: py_compile
python3 -m py_compile ~/freqtrade_console/console_server.py && echo "✅ py_compile OK"

# 测试2: 手动触发实时价格刷新
python3 -c "
import sys
sys.path.insert(0, '/Users/luxiangnan/freqtrade_console/bt_tools/backtest_core')
from m2_sr_enhanced import _prewarm_realtime_prices
_prewarm_realtime_prices()
print('✅ 实时价格预热完成')
"

# 测试3: 检查文件年龄（刷新后应为秒级）
sleep 2
python3 -c "
import os, time
for f in ['BTC', 'ETH', 'SOL']:
    path = f'/tmp/tianlu_cache/realtime_prices/{f}_USDT_rt_price.json'
    if os.path.exists(path):
        age_m = (time.time() - os.path.getmtime(path)) / 60
        print(f'{f}: {age_m:.1f}min')
"
```
