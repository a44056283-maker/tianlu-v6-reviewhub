# GPT_审核建议 · RULES_AI_STAGE_A_VALIDATION_20260504

## 审核结论

**有条件通过。批准进入 Stage B：读取逻辑补丁准备与 9090 单 bot 灰度前置准备。**

本轮 Stage A 验证有效，已经证明 P0-1 / P0-2 的最大阻断点不是 JSON 或编译问题，而是：

```text
temporary_pair_freeze 零读取路径
dca_pause_rules 零读取路径
```

因此，**现在不能直接写 overlay 并宣称 DOGE freeze / SOL DCA pause 生效**。必须先给 `v65_autopilot.py` 增加读取逻辑，并完成 shadow/dry-run 验证后，再做 9090 单机器人灰度。

---

## 一、已确认通过项

### 1. py_compile 通过

Stage A 报告显示 `v65_autopilot.py` 和 `console_server.py` 已通过 py_compile。

### 2. JSON 校验通过

Stage A 报告显示 9090 / 9093 overlay JSON 语法正确。

### 3. Mac B 验证通过

Mac B 8081-8084 SSH 已恢复，4 个 bot 存活，配置已备份。

### 4. 阻断点定位清晰

`05_FREEZE_RULE_READ_PATH_PROOF.md` 已证明：

```text
temporary_pair_freeze
pair_freeze
block_auto_entry
```

在 `v65_autopilot.py` 和 `console_server.py` 中没有读取路径。

`06_DCA_PAUSE_RULE_READ_PATH_PROOF.md` 已证明：

```text
dca_pause_rules
pause_rules
block_new_dca
dca_pause
```

在实盘代码中没有读取路径。

---

## 二、当前禁止事项

在读取逻辑补丁完成前，禁止执行：

1. 不要直接全量写入 12 个 bot overlay；
2. 不要宣称 DOGE freeze 已生效；
3. 不要宣称 SOL DCA pause 已生效；
4. 不要直接重启 9090-9097；
5. 不要直接重启 8081-8084；
6. 不要执行 force_entry / force_exit；
7. 不要调用交易所 API；
8. 不要把 Mac B 凭据写入 GitHub；
9. 不要把补丁应用到所有机器人。

---

## 三、批准 Claude 下一步执行的 Stage B

Claude 下一步应创建：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_STAGE_B_READ_LOGIC_PATCH/
```

必须输出：

```text
00_STAGE_B_SUMMARY.md
01_FREEZE_READ_LOGIC_PATCH.md
02_DCA_PAUSE_READ_LOGIC_PATCH.md
03_CONFIG_SCHEMA_AND_EXAMPLE.md
04_9090_GREY_RUN_PLAN.md
05_TEST_AND_VERIFY_PLAN.md
06_ROLLBACK_PLAN.md
07_INTERNAL_QA_CHECKLIST.md
PATCH.diff
TEST_LOG.md
REVIEW_PACKAGE.zip
```

---

## 四、Stage B 必须实现的最小逻辑

### P0-read-1：temporary_pair_freeze 读取逻辑

目标：让 `temporary_pair_freeze` 真正被代码读取。

建议实现为独立函数，不要把逻辑散落在多处：

```python
def is_pair_temporarily_frozen(pair: str, cfg: dict, now_ts: float | None = None) -> tuple[bool, str]:
    """返回该交易对是否被临时冻结，以及冻结原因。"""
    import time
    now_ts = now_ts or time.time()
    freeze_rules = (cfg or {}).get("temporary_pair_freeze", {}) or {}
    rule = freeze_rules.get(pair) or freeze_rules.get(pair.replace(":USDT", ""))
    if not isinstance(rule, dict):
        return False, ""
    if not rule.get("enabled", False):
        return False, ""
    if rule.get("until_ts") and now_ts >= float(rule.get("until_ts")):
        return False, "expired"
    if rule.get("block_auto_entry", False):
        return True, str(rule.get("reason", "temporary_pair_freeze"))
    return False, ""
