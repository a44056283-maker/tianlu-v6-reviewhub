# 07_M2_SR_DATA_FLOW_FIX_REPORT.md
## M2 S/R 数据流修复验证报告
**执行时间**: 2026-05-04 16:38 CST
**验证者**: 都察院 Stage A Agent

---

## 修复项总览

| 修复项 | 状态 | 代码位置 | 说明 |
|--------|------|---------|------|
| P1: `_price_round` BUG | ❌ 未找到描述的BUG | console_server.py:6416 | 代码正常，非BUG |
| P4: 三所交叉优先级 | ✅ 已修复 | console_server.py:25707-25737 | Triple优先于M1/M4 |
| P5: interval 单位 | ✅ 已修复 | console_server.py:6353 | 900秒（15分钟） |
| L1.5 温缓存 | ✅ 已实现 | m2_sr_enhanced.py:56-96 | 7天TTL |
| 健康检查脚本 | ⚠️ 无法验证 | Bash禁用 | 需手动检查 |
| Mac B 缓存 | ⚠️ 需远程验证 | Mac B | 需在Mac B检查 |

---

## P1: `_price_round` BUG 修复验证

**期望位置**: console_server.py:6414
**预期修复**: `_price_round` 函数BUG修复

### 实际代码（行6414-6418）

```python
6414:                    
6415: current_price = closes[-1]
6416: _pr = lambda v: round(v, 2)        # ← 本行
6417: recent_lows = sorted(set([_pr(l) for l in lows[-20:]]))[:3]
6418: recent_highs = sorted(set([_pr(h) for h in highs[-20:]]))[:3]
```

### 分析

- 行6416是 `_pr = lambda v: round(v, 2)`，这是一个局部 lambda 函数，用于将价格四舍五入到小数点后2位
- **这不是一个BUG**，而是一个正确的局部函数定义
- 该函数用于将K线的最低价和最高价四舍五入后取唯一值，找到最近的3个支撑位/压力位

**结论**: 描述中的 `_price_round BUG` 在此位置**不存在**。代码是正常的。
可能的情况：
1. BUG已在更早版本修复
2. BUG在其他位置
3. BUG描述不准确

---

## P4: 三所交叉优先级修复验证 ✅

**代码位置**: console_server.py:25707-25737

### 代码片段（行25704-25737）

```python
25704: if cached is not None and not force_live:
25705:     return jsonify(cached)
25706: if not force_live:
25707:     # 优先：Triple三所交叉数据（L1 SSD缓存，TTL=2h）
25708:     sys.path.insert(0, str(_Path(__file__).parent / "bt_tools" / "backtest_core"))
25709:     from m2_sr_enhanced import get_latest_triple
25710:     requested_pairs = [p.strip() for p in pairs_arg.split(",") if p.strip()] if pairs_arg else ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "DOGE/USDT"]
25711:     result_pairs = {}
25712:     for pair in requested_pairs:
25713:         d = get_latest_triple(pair)          # ← Triple数据优先
25714:         if d and _m2_has_valid_sr(d):
25715:             result_pairs[pair] = d
25716:     # 次优先：M1/M4 hero card数据（仅在Triple全失败时降级）
25717:     if not result_pairs:
25718:         flow = _get_m1_m4_data_flow_cached(requested_pairs)
25719:         ...
25720:     # 最终兜底：读sr_results轻量文件
25721:     if not result_pairs:
25722:         for pair in requested_pairs:
25723:             clean_pair = _pair_symbol_from_id(_pair_id_from_symbol(pair))
25724:             m2 = _m2_sr_results_file_fallback(clean_pair) else {}
25725:             ...
```

### 优先级确认

| 优先级 | 数据源 | 代码行 | 状态 |
|--------|--------|--------|------|
| 1 (最高) | Triple三所交叉 (get_latest_triple) | 25707-25715 | ✅ 已实现 |
| 2 | M1/M4 hero card | 25717-25725 | ✅ 降级处理 |
| 3 | sr_results 轻量文件 | 25727-25732 | ✅ 最终兜底 |

### API 响应 source 字段确认

```python
"source": "m2_triple_primary",   # 行25745 - Triple来源标记
```

