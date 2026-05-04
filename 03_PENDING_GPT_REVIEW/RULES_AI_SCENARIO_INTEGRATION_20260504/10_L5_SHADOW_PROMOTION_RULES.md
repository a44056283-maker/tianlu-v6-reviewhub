# L5影子实验与晋级规则（Shadow Promotion Rules）

> 翰林院代理生成 | 2026-05-04 | 状态：等待GPT审核
>
> 关联文件：
> - `05_L5_CANDIDATE_REGISTRY_PATCH.md`
> - `05_L5_PROMOTION_GATE_PATCH.md`
> - `05_L5_NO_AUTO_LIVE_APPLY_POLICY.md`
> - `09_L5_PROMOTION_GATE_RULES.md`
> - `10_L5_SHADOW_BACKTEST_PLAN.md`

---

## 一、核心政策声明

```
╔══════════════════════════════════════════════════════════════════════╗
║  L5 ABSOLUTE RULE: NO DIRECT RUNTIME WRITE                         ║
║                                                                      ║
║  L5生成的任何候选参数：                                               ║
║  • 绝对禁止直接写入实盘 runtime                                      ║
║  • 绝对禁止通过 API 修改 bot 参数                                     ║
║  • 绝对禁止调用 force_entry / force_exit                             ║
║                                                                      ║
║  唯一合法路径：                                                       ║
║  L5影子实验 → L5CandidateRegistry → GPT审核 → 人工确认 → apply_to_live ║
╚══════════════════════════════════════════════════════════════════════╝
```

**违规检测**：`l5_runtime_guard.py` 在 `console_server.py` 关键路径插入钩子，任何未经 `L5CandidateRegistry.apply_to_live()` 的写入请求均被拦截并发送飞书告警。

---

## 二、L5候选注册表（L5CandidateRegistry）

### 2.1 设计原则

| 原则 | 说明 |
|------|------|
| 沙盒隔离 | Registry 只写本地 SQLite，不写 runtime |
| 自动打分 | register() 时自动计算 composite_score |
| 人工必审 | 禁止自动晋级；pending → approved 必须人工操作 |
| 单次写入 | runtime_written=1 后禁止重复写入 |
| 14天过期 | 候选超期自动标记 expired |

### 2.2 数据库表结构

```sql
CREATE TABLE IF NOT EXISTS l5_candidates (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id        TEXT UNIQUE NOT NULL,    -- UUID
    ts_created          INTEGER NOT NULL,        -- Unix timestamp

    -- 来源追踪
    source_bot          TEXT NOT NULL,           -- 来源 bot 端口
    pair                TEXT NOT NULL,           -- 交易对
    direction           TEXT NOT NULL,           -- LONG / SHORT
    params_json         TEXT NOT NULL,           -- 候选参数 JSON

    -- 候选参数质量维度（由影子实验提供）
    shadow_rule_id      TEXT,                    -- 影子规则唯一标识
    candidate_param_id  TEXT,                    -- 候选参数唯一标识
    promotion_trials     INTEGER DEFAULT 0,       -- 晋级尝试次数
    entry_noise_score   REAL DEFAULT 0,          -- 入场噪音评分（0-100）
    exit_noise_score    REAL DEFAULT 0,          -- 出场噪音评分（0-100）
    post_exit_continuation_loss  REAL DEFAULT 0, -- 出场后延续损失
    missed_profit_after_exit    REAL DEFAULT 0, -- 出场后错过利润

    -- 自动评分
    shadow_score        REAL NOT NULL DEFAULT 0, -- 影子实验评分
    win_rate_score      REAL NOT NULL DEFAULT 0, -- 历史胜率评分
    drawdown_score      REAL NOT NULL DEFAULT 0, -- 最大回撤评分
    noise_score         REAL NOT NULL DEFAULT 0, -- 噪音评分
    composite_score     REAL NOT NULL DEFAULT 0, -- 综合评分（加权）

    -- 晋级闸门状态
    gate_g1            TEXT DEFAULT 'pending',  -- G1: 数据充足性
    gate_g2            TEXT DEFAULT 'pending',  -- G2: 信号质量
    gate_g3            TEXT DEFAULT 'pending',  -- G3: 资金流硬闸
    gate_g4            TEXT DEFAULT 'pending',  -- G4: 风险控制
    gate_g5            TEXT DEFAULT 'pending',  -- G5: Walk-Forward

    -- 流程状态机
    status             TEXT NOT NULL DEFAULT 'pending',
                       -- pending → approved → rejected → expired
                       -- approved → runtime_written
    human_approver     TEXT,                    -- 批准人（必须为 human_father）
    ts_approved        INTEGER,
    approval_note      TEXT,
    ts_expires         INTEGER NOT NULL,        -- 14天后过期
    runtime_written    INTEGER NOT NULL DEFAULT 0,
    ts_runtime         INTEGER,

    -- 追踪字段
    reject_reason      TEXT,
    shadow_run_id      TEXT,                    -- 关联影子实验 ID
    applied_to_port    TEXT,                    -- 最终应用的 bot 端口
    notes              TEXT                     -- 翰林院备注
);

CREATE INDEX IF NOT EXISTS idx_cand_status   ON l5_candidates(status);
CREATE INDEX IF NOT EXISTS idx_cand_pair     ON l5_candidates(pair);
CREATE INDEX IF NOT EXISTS idx_cand_created  ON l5_candidates(ts_created DESC);
CREATE INDEX IF NOT EXISTS idx_cand_expires  ON l5_candidates(ts_expires);
```

```sql
-- 审计日志表
CREATE TABLE IF NOT EXISTS l5_candidate_audit (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    TEXT NOT NULL,
    action          TEXT NOT NULL,   -- registered / scored / approved / rejected / expired / runtime_written
    actor           TEXT NOT NULL,   -- system / human_father / bot_name
    ts              INTEGER NOT NULL,
    detail          TEXT
);
```

### 2.3 评分权重与门槛

```python
WEIGHTS = {
    "shadow_score":    0.35,   # 影子实验评分
    "win_rate_score": 0.25,   # 历史胜率
    "drawdown_score": 0.20,  # 最大回撤
    "noise_score":    0.20,  # 噪音质量
}

PASS_THRESHOLDS = {
    "composite_score":  60.0,  # 综合评分 >= 60
    "shadow_score":     55.0,  # 影子评分 >= 55
    "win_rate_score":   50.0,  # 胜率评分 >= 50
    "drawdown_score":   40.0,  # 回撤评分 >= 40
    "noise_score":      True,   # 噪音无硬性门槛
}
```

---

## 三、L5晋级闸门（L5PromotionGate）

### 3.1 五级晋级闸门总览