```

接入点：

- 只能接入自动入场判断路径；
- 不得影响人工只读监控；
- 不得直接平仓；
- 不得删除 DOGE；
- 不得影响已有仓位风险出场。

### P0-read-2：dca_pause_rules 读取逻辑

目标：让 `dca_pause_rules` 真正阻断 DCA 新加仓。

建议实现为独立函数：

```python
def is_dca_paused(pair: str, direction: str, cfg: dict, now_ts: float | None = None) -> tuple[bool, str]:
    """返回该交易对方向是否暂停 DCA。"""
    import time
    now_ts = now_ts or time.time()
    rules = (cfg or {}).get("dca_pause_rules", {}) or {}
    keys = [
        f"{pair}:{direction}",
        f"{pair.replace(':USDT', '')}:{direction}",
        pair,
        pair.replace(":USDT", ""),
    ]
    for key in keys:
        rule = rules.get(key)
        if not isinstance(rule, dict):
            continue
        if not rule.get("enabled", False):
            continue
        if rule.get("until_ts") and now_ts >= float(rule.get("until_ts")):
            continue
        if rule.get("block_new_dca", False):
            return True, str(rule.get("reason", "dca_pause_rules"))
    return False, ""
```

接入点：

- 只接入 DCA 新加仓判断；
- 不影响已有持仓出场；
- 不影响止损风控；
- 不影响只读监控；
- 不直接修改 DCA_MAX_LAYER。

---

## 五、Stage B 配置规范

建议 overlay 字段统一如下：

```json
{
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true,
      "duration_hours": 24,
      "until_ts": null
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true,
      "allow_exit_review": true,
      "until_ts": null
    }
  }
}
```

说明：

1. `until_ts` 可为空，由调用层根据 `duration_hours` 计算；
2. `block_auto_entry` 只阻止自动新增入场；
3. `block_auto_dca` / `block_new_dca` 只阻止新增 DCA；
4. 不应影响已有仓位人工/风控出场。

---

## 六、Stage B 验证要求

Claude 必须执行并输出真实结果：

```bash
python3 -m py_compile ~/freqtrade_console/bt_tools/v65_autopilot.py
python3 -m json.tool config_9090_overlay.json >/dev/null
```

并且必须提供 grep 证明：

```bash
grep -n "temporary_pair_freeze\|is_pair_temporarily_frozen" ~/freqtrade_console/bt_tools/v65_autopilot.py
grep -n "dca_pause_rules\|is_dca_paused" ~/freqtrade_console/bt_tools/v65_autopilot.py
```

必须在 TEST_LOG.md 中明确：

```text
是否执行交易：没有
是否调用交易所 API：没有
是否重启机器人：没有
是否执行 force_entry/force_exit：没有
是否修改 12 个 bot 配置：没有，或仅生成补丁草案
```

---

## 七、Stage C 预批准条件

只有 Stage B 通过 GPT 审核后，才允许进入 Stage C：9090 单 bot 配置级灰度。

Stage C 条件：

1. `temporary_pair_freeze` 读取路径存在；
2. `dca_pause_rules` 读取路径存在；
3. 9090 overlay 备份完整；
4. 9090 JSON 校验通过；
5. py_compile 通过；
6. 9090 灰度计划明确；
7. 回滚命令可执行；
8. 用户确认。

---

## 八、注意事项

1. `06_DCA_PAUSE_RULE_READ_PATH_PROOF.md` 结论处出现 `tca_pause_rules` 拼写，应修正为 `dca_pause_rules`，避免后续搜索误判。
2. Mac B 凭据不得进入 GitHub；只允许记录“SSH 已通，4 bot 存活，配置已备份”。
3. 9091-9097 无 overlay 文件的问题需要单独确认真实配置路径，不得默认套用 9090/9093 的路径。
4. 如果读取逻辑补丁找不到合适接入点，必须停止并输出代码定位报告，不允许强插补丁。

---

## 九、最终结论

Stage A 审核结果：**有条件通过。**

允许进入：

```text
Stage B：temporary_pair_freeze / dca_pause_rules 读取逻辑补丁草案 + dry-run 验证
```

暂不允许进入：

```text
Stage C：9090 单 bot 灰度
Stage D：9091-9097 扩展
Stage E：Mac B 8081-8084 扩展
全量实盘上线
```

Claude 下一步按 Stage B 输出材料后，再提交 GPT 审核。
