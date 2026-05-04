# TianLu_Archive 高速硬盘统一 DataVault 计划

> 日期：2026-05-04  
> 用户确认：`/Volumes/TianLu_Archive` 是高速硬盘。后续备份数据、采集数据、归档数据统一以该硬盘为主数据仓。  
> 执行原则：先检查、先建目录、先复制验证、再切换路径；不得删除旧数据。

---

## 1. 目标

将天禄 V6.5 的备份数据和采集归档数据统一指向：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/
```

注意：正在运行中的热数据、数据库和实时缓存，不允许直接搬迁。必须先以“本地生成 + rsync 同步到 TianLu_Archive”的方式运行稳定后，再考虑切换 live path。

---

## 2. 标准目录

Claude 先建立以下目录：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/
├── 00_HEALTHCHECK/
├── 01_TRADING_PARAMS_BACKUP/
├── 02_OPENCLAW_CONFIG_BACKUP/
├── 03_M1_M5_CACHE_ARCHIVE/
│   ├── M1/
│   ├── M2/
│   ├── M3/
│   ├── M4/
│   ├── M5/
│   └── L5/
├── 04_L5_MARKET_DATA/
│   ├── orderbook/
│   ├── open_interest/
│   ├── liquidations/
│   ├── funding_rate/
│   ├── fear_greed/
│   └── taker_flow/
├── 05_BACKTEST_REPORTS/
├── 06_DAILY_REPORTS/
├── 07_REVIEW_HUB_MIRROR/
├── 08_LOG_ARCHIVE/
└── 99_MANIFESTS/
```

---

## 3. 关键技术约束

前序审计已确认：

```text
Python pathlib.mkdir 写外接卷失败
Python shutil.copy2 写外接卷失败
shell mkdir 成功
rsync 成功
```

因此后续凡是写入 `/Volumes/TianLu_Archive`，统一使用：

```bash
mkdir -p
rsync -a
```

Python 脚本中如果需要写外接盘，必须通过 `subprocess.run(['mkdir','-p', ...])` 和 `subprocess.run(['rsync','-a', ...])`，不再直接用 pathlib 或 shutil 写目标盘。

SQLite 或活跃数据库必须先在本地生成一致性快照，再同步到外接盘。

---

## 4. 执行阶段

### Phase 0：健康检查

只读检查：

1. `/Volumes/TianLu_Archive` 是否挂载；
2. 可用空间；
3. 当前用户是否可写；
4. `mkdir -p` 是否成功；
5. `rsync -a` 是否成功；
6. Python 文件操作是否仍失败；
7. 旧目录 `/Volumes/TianLu_Archive/tianlu_archive/` 是否需要兼容保留。

输出：

```text
05_Claude_Tasks/TIANLU_ARCHIVE_HEALTHCHECK_REPORT.md
```

### Phase 1：建立 DataVault 目录

允许 Claude 创建标准目录，但不得移动旧数据。

输出：

```text
05_Claude_Tasks/TIANLU_ARCHIVE_DATAVAULT_STRUCTURE.md
```

### Phase 2：交易参数备份切换

目标：先本地 staging，再 rsync 到：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/01_TRADING_PARAMS_BACKUP/
```

输出：

```text
05_Claude_Tasks/TRADING_PARAMS_BACKUP_TO_ARCHIVE_PLAN.md
```

### Phase 3：OpenClaw 配置备份切换

目标：OpenClaw 配置备份归档到：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/02_OPENCLAW_CONFIG_BACKUP/
```

要求脱敏，不备份真实密钥到 GitHub。

输出：

```text
05_Claude_Tasks/OPENCLAW_BACKUP_TO_ARCHIVE_PLAN.md
```

### Phase 4：M1-M5 缓存归档切换

目标：M1-M5 二级缓存归档到：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/03_M1_M5_CACHE_ARCHIVE/
```

不移动 live cache，只做归档同步。

输出：

```text
05_Claude_Tasks/M1_M5_CACHE_ARCHIVE_TO_TIANLU_ARCHIVE_PLAN.md
```

### Phase 5：L5 市场数据归档切换

目标：L5 orderbook、open_interest、liquidations、funding、fear_greed 等采集归档到：

```text
/Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/04_L5_MARKET_DATA/
```

输出：

```text
05_Claude_Tasks/L5_MARKET_DATA_TO_ARCHIVE_PLAN.md
```

---

## 5. 本轮 Claude 只允许先执行

```text
Phase 0 + Phase 1
```

也就是：检查硬盘，建立目录，生成报告。

暂不允许直接切换脚本路径，暂不允许移动旧数据，暂不允许安装新的定时任务。

---

## 6. 给 Claude 的直接提示词

```text
你现在执行 TianLu_Archive 高速硬盘统一 DataVault 计划。

用户确认：/Volumes/TianLu_Archive 是高速硬盘。后续备份数据、采集数据和归档数据统一以这个硬盘为主数据仓。

本轮只执行 Phase 0 和 Phase 1：
1. 检查 /Volumes/TianLu_Archive 是否稳定挂载；
2. 检查可用空间和写入权限；
3. 测试 shell mkdir 和 rsync；
4. 测试 Python pathlib/shutil 是否仍失败；
5. 建立 /Volumes/TianLu_Archive/Tianlu_V6_5_DataVault/ 标准目录；
6. 生成健康检查报告和目录结构报告；
7. 不移动旧数据；
8. 不删除任何数据；
9. 不切换现有脚本路径；
10. 不安装新的定时任务。

完成后 push 到 GitHub：
05_Claude_Tasks/TIANLU_ARCHIVE_HEALTHCHECK_REPORT.md
05_Claude_Tasks/TIANLU_ARCHIVE_DATAVAULT_STRUCTURE.md
```
