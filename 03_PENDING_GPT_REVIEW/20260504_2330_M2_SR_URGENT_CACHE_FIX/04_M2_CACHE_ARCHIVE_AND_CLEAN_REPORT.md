# 仓储院 · 缓存归档与清理报告

**生成时间**: 2026-05-04 23:50
**代理**: 仓储院

---

## 一、归档执行记录

### 1.1 归档源

| 目录 | 说明 |
|------|------|
| `/tmp/tianlu_cache/realtime_prices/` | Realtime prices 缓存（7小时陈旧）|

### 1.2 归档目标

```
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/stale_cache_archive/20260504_234911/
├── manifest.json          ← 归档清单
├── BNB_USDT_rt_price.json
├── BTC_USDT_rt_price.json
├── DOGE_USDT_rt_price.json
├── ETH_USDT_rt_price.json
└── SOL_USDT_rt_price.json
```

### 1.3 manifest.json 内容

```json
{
  "archive_time": "2026-05-04 23:49:11",
  "source": "/tmp/tianlu_cache/realtime_prices/",
  "destination": "/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/stale_cache_archive/20260504_234911/",
  "reason": "realtime_prices cache was 7h stale, archiving before refresh",
  "files": [
    {"name": "BNB_USDT_rt_price.json", "mtime": "2026-05-04 16:36", "age_h": 7.2},
    {"name": "BTC_USDT_rt_price.json", "mtime": "2026-05-04 16:35", "age_h": 7.2},
    {"name": "DOGE_USDT_rt_price.json", "mtime": "2026-05-04 16:36", "age_h": 7.2},
    {"name": "ETH_USDT_rt_price.json", "mtime": "2026-05-04 16:35", "age_h": 7.2},
    {"name": "SOL_USDT_rt_price.json", "mtime": "2026-05-04 16:35", "age_h": 7.2}
  ],
  "oldest_file_mtime": "2026-05-04 16:35",
  "newest_file_mtime": "2026-05-04 16:36",
  "action": "ARCHIVED"
}
```

---

## 二、清理执行记录

### 2.1 清理前状态

| 文件 | 年龄 | 操作 |
|------|------|------|
| BNB_USDT_rt_price.json | 7.2h | ✅ 已删除 |
| BTC_USDT_rt_price.json | 7.2h | ✅ 已删除 |
| DOGE_USDT_rt_price.json | 7.2h | ✅ 已删除 |
| ETH_USDT_rt_price.json | 7.2h | ✅ 已删除 |
| SOL_USDT_rt_price.json | 7.2h | ✅ 已删除 |

### 2.2 立即刷新结果

| 交易对 | 刷新后年龄 |
|--------|-----------|
| BTC/USDT | **0.8 分钟** ✅ |
| ETH/USDT | **0.6 分钟** ✅ |
| SOL/USDT | **0.2 分钟** ✅ |
| BNB/USDT | **0.1 分钟** ✅ |
| DOGE/USDT | **0.0 分钟** ✅ |

**结论**: 5个交易对实时价格全部刷新至最新，数据新鲜。

---

## 三、遵守安全边界确认

| 检查项 | 状态 |
|--------|------|
| 先归档再删除 | ✅ rsync → manifest.json → rm |
| 未删除 Triple S/R 缓存 | ✅ /tmp/tianlu_cache/sr_levels/ 未动 |
| 未删除 M2 L1.5 warm cache | ✅ sr_levels_warm 为空，未涉及 |
| 未删除实时数据 | ✅ 只删除了7小时旧缓存 |
| 未删除 live db | ✅ 未涉及任何 sqlite |
| manifest 记录完整 | ✅ 含归档时间/原因/文件列表 |

---

## 四、未涉及清理的缓存（保持原样）

| 目录 | 状态 | 不清理原因 |
|------|------|-----------|
| `/tmp/tianlu_cache/sr_levels/` | 正常（0.03h新鲜）| 正常数据 |
| `/tmp/tianlu_cache/l5/` | 未检查 | 待确认 |
| `/tmp/tianlu_cache/ohlcv/` | 未检查 | 历史数据 |
