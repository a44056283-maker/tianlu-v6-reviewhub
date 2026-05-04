# 任务D：L5 数据采集恢复计划

> 生成时间：2026-05-04 13:08
> 审计类型：只读调查，不重启任何服务

---

## 一、采集现状

### 活跃采集（M4/M5 shadow lab）✅
- 每 15 分钟：`m4_m5_shadow_lab.py run-once`（cron + LaunchAgent 双保险）
- 状态：正常，数据持续写入 `m4_m5_shadow_lab.sqlite`
- 最近活跃：`2026-05-04 12:34`

### 失效采集（L5 清算/恐惧贪婪/持仓数据）🔴

| 数据 | 路径 | 最后更新 | 失效天数 |
|------|------|---------|---------|
| 清算数据 | `cache/l5/liquidations/` | 2026-04-30 00:24 | **5天** |
| 恐惧贪婪 | `cache/l5/fear_greed/global.json` | 2026-04-30 00:23 | **5天** |
| 持仓数据 | `cache/l5/orderbook/` | 2026-04-30 00:22 | **5天** |
| 未平仓合约 | `cache/l5/open_interest/` | 2026-04-30 00:21 | **5天** |

---

## 二、采集脚本定位

L5 清算等数据由 `fund_flow_v2_collector.py` 采集。

| 脚本 | 路径 | 负责 |
|------|------|------|
| `fund_flow_v2_collector.py` | `~/freqtrade_console/l5_evolution_lab/` | 资金流 + 清算 + 恐惧贪婪 |

**是否在 cron/LaunchAgent 中调度：** 待查（需 grep `fund_flow` 或 `l5_evolution_lab` 调度配置）

---

## 三、最近错误日志分析

```
collector.out.log — 最后内容（2026-05-04 12:34）:
  shadow_only_no_order_permission 模式运行正常
  source: "shadow_only_no_order_permission"
  → M4/M5 shadow lab 本身正常，数据在更新

collector.err.log — 最后错误:
  socket.timeout: timed out
  文件: m4_m5_shadow_lab.py line 766
  调用: fetch_json("/api/hero_cards/exit_ai_status?db=1")
  → console_server API 超时，OpenClaw 修复前可能中断
```

---

## 四、根因分析

### 直接原因
`m4_m5_shadow_lab.py` 的 `fetch_json("/api/hero_cards/exit_ai_status?db=1")` 超时。
这是 shadow lab 尝试从 console_server 获取 AI 状态时网络超时。

### 深层原因
- OpenClaw 修复（minimax provider）前，console_server 的某些 API 端点可能响应慢或超时
- 采集中断期间（OpenClaw 无响应），shadow lab 无法获取 AI 数据，退化为 `shadow_only` 模式

### L5 清算数据 5 天未更新的真正原因
清算/恐惧贪婪数据由 `fund_flow_v2_collector.py` 负责，**不是 `m4_m5_shadow_lab.py`**。
需要单独确认 `fund_flow_v2_collector.py` 是否在调度中。

---

## 五、待确认事项

- [ ] `fund_flow_v2_collector.py` 是否有独立的 cron/LaunchAgent？
- [ ] `cache/l5/` 目录下哪些脚本负责写入 liquidations/fear_greed/orderbook？
- [ ] 最近一次成功采集这些数据的日志在哪里？

---

## 六、恢复计划（草案，待用户确认）

### 步骤 1：定位负责脚本
```bash
grep -rn "liquidations\|fear_greed\|orderbook" \
  ~/freqtrade_console/l5_evolution_lab/ \
  --include="*.py" | grep -v "__pycache__" | grep -v ".pyc"
```

### 步骤 2：确认调度方式
```bash
crontab -l | grep -E "fund_flow|l5|liquid"
launchctl list | grep -E "fund_flow|l5"
```

### 步骤 3：手动运行单次采集（dry-run）
```bash
cd ~/freqtrade_console/l5_evolution_lab
python3 fund_flow_v2_collector.py --dry-run  # 或 --help 查看用法
```

### 步骤 4：验证数据恢复
```bash
find ~/freqtrade_console/cache/l5 -type f -name "*.json" \
  -newer /tmp/tianlu_cache_maintenance.err | head -20
```

---

## 七、禁止事项

- 不重启 9099 console_server
- 不重启 7891 edict-server
- 不重启 9090-9097 / 8081-8084 机器人
- 不删除现有缓存文件
- 不修改任何调度（cron/LaunchAgent）

---

## 八、结论

L5 清算数据采集中断与 OpenClaw 通讯故障期间 shadow lab API 超时有关，shadow lab 本身已恢复（`shadow_only` 模式），但清算数据采集脚本是否在运行需进一步确认。

**下一步：用户确认后，执行步骤 1-4 只读调查，找到负责脚本后再决定是否恢复。**