**结论**: ✅ P4三所交叉优先级已正确实现，Triple数据优先。

---

## P5: interval 单位修复验证 ✅

**代码位置**: console_server.py:6353

### 代码片段

```python
6350: # S/R 扫描配置存储
6351: SR_CONFIG = {
6352:     'pairs': ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'DOGE/USDT'],
6353:     'interval': 900,  # 秒（15分钟）  ← 本行
6354:     'exchange': 'okx',
6355:     'download_history': False,
6356:     'auto_scan': True,
6357:     'last_scan': None,
6358:     'results': []
6359: }
```

### 分析

- `interval: 900` 已正确标注为"秒（15分钟）"
- 900秒 = 15分钟，符合注释说明
- 在 sr_auto_scan_thread 中（行6468）正确使用：

```python
interval = max(SR_CONFIG.get('interval', 5), 5)
```

**结论**: ✅ P5 interval单位已正确实现（秒）。

---

## L1.5 温缓存实现验证 ✅

**代码位置**: `m2_sr_enhanced.py:56-96`

### 代码确认

```python
# L1.5: 本地SSD (/tmp/tianlu_cache/sr_levels_warm/)   — TTL 7天（温缓存，S/R相对稳定）
_L1_WARM_CACHE_DIR = Path(os.environ.get(
    "TIANLU_M2_WARM_CACHE_DIR", "/tmp/tianlu_cache/sr_levels_warm"))
_L1_WARM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_L1_WARM_TTL = int(os.environ.get("TIANLU_M2_WARM_TTL_SEC", str(7*24*3600)))  # 7天

def _promote_to_warm_cache(pair: str, l1_data: dict):
    """将L1热缓存晋升为L1.5温缓存（7天TTL）"""
    try:
        warm_fname = _warm_cache_fname(pair)
        warm_path = _L1_WARM_CACHE_DIR / warm_fname
        with open(warm_path, "w") as f:
            json.dump(l1_data, f, indent=2, default=str)
        _enforce_warm_cache_limit()
    except Exception:
        pass
```

### 温缓存参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 目录 | `/tmp/tianlu_cache/sr_levels_warm/` | 本地SSD |
| TTL | 7天 | 604800秒 |
| 最大容量 | 500MB | `_L1_WARM_MAX_SIZE_MB` |
| 容量控制 | `_enforce_warm_cache_limit()` | 超容量删除最旧文件 |

**结论**: ✅ L1.5 温缓存已完整实现。

---

## 健康检查脚本验证 ⚠️

由于 Bash 被禁用，无法验证健康检查脚本是否存在或执行。

**建议手动检查**:
```bash
ls -la ~/freqtrade_console/bt_tools/health_check*.py 2>/dev/null && echo "存在" || echo "不存在"
```

---

## Mac B 缓存验证 ⚠️

需要在 Mac B 上验证：
```bash
ls -la /tmp/tianlu_cache/sr_levels/      # L1热缓存
ls -la /tmp/tianlu_cache/sr_levels_warm/ # L1.5温缓存
```

---

## 三所交叉数据验证

**API端点**: `GET http://127.0.0.1:9099/api/bt2/sr_levels?pairs=BTC`

由于 Bash 被禁用，无法实际调用 API 验证。

**根据代码分析**（行25704-25748）:
- Triple数据源正确优先
- 返回 payload 包含 `source: "m2_triple_primary"`
- 包含 `triple_validated_count`, `exchanges_used` 字段

---

## 结论

| 修复项 | 状态 | 详情 |
|--------|------|------|
| P1: _price_round BUG | ⚠️ 未找到描述的BUG | 代码正常，非BUG |
| P4: 三所交叉优先级 | ✅ 已修复 | Triple > M1/M4 > sr_results |
| P5: interval 单位 | ✅ 已修复 | 900秒（15分钟） |
| L1.5 温缓存 | ✅ 已实现 | 7天TTL，500MB容量控制 |
| 健康检查脚本 | ⚠️ 无法验证 | Bash禁用 |
| Mac B 缓存 | ⚠️ 需远程验证 | 需在Mac B检查 |
