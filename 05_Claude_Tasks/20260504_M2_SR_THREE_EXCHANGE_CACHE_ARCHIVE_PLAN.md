# 天禄 V6.5 · M2 S/R 三所交叉校验与二级缓存归档对接建议

> 生成方：GPT / 架构师审核员  
> 日期：2026-05-04  
> 执行方：Claude Code 多子代理协作  
> 目标：修复 M2 S/R 数据采集长期不稳定问题，建立三所交叉校验、本地 7 天热缓存、到期清理并转存至 TianLu_Archive 外接高速硬盘的数据链路。  
> 用户确认：外挂高速硬盘为 `/Volumes/TianLu_Archive`。

---

## 一、总判断

M2 S/R 是入场和出场判断中的位置质量层。当前用户反馈 M2 数据采集一直存在问题，因此不能继续把 M2 当作“稳定证据源”直接参与实盘 A 档入场。

M2 必须先完成：

```text
三所采集 → 三所归一化 → 支撑/压力计算 → 三所交叉校验 → 质量评分 → 本地7天热缓存 → 到期归档到 TianLu_Archive → 再供 EntryDecisionGate / ExitDecisionGate 调用
```

在这个链路稳定前，M2 对交易系统的作用应为：

```text
A档入场必要条件之一，但不是单独触发条件；
M2数据异常时，EntryDecisionGate 必须降级为 B/C/D；
M2不能单独触发 force_entry / force_exit。
```

---

## 二、M2 S/R 正确职责

M2 不负责判断多空方向，而负责判断：

```text
当前位置是否适合入场；
当前位置是否接近强支撑/强压力；
当前突破是否可能是假突破；
当前止盈/止损是否被支撑/压力结构支持；
价格是否处于追高/追空位置。
```

M2 输出应服务于：

1. EntryDecisionGate：判断是否允许入场；
2. ExitDecisionGate：判断是否需要观察、部分止盈、全平复核；
3. 天眼AI：解释为什么可以/不可以入场；
4. 出山AI：解释为什么继续持有/观察/建议出场复核；
5. L5 Shadow：用于回测 S/R 参数质量，不直接写实盘。

---

## 三、三所交叉校验设计

三所来源：

```text
Gate
OKX
Binance
```

每个交易所各自计算一组 S/R：

```text
support_levels
resistance_levels
touch_count
volume_confirm
distance_pct
breakout_count
false_breakout_count
timeframe
updated_at
```

然后进入聚合层：

```text
sr_consensus_score
sr_divergence_score
sr_quality_score
dominant_exchange
exchange_outlier
valid_exchange_count
nearest_support
nearest_resistance
support_distance_pct
resistance_distance_pct
false_breakout_risk
structure_alignment
```

### 1. sr_consensus_score

含义：三所是否在相近价格区间识别出相同支撑/压力。

建议：

```text
>= 0.67：至少 2/3 交易所结构一致，可作为有效证据；
0.34 - 0.66：弱一致，只能观察；
< 0.34：分歧严重，禁止作为入场证据。
```

### 2. sr_divergence_score

含义：三所 S/R 位置差异是否过大。

建议：

```text
< 0.30：结构稳定；
0.30 - 0.60：结构分歧，降级；
>= 0.60：严重分歧，禁止入场。
```

### 3. sr_quality_score

计算建议：

```text
触碰次数权重 30%
三所一致性权重 30%
成交量确认权重 20%
假突破风险反向权重 20%
```

建议裁决：

```text
>= 80：强结构；
60-79：可观察结构；
40-59：弱结构；
< 40：无效结构。
```

---

## 四、M2 对 EntryDecisionGate 的接入规则

EntryDecisionGate 中，M2 只能作为位置质量门控。

建议规则：

```text
1. M2 数据缺失 → EntryDecisionGate = D 数据不足；
2. valid_exchange_count < 2 → EntryDecisionGate 不允许 A；
3. sr_consensus_score < 0.67 → 不允许 A；
4. sr_quality_score < 60 → 不允许 A；
5. 距离最近支撑/压力 > 1.2% → 不允许 A；
6. false_breakout_risk >= 0.60 → EntryDecisionGate = C 噪音禁止；
7. 单所异常 exchange_outlier = true → EntryDecisionGate = E 单所异常降权。
```

做多时：

```text
必须靠近支撑；
不能紧贴压力；
不能在假突破高风险区追多。
```

做空时：

```text
必须靠近压力；
不能紧贴支撑；
不能在假跌破高风险区追空。
```

---

## 五、M2 对 ExitDecisionGate 的接入规则

M2 进入出山AI时，不能单独触发全平。

建议规则：

```text
1. 接近强压力，多单进入 WATCH 或 PARTIAL_EXIT_REVIEW；
2. 接近强支撑，空单进入 WATCH 或 PARTIAL_EXIT_REVIEW；
3. 如果 M1/M3/M4 仍支持原趋势，只能观察，不能直接全平；
4. false_breakout_risk 高时，禁止因一次突破直接 force_exit；
5. 出场动作必须经过 ExitDecisionGate；
6. force_exit 默认人工确认。
```

---

## 六、本地 7 天热缓存设计

本地热缓存目录建议：

```text
~/freqtrade_console/cache/m2_sr/
├── gate/
├── okx/
├── binance/
├── aggregated/
└── manifests/
```

本地缓存保存 7 天，用于：

```text
快速读取；
EntryDecisionGate 实时裁决；
ExitDecisionGate 实时裁决；
天眼/出山AI话术解释；
L5 shadow 回测读取。
```

建议文件命名：

