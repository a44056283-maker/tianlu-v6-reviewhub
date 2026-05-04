# 天禄 V6.5 数据缓存与每日备份链路审计报告

> 审计时间：2026-05-04 12:36
> 审计类型：只读，不修改任何配置

---

## 核心发现摘要

| 问题 | 状态 | 根因 |
|------|------|------|
| M1-M5 缓存二级转存外接硬盘 | 🔴 失效 | macOS APFS 同卷复制权限限制 |
| 每日交易系统参数备份 | ⚠️ 存疑 | 日志文件为空，无法确认是否成功 |
| 每日 OpenClaw 参数备份 | ⚠️ 无 LaunchAgent | 仅有 cron，无独立备份脚本 |

---

## 一、外接硬盘挂载状态

✅ **两个外接硬盘均已挂载且健康**

| 硬盘 | 容量 | 已用 | 可用 | 状态 |
|------|------|------|------|------|
| `/Volumes/TianLu_Storage` | 954GB | 75GB | 878GB | ✅ 正常 |
| `/Volumes/TianLu_Archive` | 954GB | 748MB | 953GB | ✅ 正常 |

- 挂载稳定，非临时挂载
- 两个硬盘均已正确挂载，**不是硬盘未挂载导致的问题**

---

## 二、M1-M5 缓存现状

### 原始缓存目录（本地）

| 缓存 | 路径 | 最新更新时间 | 状态 |
|------|------|------------|------|
| M1 | `~/freqtrade_console/m1_cache.db` | 2026-05-04 12:41 | ✅ 活跃 |
| M3 | `~/freqtrade_console/m3_cache.db` | 2026-05-03 11:16 | ✅ 活跃 |
| M4 | `~/freqtrade_console/m4_cache.db` | 2026-05-04 09:37 | ✅ 活跃 |
| M5 | `~/freqtrade_console/l5_evolution_lab/m4_m5_shadow_lab.sqlite` | 2026-05-04 12:34 | ✅ 活跃 |
| L5 清算/恐惧贪婪/持仓数据 | `~/freqtrade_console/cache/l5/` | **2026-04-30 00:21** | ⚠️ 5天未更新 |

### 二级缓存目标目录（外接硬盘）

| 目录 | 硬盘 | 状态 |
|------|------|------|
| `/Volumes/TianLu_Archive/tianlu_archive/backtest_reports/` | TianLu_Archive | ✅ 存在 |
| `/Volumes/TianLu_Archive/tianlu_archive/m1_m5_cold_data/` | TianLu_Archive | ✅ 存在 |
| `/Volumes/TianLu_Storage/tianlu_cache/` | TianLu_Storage | ✅ 存在（有内容）|

### M1-M5 二级缓存转存脚本

| 脚本 | 路径 | 状态 |
|------|------|------|
| `tianlu_cache_maintenance.py` | `~/freqtrade_console/scripts/` | 🔴 失效（每小时运行，持续报错）|

---

## 三、根因分析

### 🔴 根因 1：macOS APFS 同卷复制权限限制

**错误信息：**
```
PermissionError: [Errno 1] Operation not permitted:
'/Volumes/TianLu_Archive/tianlu_archive/backtest_reports/bt_tools_reports/bt_report_*.json.tmp'
```

**分析：**
- `tianlu_cache_maintenance.py` 试图在 `/Volumes/TianLu_Archive/` 内部复制文件
- macOS APFS 对同卷复制（same-volume copy）有安全限制，`shutil.copy2()` 会触发 `Operation not permitted`
- 这是 macOS 系统级限制，脚本无法绕过，必须改用硬链接（hardlink）或 `cp -la` 替代 `shutil.copy2()`

### ⚠️ 根因 2：每日设置备份日志为空

- `com.tianlu.daily-settings-backup.plist` → 每天 03:10 执行
- 日志文件：`/tmp/tianlu_daily_settings_backup.log` → **0 字节**
- 无法确认脚本是否成功运行，也可能是日志被截断

### ⚠️ 根因 3：OpenClaw 每日参数备份缺失

- 仅发现 cron：`0 23 * * * ~/.openclaw/scripts/daily_sync_learning.sh`（同步学习记忆，非参数备份）
- 无独立 OpenClaw 配置备份 LaunchAgent
- OpenClaw 参数在上次 OpenClaw fix 时已手动备份，但无定期自动化

### ⚠️ 根因 4：L5 清算/恐惧贪婪数据 5 天未更新

- `cache/l5/liquidations/ETH_USDT.json` 等 → 最后更新 2026-04-30 00:21
- 可能与 OpenClaw 通讯故障期间采集程序中断有关

---

## 四、定时任务链路

### LaunchAgents（相关备份类）

