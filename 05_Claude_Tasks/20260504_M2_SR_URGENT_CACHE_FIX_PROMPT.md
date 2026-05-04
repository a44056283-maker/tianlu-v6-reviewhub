# Claude 紧急任务：修复 M2 S/R 页面旧缓存/假实时数据问题

> 生成方：GPT / 架构师审核员  
> 日期：2026-05-04  
> 状态：给 Claude Code 立即执行  
> 目标：快速修复 M2 S/R 页面连续多天显示相同数据、像模拟数据/旧缓存的问题。  
> 高速硬盘：`/Volumes/TianLu_Archive`  

---

## 一、当前故障现象

用户反馈：

```text
M2 S/R 网页端数据连续近三天都一样，不管交易对上涨还是下跌，支撑/压力位显示都不变，看起来像模拟数据或死缓存。
```

GPT 审计判断：

```text
这不是单纯 UI 问题，而是 M2 后端接口、缓存回退、前端刷新和实时价格重算链路共同导致。
```

---

## 二、已确认的核心根因

### 根因 1：前端默认不强制刷新

M2 页面默认请求：

```text
/api/bt2/sr_levels
```

只有在 levels 缺失时才请求：

```text
/api/bt2/sr_levels?force_live=1
```

如果旧缓存结构完整但数据过期，前端仍会认为可用。

### 根因 2：后端普通模式只读缓存

`/api/bt2/sr_levels` 非 `force_live` 时优先读缓存或 fallback，不会主动调用 `compute_and_cache_triple(pair)` 重算。

### 根因 3：L1/L1.5/L2 缓存链路断裂

当前疑似情况：

```text
L1 缓存过期；
L1.5 温缓存为空；
L2 外接盘缓存未正确接入；
旧路径仍可能指向 /Volumes/TianLu_Storage；
真实高速硬盘应为 /Volumes/TianLu_Archive。
```

### 根因 4：前端覆盖实时 current_price 后没有重算距离

天眼/出山AI可能提供了新价格，但页面未重新计算：

```text
nearest_support
nearest_resistance
support_distance_pct
resistance_distance_pct
```

导致显示为“新价格 + 旧支撑压力”。

---

## 三、本次任务目标

请立即执行 M2 S/R 紧急修复，但遵守安全边界。

目标：

1. 清理顽固 M2 旧缓存，但不能直接删除；
2. 先归档旧缓存到 TianLu_Archive，再清理本地过期缓存；
3. 修复 `/api/bt2/sr_levels` 的过期缓存逻辑；
4. 让缓存过期时自动重算；
5. fallback 必须明确标记为 stale/fallback，不能伪装成实时三所数据；
6. 修复前端过期判断与实时价格重算；
7. 输出修复报告和回滚方案；
8. 推送 GitHub 等 GPT 审核。

---

## 四、绝对禁止

本轮不得：

```text
1. 不修改实盘交易策略；
2. 不重启 9090-9097 / 8081-8084 交易机器人；
3. 不调用交易所下单 API；
4. 不执行 force_entry / force_exit；
5. 不删除未归档的 live cache；
6. 不直接 rm -rf 整个 cache 目录；
7. 不把数据库原文、密钥、日志原文推送 GitHub；
8. 不安装 LaunchAgent；
9. 不移动正在写入的数据库文件。
```

---

## 五、允许做的事情

允许：

```text
1. 读取 M2 相关代码；
2. 备份 M2 页面和后端接口文件；
3. 将旧缓存 rsync 归档到 TianLu_Archive；
4. 清理本地过期 M2 缓存文件，但必须保留最近 7 天热缓存；
5. 修改 M2 前端和后端补丁草案；
6. 运行 py_compile / JSON 校验；
7. 运行只读或 force_live 的 M2 计算验证；
8. 生成 PATCH.diff / TEST_LOG / ROLLBACK_PLAN；
9. 推送 GitHub。
```

---

## 六、多子代理分工

### 1. 中书省 · 总协调

创建任务目录、分配任务、收集结果、生成总报告、打包 REVIEW_PACKAGE。

输出：

```text
00_M2_SR_URGENT_FIX_SUMMARY.md
```

### 2. 户部 · 数据链路代理

检查 M2 数据源、缓存年龄、三所数据是否真实更新。

输出：

```text
01_M2_SR_DATA_SOURCE_AUDIT.md
```

### 3. 工部 · 后端补丁代理

修复 `/api/bt2/sr_levels` 与 `m2_sr_enhanced.py` 的缓存刷新逻辑。

输出：

```text
02_M2_BACKEND_REFRESH_PATCH.md
```

### 4. 前端院 · UI 补丁代理

修复 m2_sr.html：过期判断、force_live 触发、实时价格覆盖后重算 S/R 距离、展示 data_status/cache_age。

输出：

```text
03_M2_FRONTEND_STALE_CACHE_PATCH.md
```

### 5. 仓储院 · 缓存归档代理

负责将顽固旧缓存归档到 TianLu_Archive，再安全清理本地过期缓存。

输出：

```text
04_M2_CACHE_ARCHIVE_AND_CLEAN_REPORT.md
```

### 6. 都察院 · QA 代理

负责验证没有删除 live 数据、没有重启机器人、没有触发交易、补丁可回滚。

输出：

```text
05_M2_SR_QA_CHECKLIST.md
```

---

## 七、执行目录

