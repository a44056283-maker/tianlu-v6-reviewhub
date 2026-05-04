# 缓存/备份基础设施现状及下一步行动

**审计时间**: 2026-05-04 14:30
**审计人**: 翰林院代理
**数据来源**: 目录扫描 + 文件大小统计

---

## 1. 基础设施现状总览

| 模块 | 路径 | 文件大小 | 状态 | 上次更新 |
|------|------|---------|------|---------|
| M1缓存数据库 | `~/freqtrade_console/m1_cache.db` | **72MB** | 就绪 | 2026-05-04 13:09 |
| M4缓存数据库 | `~/freqtrade_console/m4_cache.db` | **12KB** | **异常**: 严重偏小 | 2026-05-04 12:56 |
| L5影子实验DB | `~/freqtrade_console/l5_evolution_lab/m4_m5_shadow_lab.sqlite` | **736MB** | 就绪 | 2026-05-04 13:04 |
| L5资金流DB | `~/freqtrade_console/l5_evolution_lab/fund_flow_v2_shadow.sqlite` | 32KB | 静止（5月2日） | 2026-05-02 |
| L5影子报告 | `~/freqtrade_console/l5_evolution_lab/reports/*.json` | ~57KB/份 | 就绪 | 每小时生成 |
| L5 Cache JSON | `~/freqtrade_console/cache/l5/*.json` | **0个文件** | **缺失** | 无 |
| L5候选配置 | `~/freqtrade_console/bt_tools/backtest_core/config/v65_l5_candidate_20260429.json` | 存在 | 就绪 | 2026-04-29 |

---

## 2. 已就绪模块

### 2.1 M1缓存数据库（72MB） - 正常
- 大小合理（72MB），支持多交易所量比计算
- 覆盖 Gate.io / OKX / BNB 三所
- 数据源: m1_scan
- 缓存刷新: 活跃

### 2.2 L5影子实验数据库（736MB） - 正常
- 5月2日启动，至今已运行2天
- 快照样本: 3040条（5个交易对 x 每轮）
- 持仓样本: 24703条
- 报告按时生成（每小时）

### 2.3 L5影子实验代码 - 正常
- `m4_m5_shadow_lab.py`: 1101行，功能完整
- `fund_flow_v2_collector.py`: 资金流采集器
- `flow_gate_backtest.py`: 历史回测工具（尚未激活）

---

## 3. 待修复模块

### 3.1 M4缓存数据库异常（12KB，严重）

**问题**: M4_cache.db 仅12KB，远小于正常值（预期 > 1MB）

**可能原因**:
1. M4 RSI/ATR/OI 采集频率低于 M1
2. M4 采集器未正常启动
3. 数据库 schema 尚未初始化
4. 采集端点到 console_server 的网络问题

**GPT审核要点**:
- 是否需要为 M4 添加独立的 cron 采集任务？
- M4_cache.db 的预期大小是多少？
- 当前12KB是否已足够支撑影子实验所需？

**诊断建议**（翰林院代理无权执行，需GPT确认）:
```bash
# 诊断M4采集器状态
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/luxiangnan/freqtrade_console/m4_cache.db')
tables = conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()
print('Tables:', tables)
for t in tables:
    cnt = conn.execute(f'SELECT COUNT(*) FROM {t[0]}').fetchone()[0]
    print(f'{t[0]}: {cnt} rows')
"
```

### 3.2 L5 Cache JSON目录为空

**问题**: `~/freqtrade_console/cache/l5/` 目录不存在或无JSON文件

**影响**: 无法进行L5历史数据回放对照

**GPT审核要点**:
- L5 cache JSON 的预期用途是什么？
- 是否需要为L5独立建立数据采集？
- 当前影子实验直接从9099 API拉取，是否足够？

**诊断建议**:
```bash
ls -la ~/freqtrade_console/cache/ 2>/dev/null || echo "cache目录不存在"
```

### 3.3 L5候选参数样本量严重不足

**问题**:
- `closed_bt2_trades: 1`（目标: >= 100）
- `l5_replay_samples: 21`（样本严重不足）

**影响**: 当前candidate参数无统计意义，不能作为实盘晋级依据

**GPT审核要点**:
- 是否接受21个L5 replay样本的初步参数？
- 如何在不影响实盘的情况下加速积累样本？

---

## 4. 下一步行动清单（需GPT审核后才能执行）

### 优先级 P0（阻塞L5晋级）

| # | 行动 | 审核问题 | 预期工作量 |
|---|------|---------|-----------|
| P0-1 | 诊断M4_cache.db异常 | 12KB是否正常？是否需要独立采集？ | GPT决定 |
| P0-2 | 确认walk-forward测试时间表 | 历史数据回测周期？参数更新频率？ | GPT决定 |
| P0-3 | 确认L5 replay样本积累方案 | 如何在30天内达到100笔closed trades？ | GPT决定 |

### 优先级 P1（影响影子实验质量）

| # | 行动 | 审核问题 | 预期工作量 |
|---|------|---------|-----------|
| P1-1 | 分析DOGE高噪音根因 | 为何DOGE高噪音信号占64.8%？是否需要差异化参数？ | GPT审核 |
| P1-2 | 启用 flow_gate_backtest.py | 历史回测口径和周期？ | GPT审核 |
| P1-3 | 建立L5 cache JSON采集 | 当前影子实验数据流是否足够？ | GPT确认 |

### 优先级 P2（优化）

| # | 行动 | 审核问题 | 预期工作量 |
|---|------|---------|-----------|
| P2-1 | 分离各币种独立报告 | 按币种输出噪音均值和晋级建议？ | 可自主执行 |
| P2-2 | 标记数据缺失场景 | collection_health_pct: 0.0 根因分析？ | GPT审核 |
| P2-3 | L5影子实验WebUI | http://127.0.0.1:8895 是否需要部署？ | 可自主执行 |

---

## 5. GPT审核前的准备问题

在执行任何修复前，请GPT回答以下问题：

1. **M4_cache.db**: 当前12KB是否预期值？如不是，应由哪个采集器负责填充？
2. **L5 replay样本**: 当前21个样本仅作为探索性参数，是否可以接受？正式晋级前需要多少样本？
3. **各币种差异化参数**: BTC vs DOGE 的噪音差异（33.99 vs 66.29）是否需要两个独立的参数集？
4. **walk-forward测试**: 建议用多长时间的历史数据做一次walk-forward？每次更新多少参数？
5. **小资金实盘对接**: 如果进行，建议用哪个端口和多大资金规模？

---

## 6. 当前翰林院可自主执行的优化（无需GPT）

以下行动翰林院代理可以立即执行，无需GPT审核：

1. 每日影子实验报告推送到飞书尚书省（代码已实现 `send_feishu` 函数）
2. 在报告中添加各币种噪音均值的趋势图表
3. 标记连续3天噪音均值 > 60 的交易对，发出告警
4. 定期清理超过30天的旧影子报告（当前有5份报告，最早5月3日）

---

*本报告由翰林院代理生成，需GPT人工审核后执行修复*