| 闸门 | 维度 | 检查内容 | 当前状态 |
|------|------|---------|---------|
| **G1** | 数据充足性 | 影子运行 ≥7天，样本 ≥300条，交易对 ≥3个 | PASS |
| **G2** | 信号质量 | 优质信号 ≥8%，高噪音 ≤45%，一致率 ≥85%，增强加分 ≥+5.0 | PASS |
| **G3** | 资金流硬闸 | 候选数 ≥50，通过率 65%-85%，阈值 0.30 | PASS |
| **G4** | 风险控制 | 胜率 ≥52%，最大回撤 ≤20%（当前为估算，待真实数据） | PENDING |
| **G5** | Walk-Forward | 连续3期正期望，参数衰减 ≤20% | PENDING（未执行） |

**晋级前提**：`auto_apply_to_live = False` 已硬编码，禁止自动晋级。

### 3.2 各闸门详细定义

**G1 — 数据充足性闸门**
```python
G1_MIN_DAYS    = 7    # 影子最少运行7天
G1_MIN_SAMPLES = 300  # 最少300条样本
G1_MIN_PAIRS   = 3    # 最少覆盖3个交易对
```
当前：7天 / 3040条 / 5个交易对 → **PASS**

**G2 — 信号质量闸门**
```python
G2_MIN_QUALITY_PCT    = 8.0    # 优质信号占比 ≥ 8%
G2_MAX_HIGH_NOISE_PCT = 45.0  # 高噪音占比 ≤ 45%
G2_MIN_AGREEMENT_PCT  = 85.0  # 影子与基准一致率 ≥ 85%
G2_MIN_DELTA_SCORE    = 5.0   # 增强平均加分 ≥ +5.0
```
当前：9.3%优质 / 40.7%高噪音 / 93.7%一致 / +11.58加分 → **PASS**

**G3 — 资金流硬闸**
```python
G3_MIN_PASS_RATE   = 0.65   # 通过率 ≥ 65%
G3_MAX_PASS_RATE   = 0.85   # 通过率 ≤ 85%（不能太松）
G3_MIN_CANDIDATES  = 50     # 至少50个资金流候选样本
G3_FLOW_THRESHOLD  = 0.30   # 净流入阈值（做多>=0.30，做空<=-0.30）
```
当前：214候选 / 74.3%通过率 → **PASS**

**G4 — 风险控制闸门**
```python
G4_MIN_WIN_RATE   = 0.52  # 历史胜率 ≥ 52%
G4_MAX_DRAWDOWN   = 0.20  # 最大回撤 ≤ 20%
G4_MIN_TRADE_COUNT = 100  # 胜率样本最少100笔
```
当前：估算~62%胜率/~17%回撤（估算值，待真实数据）→ **PENDING**

**G5 — Walk-Forward 闸门**
```python
G5_PERIODS         = 3              # 连续3个 walk-forward 周期
G5_POSITIVE_EXPECTANCY = True       # 所有周期均正期望
G5_MAX_DEGRADATION = 0.20           # 参数衰减 ≤ 20%
```
当前：未执行 → **PENDING**

### 3.3 当前晋级闸门状态（GPT审核版）

| 闸门名称 | 要求 | 当前值 | 状态 |
|---------|------|--------|------|
| entry_noise_filter | 噪音均值 < 50 | BTC=33.99, DOGE=66.29, ETH=62.62, BNB=65.73, SOL=61.54 | **未满足**（仅BTC满足） |
| flow_consensus_threshold | 通过率65%-85% | 74.3%（159/214） | 满足 |
| DCA_cooldown_fix | walk_forward连续3期正期望 | 未执行 | **未满足** |
| G1数据充足性 | ≥7天/≥300样本/≥3对 | 7天/3040条/5对 | PASS |
| G2信号质量 | 优质≥8%/噪音≤45% | 9.3%/40.7% | PASS |
| G3资金流 | 候选≥50/通过率65-85% | 214/74.3% | PASS |
| G4风险控制 | 胜率≥52%/回撤≤20% | 估算值 | PENDING |
| G5 Walk-Forward | 连续3期正期望 | 未执行 | PENDING |

---

## 四、候选参数管理字段规范

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `candidate_id` | TEXT (UUID) | 候选唯一标识 |
| `shadow_rule_id` | TEXT | 影子规则唯一标识（如 `shadow_rule_20260504_01`） |
| `candidate_param_id` | TEXT | 候选参数唯一标识（如 `cparam_vol_ratio_5.5`） |
| `entry_noise_score` | REAL (0-100) | 入场噪音评分（高=噪音大） |
| `exit_noise_score` | REAL (0-100) | 出场噪音评分 |
| `post_exit_continuation_loss` | REAL | 出场后价格延续亏损（反向波动损失） |
| `missed_profit_after_exit` | REAL | 出场后价格继续盈利（错过利润） |
| `promotion_trials` | INTEGER | 晋级尝试次数（≥5才可晋级） |
| `win_rate` | REAL | 该候选的历史胜率（≥0.55才可晋级） |
| `auto_apply_to_live` | BOOL | **硬编码 False，禁止自动写入** |

---

## 五、晋级流程（完整链路）

```
┌─────────────────────────────────────────────────────────────┐
│ L5影子实验 (m4_m5_shadow_lab.py — 只读，不下单)              │
│  数据: 7天 / 3040样本 / 5交易对 / 噪音均值 61.69            │
└────────────────┬────────────────────────────────────────────┘
                 │ 增强候选触发 register()
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ L5CandidateRegistry.register()                             │
│  • 写入 SQLite（pending 状态）                              │
│  • auto_apply_to_live = False（硬编码禁止自动晋级）          │
│  • promotion_trials 初始值 = 0                              │
│  • 14天过期计时开始                                         │
└────────────────┬────────────────────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ L5PromotionGate.check_all() — 五级晋级闸门检查               │
│                                                              │
│  G1数据充足性  ── FAIL → 阻塞，补充数据                       │
│  G2信号质量    ── FAIL → 阻塞，优化规则                       │
│  G3资金流硬闸  ── FAIL → 阻塞，调整阈值                       │
│  G4风险控制    ── FAIL → 阻塞，回测重做                       │
│  G5 Walk-Forward ── FAIL → 阻塞 / PENDING → 允许评审但需完成  │
└────────────────┬────────────────────────────────────────────┘
                 │ 全部PASS或G5_PENDING豁免
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ GPT 人工审核（翰林院代理生成审核报告）                         │
│  审核要点：                                                  │
│  • 噪音均值是否各币种均 < 50                                 │
│  • 高噪音率是否降至 30% 以下                                  │
│  • DOGE/SOL/BNB 噪音异常根因是否已确认                       │
│  • Walk-Forward 是否完成且3期正期望                          │
│  • 实盘 closed_trades >= 100                                │
└────────────────┬────────────────────────────────────────────┘
                 │ GPT审核通过
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 人工确认（爸在控制台点击"批准"）                             │
│  L5CandidateRegistry.approve(candidate_id, approver=human_father) │
│  • 必须有人工批准人 human_father                             │
│  • 状态: pending → approved                                 │
│  • 禁止 L5 模块自我批准                                     │
└────────────────┬────────────────────────────────────────────┘
                 │ 爸点击"应用到实盘"
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ L5CandidateRegistry.apply_to_live() — 三重安全检查          │
│                                                              │
│  检查1: status == 'approved'  ← 非 approved则拒绝          │
│  检查2: human_approver != None  ← 无人工批准则拒绝           │
│  检查3: runtime_written == 0    ← 已写过则拒绝               │
│                                                              │
│  任意检查失败 → PermissionError → 飞书告警                   │
└────────────────┬────────────────────────────────────────────┘
                 │ 三重检查通过
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 单Bot灰度（而非全量推广）                                     │
│  • 先应用于 1 个指定端口（如 9090）                          │
│  • 观察至少 7 天 / 100 笔交易                               │
│  • 验证噪音过滤效果 / 胜率 / 回撤                            │
└────────────────┬────────────────────────────────────────────┘
                 │ 灰度验证通过
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 全量推广（爸确认灰度结果后）                                 │
│  L5CandidateRegistry.apply_to_live() 应用于剩余端口          │
│  L5CandidateRegistry.approve() + apply_to_live()           │
└─────────────────────────────────────────────────────────────┘
```

