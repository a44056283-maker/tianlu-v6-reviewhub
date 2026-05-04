# GPT_审核建议 · 20260504_123605_CACHE_BACKUP_AUDIT

## 审核结论

**有条件通过。**

Claude 的缓存与备份链路审计有效，已经定位出三条关键问题链路：

1. M1/M3/M4/M5 本地缓存仍在活跃写入；
2. L5 清算/恐惧贪婪/持仓类数据约 5 天未更新；
3. 二级缓存转存外接硬盘失效，疑似由 `tianlu_cache_maintenance.py` 中的 `shutil.copy2()` 在 macOS APFS 同卷/外接卷安全策略下触发 `Operation not permitted`；
4. 每日交易系统参数备份日志为空，不能确认真实执行成功；
5. OpenClaw 每日参数备份缺少独立 LaunchAgent。

当前可以进入修复阶段，但必须按“小步、可回滚、先 dry-run 后应用”的方式执行，不允许一次性重构缓存系统或删除旧缓存。

---

## 一、必须整改项

### P0-1：先验证每日交易系统参数备份是否真实可用

当前 `com.tianlu.daily-settings-backup` 存在，但 `/tmp/tianlu_daily_settings_backup.log` 为 0 字节，无法证明备份成功。

Claude 下一步先执行手动 dry-run 验证，不要立即改 LaunchAgent。

要求：

1. 定位 `tianlu_system_backup.py` 真实路径；
2. 手动执行：
   `python3 tianlu_system_backup.py --mode daily-settings --dry-run`，如果脚本不支持 dry-run，则先运行 help 或只读模式；
3. 若确认安全，再执行一次真实备份，但必须输出到新的测试目录；
4. 检查备份产物是否包含：
   - `config_shared.json`
   - `config_909*_overlay.json`
   - runtime params
   - bot_manager.sh
   - console 关键配置
5. 修正日志输出，让日志不再为空。

输出：

`TRADING_PARAMS_DAILY_BACKUP_VERIFY_REPORT.md`

---

### P0-2：建立 OpenClaw 每日参数备份脚本，但先不要装 LaunchAgent

当前只有 `~/.openclaw/scripts/daily_sync_learning.sh`，这是学习/记忆同步，不是 OpenClaw 参数备份。

Claude 应先生成脚本：

`~/Desktop/Tianlu_V6_5_Workspace/06_MAINTENANCE/backup_openclaw_daily.sh`

备份范围：

- `~/.openclaw/openclaw.json`
- `~/.openclaw/agents/*/agent/models.json`
- `~/.openclaw/agents/*/agent/auth-profiles.json`
- `~/.openclaw/cron/`
- `~/.openclaw/credentials/` 仅备份结构和脱敏摘要，真实 key 不进云端/GitHub
- `~/Library/LaunchAgents/ai.openclaw.gateway.plist`

备份目标：

优先本地：

`~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/openclaw_daily/YYYYMMDD/`

可选外接硬盘：

`/Volumes/TianLu_Storage/Tianlu_V6_5_DataVault/OPENCLAW_CONFIG_BACKUP/YYYYMMDD/`

要求：

1. 默认脱敏；
2. 不打印真实 key；
3. 日志写入 `~/Desktop/Tianlu_V6_5_Workspace/07_TEST_LOGS/backup_openclaw_daily.log`；
4. 先手动运行验证；
5. LaunchAgent 方案只生成 `.plist.draft`，等待 GPT/用户确认后再安装。

---

### P0-3：修复 `tianlu_cache_maintenance.py` 前必须先确认 APFS 根因

报告判断 `shutil.copy2()` 被 macOS APFS 同卷复制权限拦截。这个方向有可能正确，但还不能直接替换成 `os.link()`。

原因：

1. `os.link()` 只适合同一文件系统硬链接；
2. 如果源文件和目标目录不在同一卷，硬链接会失败；
3. 对 SQLite/DB 活跃写入文件做硬链接或直接复制可能产生不一致快照；
4. 对正在写入的缓存，应优先采用“临时快照 + 原子 rename”的方式。

Claude 下一步应先做最小验证脚本：

`CACHE_COPY_METHOD_PROBE.md`

测试三种方法：

1. `shutil.copy2()`；
2. `cp -p`；
3. `rsync -a --inplace` 或 `rsync -a --checksum`；
4. 若源/目标同卷，再测试 `os.link()`。

判断标准：

