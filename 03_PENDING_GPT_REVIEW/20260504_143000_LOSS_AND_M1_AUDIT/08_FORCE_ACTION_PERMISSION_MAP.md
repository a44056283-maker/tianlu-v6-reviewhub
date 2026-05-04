# 高风险动作权限矩阵
**审计时间**: 2026-05-04 14:30
**审计人**: 刑部代理
**文件**: console_server.py, v65_autopilot.py

---

## 权限总览

| 动作 | 触发入口 | 权限要求 | 当前状态 | 风险等级 |
|------|---------|---------|---------|---------|
| force_entry（开仓） | 飞书Webhook / Console UI / API | 无认证 | **完全开放** | 🔴 高 |
| force_entry（DCA加仓） | 兵部inject信号 / Console UI | 无认证 | **完全开放** | 🔴 高 |
| force_exit（全平/半平） | 飞书Webhook / Console UI / API | 无认证 | **完全开放** | 🔴 高 |
| 修改DCA参数 | Console UI / API | 无认证 | **完全开放** | 🟡 中 |
| 调整杠杆 | force_entry参数 | 无认证 | **完全开放** | 🔴 高 |
| 紧急全平（舆情） | 突发事件自动触发 | 自动 | 已实现 | 🟢 低 |
| 取消止损单 | Console UI | 无认证 | **完全开放** | 🟡 中 |

---

## 1. force_entry 入口分析

### API端点
```python
# console_server.py:5613-5671
@app.route("/api/force_entry", methods=["POST"])
def api_force_entry():
    """手动强制入场"""
```

### 入口渠道

| 渠道 | 代码位置 | 认证要求 | 冷却检查 |
|------|---------|---------|---------|
| 飞书Webhook | `console_server.py` | 无 | 有 |
| Console UI | HTML页面JS | 无 | 有 |
| 兵部inject | `v65_autopilot.py:5296-5302` | 无 | 无 |
| 直接API调用 | `console_server.py:5613` | 无 | 无 |

### force_entry冷却机制

```python
# console_server.py:5124-5135
elif act == "force_entry":
    if pair_clean:
        cd = _check_bot_cooldown(port, pair_clean, entry_direction)
        if cd.get("blocked"):
            print(f"[broadcast force_entry] 冷却拦截 port={port} pair={pair_clean} {cd['reason']}")
            continue  # 跳过,不执行加仓
```

**评估**: 冷却检查存在，但无认证机制，任何人可触发。

---

## 2. force_exit 入口分析

### API端点
```python
# console_server.py:5087-5122
elif act == "force_exit":
    # 手动平仓 - 支持部分平仓
    exit_pct = data.get("exit_pct", 100)  # 100=全平, 50=半平, 33=1/3
```

### 入口渠道

| 渠道 | 代码位置 | 认证要求 | 确认机制 |
|------|---------|---------|---------|
| Console UI | HTML确认弹窗 | 无 | 有(typed confirm) |
| 批量平仓 | JS多选+确认 | 无 | 有(typed confirm) |
| 飞书Webhook | `console_server.py` | 无 | 无 |
| sentiment监控 | `monitor_sentiment.py:131` | 自动 | 无 |

### Console UI确认机制

```javascript
// console_server.py:2004-2013
if (exitPct <= 0 || exitPct > 100) {
    alert('平仓比例需在1~100之间'); return;
}
// typed confirm 要求用户输入确认
if (!await requireTypedConfirm('批量全平持仓交易对', '批量全平', `已选持仓: ${checkedTrades.length}...`))
    return;
```

**评估**: Console UI有确认机制，但飞书/Webhook无确认。

---

## 3. DCA参数修改权限

### 可修改参数
```python
# v65_autopilot.py:7865-7871
"dca_enabled":          ("_DCA_ENABLED", bool, False, True, "💰 [L5] 补仓启用"),
"dca_trigger_pct_l1":   ("_DCA_TRIGGER_PCTS[0]", float, 0.5, 20.0, "💰 [L5] 第1层补仓触发%"),
"dca_trigger_pct_l2":   ("_DCA_TRIGGER_PCTS[1]", float, 1.0, 30.0, "💰 [L5] 第2层补仓触发%"),
"dca_flow_strong_trigger": ("_DCA_FLOW_STRONG_TRIGGER", bool, False, True, "💰 [L5] 资金流强触发"),
"dca_max_layer":         ("_DCA_MAX_LAYER", int, 1, 20, "💰 [L5] 最大补仓层数"),
"dca_sr_check":          ("_DCA_SR_CHECK", bool, False, True, "💰 [L5] S/R位置检查"),
```

