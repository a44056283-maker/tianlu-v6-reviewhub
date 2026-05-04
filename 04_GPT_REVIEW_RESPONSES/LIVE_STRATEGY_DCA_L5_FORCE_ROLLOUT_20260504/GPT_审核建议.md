# GPT_审核建议 · LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT_20260504

## 审核结论

**有条件通过，但只允许执行配置级止血验证，不批准直接应用代码补丁。**

本轮 Claude 交付完整，包含总报告、QA、回滚计划、PATCH.diff、TEST_LOG、PENDING_PATCH 与备份。方向正确，但代码补丁存在实现风险，不能直接进实盘。

---

## 一、允许立即执行的范围

### 允许 P0-1 / P0-2 进入“配置级止血灰度”

允许优先处理：

1. DOGE/USDT 自动新增入场冻结 24 小时；
2. SOL/USDT SHORT 自动 DCA 暂停。

但执行前必须先验证策略是否真的读取以下字段：

```json
"temporary_pair_freeze"
"dca_pause_rules"
```

如果 `v65_autopilot.py` / `api_autopilot.py` / FOttStrategy 没有读取这些字段，那么仅修改 overlay 配置不会生效，不能宣称止血完成。

执行条件：

1. 先 grep 确认读取路径；
2. 若没有读取逻辑，先只生成接入补丁草案，不要直接应用；
3. 若已有读取逻辑，可先灰度 9090 一个机器人；
4. 观察 15-30 分钟；
5. 再决定是否扩展到 9091-9097；
6. Mac B 8081-8084 需单独 SSH 人工执行，不能用 Mac A 占位文件代替。

---

## 二、暂不批准直接执行的代码补丁

### P0-3：DCA 不清除止损冷却补丁暂不批准

当前 PATCH.diff 中建议：

```python
if pair in _stoploss_state and not (_dca_triggered):
    del _stoploss_state[pair]
```

风险：

1. `_dca_triggered` 在该代码段上下文中未证明已定义，可能引发 `NameError`；
2. 如果变量作用域不一致，可能导致整个出场/加仓逻辑异常；
3. 该补丁只改删除条件，没有明确 DCA 与外部全平/止损事件的来源区分。

要求 Claude 重写为安全函数式补丁：

```python
def should_clear_stoploss_state(pair, reason, is_dca=False):
    if is_dca:
        return False
    return reason in {"external_full_exit", "manual_exit", "confirmed_stoploss"}
```

并补充 dry-run / 单元级检查后再提交。

---

### P0-4：ExitDecisionGate 当前实现暂不批准

PATCH.diff 当前写法在原逻辑中：

```python
gate = ExitDecisionGate()
```

风险：

1. 每次调用都新建 gate，状态不会持久化；
2. `_post_loss_observation` 和 `_post_exit_continuation` 不能跨调用生效；
3. 没有接入现有 `_dynamic_exit_state` / `_partial_exit_tracker`；
4. 不清楚会不会与现有 `_temp_thresh_override` 冲突。

要求：

1. 使用全局单例 `_EXIT_DECISION_GATE`；
2. 状态可持久化或至少和现有状态字典一致；
3. 不得绕过现有 P1/P2/P3；
4. 增加日志但不改变交易执行，先 shadow-only。

---

### P1-1：ForceGuard 审计日志暂不算完整

当前补丁只增加 `_log_force_action()`，但没有接入任何真实 force_entry / force_exit 调用点。

要求下一版必须列出并接入：

1. console_server.py 中所有 force 相关 endpoint；
2. OpenClaw / Feishu / 微信触发入口；
3. CLI / bot_manager 触发入口；
4. API 自动化触发入口。

默认策略：

```text
force_entry：默认禁止自动执行
force_exit：默认进入 pending queue + 人工确认
emergency_exit：只生成风险待确认，不直接执行
```

---

### P1-3：L5PromotionGate 语义需要修正

当前 `is_promotion_ready()` 里要求：

```python
auto_apply_to_live is False
```

这可以防止自动写实盘，但函数返回 True 可能会被误解为“可晋级”。

要求改成更清晰的双阶段语义：

```text
shadow_passed: bool
manual_review_required: true
live_apply_allowed: false
```

禁止任何自动写 live runtime / config overlay / 策略源码。

---

## 三、执行顺序建议

### 阶段 A：只读验证

1. grep 确认 `temporary_pair_freeze` 是否被读取；
2. grep 确认 `dca_pause_rules` 是否被读取；
3. 确认 12 个 overlay 的 JSON 语法；
4. 确认 Mac B 8081-8084 实际配置路径。

### 阶段 B：配置级灰度

1. 仅 9090 应用 DOGE freeze + SOL DCA pause；
2. 不改代码；
3. 不重启全部机器人；
4. 观察日志；
5. 确认配置生效。

### 阶段 C：扩展至 Mac A

若 9090 验证通过，再应用 9091-9097。

### 阶段 D：Mac B 手动执行

Mac B SSH 被拒绝，必须用户/Claude 单独在 Mac B 上执行，不得用 Mac A 占位补丁替代。

### 阶段 E：代码补丁重写后再审

P0-3、P0-4、P1-1、P1-2、P1-3 必须重写并重新提交 GPT 审核。

---

## 四、必须整改项

1. 证明 `temporary_pair_freeze` 与 `dca_pause_rules` 被策略读取；
2. 重写 P0-3，避免 `_dca_triggered` 未定义；
3. 重写 P0-4，ExitDecisionGate 必须是全局状态，不是每次新建；
4. ForceGuard 必须接入真实 force 调用点，而不是只写 helper；
5. L5PromotionGate 必须区分 shadow passed 与 live apply allowed；
6. Mac B 8081-8084 必须独立补齐实际配置，不接受占位符；
7. TEST_LOG 中的路径 `~/freqtrade_bots/user_data_*` 需确认真实存在，否则改为真实日志路径；
8. 所有代码补丁必须先 py_compile，再 shadow-only，再灰度。

---

## 五、最终结论

本轮交付：**有条件通过**。

允许立即推进：

```text
P0-1 DOGE freeze 与 P0-2 SOL DCA pause 的配置级灰度验证
```

暂不允许直接推进：

```text
P0-3 DCA冷却代码补丁
P0-4 ExitDecisionGate代码补丁
P1-1 ForceGuard代码补丁
P1-2 PostExitContinuation
P1-3 L5PromotionGate
全量 12 机器人重启
自动 force_entry / force_exit
L5 自动写实盘
```

下一步 Claude 应输出新的目录：

```text
03_PENDING_GPT_REVIEW/YYYYMMDD_HHMM_LIVE_ROLLOUT_STAGE_A_CONFIG_GREY/
```

内容包括：

```text
01_FREEZE_RULE_READ_PATH_PROOF.md
02_DCA_PAUSE_RULE_READ_PATH_PROOF.md
03_9090_GREY_APPLY_PLAN.md
04_VERIFY_LOG_PATHS.md
05_MACB_MANUAL_PATCH_PLAN.md
06_REVISED_CODE_PATCH_REQUIREMENTS.md
TEST_LOG.md
REVIEW_PACKAGE.zip
```

只有 Stage A 审核通过后，才允许进入真正实盘应用。
