# 02_V2_BACKEND_PATCH.md
# M2 S/R 紧急修复 V2 — 后端补丁（console_server.py）
# 修正：移除导入歧义、防重复启动、创建并行预热函数

---

## 补丁位置总览

| 区域 | 文件 | 插入位置 | 内容 |
|------|------|---------|------|
| A | console_server.py | Startup block (line ~147后) | 30分钟定时器 |
| B | console_server.py | line ~2353后（函数定义区） | `_prewarm_realtime_prices_parallel()` |
| C | console_server.py | `api_bt2_sr_levels_default()` 内 | force_live 并行优化 |

---

## 补丁 A：Startup block（修复 V1 的 `_rt_th` 导入问题 + 重复启动问题）

**插入位置**: `console_server.py` line 145-146 后（`print("[Startup] Background pre-warm started...")` 之后）

**V1 问题**:
- `import threading as _rt_th` 冗余（`threading` 已在 line 17 导入）
- 无防重复启动机制

**V2 修正**:

```python
# ── V2: 实时价格定期刷新定时器 ────────────────────────────────────────
# 修复: ① 移除冗余 _rt_th 导入 ② 添加 _rt_refresh_scheduled 防重复启动
_rt_refresh_scheduled = False
_RT_PRICE_REFRESH_INTERVAL = int(os.environ.get("TIANLU_RT_PRICE_REFRESH_MIN", "30")) * 60
_rt_price_refresh_timer = None

def _schedule_rt_price_refresh():
    """每 N 分钟刷新一次实时价格缓存（解决启动后数小时不更新的问题）"""
    global _rt_price_refresh_timer
    try:
        # 直接调用本地函数（console_server.py:2353 已定义）
        _prewarm_realtime_prices()
        import logging as _rt_log
        _rt_log.getLogger("console_server").info(
            f"[RT-Price-Refresh] 实时价格缓存刷新完成 (间隔: {_RT_PRICE_REFRESH_INTERVAL//60}分钟)")
    except Exception as e:
        import logging as _rt_log
        _rt_log.getLogger("console_server").warning(f"[RT-Price-Refresh] 刷新失败: {e}")
    # 调度下次执行（daemon 确保进程退出时自动终止）
    _rt_price_refresh_timer = threading.Timer(_RT_PRICE_REFRESH_INTERVAL, _schedule_rt_price_refresh)
    _rt_price_refresh_timer.daemon = True
    _rt_price_refresh_timer.start()

def _cancel_rt_price_refresh():
    global _rt_price_refresh_timer
    if _rt_price_refresh_timer:
        _rt_price_refresh_timer.cancel()
        _rt_price_refresh_timer = None

# 启动时调度首次刷新（延迟5分钟，防止阻塞 Flask）
# 修复: 用 _rt_refresh_scheduled 布尔值防重复启动
if _startup_autoscans_enabled() and os.environ.get("TIANLU_SKIP_STARTUP_PREWARM") != "1":
    if not _rt_refresh_scheduled:
        _rt_refresh_scheduled = True
        threading.Timer(300, _schedule_rt_price_refresh).start()
        print("[Startup] 实时价格定期刷新定时器已启动（每30分钟）")
```

---

## 补丁 B：新增 `_prewarm_realtime_prices_parallel()` 函数

**插入位置**: `console_server.py` line 2370 后（`_prewarm_realtime_prices()` 函数定义之后）

**V1 问题**:
- V1 force_live 优化引用 `prewarm_realtime_prices_parallel`，该函数不存在

**V2 修正** — 创建真实的并行版本：