### 修改路径
```python
# v65_autopilot.py:7167-7169
if "dca_max_layer" in params:
    _DCA_MAX_LAYER = int(params["dca_max_layer"])
    updated["dca_max_layer"] = _DCA_MAX_LAYER
```

**风险**: 可通过API将 `dca_max_layer` 从2改为20，绕过封顶限制。

---

## 4. 杠杆调整权限

### 杠杆来源

| 来源 | 代码位置 | 限制 | 风险 |
|------|---------|------|------|
| force_entry参数 | `console_server.py:5639` | 无 | 🔴 可传任意值 |
| 自动计算 | `v65_autopilot.py:3707-3734` | ≤MAX_LEVERAGE | 🟢 已限制 |
| DCA层级Boost | `v65_autopilot.py:3720-3734` | ≤MAX_LEVERAGE | 🟢 已限制 |

### 手动force_entry杠杆传递
```python
# console_server.py:5638-5639
if data.get("leverage") is not None:
    body["leverage"] = data.get("leverage")
```

**风险**: 用户可通过API直接指定杠杆值，绕过策略限制。

---

## 5. 紧急平仓（舆情/突发事件）

### 自动触发条件
```python
# v65_autopilot.py:2309-2316
if emergency:
    _log("🚨 突发事件检测！全部平仓离场！", "ERROR")
    return [], {
        "long_allowed": False, "short_allowed": False,
        "leverage_mult": 0.0, "emergency_exit": True,
        ...
    }
```

### sentiment监控触发
```python
# monitor_sentiment.py:129-131
action = "force_exit"
elif action == "force_exit":
    exit_result = execute_force_exit()
```

**评估**: 自动平仓机制存在但依赖外部数据源。

---

## 6. 权限风险矩阵

```
                    │ 无认证 │ 有确认 │ 自动触发 │ 需冷却
────────────────────┼────────┼────────┼─────────┼──────
force_entry(开仓)   │   🔴   │   🟡   │    🟢   │  🟡
force_entry(DCA)    │   🔴   │   🟡   │    🔴   │  🟡
force_exit(全平)    │   🔴   │   🟢   │    🟢   │  🟢
force_exit(半平)    │   🔴   │   🟢   │    🟢   │  🟢
修改DCA参数         │   🔴   │   🟡   │    🔴   │  🔴
调整杠杆(手动)      │   🔴   │   🟡   │    🔴   │  🔴
紧急平仓(舆情)     │   🔴   │   🔴   │    🟢   │  🟢
取消止损单          │   🔴   │   🟡   │    🔴   │  🔴
```

---

## 7. 建议安全措施

### 高优先级（应立即实施）

1. **飞书Webhook认证**
   - 增加HMAC签名验证
   - 限制可调用IP
   - 参考: `console_server.py` 中飞书webhook处理逻辑

2. **force_entry杠杆限制**
   ```python
   # 在console_server.py:5639后添加
   body["leverage"] = min(max(body.get("leverage", 10), 1), _MAX_LEVERAGE)
   ```

3. **DCA参数修改审批**
   - `dca_max_layer` 修改需二次确认
   - 记录所有参数修改日志

### 中优先级（建议实施）

4. **API调用速率限制**
   - 同一IP/端口的force_entry频率限制
   - 参考: `_check_bot_cooldown()` 机制

5. **敏感操作审计日志**
   - 记录所有force_entry/exit的时间、端口、交易对
   - 记录参数修改前后值

### 低优先级（可选）

6. **UI操作员分级**
   - 普通操作员：只能查看
   - 高级操作员：可force_exit
   - 管理员：可force_entry + 修改参数

---

## 附录：关键代码索引

```
console_server.py:
├── api_force_entry()           # 5613-5671
├── force_entry冷却检查         # 5124-5135
├── force_exit处理             # 5087-5122
├── typed confirm机制           # 2004-2013
└── 飞书Webhook处理            # (webhook路由)

v65_autopilot.py:
├── 舆情emergency触发          # 2309-2316
├── 兵部inject处理             # 5296-5302
├── DCA参数动态更新            # 7167-7169
└── 止损冷却检查               # 6274-6285
```