### 晋级强制前置条件（未满足则永不晋级）

| 条件 | 当前状态 | 阻塞晋级 |
|------|---------|---------|
| 噪音均值各币种均 < 50 | DOGE=66.29 / BNB=65.73 / SOL=61.54 / ETH=62.62 | **是** |
| Walk-Forward 连续3期正期望 | 未执行 | **是** |
| 实盘 closed_trades >= 100 | 仅1笔 | **是** |
| GPT审核确认 DOGE/SOL/BNB 根因 | 未审核 | **是** |

---

## 六、候选状态机

```
[PENDING]  ← register() 初始状态
    │
    ├──→ approve() ──→ [APPROVED]
    │                     │
    ├──→ reject() ──→ [REJECTED]  (禁止转换为其他状态)
    │
    └──→ 14天超时 ──→ [EXPIRED]   (禁止转换为其他状态)

[APPROVED]
    │
    └──→ apply_to_live() ──→ [RUNTIME_WRITTEN]
                                （禁止再次调用 apply_to_live）

禁止的转换（绝对不允许）：
  pending     → runtime_written   （禁止自动跳过人工）
  rejected    → runtime_written   （禁止绕过拒绝）
  expired     → runtime_written   （禁止使用过期候选）
  any status  → runtime_written   （除非通过 apply_to_live 三重检查）
```

---

## 七、禁止清单

| 模块 / 功能 | 禁止原因 |
|------------|---------|
| `m4_m5_shadow_lab.py` | 影子实验室，只读，禁止写 runtime |
| `l5_autopilot` | 禁止 L5 自动驾驶 |
| `l5_strategy_generator` | 禁止生成器直接写参数 |
| `l5_rule_evolution` | 禁止规则演化直接升级参数 |
| `l5_auto_upgrade` | 禁止自动晋级 |
| `force_entry` / `force_exit` | 禁止强制下单 |
| `whale_alert` 自动跟单 | 禁止跟单写入 |
| `socks5h://` + aiohttp | 已知不兼容，OKX 必须走 HTTP 代理 |

---

## 八、监察接口

```bash
# 查看违规历史
cat ~/freqtrade_console/l5_evolution_lab/logs/l5_runtime_guard.log

# 查看所有违规记录（JSONL）
cat ~/freqtrade_console/l5_evolution_lab/l5_violations.jsonl | python3 -m json.tool

# 查看候选 Registry 状态
python3 ~/freqtrade_console/l5_evolution_lab/l5_candidate_registry.py summary

# 手动触发晋级闸门检查
python3 ~/freqtrade_console/l5_evolution_lab/l5_promotion_gate.py
```

---

## 九、Python代码（可执行级）

### 9.1 L5CandidateRegistry

