# 05_ROLLBACK_STATUS.md
# 回滚状态

**状态**: ✅ 未触发回滚

---

## 回滚触发条件

| 条件 | 状态 |
|------|------|
| py_compile 失败 | ✅ 未触发 |
| 9099 无法启动 | ✅ 未触发 |
| M2 页面 JS 报错 | ✅ 待浏览器验证 |
| /api/bt2/sr_levels 无法返回 | ✅ 未触发 |
| 机器人进程异常 | ✅ 未触发 |
| 用户要求回滚 | ✅ 未触发 |

---

## 回滚路径（备用）

若需回滚，执行：

```bash
# 1. 停止 console_server
kill $(lsof -ti:9099)

# 2. 恢复备份
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/console_server.py.bak.20260505_003300 \
   ~/freqtrade_console/console_server.py
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/m2_sr.html.bak.20260505_003300 \
   ~/freqtrade_console/static/tabs/m2_sr.html

# 3. py_compile
python3 -m py_compile ~/freqtrade_console/console_server.py

# 4. 重启
launchctl kickstart -k gui/$(id -u)/com.tianlu.console-server
```