- 是否成功；
- 是否保留 mtime；
- 是否触发 Operation not permitted；
- 是否跨卷可用；
- 是否适合 SQLite 活跃文件。

推荐修复方向优先级：

1. 对普通 JSON/报告：`rsync -a`；
2. 对 SQLite/DB：先复制到本地临时快照，再 `rsync` 到外接硬盘；
3. 只有确认同卷且文件非活跃写入时才考虑 `os.link()`；
4. 不建议直接将所有 copy2 全部替换成 hardlink。

---

### P0-4：L5 清算/恐惧贪婪/持仓数据 5 天未更新，先查采集任务，不要直接重启全部服务

Claude 应定位：

- 采集脚本；
- 调度方式；
- 最近日志；
- 是否因 OpenClaw 故障期间中断；
- 是否因 API 错误、路径错误、权限错误或 cron/LaunchAgent 未执行。

要求生成：

`L5_DATA_COLLECTOR_RECOVERY_PLAN.md`

只允许先执行只读检查。若需要恢复采集，只能先运行单次 dry-run 或 run-once，不要重启 9099/7891/机器人。

---

## 二、推荐执行顺序

### 第一步：备份链路验证

1. 验证 `tianlu_system_backup.py --mode daily-settings`；
2. 修复日志为空问题；
3. 生成交易系统参数备份验证报告。

### 第二步：OpenClaw 每日备份

1. 创建 `backup_openclaw_daily.sh`；
2. 手动运行一次；
3. 检查脱敏和产物；
4. 生成 LaunchAgent 草案，不安装。

### 第三步：缓存转存修复方案

1. 对 `tianlu_cache_maintenance.py` 做 copy 方法探针；
2. 明确源/目标是否同卷；
3. 选择 `rsync`/临时快照/硬链接之一；
4. 先 dry-run，后修复。

### 第四步：L5 数据采集恢复

1. 查 L5 collector；
2. 查最近日志；
3. 单次 run-once 验证；
4. 再决定是否恢复调度。

### 第五步：DataVault 结构

在前三步稳定后，再创建完整 DataVault：

```text
/Volumes/TianLu_Storage/Tianlu_V6_5_DataVault/
├── M1_M5_CACHE_ARCHIVE/
├── TRADING_PARAMS_BACKUP/
├── OPENCLAW_CONFIG_BACKUP/
├── REVIEWHUB_MIRROR/
└── DAILY_REPORTS/
```

---

## 三、暂不允许执行的事项

1. 不允许删除任何缓存；
2. 不允许移动真实缓存；
3. 不允许直接覆盖旧备份；
4. 不允许直接安装新的 LaunchAgent；
5. 不允许重启 9090-9097 / 8081-8084；
6. 不允许调用交易所 API；
7. 不允许把 OpenClaw credentials 原文备份到 GitHub；
8. 不允许把数据库、日志原文、api_keys 原文推送到 GitHub；
9. 不允许直接把所有 `shutil.copy2()` 改成 `os.link()`。

---

## 四、允许 Claude 立即执行的任务

### 任务 A：每日交易系统参数备份验证

输出：

`05_Claude_Tasks/TRADING_PARAMS_BACKUP_VERIFY_REPORT.md`

### 任务 B：OpenClaw 每日备份脚本草案

输出：

- `05_Claude_Tasks/backup_openclaw_daily.sh.draft`
- `05_Claude_Tasks/com.tianlu.openclaw-daily-backup.plist.draft`
- `05_Claude_Tasks/OPENCLAW_DAILY_BACKUP_PLAN.md`

### 任务 C：缓存复制方法探针

输出：

- `05_Claude_Tasks/CACHE_COPY_METHOD_PROBE.md`
- `05_Claude_Tasks/CACHE_MAINTENANCE_FIX_PLAN.md`

### 任务 D：L5 数据采集恢复计划

输出：

- `05_Claude_Tasks/L5_DATA_COLLECTOR_RECOVERY_PLAN.md`

---

## 五、最终审核结论

当前审计结论：**有条件通过，可以进入修复准备阶段，但不要直接应用大改。**

下一步 Claude 应执行：

1. 交易参数备份验证；
2. OpenClaw 每日备份草案；
3. cache copy 方法探针；
4. L5 数据采集恢复计划。

完成后推送到：

`05_Claude_Tasks/`

再由 GPT 审核后决定是否真正安装 LaunchAgent 或修改 `tianlu_cache_maintenance.py`。