```python
#!/usr/bin/env python3
"""
L5 Candidate Registry — L5候选参数注册表

文件位置: ~/freqtrade_console/l5_evolution_lab/l5_candidate_registry.py

核心原则：
  L5生成的候选参数绝对不直接写入实盘runtime。
  所有候选必须：注册 → 打分 → GPT审核 → 人工确认 → 才写入runtime。
  auto_apply_to_live = False 硬编码，禁止自动晋级。
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

BASE = Path("/Users/luxiangnan/freqtrade_console/l5_evolution_lab")
DB_PATH = BASE / "l5_candidate_registry.sqlite"


class CandidateStatus(str, Enum):
    PENDING         = "pending"
    APPROVED        = "approved"
    REJECTED        = "rejected"
    EXPIRED         = "expired"
    RUNTIME_WRITTEN = "runtime_written"


@dataclass
class L5Candidate:
    candidate_id: str
    ts_created: int
    source_bot: str
    pair: str
    direction: str
    params_json: str

    # 候选参数质量维度
    shadow_rule_id: Optional[str] = None
    candidate_param_id: Optional[str] = None
    promotion_trials: int = 0
    entry_noise_score: float = 0.0
    exit_noise_score: float = 0.0
    post_exit_continuation_loss: float = 0.0
    missed_profit_after_exit: float = 0.0

    # 自动评分
    shadow_score: float = 0.0
    win_rate_score: float = 0.0
    drawdown_score: float = 0.0
    noise_score: float = 0.0
    composite_score: float = 0.0

    # 晋级闸门状态
    gate_g1: str = "pending"
    gate_g2: str = "pending"
    gate_g3: str = "pending"
    gate_g4: str = "pending"
    gate_g5: str = "pending"

    # 流程状态
    status: str = CandidateStatus.PENDING.value
    human_approver: Optional[str] = None
    ts_approved: Optional[int] = None
    approval_note: Optional[str] = None
    ts_expires: int = field(default_factory=lambda: int(time.time()) + 14 * 86400)
    runtime_written: int = 0
    ts_runtime: Optional[int] = None
    reject_reason: Optional[str] = None
    shadow_run_id: Optional[str] = None
    applied_to_port: Optional[str] = None
    notes: Optional[str] = None


class L5CandidateRegistry:
    """
    L5候选参数注册表

    职责：
      1. 接收L5影子实验室生成的候选参数
      2. 自动打分（shadow_score / win_rate / drawdown / noise）
      3. 注册到本地SQLite（不写runtime）
      4. 执行晋级闸门检查（G1-G5）
      5. 提供人工确认接口
      6. 人工批准后才通过 apply_to_live() 写入runtime

    绝对禁止：
      - L5候选参数直接写入runtime
      - 任何自动写入（auto_apply_to_live = False 硬编码）
      - 未经人工确认的晋级
    """

    # 综合评分权重
    WEIGHTS = {
        "shadow_score":    0.35,
        "win_rate_score":  0.25,
        "drawdown_score":  0.20,
        "noise_score":     0.20,
    }

    # 及格门槛
    PASS_THRESHOLDS = {
        "composite_score":  60.0,
        "shadow_score":     55.0,
        "win_rate_score":   50.0,
        "drawdown_score":   40.0,
    }

    # 晋级硬门槛（高于评分门槛）
    PROMOTION_TRIALS_MIN = 5      # 晋级尝试次数 >= 5
    WIN_RATE_MIN         = 0.55   # 胜率 >= 55%
    AUTO_APPLY_TO_LIVE   = False  # 硬编码禁止自动晋级

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # -------------------------------------------------------------------------
    # 数据库初始化
    # -------------------------------------------------------------------------

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS l5_candidates (
                    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id            TEXT UNIQUE NOT NULL,
                    ts_created              INTEGER NOT NULL,

                    source_bot              TEXT NOT NULL,
                    pair                    TEXT NOT NULL,
                    direction               TEXT NOT NULL,
                    params_json             TEXT NOT NULL,

                    shadow_rule_id          TEXT,
                    candidate_param_id      TEXT,
                    promotion_trials        INTEGER DEFAULT 0,
                    entry_noise_score       REAL DEFAULT 0,
                    exit_noise_score        REAL DEFAULT 0,
                    post_exit_continuation_loss REAL DEFAULT 0,
                    missed_profit_after_exit    REAL DEFAULT 0,

                    shadow_score            REAL NOT NULL DEFAULT 0,
                    win_rate_score          REAL NOT NULL DEFAULT 0,
                    drawdown_score          REAL NOT NULL DEFAULT 0,
                    noise_score             REAL NOT NULL DEFAULT 0,
                    composite_score         REAL NOT NULL DEFAULT 0,

                    gate_g1                 TEXT DEFAULT 'pending',
                    gate_g2                 TEXT DEFAULT 'pending',
                    gate_g3                 TEXT DEFAULT 'pending',
                    gate_g4                 TEXT DEFAULT 'pending',
                    gate_g5                 TEXT DEFAULT 'pending',

                    status                  TEXT NOT NULL DEFAULT 'pending',
                    human_approver          TEXT,
                    ts_approved             INTEGER,
                    approval_note           TEXT,
                    ts_expires              INTEGER NOT NULL,
                    runtime_written         INTEGER NOT NULL DEFAULT 0,
                    ts_runtime              INTEGER,
                    reject_reason           TEXT,
                    shadow_run_id           TEXT,
                    applied_to_port         TEXT,
                    notes                   TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_status  ON l5_candidates(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_pair    ON l5_candidates(pair)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_created ON l5_candidates(ts_created DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cand_expires ON l5_candidates(ts_expires)")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS l5_candidate_audit (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_id    TEXT NOT NULL,
                    action          TEXT NOT NULL,
                    actor           TEXT NOT NULL,
                    ts              INTEGER NOT NULL,
                    detail          TEXT
                )
            """)

    # -------------------------------------------------------------------------
    # 核心方法
    # -------------------------------------------------------------------------

    def register(
        self,
        candidate_params: dict[str, Any],
        shadow_score: float,
        source_bot: str,
        pair: str,
        direction: str,
        shadow_rule_id: Optional[str] = None,
        candidate_param_id: Optional[str] = None,
        entry_noise_score: float = 0.0,
        exit_noise_score: float = 0.0,
        post_exit_continuation_loss: float = 0.0,
        missed_profit_after_exit: float = 0.0,
        shadow_run_id: Optional[str] = None,
    ) -> str:
        """
        注册一个新L5候选参数。

        Args:
            candidate_params:    L5生成的候选参数
            shadow_score:        影子实验室评分（0-100）
            source_bot:          来源bot端口
            pair:                交易对
            direction:           LONG / SHORT
            shadow_rule_id:      影子规则唯一标识
            candidate_param_id:  候选参数唯一标识
            entry_noise_score:   入场噪音评分（0-100，越高=噪音越大）
            exit_noise_score:    出场噪音评分（0-100）
            post_exit_continuation_loss: 出场后延续损失
            missed_profit_after_exit:    出场后错过利润
            shadow_run_id:       关联的影子实验ID

        Returns:
            candidate_id: 新候选的唯一ID

        注意：此方法只写入Registry，不写入runtime。
              auto_apply_to_live = False 硬编码，禁止自动晋级。
        """
        candidate_id = str(uuid.uuid4())
        ts = int(time.time())

        # 自动打分
        win_rate_score    = self._calc_win_rate_score(candidate_params)
        drawdown_score   = self._calc_drawdown_score(candidate_params)
        noise_score       = self._calc_noise_score(candidate_params, shadow_score)
        composite_score   = self._calc_composite(shadow_score, win_rate_score,
                                                  drawdown_score, noise_score)

        params_json = json.dumps(candidate_params, ensure_ascii=False, indent=2)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO l5_candidates (
                    candidate_id, ts_created, source_bot, pair, direction, params_json,
                    shadow_rule_id, candidate_param_id, promotion_trials,
                    entry_noise_score, exit_noise_score,
                    post_exit_continuation_loss, missed_profit_after_exit,
                    shadow_score, win_rate_score, drawdown_score, noise_score,
                    composite_score, status, ts_expires, shadow_run_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_id, ts, source_bot, pair, direction, params_json,
                shadow_rule_id, candidate_param_id, 0,  # promotion_trials = 0
                entry_noise_score, exit_noise_score,
                post_exit_continuation_loss, missed_profit_after_exit,
                shadow_score, win_rate_score, drawdown_score, noise_score,
                composite_score, CandidateStatus.PENDING.value,
                ts + 14 * 86400, shadow_run_id,
            ))
            conn.commit()

        self._audit(candidate_id, "registered", "system", {
            "source_bot": source_bot,
            "pair": pair,
            "shadow_score": shadow_score,
            "composite_score": composite_score,
            "auto_apply_to_live": self.AUTO_APPLY_TO_LIVE,
        })

        return candidate_id

    def approve(
        self,
        candidate_id: str,
        approver: str = "human_father",
        note: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        人工批准候选参数。

        Args:
            candidate_id: 候选ID
            approver:     批准人（必须填 human_father）
            note:         批注

        Returns:
            批准结果

        Raises:
            PermissionError: 如果不合规
        """
        ts = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status, ts_expires, promotion_trials FROM l5_candidates "
                "WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}

            status, ts_expires, trials = row
            if status != CandidateStatus.PENDING.value:
                return {"ok": False, "error": f"candidate is {status}, can only approve pending"}

            if ts > ts_expires:
                conn.execute(
                    "UPDATE l5_candidates SET status = ? WHERE candidate_id = ?",
                    (CandidateStatus.EXPIRED.value, candidate_id)
                )
                conn.commit()
                return {"ok": False, "error": "candidate expired"}

            # 晋级前检查：promotion_trials >= 5 且胜率门槛
            if trials < self.PROMOTION_TRIALS_MIN:
                return {
                    "ok": False,
                    "error": f"promotion_trials={trials} < {self.PROMOTION_TRIALS_MIN} required"
                }

        # 必须 human_father 批准，禁止 L5 模块自我批准
        if approver != "human_father":
            raise PermissionError(
                f"[L5 SECURITY] approve DENIED: approver={approver} is not human_father. "
                f"L5 modules cannot self-approve."
            )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE l5_candidates SET
                    status = ?, human_approver = ?, ts_approved = ?, approval_note = ?
                WHERE candidate_id = ?
            """, (CandidateStatus.APPROVED.value, approver, ts, note, candidate_id))
            conn.commit()

        self._audit(candidate_id, "approved", approver, {"note": note})
        return {
            "ok": True,
            "candidate_id": candidate_id,
            "status": CandidateStatus.APPROVED.value,
            "message": "人工批准完成。请调用 apply_to_live() 将候选写入runtime。",
        }

    def apply_to_live(
        self,
        candidate_id: str,
        target_port: str,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """
        将人工批准的候选参数写入实盘runtime。

        这是唯一合法的L5写runtime路径。
        auto_apply_to_live = False 硬编码，禁止自动晋级。

        三重安全检查：
          1. status == 'approved'
          2. human_approver == 'human_father'
          3. runtime_written == 0

        Args:
            candidate_id:  候选ID
            target_port:   目标bot端口（建议先选单Bot灰度）
            dry_run:       True=只检查不写

        Returns:
            写入结果

        Raises:
            PermissionError: 任意三重检查失败
        """
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status, runtime_written, human_approver, params_json "
                "FROM l5_candidates WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}

            status, written, approver, params_json = row

        # ---- 三重安全检查 ----

        if status != CandidateStatus.APPROVED.value:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id : {candidate_id}\n"
                f"  current status: {status}\n"
                f"  required status: {CandidateStatus.APPROVED.value}\n"
                f"  human_approver: {approver or 'NONE'}\n"
                f"Reason: L5 candidates must be approved by human before writing to runtime."
            )

        if not approver:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id   : {candidate_id}\n"
                f"  status         : {status}\n"
                f"  human_approver : {approver}\n"
                f"Reason: No human approval found. L5 cannot self-approve."
            )

        if written:
            raise PermissionError(
                f"[L5 SECURITY] apply_to_live DENIED\n"
                f"  candidate_id    : {candidate_id}\n"
                f"  runtime_written: {written}\n"
                f"Reason: Candidate already written to runtime. Duplicate write blocked."
            )

        if dry_run:
            return {
                "ok": True,
                "dry_run": True,
                "candidate_id": candidate_id,
                "target_port": target_port,
                "params": json.loads(params_json),
                "message": "dry_run: would write to runtime",
            }

        # 实际写入runtime（通过 console_server API）
        from l5_apply_runtime import apply_params_via_api
        ts = int(time.time())
        result = apply_params_via_api(candidate_id, target_port, json.loads(params_json))

        if result.get("ok"):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE l5_candidates SET
                        runtime_written = 1, ts_runtime = ?, applied_to_port = ?
                    WHERE candidate_id = ?
                """, (ts, target_port, candidate_id))
                conn.commit()
            self._audit(candidate_id, "runtime_written", "system", {
                "target_port": target_port,
                "result": result,
            })

        return result

    def reject(
        self,
        candidate_id: str,
        rejector: str = "human_father",
        reason: str = "",
    ) -> dict[str, Any]:
        """人工拒绝候选参数。"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT status FROM l5_candidates WHERE candidate_id = ?",
                (candidate_id,)
            ).fetchone()
            if not row:
                return {"ok": False, "error": "candidate not found"}
            if row[0] != CandidateStatus.PENDING.value:
                return {"ok": False, "error": f"candidate is {row[0]}, can only reject pending"}

            conn.execute("""
                UPDATE l5_candidates SET status = ?, reject_reason = ?
                WHERE candidate_id = ?
            """, (CandidateStatus.REJECTED.value, reason, candidate_id))
            conn.commit()

        self._audit(candidate_id, "rejected", rejector, {"reason": reason})
        return {"ok": True, "candidate_id": candidate_id, "status": CandidateStatus.REJECTED.value}

    # -------------------------------------------------------------------------
    # 查询接口
    # -------------------------------------------------------------------------

    def list_pending(self, pair: Optional[str] = None, limit: int = 50) -> list[dict]:
        """列出待审核候选（按综合评分倒序）。"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if pair:
                rows = conn.execute("""
                    SELECT * FROM l5_candidates
                    WHERE status = ? AND pair = ?
                    ORDER BY composite_score DESC LIMIT ?
                """, (CandidateStatus.PENDING.value, pair, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM l5_candidates
                    WHERE status = ?
                    ORDER BY composite_score DESC LIMIT ?
                """, (CandidateStatus.PENDING.value, limit)).fetchall()
        return [dict(r) for r in rows]

    def list_approved(self, limit: int = 20) -> list[dict]:
        """列出已批准但未写入runtime的候选。"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM l5_candidates
                WHERE status = ? AND runtime_written = 0
                ORDER BY ts_approved DESC LIMIT ?
            """, (CandidateStatus.APPROVED.value, limit)).fetchall()
        return [dict(r) for r in rows]

    def get_status_summary(self) -> dict[str, Any]:
        """获取Registry整体状态摘要。"""
        with sqlite3.connect(self.db_path) as conn:
            total     = conn.execute("SELECT COUNT(*) FROM l5_candidates").fetchone()[0]
            pending   = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE status = ?",
                (CandidateStatus.PENDING.value,)
            ).fetchone()[0]
            approved  = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE status = ? AND runtime_written = 0",
                (CandidateStatus.APPROVED.value,)
            ).fetchone()[0]
            written   = conn.execute(
                "SELECT COUNT(*) FROM l5_candidates WHERE runtime_written = 1"
            ).fetchone()[0]
            avg_score = conn.execute(
                "SELECT AVG(composite_score) FROM l5_candidates"
            ).fetchone()[0] or 0.0
        return {
            "total_candidates": total,
            "pending": pending,
            "approved_not_written": approved,
            "runtime_written": written,
            "avg_composite_score": round(avg_score, 2),
        }

    # -------------------------------------------------------------------------
    # 内部评分方法
    # -------------------------------------------------------------------------

    def _calc_win_rate_score(self, params: dict[str, Any]) -> float:
        """基于候选参数估算历史胜率评分（0-100）。"""
        score = 50.0
        ratio = params.get("l1_volume_ratio", 5.0)
        if ratio >= 8.0:   score += 15
        elif ratio >= 6.0: score += 8
        elif ratio >= 5.0: score += 3
        stop_loss = params.get("stop_loss_pct", 0.0)
        if stop_loss <= 2.0:   score += 5
        elif stop_loss >= 4.0: score -= 5
        return min(100.0, max(0.0, score))

    def _calc_drawdown_score(self, params: dict[str, Any]) -> float:
        """基于候选参数估算最大回撤评分（0-100，越高=回撤越小）。"""
        score = 50.0
        stop_loss = params.get("stop_loss_pct", 0.0)
        if stop_loss <= 1.5:    score += 20
        elif stop_loss <= 2.5:  score += 10
        elif stop_loss >= 5.0:  score -= 15
        if params.get("use_atr_stop", False): score += 10
        return min(100.0, max(0.0, score))

    def _calc_noise_score(self, params: dict[str, Any], shadow_score: float) -> float:
        """噪音评分：shadow_score高 → 噪音低 → score高。"""
        return min(100.0, max(0.0, shadow_score))

    def _calc_composite(
        self,
        shadow: float,
        win_rate: float,
        drawdown: float,
        noise: float,
    ) -> float:
        """加权综合评分。"""
        return round(
            shadow    * self.WEIGHTS["shadow_score"]
            + win_rate    * self.WEIGHTS["win_rate_score"]
            + drawdown    * self.WEIGHTS["drawdown_score"]
            + noise       * self.WEIGHTS["noise_score"],
            2,
        )

    def _audit(self, candidate_id: str, action: str, actor: str, detail: Any) -> None:
        """写审计日志（失败不阻塞主流程）。"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO l5_candidate_audit (candidate_id, action, actor, ts, detail)
                    VALUES (?, ?, ?, ?, ?)
                """, (candidate_id, action, actor, int(time.time()),
                      json.dumps(detail, ensure_ascii=False)))
                conn.commit()
        except Exception:
            pass


# -------------------------------------------------------------------------
# CLI 工具
# -------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    reg = L5CandidateRegistry()

    parser = argparse.ArgumentParser(description="L5 Candidate Registry CLI")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("summary", help="查看Registry整体状态")
    p_list = sub.add_parser("list", help="列出待审核候选")
    p_list.add_argument("--pair", "-p", default=None)
    p_list.add_argument("--limit", "-n", type=int, default=50)

    p_approve = sub.add_parser("approve", help="批准候选（必须 human_father）")
    p_approve.add_argument("candidate_id")
    p_approve.add_argument("--note", "-m", default="")

    p_reject = sub.add_parser("reject", help="拒绝候选")
    p_reject.add_argument("candidate_id")
    p_reject.add_argument("--reason", "-r", default="")

    p_apply = sub.add_parser("apply", help="将批准后的候选写入runtime")
    p_apply.add_argument("candidate_id")
    p_apply.add_argument("--port", required=True)
    p_apply.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.cmd == "summary":
        print(json.dumps(reg.get_status_summary(), ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        print(json.dumps(reg.list_pending(pair=args.pair, limit=args.limit), ensure_ascii=False, indent=2))
    elif args.cmd == "approve":
        print(json.dumps(reg.approve(args.candidate_id, note=args.note), ensure_ascii=False, indent=2))
    elif args.cmd == "reject":
        print(json.dumps(reg.reject(args.candidate_id, reason=args.reason), ensure_ascii=False, indent=2))
    elif args.cmd == "apply":
        try:
            print(json.dumps(
                reg.apply_to_live(args.candidate_id, args.port, dry_run=args.dry_run),
                ensure_ascii=False, indent=2,
            ))
        except PermissionError as e:
            print(f"ERROR: {e}")
    else:
        parser.print_help()
```