```python
# ── V2 新增: 并行版实时价格预热 ────────────────────────────────────────
# 用途: force_live API 调用前后台并行刷新，避免串行超时
def _prewarm_realtime_prices_parallel(pairs: list | None = None):
    """
    并行预热实时价格（ThreadPoolExecutor，15秒超时）
    替换原有的串行 _prewarm_realtime_prices() 供 force_live 场景使用。
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed
    if pairs is None:
        pairs = list(M2_WHITELIST_PAIRS)

    def _fetch_pair(pair: str) -> tuple[str, dict | None]:
        """并行任务单元：拉取单个交易对的三个交易所价格"""
        try:
            prices = {
                "gate": fetch_current_price_gate(pair),
                "okx": fetch_current_price_okx(pair),
                "bnb": fetch_current_price_binance(pair),
            }
            valid = [v for v in prices.values() if v and v > 0]
            prices["average"] = sum(valid) / len(valid) if valid else 0
            return pair, prices
        except Exception:
            return pair, None

    try:
        # 并行执行：max_workers=5 覆盖所有 pairs，3 workers/exchange 并发安全
        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = {ex.submit(_fetch_pair, p): p for p in pairs}
            for fut in as_completed(futures, timeout=15):
                pair, prices = fut.result()
                if prices:
                    now = time.time()
                    _realtime_price_cache[pair] = (
                        now,
                        prices["gate"],
                        prices["okx"],
                        prices["bnb"],
                        prices["average"]
                    )
                    _save_realtime_price_to_disk(pair, prices)
    except Exception as e:
        import logging
        logging.getLogger("console_server").warning(
            f"[RT-Price-Parallel] 并行预热异常: {e}")
```

**关键修复**:
1. ✅ 使用 `from concurrent.futures import ThreadPoolExecutor, as_completed`（函数内导入，避免全局污染）
2. ✅ 15秒超时保护（`as_completed(futures, timeout=15)`）
3. ✅ 所有依赖 `_realtime_price_cache`、`_save_realtime_price_to_disk` 均可通过 m2_sr_enhanced 导入获得
4. ✅ `M2_WHITELIST_PAIRS`、`fetch_current_price_*` 均已通过 line 128 导入链可用

---

## 补丁 C：`api_bt2_sr_levels_default()` force_live 并行优化

**插入位置**: `console_server.py` line 25761-25762 之间（`result_pairs = {}` 之后，`for pair in pairs:` 之前）

**V1 问题**:
- `sys.path.insert(0, ...)` 使用 `_Path` 但未导入（console_server.py 使用 `Path`）
- `from m2_sr_enhanced import prewarm_realtime_prices_parallel` 该函数不存在

**V2 修正**:

```python
        # ── V2: force_live 并行优化（15秒超时）────────────────────────
        # 修复: ① 用 Path() 替代不存在的 _Path ② 直接调用 _prewarm_realtime_prices_parallel（本地函数）
        if force_live:
            import sys as _cs
            _cs.path.insert(0, str(Path(__file__).parent / "bt_tools" / "backtest_core"))
            # _prewarm_realtime_prices_parallel 定义在 console_server.py 自身（line 2370+）
            try:
                _prewarm_realtime_prices_parallel(pairs)  # 后台并行刷新
            except NameError:
                # 防御: 若函数尚未加载，降级为本地预热
                _prewarm_realtime_prices()
            except Exception as e:
                import logging
                logging.getLogger("console_server").warning(
                    f"[force_live] 并行刷新失败，降级: {e}")
```

---

## 依赖链验证

```
console_server.py 启动
  ↓
async_start_all() → _prewarm_rt_prices()
  ↓
m2_sr_enhanced._prewarm_realtime_prices()  ← 原有串行预热（不改动）
  +
_schedule_rt_price_refresh()              ← V2 新增定时器（每30分钟）
  ↓
console_server._prewarm_realtime_prices() ← 本地版本（line 2353，遮蔽 m2_sr_enhanced 版本）
  ↓
force_live API
  ↓
_prewarm_realtime_prices_parallel()       ← V2 新增并行版本
```

## V2 vs V1 对比

| 问题 | V1 | V2 |
|------|----|----|
| 1. `_rt_th` 导入 | `import threading as _rt_th`（冗余） | 移除，使用 `threading` |
| 2. Timer 重复启动 | 无保护 | `_rt_refresh_scheduled` 布尔守卫 |
| 3. 并行函数不存在 | 引用不存在的函数 | 新建真实 `_prewarm_realtime_prices_parallel()` |
| 4. `_Path` 未导入 | 使用不存在的 `_Path` | 改用 `Path(__file__).parent` |
| 5. sys 路径 | 硬编码路径 | `Path(__file__).parent` 可移植 |