| 服务 | 调度 | 脚本 | 状态 |
|------|------|------|------|
| `com.tianlu.daily-settings-backup` | 03:10 每日 | `tianlu_system_backup.py --mode daily-settings` | ⚠️ 日志为空 |
| `com.tianlu.weekly-full-backup` | 周一 04:10 | `tianlu_system_backup.py --mode weekly-full` | ⚠️ 日志为空 |
| `com.tianlu.cache-maintenance` | 每小时 | `tianlu_cache_maintenance.py` | 🔴 持续报错 |
| `com.tianlu.l5-m4m5-shadow-collector` | 每15分钟 | `m4_m5_shadow_lab.py run-once` | ✅ 运行中 |
| `com.tianlu.l5-m4m5-shadow-daily-report` | 09:15 每日 | `m4_m5_shadow_lab.py send-report` | ✅ 运行中 |

### Cron（相关）

| 调度 | 命令 | 状态 |
|------|------|------|
| 23:00 每日 | `~/.openclaw/scripts/daily_sync_learning.sh` | ⚠️ 非参数备份 |
| 15分钟 | `m4_m5_shadow_lab.py run-once` | ✅ 等同 LA |
| 09:05 每日 | `m4_m5_shadow_lab.py send-report` | ✅ 等同 LA |

---

## 五、现有备份文件位置

### 交易系统备份
- 主备份：`~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/`（最近：2026-05-02）
- 外接硬盘：`/Volumes/TianLu_Storage/V65_*_备份*/`
- TianLu_Archive：`/Volumes/TianLu_Archive/tianlu_archive/system_backups/`

### OpenClaw 备份
- 手动备份：`~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/openclaw_minimax_unified_fix_*/`（2026-05-04）
- OpenClaw-Backups：`~/OpenClaw-Backups/`（多个版本快照）

---

## 六、绝对禁止修改项（GPT 审计确认）

1. 不修改 `~/freqtrade` 交易策略
2. 不修改 9090-9097 / 8081-8084 机器人配置
3. 不启动/停止/重启交易机器人
4. 不调用交易所 API
5. 不执行 force_entry / force_exit
6. 不删除任何缓存
7. 不移动任何真实缓存
8. 不覆盖任何备份
9. 不打印真实 API key / secret / token / password
10. 不修改 LaunchAgents 或 crontab（修复阶段除外，需用户确认）

---

## 七、修复方案（三选一）

### A. 保守方案 ✅ 推荐先执行
只修复每日备份，不动外接硬盘二级缓存。

**修复内容：**
1. 确认 `tianlu_system_backup.py --mode daily-settings` 能正常运行
2. 创建 `backup_openclaw_daily.sh` + LaunchAgent（每日 04:00）
3. 验证备份日志有实际输出

### B. 推荐方案
保守方案 + 修复 `tianlu_cache_maintenance.py` 的 APFS 权限问题（改用硬链接）

**修复内容：**
1. 保守方案全部内容
2. 将 `shutil.copy2()` 替换为 `os.link()`（硬链接，同卷有效）
3. 修复 L5 清算数据采集（可能需要重启采集进程）

### C. 完整方案
推荐方案 + 建立完整 DataVault 结构

**目录结构：**
```
/Volumes/TianLu_Storage/Tianlu_V6_5_DataVault/
├── M1_M5_CACHE_ARCHIVE/      ← 二级缓存
├── TRADING_PARAMS_BACKUP/     ← 每日交易参数
├── OPENCLAW_CONFIG_BACKUP/   ← 每日 OpenClaw 配置
├── REVIEWHUB_MIRROR/         ← GitHub review hub 本地镜像
└── DAILY_REPORTS/            ← 每日报告归档
```

---

## 八、建议执行顺序

```
第一步（立即）：确认外接硬盘路径稳定 → 已确认稳定 ✅
第二步（保守）：验证 daily-settings-backup 是否真正在运行
第三步（推荐）：创建 OpenClaw 每日备份 LaunchAgent
第四步（推荐）：修复 tianlu_cache_maintenance.py 的 APFS 硬链接问题
第五步（可选）：恢复 L5 清算数据采集
第六步（可选）：建立完整 DataVault 目录结构
```

---

## 九、是否建议进入修复阶段

**是，但按顺序执行：**

1. **先确认** `tianlu_system_backup.py --mode daily-settings` 能否单独运行成功（手动执行一次看日志）
2. **再创建** OpenClaw 每日备份脚本 + LaunchAgent
3. **最后修复** `tianlu_cache_maintenance.py` 的 APFS 问题（不急，外接硬盘有878GB可用）

---

## 十、给 GPT 的审核问题

1. macOS APFS 同卷硬链接限制是否有其他绕过方案（除 `os.link()` 外）？
2. `tianlu_system_backup.py` 日志为空的最可能原因？
3. L5 清算数据 5 天未更新是否需要重启采集进程？

---

*审计结论：基础设施链路存在但有两处失效，无硬盘挂载问题，优先修复备份脚本和 OpenClaw 每日备份*
