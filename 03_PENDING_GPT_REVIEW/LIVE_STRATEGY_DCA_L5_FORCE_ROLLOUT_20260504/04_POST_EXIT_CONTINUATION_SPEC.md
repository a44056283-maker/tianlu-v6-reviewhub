# Post-Exit Continuation 观测规范
> 出山院代理生成 | 日期: 2026-05-04 | 状态: PENDING REVIEW

---

## 一、概念定义

### 什么是 post_exit_continuation？

**Post-Exit Continuation**（出场后延续观测）是一种保护机制：

> 在连续亏损发生后，系统进入 **观察期（Observation Period）**，期间禁止一切自学习收紧止盈、自动DCA、自动反向入场等「可能加剧亏损的自适应行为」，直到：

1. 观察期结束（24小时自动解除）
2. 出现连续2次盈利（主动解除）
3. 人工干预清除状态

---

## 二、状态机

```
                              ┌─────────────────────────────────┐
                              │                                 │
                              │  NORMAL ──(连续亏损>=2)──► OBSERVATION
                              │    ▲                             │
                              │    │ 连续2次盈利 或 24h到期       │
                              │    │ 或 人工清除                  │
                              │    └──────────────────────────────┘
                              │
                              │    OBSERVATION 内:
                              │    - 禁止: auto_profit_tighten
                              │    - 禁止: auto_dca
                              │    - 禁止: auto_reentry
                              │    - 正常: 规则P1/P2/P3（不经自学习）
                              └─────────────────────────────────┘
```

---

## 三、数据结构

### 存储位置
```python
# 全局变量（在 v65_autopilot.py 中声明）
_post_exit_continuation: dict = {}  # pair → PostExitContinuation
```

### Schema

```python
@dataclass
class PostExitContinuation:
    """
    出场后延续观测状态

    字段说明:
        observation_active: bool      观测期是否激活
        consecutive_losses: int      触发观测的连续亏损次数
        observation_start_ts: float   观测开始时间戳（Unix UTC）
        observation_end_ts: float     观测结束时间戳（Unix UTC）
        loss_threshold: int          触发阈值（配置值，默认2）
        observation_period_hours: int 观测期时长（配置值，默认24）
        actions_blocked: list[str]   被禁止的动作列表
        last_loss_pair: str          最后一次亏损涉及的交易对
        unlock_trigger: str | None   解锁触发原因
    """
    observation_active: bool = False
    consecutive_losses: int = 0
    observation_start_ts: float = 0.0
    observation_end_ts: float = 0.0
    loss_threshold: int = 2
    observation_period_hours: int = 24
    actions_blocked: list[str] = field(default_factory=lambda: [
        "auto_profit_tighten",  # 自学习自动收紧止盈（10%阈值）
        "auto_dca",             # 自动DCA加仓
        "auto_reentry",         # 自动反向入场
    ])
    last_loss_pair: str = ""
    unlock_trigger: str | None = None


# 序列化格式（用于持久化到 state 文件）
_POST_EXIT_CONTINUATION_PATH: Path = Path.home() / "freqtrade_console" / "state" / "post_exit_continuation.json"
```

### 持久化