创建目录：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_M2_SR_URGENT_CACHE_FIX/
```

必须包含：

```text
00_M2_SR_URGENT_FIX_SUMMARY.md
01_M2_SR_DATA_SOURCE_AUDIT.md
02_M2_BACKEND_REFRESH_PATCH.md
03_M2_FRONTEND_STALE_CACHE_PATCH.md
04_M2_CACHE_ARCHIVE_AND_CLEAN_REPORT.md
05_M2_SR_QA_CHECKLIST.md
PATCH.diff
TEST_LOG.md
ROLLBACK_PLAN.md
REVIEW_PACKAGE.zip
```

---

## 八、必须先备份

备份目录：

```text
~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/m2_sr_urgent_fix_时间戳/
```

至少备份：

```text
m2_sr.html
console_server.py
m2_sr_enhanced.py
M2/SR 相关 cache manifest
```

不要备份完整数据库到 GitHub。

---

## 九、顽固缓存处理规则

必须按这个顺序处理，不允许直接删除。

### 第一步：定位 M2 缓存目录

检查：

```bash
find ~/freqtrade_console -maxdepth 5 -type d | grep -Ei 'm2|sr|support|resistance|cache'
find /tmp/tianlu_cache -maxdepth 4 -type d 2>/dev/null | grep -Ei 'sr|m2'
find /Volumes/TianLu_Archive -maxdepth 5 -type d 2>/dev/null | grep -Ei 'sr|m2|Tianlu_V6_5_DataVault'
```

### 第二步：归档旧缓存

目标目录：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/stale_cache_archive/时间戳/
```

使用：

```bash
mkdir -p "$ARCHIVE_DIR"
rsync -a "$SRC_CACHE_DIR/" "$ARCHIVE_DIR/"
```

### 第三步：生成 manifest

manifest 必须记录：

```text
源目录
目标目录
文件数量
最老文件时间
最新文件时间
是否删除本地旧缓存
```

### 第四步：清理本地过期缓存

只允许清理：

```text
超过 7 天的 M2/SR 缓存文件；
确认已归档成功的文件；
非 live sqlite/db 文件；
非当前写入文件。
```

禁止：

```text
rm -rf 整个 cache；
删除最近7天热缓存；
删除 live db；
删除未归档文件。
```

---

## 十、后端补丁要求

### P0：修 `/api/bt2/sr_levels`

逻辑要求：

```text
1. memory cache 只允许短 TTL；
2. L1 未过期才直接返回；
3. L1 过期必须触发 compute_and_cache_triple(pair)；
4. compute 成功返回新数据；
5. compute 失败才 fallback；
6. fallback 必须标记 data_status=fallback 或 stale；
7. 不允许 fallback 伪装成 m2_triple_primary；
8. 响应必须包含 timestamp/cache_age_sec/source/data_status/force_live_used。
```

### P1：统一外接缓存路径

外接缓存必须指向：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/
```

不得继续默认指向：

```text
/Volumes/TianLu_Storage/tianlu_cache/sr_levels
```

---

## 十一、前端补丁要求

### m2_sr.html 必须新增：

```text
_m2PayloadIsStale(rawPairs)
_recomputeM2AfterPriceUpdate(pair)
```

触发条件：

```text
cache_age_sec > 7200
或 data_status in [cached_stale, stale, fallback]
或 timestamp 超过 2 小时
或 source 缺失
```

如果过期：

```text
自动请求 /api/bt2/sr_levels?force_live=1
```

实时价格覆盖后必须重算：

```text
nearest_support
nearest_resistance
support_distance_pct
resistance_distance_pct
```

页面必须显示：

```text
source
data_status
timestamp
cache_age_sec
force_live_used
valid_exchange_count
sr_consensus_score
sr_quality_score
```

---

## 十二、测试要求

必须执行：

```bash
python3 -m py_compile ~/freqtrade_console/console_server.py
python3 -m py_compile ~/freqtrade_console/l5_evolution_lab/m2_sr_enhanced.py 2>/dev/null || true
```

如果实际路径不同，报告中写明。

必须执行：

```bash
curl -s 'http://127.0.0.1:9099/api/bt2/sr_levels?force_live=1' | head
curl -s 'http://127.0.0.1:9099/api/bt2/sr_levels' | head
```

不调用交易所下单 API。

---

## 十三、交付后结论必须回答

总报告必须回答：

```text
1. M2 页面是否真的用了旧缓存？
2. 顽固缓存文件在哪里？
3. 是否已归档到 TianLu_Archive？
4. 是否安全清理了过期本地缓存？
5. /api/bt2/sr_levels 是否会在过期时强制重算？
6. fallback 是否明确标记 stale/fallback？
7. 前端是否会显示 cache_age_sec/data_status？
8. 实时价格覆盖后是否会重新计算 S/R 距离？
9. 是否需要重启 console_server？
10. 如何回滚？
```

---

## 十四、给 Claude 的直接执行话术

```text
你现在立即执行 M2 S/R 紧急缓存修复任务。

目标：解决 M2 S/R 网页端连续多天显示相同旧数据、像模拟数据的问题。

先按 GPT 任务书执行：
1. 备份 m2_sr.html、console_server.py、m2_sr_enhanced.py；
2. 定位 M2/SR 顽固旧缓存；
3. 先 rsync 归档到 /Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/M2_SR/；
4. 只清理已归档且超过7天的本地旧缓存；
5. 修复 /api/bt2/sr_levels 过期缓存策略；
6. 修复前端 stale 判断与实时价格重算；
7. 输出 PATCH.diff、TEST_LOG、ROLLBACK_PLAN；
8. 不重启交易机器人；
9. 不调用交易所交易 API；
10. 完成后 push GitHub 等 GPT 审核。
```
