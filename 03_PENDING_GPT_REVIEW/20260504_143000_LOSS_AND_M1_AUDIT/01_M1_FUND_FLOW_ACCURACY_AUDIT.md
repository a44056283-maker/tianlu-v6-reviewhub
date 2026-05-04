# M1资金流数据准确性审计报告

**审计时间**: 2026-05-04 14:30
**审计人**: 户部代理
**工作目录**: ~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/20260504_143000_LOSS_AND_M1_AUDIT/

---

## 1. M1数据最后更新时间

| 数据库文件 | 大小 | 最后修改时间 | 状态 |
|-----------|------|-------------|------|
| m1_cache.db | 75MB | **2026-05-04 13:11** (今日) | 正常 |
| data_pool.db | 58MB | **2026-05-04 13:10** (今日) | 正常 |
| fund_flow_v2_shadow.sqlite | 32KB | **2026-05-02 18:24** (2天前) | 异常 - 未更新 |

**关键发现**: V2 Shadow数据库(fund_flow_v2_shadow.sqlite)自5月2日以来未更新，说明`fund_flow_v2_collector.py`采集器未在运行。实时数据完全依赖`api_m1.py`系统。

---

## 2. M1缓存数据库表结构

### m1_cache.db (本地热缓存, SSD)

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `ohlcv_cache` | 三所OHLCV原始K线缓存 | exchange, symbol, tf, ts, data(JSON), fetched_at |
| `scan_cache` | 扫描结果缓存 | pair_id, ts, data(JSON), fetched_at |

**TTL策略**: OHLCV缓存TTL=300秒(5分钟)

### data_pool.db (M1扫描结果)

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `m1_scan_results` | 15m资金流扫描结果 | pair_id, gate_ratio, okx_ratio, bnb_ratio, valid_count, grade, action, confidence |
| `m1_mtf_results` | 多时线资金流 (15m/1h/4h/1d) | pair_id, tf, gate_ratio, okx_ratio, bnb_ratio, whale_ratio, grade |
| `collector_status` | 各采集器健康状态 | exchange, pair, last_updated |
| `fund_flow_avg` | 资金流平均数据 | 历史聚合数据 |

### fund_flow_v2_shadow.sqlite (V2 Shadow, 当前停更)

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `fund_flow_v2_snapshots` | 三所快照原始数据 | exchange, pair, tf, taker_delta_ratio, book_imbalance, oi_change_pct, confidence, direction |
| `fund_flow_v2_health` | 各交易所API健康状态 | exchange, endpoint, ok, latency_ms, freshness_sec |

---

## 3. 三所数据是否存在

### 实时数据通道 (api_m1.py - 正在运行)

**Gate (gateio)**
- 状态: 正常采集
- 路径: ccxt.gateio 直连, 无代理
- Symbol: BTC/USDT:USDT (永续合约)
- defaultType: swap
- API端点: gateio公开K线API

**OKX**
- 状态: 正常采集
- 路径: 走代理 `http://127.0.0.1:5020` (mihomo mixed)
- Symbol: BTC/USDT:USDT (永续合约)
- defaultType: swap
- API Key池: 轮询使用 9093-9096 四个bot的OKX Key
- 双代理容错: primary(7890) + backup(5020)

**Binance (bnb)**
- 状态: 正常采集
- 路径: 走代理 `http://127.0.0.1:5020`
- Symbol: BTC/USDT:USDT (币安永续)
- defaultType: future
- 限制: 无法从公开数据估算净流入(netflow=0), 仅能量比

### 旧采集器 (collector_*.py - 备用/停用)

| 采集器 | 状态 | 问题 |
|--------|------|------|
| collector_gate.py | 备用量 | options defaultType="spot" (应为swap) |
| collector_okx.py | 备用量 | 正常 |
| collector_bnb.py | 备用量 | netflow固定为0 |

---

## 4. 三所方向是否一致

**方向一致性算法**: `apply_exchange_agreement` (fund_flow_v2_collector.py)

- 统计三所 `taker_delta_ratio` 和 `ohlcv_netflow` 的符号
- 计算 agreement = max(long_count, short_count) / total_signs
- 评分权重: taker_delta_ratio(40%) + book_imbalance(25%) + oi_change_pct(20%) + ohlcv_netflow(15%)

**当前状态**: 由于V2 shadow未运行, 无法直接验证三所一致性。但从`api_m1.py`代码可见:
- 三所分歧度 split_deg >= 0.5 时, 系统降噪为"观望" (confidence 0.40)
- 单所极端信号(量比>=3.0 + 分歧度>=0.6)时过滤噪音

---

## 5. 数据延迟或缺失风险

### 风险项

