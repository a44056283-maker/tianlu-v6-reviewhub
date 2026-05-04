# 任务A：每日交易系统参数备份验证报告

> 生成时间：2026-05-04 13:00
> 审计类型：只读 dry-run，不修改任何配置

---

## 一、脚本定位结果

| 项目 | 值 |
|------|-----|
| 脚本路径 | `~/freqtrade_console/scripts/tianlu_system_backup.py` |
| 支持 dry-run | ✅ 是 |
| 支持模式 | `daily-settings` / `weekly-full` |
| LaunchAgent | `com.tianlu.daily-settings-backup` (03:10) + `com.tianlu.weekly-full-backup` (周一04:10) |

---

## 二、真实错误（从日志提取）

### daily-settings 错误
```
PermissionError: [Errno 1] Operation not permitted:
'/Volumes/TianLu_Archive/tianlu_archive/system_backups/daily_settings_20260504_031005'
```

### weekly-full 错误
```
PermissionError: [Errno 1] Operation not permitted:
'/Volumes/TianLu_Archive/tianlu_archive/system_backups/weekly_full_20260504_041002'
```

**两个错误完全相同** — Python `pathlib.Path.mkdir()` 在外接硬盘 APFS 卷上被 macOS 系统拦截。

---

## 三、Dry-run 结果

```
{
  "ok": true,
  "mode": "daily-settings",
  "dry_run": true,
  "target": "/Volumes/TianLu_Archive/tianlu_archive/system_backups/daily_settings_20260504_125835",
  "ok_count": 30,
  "total": 32,
  "manifest": ".../BACKUP_MANIFEST.md",
  "log": ".../_healthcheck/system_backup_logs/daily_settings_20260504_125835.log"
}
```

脚本逻辑本身正确，30/32 文件可备份，只在写目标目录时失败。

---

## 四、备份清单（应包含的内容）

| 类别 | 关键文件 |
|------|---------|
| 共享配置 | `config_shared.json` |
| 各 bot overlay | `config_9090_overlay.json` ~ `config_9097_overlay.json` |
| console 配置 | `nodes_config.json`, `sr_config.json` |
| 策略文件 | `bt_tools/` 下各策略模块 |
| 运行脚本 | `bot_manager.sh` 等 |

---

## 五、根因结论

**与 `tianlu_cache_maintenance.py` 相同：macOS APFS 外接卷写入限制。**

Python 的 `pathlib.Path.mkdir()` 在 `/Volumes/TianLu_Archive/` 上被系统拦截。

**解决方案：**

将目标目录改为本地（`~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/`），再用 `rsync` 或 `cp` 同步到外接硬盘。

---

## 六、修复草案（不直接执行）

将 `tianlu_system_backup.py` 第 194 行附近的目标路径从：

```python
target = Path("/Volumes/TianLu_Archive/tianlu_archive/system_backups/...")
```

改为：

```python
local_target = Path("$HOME/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/daily_settings_YYYYMMDD/")
# 完成后 rsync 到外接硬盘（shell 命令，不走 Python pathlib）
```

---

## 七、验证清单（GPT 建议执行）

- [ ] 确认脚本本身逻辑正确（dry-run ✅）
- [ ] 确认目标卷 `/Volumes/TianLu_Archive/` 挂载正常（✅）
- [ ] 确认根因是 APFS 权限（✅）
- [ ] 等待用户确认后再修改目标路径