```python
def _save_post_exit_continuation_state() -> None:
    """持久化 post_exit_continuation 到 JSON 文件"""
    try:
        _POST_EXIT_CONTINUATION_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = {pair: dict(state) for pair, state in _post_exit_continuation.items()}
        _POST_EXIT_CONTINUATION_PATH.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8"
        )
    except Exception as e:
        _log(f"[PostExitContinuation] 持久化失败: {e}")


def _load_post_exit_continuation_state() -> None:
    """从 JSON 文件加载 post_exit_continuation 状态（启动时调用）"""
    global _post_exit_continuation
    if not _POST_EXIT_CONTINUATION_PATH.exists():
        return
    try:
        data = json.loads(_POST_EXIT_CONTINUATION_PATH.read_text(encoding="utf-8"))
        for pair, state in data.items():
            # 过滤已过期的观测（防止状态文件残留）
            if state.get("observation_end_ts", 0) > time.time():
                _post_exit_continuation[pair] = state
            else:
                _log(f"[PostExitContinuation] 已过期，忽略: {pair}")
    except Exception as e:
        _log(f"[PostExitContinuation] 加载失败: {e}")


def _activate_post_exit_continuation(pair: str, consec_losses: int) -> None:
    """
    激活 post_exit_continuation 观测期

    调用时机: check_exit_conditions() 检测到连续亏损 >= loss_threshold 时
    """
    now = time.time()
    period_hours = _EXIT_GATE_OBSERVATION_HOURS  # 默认24
    _post_exit_continuation[pair] = {
        "observation_active": True,
        "consecutive_losses": consec_losses,
        "observation_start_ts": now,
        "observation_end_ts": now + period_hours * 3600,
        "loss_threshold": _EXIT_GATE_LOSS_THRESHOLD,
        "observation_period_hours": period_hours,
        "actions_blocked": _EXIT_GATE_BLOCKED_ACTIONS,
        "last_loss_pair": pair,
        "unlock_trigger": None,
    }
    _log(f"[PostExitContinuation] 🚦 激活观测期: {pair} "
         f"连续亏损{consec_losses}次, 观测期={period_hours}h, "
         f"禁止动作={_EXIT_GATE_BLOCKED_ACTIONS}")
    _save_post_exit_continuation_state()


def _deactivate_post_exit_continuation(pair: str, trigger: str) -> None:
    """
    解除 post_exit_continuation 观测期

    调用时机:
        1. 观察期到期（time.time() >= observation_end_ts）
        2. 连续2次盈利（主动解除）
        3. 人工干预（兵部操作）
    """
    if pair in _post_exit_continuation:
        _post_exit_continuation[pair]["observation_active"] = False
        _post_exit_continuation[pair]["unlock_trigger"] = trigger
        _log(f"[PostExitContinuation] ✅ 解除观测期: {pair} 原因={trigger}")
        # 延迟删除（保留日志记录）
        _post_exit_continuation.pop(pair, None)
        _save_post_exit_continuation_state()
```

---

## 四、连续亏损观察期逻辑

### 4.1 触发条件

```python
# 在 check_exit_conditions() 的「方案四」逻辑中触发
# 替换原 4670-4675 行

def _handle_consecutive_loss_tighten(pair: str, consec_losses: int, profit_pct: float):
    """
    处理连续亏损后的自学习收紧逻辑（已受 ExitDecisionGate 保护）

    流程:
    1. 检查是否已有 active 观测期 → 跳过
    2. 检查是否达到触发阈值(>=2) → 激活观测期
    3. 观测期内 → 拦截收紧阈值下发
    4. 观察期结束 → 清除状态，允许恢复正常
    """
    base = pair.split("/")[0]

    # Step 1: 已有激活的观测期
    current_state = _post_exit_continuation.get(pair)
    if current_state and current_state.get("observation_active"):
        end_ts = current_state.get("observation_end_ts", 0)
        if time.time() >= end_ts:
            # 观察期到期，自动解除
            _deactivate_post_exit_continuation(pair, trigger="observation_period_expired")
        else:
            # 仍在观测期：拦截收紧阈值
            _temp_thresh_override.pop(base, None)
            _log(f"[PostExitContinuation] 🚫 观测期内，拦截 {pair} 自学习收紧阈值下发")
            return

    # Step 2: 达到触发阈值 → 激活观测期
    if consec_losses >= _EXIT_GATE_LOSS_THRESHOLD:
        _activate_post_exit_continuation(pair, consec_losses)
        # 观测期激活后，拦截收紧阈值
        _temp_thresh_override.pop(base, None)
        return

    # Step 3: 未达阈值，正常下发（如果有的话）
    # 注意：此路径需配合 ExitDecisionGate.evaluate() 的返回值
    pass
```