```text
{exchange}_{pair}_{timeframe}_{YYYYMMDDHHmm}.json
aggregated_{pair}_{timeframe}_{YYYYMMDDHHmm}.json
```

建议缓存字段：

```json
{
  "pair": "DOGE/USDT:USDT",
  "timeframe": "15m",
  "updated_at": 1740000000,
  "source_count": 3,
  "valid_exchange_count": 3,
  "support_levels": [],
  "resistance_levels": [],
  "nearest_support": null,
  "nearest_resistance": null,
  "support_distance_pct": null,
  "resistance_distance_pct": null,
  "touch_count": 0,
  "sr_consensus_score": 0.0,
  "sr_divergence_score": 0.0,
  "sr_quality_score": 0.0,
  "false_breakout_risk": 0.0,
  "exchange_outlier": null,
  "structure_alignment": "unknown",
  "decision_grade": "D"
}
```

---

## 七、7 天到期清理与转存至 TianLu_Archive

外接高速硬盘目标目录：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/
```

目录结构建议：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/
├── gate/
├── okx/
├── binance/
├── aggregated/
└── manifests/
```

转存策略：

```text
1. 本地缓存保留 7 天；
2. 超过 7 天的缓存先 rsync 到 TianLu_Archive；
3. rsync 成功并生成 manifest 后，才允许删除本地旧缓存；
4. 删除本地旧缓存前必须二次确认归档存在；
5. 不删除最近 7 天热缓存；
6. 不删除活跃写入中的文件；
7. 不将数据库原文推送 GitHub。
```

由于 APFS 外接卷已确认 Python pathlib / shutil 可能失败，因此必须使用 shell：

```bash
mkdir -p /Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR
rsync -a source/ target/
```

不要让 Python 直接对 `/Volumes/TianLu_Archive` 执行 pathlib.mkdir 或 shutil.copy2。

---

## 八、Claude 应生成的脚本草案

Claude 下一步只生成草案，不直接安装定时任务。

### 1. M2 采集健康检查脚本

```text
06_MAINTENANCE/check_m2_sr_health.sh
```

功能：

```text
检查三所最新 M2 缓存时间；
检查 valid_exchange_count；
检查 aggregated 输出；
检查最近 false_breakout_risk；
输出健康报告。
```

### 2. M2 归档脚本

```text
06_MAINTENANCE/archive_m2_sr_cache_to_tianlu_archive.sh
```

功能：

```text
查找本地 M2 缓存超过 7 天的文件；
rsync 到 TianLu_Archive；
生成 manifest；
确认成功后删除本地旧缓存；
记录日志。
```

### 3. LaunchAgent 草案

```text
06_MAINTENANCE/com.tianlu.m2-sr-cache-archive.plist.draft
```

建议：每天 03:40 执行一次。

注意：只生成草案，不安装。安装需用户确认。

---

## 九、Claude 多子代理分工

### 户部：M2 数据结构与三所校验

输出：

```text
M2_SR_THREE_EXCHANGE_SCHEMA.md
M2_SR_CONSENSUS_RULES.md
```

### 工部：缓存与归档脚本

输出：

```text
check_m2_sr_health.sh.draft
archive_m2_sr_cache_to_tianlu_archive.sh.draft
com.tianlu.m2-sr-cache-archive.plist.draft
```

### 天眼院：入场接入

输出：

```text
M2_ENTRY_GATE_INTEGRATION.md
```

### 出山院：出场接入

输出：

```text
M2_EXIT_GATE_INTEGRATION.md
```

### 都察院：QA

输出：

```text
M2_SR_QA_CHECKLIST.md
```

---

## 十、Claude 下一步输出目录

Claude 应创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_THREE_EXCHANGE_CACHE_PLAN/
```

必须包含：

```text
00_M2_SR_MASTER_PLAN.md
01_M2_SR_THREE_EXCHANGE_SCHEMA.md
02_M2_SR_CONSENSUS_RULES.md
03_M2_ENTRY_GATE_INTEGRATION.md
04_M2_EXIT_GATE_INTEGRATION.md
05_M2_CACHE_7DAY_ARCHIVE_PLAN.md
06_CHECK_M2_SR_HEALTH_SCRIPT_DRAFT.md
07_ARCHIVE_M2_SR_CACHE_SCRIPT_DRAFT.md
08_LAUNCHAGENT_DRAFT.md
09_M2_SR_QA_CHECKLIST.md
REVIEW_PACKAGE.zip
```

---

## 十一、禁止事项

Claude 本轮不得：

1. 不直接修改实盘策略；
2. 不删除 M2 旧缓存；
3. 不移动 live cache；
4. 不安装 LaunchAgent；
5. 不重启 9090-9097 / 8081-8084；
6. 不调用交易所交易 API；
7. 不执行 force_entry / force_exit；
8. 不把数据库原文、密钥、日志原文推送 GitHub。

---

## 十二、给 Claude 的直接执行话术

```text
你现在执行 M2 S/R 三所交叉校验与二级缓存归档设计任务。

用户确认：M2 S/R 数据采集一直存在问题。系统采用三所交叉校验和二级缓存采集。本地热缓存保留7天，到期后归档到 /Volumes/TianLu_Archive 高速硬盘。

本轮只允许生成设计、脚本草案、QA 和 REVIEW_PACKAGE，不直接修改实盘策略，不删除旧缓存，不安装 LaunchAgent。

请通过户部、工部、天眼院、出山院、都察院多子代理协作完成，并输出到：
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_THREE_EXCHANGE_CACHE_PLAN/
```
