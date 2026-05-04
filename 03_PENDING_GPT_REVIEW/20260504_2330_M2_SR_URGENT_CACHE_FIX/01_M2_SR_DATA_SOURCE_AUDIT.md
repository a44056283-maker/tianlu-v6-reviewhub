# 户部 · M2 S/R 数据链路审计报告

**生成时间**: 2026-05-04 23:50
**代理**: 户部 · 数据链路代理

---

## 一、故障确认

**用户反馈**: M2/S/R 网页连续近三天数据不变，不管市场涨跌，支撑/压力位看起来像死缓存。

**结论**: 故障属实，但根本原因不是"数据不动"，而是**实时价格缓存7小时未刷新**，且**前端无年龄提示导致用户误判数据为"死数据"**。

---

## 二、审计结果

### 2.1 Triple S/R 缓存 — ✅ 正常

| 指标 | 状态 |
|------|------|
| 文件年龄 | 0.03h（2分钟前更新）|
| triple_validated | BTC: 16, ETH: 20, SOL: 22 |
| exchanges_used | gate + okx + bnb（三所全通）|
| levels 数量 | BTC: 39, ETH: 48 |
| data_source | m2_triple_exchange |

**结论**: Triple S/R 缓存本身完全正常，数据新鲜。

### 2.2 Realtime Prices 缓存 — 🔴 严重陈旧

| 指标 | 数值 |
|------|------|
| BTC_USDT_rt_price.json | **7小时11分钟**前更新 |
| ETH_USDT_rt_price.json | **7小时11分钟**前更新 |
| SOL_USDT_rt_price.json | **7小时11分钟**前更新 |

**根因**: `_prewarm_rt_prices()` 仅在 console_server 启动时（16:34）执行一次，之后永不刷新。console_server 已在 16:34 启动并预热，之后再无触发。

### 2.3 API Short Cache — 🟡 正常（但有设计问题）

| 指标 | 数值 |
|------|------|
| API Short Cache TTL | 90秒 |
| 实际响应 | `{"_cache":{"age_sec":6.36,"state":"memory","ttl_sec":90}}` |
| force_live=1 | 超时（>20秒，5对×多交易所串行调用）|

**问题**: `force_live=1` 调用 `compute_and_cache_triple()` 对每个 pair 串行执行 Gate+OKX+Binance，导致 5对 × 3所 × 重试 = 超时。

### 2.4 前端 — 🔴 无数据年龄提示

| 指标 | 状态 |
|------|------|
| 状态栏文字 | "就绪"（固定，无动态更新）|
| scan-ts | 显示当前时间（负载时间，非数据时间）|
| cache_age_sec 显示 | ❌ 无 |
| data_source 显示 | ❌ 无 |
| data_status 显示 | ❌ 无 |
| 过期警告 | ❌ 无 |

**用户视角**: 页面右上角显示绿色点 + "就绪"，用户无法判断数据是否新鲜。

---

## 三、数据流链路图

```
console_server 启动 (16:34)
    │
    └── _prewarm_rt_prices()
            │
            └── _prewarm_realtime_prices()
                    │
                    └── /tmp/tianlu_cache/realtime_prices/BTC_USDT_rt_price.json
                            │
                            └─ ⚠️ 之后再无刷新（7小时+）
                                    │
m2_sr.html 加载
    │
    └── /api/bt2/sr_levels
            │
            ├── 90s short API cache ✅（正常）
            │
            └── get_latest_triple(pair)
                    │
                    └── /tmp/tianlu_cache/sr_levels/BTC_USDT_triple_latest.json
                            │
                            └── ✅ 正常（2分钟前）
                                    │
                                    └─ 显示: triple_validated=16（三所全通）

天眼AI更新 current_price
    │
    └── 7小时前缓存价格 + 新实时价格混用
            │
            └── 用户看到: S/R位不动但价格有小幅波动
```

---

## 四、根因总结

| 优先级 | 根因 | 位置 | 影响 |
|--------|------|------|------|
| P0 | realtime_prices 只在启动时刷新一次 | console_server.py:124-132 | 7小时陈旧价格 |
| P1 | 前端无 cache_age/data_source 展示 | m2_sr.html:176-178 | 用户无法判断数据新鲜度 |
| P2 | force_live 串行超时 | m2_sr_enhanced.py | 无法强制刷新 |
| P3 | API short cache TTL(90s) vs file cache TTL(2h) 不匹配 | console_server.py:50 | 页面显示90s内相同数据 |

---

## 五、已验证正常的模块

- m2_sr_enhanced.py P1-P5 修复 ✅
- Triple 三所交叉验证 ✅
- Dual validated count ✅
- M2 L1.5 warm cache 架构 ✅
- M2 健康检查 LaunchAgent ✅
- M2 归档脚本 LaunchAgent ✅
