# 00_M2_SR_URGENT_FIX_SUMMARY.md

## M2 S/R 紧急缓存修复 — 总报告

**生成时间**: 2026-05-04 23:55
**状态**: 草案（DRAFT）—— 禁止直接写入实盘

---

## 执行边界（铁律）

1. ✅ 不修改实盘交易策略
2. ✅ 不重启 9090-9097 / 8081-8084
3. ✅ 不调用交易所下单 API
4. ✅ 不执行 force_entry / force_exit
5. ✅ 先归档再清理缓存
6. ✅ 不直接 rm -rf 整个 cache
7. ✅ 不推送数据库原文到 GitHub

---

## 故障结论

| 问题 | 结论 |
|------|------|
| M2页面数据是否真的用了旧缓存？ | ❌ 否。Triple S/R数据正常（0.03h）。问题在于**realtime_prices缓存7小时未刷新**，且**前端无数据年龄展示**。 |
| 顽固缓存文件在哪里？ | `/tmp/tianlu_cache/realtime_prices/` 5个文件（7小时旧）|
| 是否已归档到 TianLu_Archive？ | ✅ 已归档: `Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/stale_cache_archive/20260504_234911/` |
| 是否安全清理了过期本地缓存？ | ✅ 已清理5个旧文件（manifest记录完整）|
| /api/bt2/sr_levels 过期时强制重算？ | 🔧 待补丁应用（新增30分钟定期刷新器）|
| fallback 明确标记 stale/fallback？ | ✅ 已有 data_source 字段，前端待补丁展示 |
| 前端显示 cache_age_sec/data_status？ | 🔧 待补丁应用（新增 `_updateCacheIndicator()`）|
| 实时价格覆盖后重算 S/R 距离？ | 🔧 待补丁应用（新增 `_recomputeSRDistances()`）|
| 是否需要重启 console_server？ | ⚠️ 补丁应用后需重启（不重启机器人）|
| 如何回滚？ | 见 ROLLBACK_PLAN.md |

---

## 核心修复内容

### P0: Realtime prices 定期刷新（已执行）
- ✅ 归档旧缓存到 TianLu_Archive
- ✅ 清理7小时旧缓存
- ✅ 立即触发刷新（所有5对 <1分钟新鲜）
- 🔧 补丁: console_server.py 新增 30分钟定时器

### P1: 前端数据年龄展示（补丁草案）
- 🔧 m2_sr.html 新增 `m2-cache-indicator` 状态栏
- 🔧 新增 `_updateCacheIndicator()` 函数
- 🔧 缓存 >2小时显示 🔴 警告
- 🔧 缓存 >15分钟显示 🟠 警告

### P2: 实时价格覆盖后重算（补丁草案）
- 🔧 新增 `_recomputeSRDistances(pair, data)` 函数
- 🔧 天眼AI更新 current_price 后自动触发重算

### P3: 过期自动 force_live（补丁草案）
- 🔧 Triple缓存 >2小时自动触发 `/api/bt2/sr_levels?force_live=1`

---

## 交付包清单

| 文件 | 说明 |
|------|------|
| `00_M2_SR_URGENT_FIX_SUMMARY.md` | 本文，总报告 |
| `01_M2_SR_DATA_SOURCE_AUDIT.md` | 户部：数据链路审计 |
| `02_M2_BACKEND_REFRESH_PATCH.md` | 工部：后端补丁（console_server.py）|
| `03_M2_FRONTEND_STALE_CACHE_PATCH.md` | 前端院：前端补丁（m2_sr.html）|
| `04_M2_CACHE_ARCHIVE_AND_CLEAN_REPORT.md` | 仓储院：归档清理报告 |
| `05_M2_SR_QA_CHECKLIST.md` | 都察院：QA清单 |
| `PATCH.diff` | 代码补丁（草案）|
| `TEST_LOG.md` | 测试执行日志 |
| `ROLLBACK_PLAN.md` | 回滚方案 |
| `REVIEW_PACKAGE.zip` | 交付包 |

---

## 下一步

1. **GPT 审核本包** → 确认补丁逻辑
2. **爸确认后应用补丁** → py_compile → 重启 console_server
3. **观察3天** → 确认 realtime_prices 每30分钟刷新
4. **前端补丁部署** → 刷新页面 → 确认 cache-indicator 正常显示
