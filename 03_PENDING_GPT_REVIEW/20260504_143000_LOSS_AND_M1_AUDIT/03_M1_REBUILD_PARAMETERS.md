# M1重建参数草案

**审计时间**: 2026-05-04 14:30
**基于代码**: api_m1.py, fund_flow_v2_collector.py, m1_v2.html
**输出路径**: ~/Desktop/Tianlu_V6_5_Workspace/03_PENDING_GPT_REVIEW/20260504_143000_LOSS_AND_M1_AUDIT/

---

## 1. flow_consensus_score (流量共识分)

**定义**: 三所资金流向方向一致程度的量化指标。衡量三所(Gate/OKX/BNB)在资金流入/流出方向上的一致性。

**计算公式**:
```python
# 伪代码
signs = []
for each exchange (gate, okx, bnb):
    s = sign(taker_delta_ratio)
    if s == 0:
        s = sign(ohlcv_netflow)  # 降级使用OHLCV方向
    if s != 0:
        signs.append(s)
long_count = signs.count(1)   # 做多信号数
short_count = signs.count(-1)  # 做空信号数
flow_consensus_score = max(long_count, short_count) / len(signs)
```

**建议阈值**:

| 阈值范围 | 共识等级 | 含义 | 建议动作 |
|---------|---------|------|---------|
| >= 1.0 | 完美共识 | 三所方向完全一致 | 信任信号 |
| 0.67 ~ 0.99 | 强共识 | 2/3所以上同向 | 高置信执行 |
| 0.50 ~ 0.66 | 弱共识 | 仅2所同向, 1所偏离 | 降权执行或观望 |
| < 0.50 | 无共识 | 三所分歧严重 | 强制观望 |

---

## 2. flow_divergence_score (流量分歧度)

**定义**: 三所量比(Volume Ratio)偏离程度的指标。衡量三所在放量幅度上的差异,而非方向差异。

**计算公式**:
```python
all_ratios = [gate_ratio, okx_ratio, bnb_ratio]  # 仅包含 > 0 的值
if not all_ratios:
    return 1.0  # 无数据时最大分歧
max_ratio = max(all_ratios)
min_ratio = min(all_ratios)
flow_divergence_score = (max_ratio - min_ratio) / max_ratio
# 例: Gate=4.5, OKX=2.1, BNB=1.8 → 分歧度 = (4.5-1.8)/4.5 = 0.60
```

**建议阈值**:

| 阈值 | 分歧等级 | 含义 | 建议动作 |
|------|---------|------|---------|
| < 0.30 | 低分歧 | 三所量比接近 | 正常处理 |
| 0.30 ~ 0.49 | 中分歧 | 一所偏高但可接受 | 关注但执行 |
| 0.50 ~ 0.59 | 高分歧 | 单所极端,需关注 | 降噪观望 |
| >= 0.60 | 严重分歧 | 单所拉偏可能性高 | 禁止执行 |

**关键触发条件** (V6.5标准):
```python
# 量价背离: 放量但净流出
if ratio >= 2.0 and netflow < -0.5 and valid_count >= 2:
    return "观望"  # 不管分歧度,背离优先

# 单所极端 + 分歧严重
if max_ratio >= 3.0 and flow_divergence_score >= 0.6:
    return "噪音过滤"  # 单所异常拉偏,强制降噪
```

---

## 3. dominant_exchange (主导交易所)

**定义**: 在某交易对上量比最高、资金流入最活跃的交易所。用于识别哪个交易所的信号最强,以及当出现分歧时判断是否为单所异常。

**计算逻辑**:
```python
exchanges = {"gate": gate_ratio, "okx": okx_ratio, "bnb": bnb_ratio}
dominant_exchange = max(exchanges.items(), key=lambda x: x[1] if x[1] > 0 else 0)[0]
# 返回: "gate" | "okx" | "bnb" | None
```

**使用场景**:

| 场景 | dominant_exchange | 处理方式 |
|------|------------------|---------|
| 三所分歧严重 | 非空 | 降低该所权重,用另外两所聚合 |
| V2单所极端信号 | 非空 | 触发exchange_outlier检测 |
| 三所接近 | None | 无主导,信任聚合结果 |

---

## 4. exchange_outlier (交易所异常)

**定义**: 某交易所的数据与其他两所显著偏离,可能被该交易所的局部事件(如交易所维护、大户操纵、API异常)拉偏,需要降低其权重或排除。

**检测条件**:
```python
def is_exchange_outlier(exchange_ratio: float,
                        other_mean: float,
                        threshold: float = 0.60) -> bool:
    """
    判断某交易所是否为异常值
    threshold=0.60: 该所量比超过其他均值+60%则标记为异常
    """
    if other_mean <= 0:
        return False
    deviation = (exchange_ratio - other_mean) / other_mean
    return deviation >= threshold
```

**建议阈值**:

| 参数 | 值 | 说明 |
|------|-----|------|
| outlier_threshold | 0.60 | 量比超过其他均值60%则标记 |
| min_other_count | 2 | 至少需要2个其他数据源才能判断 |
| outlier_action | "downweight" | 降低该所权重至0.3 |

**V2置信度计算中的outlier处理**:
```python
# 当某所被标记为outlier时,其置信度贡献降至30%
if exchange_outlier:
    component_confidence *= 0.3
```

---

## 5. source_count (最小数据源要求)

