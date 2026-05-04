# 04_9090_GREY_RUN_PLAN.md

## 9090 单 bot 灰度运行计划

**草案文件** | **Stage B 通过后执行**

---

## 1. 灰度范围

| 项目 | 范围 |
|------|------|
| 目标 bot | 9090（Gate.io 账号 a17656685222）|
| 补丁范围 | `temporary_pair_freeze` 读取逻辑 + `dca_pause_rules` 读取逻辑 |
| 灰度模式 | **Shadow Dry-run**（只记录日志，不执行阻断）|
| 时间窗口 | 爸确认后执行 |

**暂不涉及**: 9091-9097, 8081-8084

---

## 2. Stage B 与 Stage C 的分界线

```
Stage B: 写补丁草案 → py_compile 通过 → grep 验证读取路径存在
Stage C: 应用补丁到 9090 → Shadow Dry-run → 爸观察日志 → 确认无误 → 升级阻断模式
```

**Stage C 触发条件**:
1. Stage B GPT 审核通过
2. 9090 overlay JSON 语法验证通过
3. `v65_autopilot.py` py_compile 通过（补丁应用后）
4. 爸确认 Shadow 日志无异常
5. 爸明确指示升级为阻断模式

---

## 3. 9090 Shadow Dry-run 步骤

### 步骤 0：备份（执行前）

```bash
# 备份当前 v65_autopilot.py
cp ~/freqtrade_console/bt_tools/v65_autopilot.py \
   ~/freqtrade_console/bt_tools/v65_autopilot.py.bak.20260504

# 备份 9090 overlay
cp ~/freqtrade/config_9090_overlay.json \
   ~/freqtrade/config_9090_overlay.json.bak.20260504

# 记录 git commit
cd ~/freqtrade_console && git add bt_tools/v65_autopilot.py
git commit -m "Stage B: 添加 temporary_pair_freeze / dca_pause_rules 读取逻辑（Shadow模式）
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### 步骤 1：应用补丁

```bash
# 应用 PATCH.diff（仅 9090 Shadow 测试标签）
cd ~/freqtrade_console
git apply --3way 04_PENDING_GPT_REVIEW/.../PATCH.diff
# 或手动应用补丁（见 PATCH.diff）
```

### 步骤 2：py_compile 验证

```bash
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py && echo "✅ py_compile OK"
```

### 步骤 3：重启 console_server（不改 bot）

```bash
# 不重启 9090 bot，只重启 console_server
pkill -f "console_server.py" && sleep 2
cd ~/freqtrade_console && nohup python3 console_server.py >> ~/.console_server.log 2>&1 &
sleep 5
curl -s http://127.0.0.1:9099/api/health | python3 -m json.tool | grep ok
```

### 步骤 4：Shadow 模式验证

```bash
# 检查日志，确认 is_pair_temporarily_frozen 和 is_dca_paused 被调用
grep -E "\[Freeze\]|DCA 暂停中|is_pair_temporarily_frozen|is_dca_paused" \
    ~/.console_server.log | tail -20

# 确认 Shadow 模式日志
grep -E "Shadow|DRY|SIMULATE" ~/.console_server.log | tail -10
```

### 步骤 5：爸观察（1-2小时）

- 观察 console_server 日志
- 确认无异常阻断
- 确认冻结/暂停币对日志格式正确

### 步骤 6：升级阻断模式

爸确认 Shadow 无误后，修改代码中的 `_SHADOW_MODE = True` → `False`，重新 py_compile，重启 console_server。

---

## 4. 9090 overlay 准备

在 Shadow 测试前，需先在 9090 overlay 中写入测试规则：

```bash
# 临时添加 DOGE 冻结测试规则（Shadow模式下只记录，不执行）
python3 -c "
import json
cfg = json.load(open('$HOME/freqtrade/config_9090_overlay.json'))
cfg.setdefault('temporary_pair_freeze', {})
cfg['temporary_pair_freeze']['DOGE/USDT:USDT'] = {
    'enabled': True,
    'reason': 'shadow_test_no_freeze',
    'block_auto_entry': True,
    'duration_hours': 24,
    'until_ts': None,
    'created_by': 'claude-stage-c-shadow-test'
}
print(json.dumps(cfg, indent=2, ensure_ascii=False))
" > /tmp/config_9090_overlay_test.json

# 验证 JSON
python3 -m json.tool /tmp/config_9090_overlay_test.json >/dev/null && echo "✅ JSON OK"
```

---

## 5. 9091-9097 扩展条件（Stage D）

Stage C 稳定运行 7 天后，且爸确认 9090 无问题后：

1. 逐一备份各 overlay（9091-9097）
2. 同样写入 freeze/pause 测试规则
3. 观察各 bot 日志
4. 确认无阻断异常后，推广到全部

---

## 6. 禁止事项（铁律）

| 禁止项 | 说明 |
|--------|------|
| 不重启 9090 bot | 只重启 console_server |
| 不修改其他 bot overlay | 只动 9090 |
| 不执行 force_entry / force_exit | 只观察日志 |
| 不删除 whitelist 中的币对 | freeze 不等于删除 |
| 不在全量 bot 推广前宣称 freeze/pause 生效 | 必须在单 bot 验证后 |