### 4.2 观察期内的行为

| 行为 | 是否允许 | 说明 |
|------|----------|------|
| 规则P1触发（15%基准） | ✅ 允许 | 正常L4止盈规则，与自学习无关 |
| 规则P2触发（25%基准） | ✅ 允许 | 正常L4止盈规则 |
| 规则P3触发（35%基准） | ✅ 允许 | 正常L4止盈规则 |
| 自学习收紧至10%阈值 | ❌ 禁止 | `auto_profit_tighten` 被拦截 |
| 自动DCA加仓 | ❌ 禁止 | `auto_dca` 被拦截 |
| 自动反向入场 | ❌ 禁止 | `auto_reentry` 被拦截 |
| 人工手动入场 | ✅ 允许 | 人工决策不受限制 |
| ATR止损触发 | ✅ 允许 | 硬风控不可绕过 |
| 出山AI强制出场 | ✅ 允许 | 持仓卫士优先 |

### 4.3 观察期结束条件

```
OR
├── 条件A: time.time() >= observation_end_ts（24小时后自动到期）
├── 条件B: 连续2次盈利（_get_consecutive_losses(pair) == 0 后再检查1次）
└── 条件C: 兵部人工清除（调用 _deactivate_post_exit_continuation(pair, "manual")）
```

### 4.4 盈利后主动解除

```python
# 在 check_exit_conditions() 止盈成功后的回调中调用
def _on_profit_exit(pair: str, profit_pct: float):
    """
    止盈成功后的回调

    功能:
    1. 检查是否在观测期内
    2. 如果连续亏损计数器归零，检查是否可解除观测
    3. 记录交易结果到自学习数据库
    """
    consec_losses = _get_consecutive_losses(pair)
    if consec_losses == 0:
        # 盈利 → 连续亏损计数器归零
        # 检查是否有激活的观测期
        state = _post_exit_continuation.get(pair)
        if state and state.get("observation_active"):
            # 检查是否连续2次盈利（需要上一次也是盈利）
            if state.get("_profit_count", 0) >= 1:
                _deactivate_post_exit_continuation(pair, trigger="consecutive_profits_2")
            else:
                # 记录第一次盈利
                state["_profit_count"] = state.get("_profit_count", 0) + 1
                _log(f"[PostExitContinuation] {pair} 第一次盈利，连续计数={state['_profit_count']}")
    else:
        # 仍有亏损记录，重置盈利计数
        state = _post_exit_continuation.get(pair)
        if state:
            state["_profit_count"] = 0
```

---

## 五、被禁止的动作列表

```python
# _EXIT_GATE_BLOCKED_ACTIONS 定义了观察期内被禁止的行为

_EXIT_GATE_BLOCKED_ACTIONS = [
    "auto_profit_tighten",   # 自学习自动收紧止盈阈值（原方案四，10%触发）
    "auto_dca",              # 自动DCA加仓（连续亏损后不应该再加仓摊低成本）
    "auto_reentry",          # 自动反向入场（连续亏损后应等待市场确认）
]
```

### 5.1 auto_profit_tighten

**原问题代码**（已修复）:
```python
# 行 4670-4675（旧版有bug）
if consec_losses >= 2 and profit_pct > 5:
    thresh = 10  # 绕过门控直接写入
    _temp_thresh_override[base] = thresh
```

**修复后**:
```python
# 通过 ExitDecisionGate 门控，观测期内拒绝下发
gate = ExitDecisionGate()
gate_result = gate.evaluate(position, m1_payload, l5_payload)
if gate_result["action"] in ("block", "observe"):
    _temp_thresh_override.pop(base, None)  # 清除待下发阈值
```

### 5.2 auto_dca（待实现）

