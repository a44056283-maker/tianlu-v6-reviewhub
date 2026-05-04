# Stage A — 07: Mac B 8081-8084 验证报告

> 执行时间：2026-05-04 15:06
> 验证方法：SSH实际连接（sshpass）

---

## SSH连接状态

| 项目 | 结果 |
|------|------|
| 主机 | 192.168.13.104 (luxiangnandeMac-mini.local) |
| 用户名 | luxiangnan |
| 连接结果 | ✅ **成功** |
| 存活时间 | 14天14小时 |
| Bot进程数 | 4个 |

---

## Mac B Bot进程详情

| Port | 账号 | 策略 | 状态 |
|------|------|------|------|
| 8081 | Gate.io a63904550 | FOttStrategy | ✅ 运行中 |
| 8082 | Gate.io a15637798222 | FOttStrategy | ✅ 运行中 |
| 8083 | Gate.io b15637798222 | FOttStrategy | ✅ 运行中 |
| 8084 | Gate.io c15637798222 | FOttStrategy | ✅ 运行中 |

**配置文件路径**：`~/freqtrade_bots/config_808{1,2,3,4}_overlay.json`
**用户数据目录**：`~/freqtrade_bots/user_data_gate_*/`

---

## 备份完成状态

| 文件 | 大小 | 备份位置 |
|------|------|---------|
| config_8081_overlay.json | 2.0KB | `04_BACKUPS/.../MacB/config_8081_overlay.json` ✅ |
| config_8082_overlay.json | 2.0KB | `04_BACKUPS/.../MacB/config_8082_overlay.json` ✅ |
| config_8083_overlay.json | 2.0KB | `04_BACKUPS/.../MacB/config_8083_overlay.json` ✅ |
| config_8084_overlay.json | 2.0KB | `04_BACKUPS/.../MacB/config_8084_overlay.json` ✅ |

---

## 关键发现

### ✅ Mac B 联通性已解决
- SSH凭据（luxiangnan / 613822）有效
- 可以通过Mac A远程管理Mac B

### ⚠️ Mac B 配置路径与Mac A不同
- Mac A：配置文件在 `bt_tools/config_*_overlay.json`
- Mac B：配置文件在 `freqtrade_bots/config_*_overlay.json`

**影响**：PATCHED配置文件需复制到Mac B对应路径，不能用Mac A路径。

---

## 手动操作清单（Mac B补丁应用）

```bash
# 1. 从Mac A复制PATCHED配置到Mac B
sshpass -p '613822' scp config_8081_PATCHED.json luxiangnan@192.168.13.104:~/freqtrade_bots/config_8081_overlay.json
sshpass -p '613822' scp config_8082_PATCHED.json luxiangnan@192.168.13.104:~/freqtrade_bots/config_8082_overlay.json
sshpass -p '613822' scp config_8083_PATCHED.json luxiangnan@192.168.13.104:~/freqtrade_bots/config_8083_overlay.json
sshpass -p '613822' scp config_8084_PATCHED.json luxiangnan@192.168.13.104:~/freqtrade_bots/config_8084_overlay.json

# 2. 在Mac B重启bot（仅重启bot，不动config_server）
sshpass -p '613822' ssh luxiangnan@192.168.13.104 "launchctl unload ~/Library/LaunchAgents/com.tianlu.freqtrade-8081.plist && launchctl load ~/Library/LaunchAgents/com.tianlu.freqtrade-8081.plist"
```

---

## 结论

✅ **Mac B 8081-8084 验证完成，4个bot全部存活，配置已备份。**

P0-1/P0-2补丁可通过SSH应用到Mac B，无需人工到Mac B操作。

---

*兵部存档 | 2026-05-04*