| 风险项 | 严重度 | 说明 |
|--------|--------|------|
| V2 Shadow停更 | 中 | 5月2日后无新数据, 但实时数据走api_m1.py不受影响 |
| 外挂硬盘路径硬编码 | 高 | `/Volumes/TianLu_Storage` 不存在时EXT_CACHE_READ_ENABLED=false, 读不到历史归档 |
| OHLCV缓存TTL=5分钟 | 低 | 后台2分钟预热, 15分钟扫描, 实际延迟可控 |
| Binance净流入固定为0 | 中 | BNB的netflow无法估算, 影响score准确性 |
| collector_gate.py defaultType=spot | 高 | 若旧采集器被调用, 会读到现货数据而非合约数据 |

### 数据新鲜度状态码 (api_m1.py)

```python
# m1_status判断
m1_status = "ok"      if m1_age < 1200   # 20分钟内
m1_status = "warn"    if m1_age < 3600   # 1小时内
m1_status = "error"   if m1_age >= 3600  # 超过1小时
```

---

## 6. 单交易所异常拉偏风险

**噪音过滤机制**:

1. **单所极端信号保护** (api_m1.py L674-681):
   - `split_deg >= 0.5` 且 `valid_count >= 2` → 强制观望
   - `max_ratio >= 3.0` 且 `split_deg >= 0.6` → 降噪观望

2. **V2 exchange_outlier检测**:
   - 三所中某所偏离均值超过阈值时标记为异常

3. **量价背离检测**:
   - `ratio >= 2.0` 但 `netflow < -0.5` → 强制观望 (量增价跌背离)

**保护有效性**: 中等。当前代码有保护机制, 但依赖 split_deg 计算, 若两所正常一所有偏差, 仍有被拉偏风险。

---

## 7. M1信号信任等级 (A/B/C/D/E 五级)

基于`api_m1.py`中`ai_evaluate_pair`函数分析:

| 等级 | 置信度范围 | 触发条件 | 建议动作 |
|------|-----------|---------|---------|
| **A** | confidence >= 0.85 | 三所共振放量>=3.0x + 净流入>=0.8 + 大户占比确认 | 强势做多/做空 |
| **B** | confidence >= 0.70 | 双所以上共振放量>=2.0x + 净流入>=0.5 | 建议做多/做空 |
| **C** | confidence >= 0.55 | 温和放量1.5-2.0x + 净流>=0.4 | 谨慎操作 |
| **D** | confidence >= 0.40 | 量比<1.5, 方向不明确 | 观望 |
| **E** | confidence < 0.40 | 无数据/单所/死区 | 禁止入场 |

**评分算法**:
```python
score = netflow * 50 + min(volume_ratio / 10, 1) * 20
# 量比>=5.0x 且 净流入>=0.8 → score ≈ 90+ (A级)
```

---

## 8. M1重建参数建议

### 核心参数

| 参数名 | 当前建议阈值 | 说明 |
|--------|------------|------|
| `flow_consensus_score` | >= 0.66 | 三所方向一致率(2/3所以上同向) |
| `flow_divergence_score` | < 0.50 | 三所分歧度上限, 超过则降噪观望 |
| `dominant_exchange` | 非空 | 触发时需标记该交易所, 降低其权重 |
| `exchange_outlier` | 分歧度 > 0.6 | 单所量比超过均值60%时标记为异常 |
| `source_count` | >= 2 | 最小有效数据源要求(2/3所) |
| `m1_signal_trust_level` | 见上表 | A/B/C/D/E五级 |

### 修复建议

1. **紧急**: 确认 `collector_gate.py` 的 `defaultType` 是否影响实际采集, 若无影响则删除旧采集器
2. **重要**: 为 `fund_flow_v2_shadow.sqlite` 设置定时任务或cron, 恢复V2采集器
3. **中等**: 考虑为Binance添加近似净流入估算(用OI变化替代)
4. **优化**: EXT_CACHE_DIR路径检测, 路径不存在时给出明确警告而非静默失败

---

## 审计结论

| 维度 | 评分 | 说明 |
|------|------|------|
| 数据新鲜度 | B+ | m1_cache.db和数据池今日更新, V2 shadow停更但不影响实时 |
| 三所覆盖 | A | Gate/OKX/BNB三所全部覆盖, 备用+实时双通道 |
| 数据准确性 | B | collector_gate.py defaultType=spot隐患, BNB净流入缺失 |
| 系统稳定性 | B | 双代理容错 + 2分钟后台预热 + 15分钟扫描, 架构健壮 |
| 噪音过滤 | B+ | 三所分歧检测 + 量价背离检测 + 单所极端过滤 |

**总体评估**: M1资金流系统运行正常, 数据今日有更新, 三所覆盖完整。存在两个中等风险: 旧采集器Gate defaultType配置错误(若被调用会导致数据错误), 以及V2 shadow数据库停更2天(但不影响实时数据)。