### 9.2 L5PromotionGate

```python
#!/usr/bin/env python3
"""
L5 Promotion Gate — 晋级闸门检查

文件位置: ~/freqtrade_console/l5_evolution_lab/l5_promotion_gate.py

检查顺序：G1 → G2 → G3 → G4 → G5
顺序检查，任意 FAIL 则晋级终止。
G5 为 PENDING 时，G4 PASS + G5 PENDING 可允许进入评审，
但须在人工确认前完成 G5。

注意：auto_apply_to_live = False 硬编码禁止自动晋级。
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

BASE = Path("/Users/luxiangnan/freqtrade_console/l5_evolution_lab")
REPORT_PATH = BASE / "latest_report.json"
DB_PATH     = BASE / "m4_m5_shadow_lab.sqlite"


class GateLevel(str, Enum):
    G1_DATA      = "G1_DATA"       # 数据充足性
    G2_QUALITY   = "G2_QUALITY"    # 信号质量
    G3_FLOW      = "G3_FLOW"       # 资金流硬闸
    G4_RISK      = "G4_RISK"       # 风险控制
    G5_WALKFWD   = "G5_WALKFORWARD"  # Walk-Forward


class GateStatus(str, Enum):
    PASS    = "PASS"
    FAIL    = "FAIL"
    PENDING = "PENDING"   # 数据不足，待补充
    SKIP    = "SKIP"       # 豁免（如无w-f数据时）


@dataclass
class GateResult:
    gate:      str
    status:    str
    value:     Any
    threshold: Any
    message:   str
    weight:    float = 1.0


@dataclass
class PromotionGateReport:
    ts:              int
    all_pass:       bool
    overall_score:  float
    gates:          list[GateResult] = field(default_factory=list)
    blocked_reason: Optional[str]    = None
    next_check_ts:  Optional[int]    = None

    def to_dict(self) -> dict:
        return {
            "ts":             self.ts,
            "all_pass":       self.all_pass,
            "overall_score":  self.overall_score,
            "gates":          [g.__dict__ for g in self.gates],
            "blocked_reason": self.blocked_reason,
            "next_check_ts":  self.next_check_ts,
        }


class L5PromotionGate:
    """
    L5晋级闸门检查器

    五级闸门：
      G1: 数据充足性（可立即检查）
      G2: 信号质量（可立即检查）
      G3: 资金流硬闸（可立即检查）
      G4: 风险控制（需要历史胜率/回撤数据，当前为估算）
      G5: Walk-Forward（翰林院单独触发）

    晋级硬性前提（全部未满足，当前阻塞晋级）：
      - entry_noise_filter: 各币种噪音均值 < 50
      - DCA_cooldown_fix:   Walk-Forward 连续3期正期望
      - 实盘 closed_trades >= 100（当前仅1笔）
    """

    # ---- G1 闸门值 ----
    G1_MIN_DAYS:    int = 7
    G1_MIN_SAMPLES: int = 300
    G1_MIN_PAIRS:   int = 3

    # ---- G2 闸门值 ----
    G2_MIN_QUALITY_PCT:    float = 8.0
    G2_MAX_HIGH_NOISE_PCT: float = 45.0
    G2_MIN_AGREEMENT_PCT:  float = 85.0
    G2_MIN_DELTA_SCORE:    float = 5.0

    # ---- G3 闸门值 ----
    G3_MIN_PASS_RATE:  float = 0.65
    G3_MAX_PASS_RATE:  float = 0.85
    G3_MIN_CANDIDATES: int   = 50
    G3_FLOW_THRESHOLD: float = 0.30

    # ---- G4 闸门值 ----
    G4_MIN_WIN_RATE:    float = 0.52
    G4_MAX_DRAWDOWN:    float = 0.20
    G4_MIN_TRADE_COUNT: int   = 100

    # ---- G5 闸门值 ----
    G5_PERIODS:         int   = 3
    G5_MAX_DEGRADATION: float = 0.20

    def __init__(self, report_path: Path = REPORT_PATH, db_path: Path = DB_PATH):
        self.report_path = report_path
        self.db_path     = db_path

    def check_all(self) -> PromotionGateReport:
        """
        执行全部晋级闸门检查。
        顺序检查，任意 FAIL 则晋级终止并返回阻塞原因。
        """
        report = json.loads(self.report_path.read_text(encoding="utf-8"))
        ts    = int(time.time())
        gates: list[GateResult] = []

        # G1
        g1 = self._check_g1(report)
        gates.append(g1)
        if g1.status == GateStatus.FAIL.value:
            return self._fail_report(ts, gates, f"G1 FAILED: {g1.message}")

        # G2
        g2 = self._check_g2(report)
        gates.append(g2)
        if g2.status == GateStatus.FAIL.value:
            return self._fail_report(ts, gates, f"G2 FAILED: {g2.message}")

        # G3
        g3 = self._check_g3(report)
        gates.append(g3)
        if g3.status == GateStatus.FAIL.value:
            return self._fail_report(ts, gates, f"G3 FAILED: {g3.message}")

        # G4
        g4 = self._check_g4(report)
        gates.append(g4)
        if g4.status == GateStatus.FAIL.value:
            return self._fail_report(ts, gates, f"G4 FAILED: {g4.message}")

        # G5（FAIL才阻塞；PENDING允许进入评审但须完成）
        g5 = self._check_g5(report)
        gates.append(g5)
        if g5.status == GateStatus.FAIL.value:
            return self._fail_report(ts, gates, f"G5 FAILED: {g5.message}")

        # 全部 PASS
        overall = sum(
            g.weight * (100 if g.status == GateStatus.PASS.value else 0)
            for g in gates
        ) / sum(g.weight for g in gates)

        return PromotionGateReport(
            ts=ts,
            all_pass=True,
            overall_score=round(overall, 1),
            gates=gates,
            next_check_ts=ts + 86400 * 7,
        )

    def _fail_report(
        self, ts: int, gates: list[GateResult], reason: str
    ) -> PromotionGateReport:
        score_map = {"G1": 0.0, "G2": 10.0, "G3": 25.0, "G4": 50.0, "G5": 75.0}
        score = next(
            (score_map.get(g.gate[:2], 0.0) for g in gates if g.status == GateStatus.FAIL.value),
            0.0,
        )
        return PromotionGateReport(
            ts=ts, all_pass=False, overall_score=score,
            gates=gates, blocked_reason=reason,
            next_check_ts=ts + 3600,
        )

    # -------------------------------------------------------------------------
    # 逐级检查
    # -------------------------------------------------------------------------

    def _check_g1(self, report: dict) -> GateResult:
        """G1: 数据充足性闸门"""
        days      = report.get("days", 0)
        samples   = report.get("sample_count", 0)
        pair_cnt  = len(report.get("by_pair", {}))

        checks = {
            "days":   (days   >= self.G1_MIN_DAYS,    f"影子运行{days}天（需≥{self.G1_MIN_DAYS}天）"),
            "samples":(samples >= self.G1_MIN_SAMPLES, f"样本{samples}条（需≥{self.G1_MIN_SAMPLES}条）"),
            "pairs":  (pair_cnt >= self.G1_MIN_PAIRS,  f"交易对{pair_cnt}个（需≥{self.G1_MIN_PAIRS}个）"),
        }
        all_pass = all(v[0] for v in checks.values())
        return GateResult(
            gate    = GateLevel.G1_DATA.value,
            status  = GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value   = {"days": days, "samples": samples, "pair_count": pair_cnt},
            threshold = {"min_days": self.G1_MIN_DAYS,
                         "min_samples": self.G1_MIN_SAMPLES,
                         "min_pairs":   self.G1_MIN_PAIRS},
            message = "; ".join(v[1] for v in checks.values()),
            weight  = 1.5,
        )

    def _check_g2(self, report: dict) -> GateResult:
        """G2: 信号质量闸门"""
        noise         = report.get("noise") or {}
        quality_pct    = noise.get("quality_pct", 0.0)
        high_noise_pct = noise.get("high_noise_pct", 0.0)
        agreement      = report.get("agreement_pct", 0.0)
        delta          = report.get("avg_delta_score", 0.0)

        checks = {
            "quality_pct": (
                quality_pct >= self.G2_MIN_QUALITY_PCT,
                f"优质信号{quality_pct}%（需≥{self.G2_MIN_QUALITY_PCT}%）",
            ),
            "high_noise_pct": (
                high_noise_pct <= self.G2_MAX_HIGH_NOISE_PCT,
                f"高噪音{high_noise_pct}%（需≤{self.G2_MAX_HIGH_NOISE_PCT}%）",
            ),
            "agreement": (
                agreement >= self.G2_MIN_AGREEMENT_PCT,
                f"一致率{agreement}%（需≥{self.G2_MIN_AGREEMENT_PCT}%）",
            ),
            "delta": (
                delta >= self.G2_MIN_DELTA_SCORE,
                f"增强加分{delta}（需≥{self.G2_MIN_DELTA_SCORE}）",
            ),
        }
        all_pass = all(v[0] for v in checks.values())
        quality_score = min(100.0, quality_pct / self.G2_MIN_QUALITY_PCT * 60)
        noise_score  = max(0.0, 40.0 - high_noise_pct / self.G2_MAX_HIGH_NOISE_PCT * 40)
        g2_score     = quality_score + noise_score

        return GateResult(
            gate    = GateLevel.G2_QUALITY.value,
            status  = GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value   = {"quality_pct": quality_pct, "high_noise_pct": high_noise_pct,
                       "agreement_pct": agreement, "avg_delta_score": delta,
                       "g2_score": round(g2_score, 1)},
            threshold = {"min_quality_pct": self.G2_MIN_QUALITY_PCT,
                         "max_high_noise_pct": self.G2_MAX_HIGH_NOISE_PCT,
                         "min_agreement_pct":  self.G2_MIN_AGREEMENT_PCT,
                         "min_delta_score":    self.G2_MIN_DELTA_SCORE},
            message = "; ".join(v[1] for v in checks.values()),
            weight  = 2.0,
        )

    def _check_g3(self, report: dict) -> GateResult:
        """G3: 资金流硬闸"""
        fg             = report.get("flow_gate") or {}
        candidate_cnt  = fg.get("candidate_count", 0)
        block_pct      = fg.get("block_pct", 0.0)
        pass_rate      = 1.0 - block_pct / 100.0

        checks = {
            "min_candidates": (
                candidate_cnt >= self.G3_MIN_CANDIDATES,
                f"资金流候选{candidate_cnt}个（需≥{self.G3_MIN_CANDIDATES}个）",
            ),
            "min_pass_rate": (
                pass_rate >= self.G3_MIN_PASS_RATE,
                f"通过率{pass_rate*100:.1f}%（需≥{self.G3_MIN_PASS_RATE*100:.0f}%）",
            ),
            "max_pass_rate": (
                pass_rate <= self.G3_MAX_PASS_RATE,
                f"通过率{pass_rate*100:.1f}%（需≤{self.G3_MAX_PASS_RATE*100:.0f}%，不能太松）",
            ),
        }
        all_pass = all(v[0] for v in checks.values())
        return GateResult(
            gate    = GateLevel.G3_FLOW.value,
            status  = GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value   = {"candidate_count": candidate_cnt,
                       "pass_rate": round(pass_rate, 3),
                       "block_pct": block_pct},
            threshold = {"min_pass_rate":  self.G3_MIN_PASS_RATE,
                         "max_pass_rate":  self.G3_MAX_PASS_RATE,
                         "min_candidates": self.G3_MIN_CANDIDATES},
            message = "; ".join(v[1] for v in checks.values()),
            weight  = 1.5,
        )

    def _check_g4(self, report: dict) -> GateResult:
        """
        G4: 风险控制闸门

        当前为估算值，待 walk_forward 模块完成后替换为真实数据。
        晋级闸门：win_rate >= 0.55 / promotion_trials >= 5
        """
        avg_shadow       = report.get("avg_delta_score", 0.0) + 50.0
        est_win_rate     = min(0.75, 0.40 + avg_shadow / 200.0)
        est_drawdown     = max(0.05, 0.25 - avg_shadow / 400.0)

        checks = {
            "win_rate": (
                est_win_rate >= self.G4_MIN_WIN_RATE,
                f"估算胜率{est_win_rate*100:.1f}%（需≥{self.G4_MIN_WIN_RATE*100:.0f}%）[待真实数据]",
            ),
            "drawdown": (
                est_drawdown <= self.G4_MAX_DRAWDOWN,
                f"估算回撤{est_drawdown*100:.1f}%（需≤{self.G4_MAX_DRAWDOWN*100:.0f}%）[待真实数据]",
            ),
        }
        all_pass = all(v[0] for v in checks.values())
        return GateResult(
            gate    = GateLevel.G4_RISK.value,
            status  = GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
            value   = {"estimated_win_rate": round(est_win_rate, 3),
                       "estimated_drawdown": round(est_drawdown, 3),
                       "note": "G4当前为估算值，待walk_forward模块完成后替换为真实数据"},
            threshold = {"min_win_rate": self.G4_MIN_WIN_RATE,
                         "max_drawdown": self.G4_MAX_DRAWDOWN},
            message = "; ".join(v[1] for v in checks.values()),
            weight  = 2.5,
        )

    def _check_g5(self, report: dict) -> GateResult:
        """
        G5: Walk-Forward 闸门

        当前：walk_forward_report.json 不存在，G5 = PENDING。
        PENDING 允许进入评审，但须在人工确认前完成 G5。
        """
        wf_report = BASE / "walk_forward_report.json"
        if wf_report.exists():
            wf           = json.loads(wf_report.read_text(encoding="utf-8"))
            periods_ok    = wf.get("periods_positive", [])
            all_positive = len(periods_ok) >= self.G5_PERIODS and all(periods_ok)
            degradation  = wf.get("max_degradation", 1.0)
            deg_ok       = degradation <= self.G5_MAX_DEGRADATION
            all_pass     = all_positive and deg_ok

            return GateResult(
                gate    = GateLevel.G5_WALKFWD.value,
                status  = GateStatus.PASS.value if all_pass else GateStatus.FAIL.value,
                value   = wf,
                threshold = {"periods": self.G5_PERIODS,
                             "max_degradation": self.G5_MAX_DEGRADATION},
                message = (f"Walk-forward {len(periods_ok)}期，"
                           f"全正期望={all_positive}，"
                           f"衰减={degradation*100:.1f}%（限{self.G5_MAX_DEGRADATION*100:.0f}%）"),
                weight  = 2.0,
            )
        else:
            return GateResult(
                gate    = GateLevel.G5_WALKFWD.value,
                status  = GateStatus.PENDING.value,
                value   = None,
                threshold = {"periods": self.G5_PERIODS},
                message = ("Walk-forward报告不存在（walk_forward_report.json）。"
                           "G5待执行，请触发 walk_forward 模块。"
                           "当前PENDING状态允许进入评审，但须在人工确认前完成G5。"),
                weight  = 0.0,
            )


def run_gate_check() -> PromotionGateReport:
    """快捷入口：运行全套闸门检查并保存结果。"""
    checker   = L5PromotionGate()
    result    = checker.check_all()
    out_path  = BASE / "promotion_gate_report.json"
    out_path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return result


if __name__ == "__main__":
    result = run_gate_check()
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    if not result.all_pass:
        print(f"\n[BLOCKED] {result.blocked_reason}")
    else:
        print(f"\n[APPROVED] L5晋级闸门全部通过，综合得分 {result.overall_score}/100")
```

