# TianLu_Archive DataVault 标准目录结构

> 建立时间：2026-05-04 13:50
> Phase 1 完成，未移动任何数据

---

## 目录结构

```
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/
├── 00_HEALTHCHECK/
│   └── （用于存储健康检查日志）
├── 01_TRADING_PARAMS_BACKUP/
│   └── （每日交易系统参数备份）
├── 02_OPENCLAW_CONFIG_BACKUP/
│   └── （OpenClaw 配置备份，脱敏后归档）
├── 03_M1_M5_CACHE_ARCHIVE/
│   ├── M1/   （M1 英雄卡数据归档）
│   ├── M2/   （M2 入场评分归档）
│   ├── M3/   （M3 持仓追踪归档）
│   ├── M4/   （M4 技术分析归档）
│   ├── M5/   （M5 市场情绪归档）
│   └── L5/   （L5 进化实验室归档）
├── 04_L5_MARKET_DATA/
│   ├── orderbook/     （盘口数据）
│   ├── open_interest/  （持仓量数据）
│   ├── liquidations/   （清算数据）
│   ├── funding_rate/   （资金费率）
│   ├── fear_greed/    （恐惧贪婪指数）
│   └── taker_flow/    （主动买卖流）
├── 05_BACKTEST_REPORTS/
│   └── （回测报告归档）
├── 06_DAILY_REPORTS/
│   └── （每日报告归档）
├── 07_REVIEW_HUB_MIRROR/
│   └── （GitHub review hub 本地镜像）
├── 08_LOG_ARCHIVE/
│   └── （日志归档）
└── 99_MANIFESTS/
    └── （备份清单和校验文件）
```

---

## 使用原则

| 原则 | 说明 |
|------|------|
| 热数据不动 | `~/freqtrade_console/` 内的实时缓存留在本地 |
| 归档走这里 | 每日备份、配置快照、报告归档进入 DataVault |
| Python 直接写 | 健康检查确认 Python 可直接写入此卷 |
| rsync 备用 | 如 Python 偶发失败，用 `rsync -a`兜底 |
| 不删除旧数据 | `tianlu_archive/` 旧目录保留兼容 |

---

## Phase 0+1 完成状态

| Phase | 状态 | 说明 |
|-------|------|------|
| Phase 0 健康检查 | ✅ 完成 | 见 `TIANLU_ARCHIVE_HEALTHCHECK_REPORT.md` |
| Phase 1 建立目录 | ✅ 完成 | 23个目录已创建 |
| Phase 2 交易备份切换 | ⏳ 待执行 | 等待用户/GPT确认 |
| Phase 3 OpenClaw备份切换 | ⏳ 待执行 | 等待用户/GPT确认 |
| Phase 4 M1-M5缓存归档 | ⏳ 待执行 | 等待用户/GPT确认 |
| Phase 5 L5市场数据归档 | ⏳ 待执行 | 等待用户/GPT确认 |

---

## 下一步（待用户下达）

Phase 2-5 需用户/GPT审核后再执行，不在本次任务范围内。
