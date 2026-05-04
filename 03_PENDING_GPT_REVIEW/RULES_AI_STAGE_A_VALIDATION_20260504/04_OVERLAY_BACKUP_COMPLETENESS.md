# Stage A — 04: Overlay备份完整性验证

> 执行时间：2026-05-04 15:00
> 备份目录：~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/

---

## Mac A Overlay配置文件现状

| Port | 配置文件路径 | 存在状态 |
|------|------------|---------|
| 9090 | bt_tools/config_9090_overlay.json | ✅ 独立FOttStrategy配置 |
| 9091 | bt_tools/config_9091_overlay.json | ❌ 不存在 |
| 9092 | bt_tools/config_9092_overlay.json | ❌ 不存在 |
| 9093 | bt_tools/config_9093_overlay.json | ✅ 独立OKX配置 |
| 9094-9097 | bt_tools/config_9094-9097_overlay.json | ❌ 不存在 |

**说明**：9091-9092, 9094-9097 无独立overlay文件，意味着这些bot使用默认配置（由freqtrade主程序管理），而非通过overlay注入参数。

---

## 备份清单

| 备份文件 | 大小 | 状态 |
|---------|------|------|
| config_9090_overlay.json.bak_20260504_150000 | 1.3KB | ✅ |
| config_9093_overlay.json.bak_20260504_144132 | 2.2KB | ✅ |
| config_8081_overlay.json.bak_20260504_150000_MacA_ref | 2.1KB | ⚠️ Mac A参考文件，非Mac B真实备份 |
| v65_autopilot.py.bak_20260504_142502 | 447KB | ✅ |
| console_server.py.bak_20260504_142502 | 1.4MB | ✅ |

---

## 关键问题

### 🔴 BLOCKING-1：9091-9092, 9094-9097 无独立overlay配置

**问题**：这些bot没有独立overlay文件，无法通过overlay注入 `temporary_pair_freeze` 和 `dca_pause_rules`。

**解决方案**：
1. 如果bot读取freqtrade标准配置（tradesv3.sqlite中的pairlists），P0-1/P0-2补丁需直接写入bot的config.json，而非overlay
2. 或者为这些bot创建独立overlay文件

**需人工确认**：这些bot的实际配置在哪里？

### ⚠️ BLOCKING-2：Mac B 8081-8084 无真实备份

Mac A上仅有 `config_8081_overlay.json.bak` 作为参考文件，不代表Mac B真实状态。Mac B SSH不可达。

---

## Overlay PATCHED文件生成情况

| Port | PATCHED文件 | 位置 |
|------|-----------|------|
| 9090 | config_9090_PATCHED.json | PENDING_PATCH/ |
| 9091 | config_9091_PATCHED.json | PENDING_PATCH/ ⚠️ 无源文件对照 |
| 9092 | config_9092_PATCHED.json | PENDING_PATCH/ ⚠️ 无源文件对照 |
| 9093 | config_9093_PATCHED.json | PENDING_PATCH/ |
| 9094-9097 | config_9094-9097_PATCHED.json | PENDING_PATCH/ ⚠️ 无源文件对照 |

---

## 结论

| 状态 | 说明 |
|------|------|
| ✅ 可执行 | 9090, 9093 overlay备份完整，PATCHED文件可用 |
| 🔴 BLOCKING | 9091-9092, 9094-9097 无overlay，无法注入freeze/pause字段 |
| 🔴 BLOCKING | Mac B 8081-8084 无真实备份，PATCHED占位符不能应用 |

**Stage A 前置条件**：需先确认9091-9092, 9094-9097的配置路径，或为其创建overlay。

---

*兵部存档 | 2026-05-04*
