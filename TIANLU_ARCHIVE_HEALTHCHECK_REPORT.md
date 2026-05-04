# TianLu_Archive 健康检查报告

> 检查时间：2026-05-04 13:48
> Phase 0，仅读检查，未修改任何数据

---

## 一、挂载状态

| 项目 | 结果 |
|------|------|
| 挂载点 | `/Volumes/TianLu_Archive` |
| 设备 | `/dev/disk7s1` (1TB Apple_APFS) |
| 状态 | ✅ 稳定挂载 |
| 挂载时间 | 2026-05-04 09:03 |

---

## 二、空间状态

| 项目 | 值 |
|------|-----|
| 总容量 | 954GB |
| 已用 | 750MB |
| 可用 | **953GB** |
| 使用率 | 1% |

✅ 空间充裕，足够多年备份需求。

---

## 三、写入测试结果

| 测试项 | 方法 | 结果 | 说明 |
|--------|------|------|------|
| 创建目录 | shell `mkdir` | ✅ 成功 | 标准 Unix 权限 |
| 文件同步 | `rsync -a` | ✅ 成功 | 保留时间戳 |
| Python mkdir | `pathlib.Path.mkdir()` | ✅ 成功 | 直接可写 |
| Python copy2 | `shutil.copy2()` | ✅ 成功 | 直接可写 |

**结论：Python 现在可以直接写入 `/Volumes/TianLu_Archive/` 根目录。**

---

## 四、关键发现：Python 在子目录写入的历史错误

### 历史错误回顾
```
# 错误1: tianlu_system_backup.py
PermissionError: [Errno 1] Operation not permitted:
'/Volumes/TianLu_Archive/tianlu_archive/system_backups/daily_settings_20260504_031005'
  → Python pathlib mkdir in tianlu_archive/system_backups/

# 错误2: tianlu_cache_maintenance.py
PermissionError: [Errno 1] Operation not permitted:
'/Volumes/TianLu_Archive/tianlu_archive/backtest_reports/bt_tools_reports/bt_report_*.json.tmp'
  → Python shutil.copy2 in tianlu_archive/backtest_reports/
```

### 可能原因分析

| 可能原因 | 证据 | 结论 |
|---------|------|------|
| 子目录有 immutable flag | `ls -laOd` 显示无 `uchg` | ❌ 不成立 |
| launchd 以 root 运行写入用户目录 | daily backup LA 无 `UserName` | ⚠️ 可能 |
| Apple System Integrity Protection | 只有 /System 可用 | ❌ 不适用 |
| 子目录被占用/锁定 | `.tmp` 文件被其他进程持有 | ⚠️ 可能 |

### 根因最可能：launchd 以 root 权限写入但目录属于 luxiangnan

daily-settings-backup LaunchAgent 的 `ProgramArguments` 没有 `UserName` 字段，launchd 可能以 root 身份执行，写入时触发 APFS 权限检查。

**但当前测试显示 Python 可以直接写入，说明问题可能是特定的执行上下文导致的。**

---

## 五、现有目录结构

```
/Volumes/TianLu_Archive/
├── tianlu_archive/              (352MB)
│   ├── _healthcheck/
│   ├── backtest_reports/       ⚠️ 写入历史报错
│   ├── l5_replay_samples/
│   ├── m1_m5_cold_data/
│   ├── ohlcv_history/
│   ├── system_backups/         ⚠️ 写入历史报错
│   └── trade_logs/
├── Knowledge_Strategy_Base/    (284MB)
└── 其他文件
```

---

## 六、Phase 1 准备确认

| 检查项 | 状态 |
|--------|------|
| `/Volumes/TianLu_Archive` 可写 | ✅ |
| 可用空间 953GB | ✅ |
| shell mkdir 成功 | ✅ |
| rsync 成功 | ✅ |
| Python pathlib 可写 | ✅ |
| Python shutil 可写 | ✅ |
| 建议建立 DataVault 目录 | ✅ 可执行 |

---

## 七、建议

1. **立即执行 Phase 1**：建立标准 DataVault 目录
2. **监控 Phase 2**：交易参数备份脚本重新指向新目录后，验证 Python 写入成功
3. **根因**：历史错误可能是 launchd 以 root 身份执行导致，后续验证备份脚本时注意 `UserName` 字段
4. **安全**：备份脚本应明确 `UserName: luxiangnan`，避免权限问题