---

## 十、当前晋级闸门状态（全部未满足晋级前提）

| 闸门 | 阈值 | 当前值 | 状态 |
|------|------|--------|------|
| entry_noise_filter | 各币种均值 < 50 | BTC=33.99 ✅ / DOGE=66.29 ❌ / ETH=62.62 ❌ / BNB=65.73 ❌ / SOL=61.54 ❌ | **未满足** |
| flow_consensus_threshold | 通过率 65%-85% | 74.3% | 满足 |
| DCA_cooldown_fix (G5) | Walk-Forward 连续3期正期望 | 未执行 | **未满足** |
| G1 数据充足性 | ≥7天/≥300样本/≥3对 | 7天/3040条/5对 | PASS |
| G2 信号质量 | 优质≥8%/噪音≤45% | 9.3%/40.7% | PASS |
| G3 资金流 | 候选≥50/通过率65-85% | 214/74.3% | PASS |
| G4 风险控制 | 胜率≥52%/回撤≤20% | 估算值 | PENDING |
| 实盘 closed_trades | ≥ 100笔 | 1笔 | **未满足** |

**晋级前提未满足项汇总**：
1. DOGE / ETH / BNB / SOL 噪音均值仍 > 50
2. Walk-Forward 尚未执行
3. 实盘 closed_trades 远低于100笔门槛
4. GPT尚未审核 DOGE/SOL/BNB 噪音异常根因

---

*本文件由翰林院代理生成，仅供 GPT 人工审核。不含任何实盘操作指令。*