**规范**: 在 DCA L1/L2 触发检测前，增加观测期检查

```python
def _check_dca_in_observation(pair: str) -> tuple[bool, str]:
    """检查DCA是否在观测期内被禁止"""
    state = _post_exit_continuation.get(pair)
    if state and state.get("observation_active"):
        if "auto_dca" in state.get("actions_blocked", []):
            return True, f"观测期内禁止DCA（剩余{_remaining_obs_hours(state):.1f}h）"
    return False, ""
```

### 5.3 auto_reentry（待实现）

**规范**: 在入场决策前，增加观测期检查

```python
def _check_reentry_in_observation(pair: str) -> tuple[bool, str]:
    """检查反向入场是否在观测期内被禁止"""
    state = _post_exit_continuation.get(pair)
    if state and state.get("observation_active"):
        if "auto_reentry" in state.get("actions_blocked", []):
            return True, f"观测期内禁止反向入场（剩余{_remaining_obs_hours(state):.1f}h）"
    return False, ""
```

---

## 六、日志规范

### 激活观测期
```
[PostExitContinuation] 🚦 激活观测期: BTC/USDT 连续亏损2次, 观测期=24h, 禁止动作=['auto_profit_tighten', 'auto_dca', 'auto_reentry']
```

### 拦截收紧
```
[ExitDecisionGate] BLOCKED: auto_tighten_blocked_require_observation (consecutive_losses=3)
[PostExitContinuation] 🚫 观测期内，拦截 BTC/USDT 自学习收紧阈值下发
```

### 观测期到期
```
[PostExitContinuation] ✅ 解除观测期: BTC/USDT 原因=observation_period_expired
```

### 连续盈利解除
```
[PostExitContinuation] ✅ 解除观测期: BTC/USDT 原因=consecutive_profits_2
```

---

## 七、与现有代码的集成点

### 7.1 全局变量声明位置
```python
# v65_autopilot.py 约 1520 行附近（与 _temp_thresh_override 相邻）
_post_exit_continuation: dict = {}   # pair → PostExitContinuation
```

### 7.2 check_exit_conditions() 调用位置
```python
# 在「方案四」逻辑之前（约 4650 行）
# 调用 _handle_consecutive_loss_tighten()
```

### 7.3 止盈成功后的回调位置
```python
# 在 _rpc_force_exit() 成功返回后（约 4726 行附近）
# 调用 _on_profit_exit(pair, profit_pct)
```

### 7.4 启动时加载
```python
# 在 v65_autopilot.py 的初始化部分（约 150 行附近）
_load_post_exit_continuation_state()
```

### 7.5 定时持久化（可选，防止进程崩溃丢失状态）
```python
# 每小时自动保存一次
_last_save_ts = 0
_SAVE_INTERVAL = 3600  # 秒

def _auto_save_loop():
    global _last_save_ts
    while True:
        time.sleep(_SAVE_INTERVAL)
        if _post_exit_continuation:
            _save_post_exit_continuation_state()
            _log(f"[PostExitContinuation] 定时保存完成，共{len(_post_exit_continuation)}条")
```

---

## 八、验证检查清单

- [ ] `_post_exit_continuation` 全局变量已声明
- [ ] `_activate_post_exit_continuation()` 函数已实现
- [ ] `_deactivate_post_exit_continuation()` 函数已实现
- [ ] `_handle_consecutive_loss_tighten()` 替换原方案四逻辑
- [ ] `_on_profit_exit()` 在止盈成功后正确调用
- [ ] 观测期激活后，`_temp_thresh_override[base]` 不再被写入
- [ ] 观测期内 DCA 检测增加 `auto_dca` 拦截
- [ ] 观测期内反向入场检测增加 `auto_reentry` 拦截
- [ ] 状态持久化到 `post_exit_continuation.json`
- [ ] 启动时正确加载已激活的观测期（过滤过期项）
- [ ] 日志输出符合规范