**定义**: 在进行资金流判断前,需要确认有效的交易所数据源数量。数量不足时信号不可信。

**建议阈值**:

| source_count | 含义 | 信任等级 | 建议动作 |
|-------------|------|---------|---------|
| 3 | 三所全部有效 | 最高 | 全信 |
| 2 | 两所有效 | 中高 | 信任但关注分歧 |
| 1 | 仅单所有效 | 低 | 观望,不执行 |
| 0 | 无有效数据 | 无 | 禁止入场 |

**实现代码**:
```python
valid_count = len([r for r in [gate_data, okx_data, bnb_data] if r is not None])

if valid_count == 0:
    return {"action": "禁止入场", "confidence": 0.0}
if valid_count == 1:
    return {"action": "观望", "confidence": 0.35}  # 单所不可信
if valid_count == 2:
    # 双所: 检查分歧度
    if flow_divergence_score >= 0.5:
        return {"action": "观望", "confidence": 0.40}
    return {"action": "建议执行", "confidence": 0.75}
# valid_count == 3
return {"action": "信任信号", "confidence": 0.85 + 0.10 * flow_consensus_score}
```

---

## 6. m1_signal_trust_level (信号信任等级 A/B/C/D/E)

**定义**: 综合flow_consensus_score、flow_divergence_score、volume_ratio、netflow等指标,对M1资金流信号的最终信任等级划分。

| 等级 | 置信度 | 量比要求 | 净流入要求 | 共识要求 | 动作 |
|------|--------|---------|---------|---------|------|
| **A级** | >= 85% | >= 3.0x | >= 0.8 | 三所全一致 | 强势执行 |
| **B级** | 70-84% | >= 2.0x | >= 0.5 | >=2所一致 | 建议执行 |
| **C级** | 55-69% | 1.5-2.0x | >= 0.4 | >=2所一致 | 谨慎执行 |
| **D级** | 40-54% | < 1.5x | 任意 | < 2所一致 | 观望 |
| **E级** | < 40% | 极低或无 | 无 | < 2所 | 禁止入场 |

**详细判定逻辑** (伪代码):
```python
def get_signal_trust_level(data: dict) -> str:
    ratio = data["aggregated"]["ratio"]
    netflow = data["aggregated"]["netflow"]
    valid_count = data["aggregated"]["valid_count"]
    consensus = data.get("exchange_agreement", 0)
    divergence = data.get("flow_divergence_score", 0)

    # S级做多: 三所共振极端放量
    if ratio >= 3.0 and netflow >= 0.8 and valid_count == 3 and consensus >= 0.66:
        return "A级"

    # A级做多: 双所共振 + 净流入确认
    if ratio >= 2.0 and netflow >= 0.5 and valid_count >= 2:
        return "B级"

    # B级: 温和放量信号
    if 1.5 <= ratio < 2.0 and abs(netflow) >= 0.4:
        return "C级"

    # D级: 方向不明确
    if ratio < 1.5 or divergence >= 0.5:
        return "D级"

    # E级: 无数据/死区
    if valid_count <= 1 or ratio < 0.5:
        return "E级"

    return "D级"  # 兜底
```

---

## 7. 完整参数汇总表

| 参数名 | 类型 | 当前代码值/建议 | 建议阈值 | 备注 |
|--------|------|---------------|---------|------|
| `flow_consensus_score` | float [0,1] | 建议 >= 0.66 | >= 0.66 执行, < 0.50 观望 | 三所方向一致率 |
| `flow_divergence_score` | float [0,1] | 建议 < 0.50 | < 0.50 正常, >= 0.60 异常 | 三所量比分歧度 |
| `dominant_exchange` | str | 动态计算 | 非空时降权处理 | "gate"\|"okx"\|"bnb"\|None |
| `exchange_outlier` | bool | deviation >= 0.60 | 触发时该所权重=0.3 | 单所偏离检测 |
| `source_count` | int | 建议 >= 2 | >= 2 执行, < 2 观望 | 有效数据源数 |
| `m1_signal_trust_level` | str | A/B/C/D/E五级 | 见上表 | 最终信任等级 |
| `volume_ratio_threshold` | float | L1=5.0x, L2=2.0x | 5.0x 强信号, 2.0x 确认信号 | 量比阈值 |
| `netflow_threshold` | float | 建议 >= 0.5 | >= 0.5 确认方向 | 净流入阈值 |
| `confidence_base` | float | 0.45*coverage + 0.35*strength + 0.20*agreement | 同左 | V2置信度公式 |
| `ohlcv_cache_ttl` | int | 300秒 | 300秒 | 缓存TTL |
| `scan_interval` | int | 900秒(15分钟) | 900秒 | 主扫描间隔 |

---

## 8. 实施注意事项

1. **Binance净流入缺失**: 当前BNB的netflow=0,会导致聚合netflow偏低。建议为BNB使用OI变化率作为替代净流入指标。

2. **V2 Shadow数据停更**: fund_flow_v2_shadow.sqlite自5月2日未更新,建议:
   - 恢复V2采集器cron任务
   - 或确认是否有意废弃V2 shadow系统,专注api_m1.py实时系统

3. **外置硬盘路径**: `/Volumes/TianLu_Storage` 路径硬编码,不存在时静默失败。建议增加路径存在性检测和明确警告。

4. **旧采集器清理**: collector_gate.py的`defaultType=spot`配置错误,如api_m1.py正常则建议删除旧采集器代码。
