# 06_DRY_RUN_TEST_PLAN.md
# Dry-run 测试计划（Shadow模式验证）

## 概述

Dry-run测试用于验证 EntryDecisionGate 的 shadow 模式行为，确保：
1. 日志正确输出
2. verdict和score计算正确
3. 不执行任何交易操作
4. 对接现有API不报错

---

## 测试环境准备

```bash
# 1. 设置Dry-run模式
export TIANLU_ENTRY_GATE_MODE=dry    # 不调用AI
export TIANLU_EXIT_GATE_MODE=dry

# 2. 或设置Shadow模式（完整测试）
export TIANLU_ENTRY_GATE_MODE=shadow  # 默认，已设置
export TIANLU_EXIT_GATE_MODE=shadow

# 3. 验证日志目录存在
mkdir -p /tmp/tianlu_gate_logs

# 4. 启动console_server并观察日志
tail -f /tmp/tianlu_gate_logs/entry_decisions.json
tail -f /tmp/tianlu_gate_logs/exit_recommendations.json
```

---

## 测试场景矩阵

### S/R 场景类型 × 交易对

| 场景编号 | S/R类型 | Direction | 距S/R距离 | 预期Verdict |
|---------|---------|-----------|----------|------------|
| SR-01 | support（触底3次） | LONG | -0.5%（支撑下方） | SHADOW + score>=50 |
| SR-02 | support（触底3次） | LONG | +1.5%（支撑上方） | SHADOW + score<50（L4拒绝） |
| SR-03 | support（触底1次） | LONG | -0.5% | SHADOW + L4拒绝 |
| SR-04 | resistance（触顶3次） | SHORT | +0.5%（压力上方） | SHADOW + score>=50 |
| SR-05 | resistance（触顶3次） | SHORT | -1.5%（压力下方） | SHADOW + score<50（L4拒绝） |
| SR-06 | 无S/R | LONG | N/A | SHADOW + L4拒绝 |

### 量比场景

| 场景编号 | 量比 | 净流入 | 三所一致率 | 预期Score范围 |
|---------|------|--------|-----------|--------------|
| VOL-01 | >= 5.0x | 正向 | 3所同向 | 70-100 |
| VOL-02 | 3.0x-5.0x | 正向 | 2所同向 | 50-70 |
| VOL-03 | 1.0x-3.0x | 正向 | 1所 | 30-50 |
| VOL-04 | < 1.0x | 负向 | 背离 | < 30 |

### 综合场景

| 场景编号 | M1 | M2 | M3 | M4 | L5 | 预期Verdict |
|---------|----|----|----|----|----|------------|
| COMP-01 | 强 | 强 | 有信号 | 健康 | PASS | ALLOW/SHADOW |
| COMP-02 | 强 | 弱 | 无信号 | 健康 | PASS | SHADOW + score<50 |
| COMP-03 | 弱 | 强 | 有信号 | 健康 | PASS | SHADOW + score<50 |
| COMP-04 | 强 | 强 | 有信号 | 超买 | DOWNGRADE | SHADOW + score<50 |
| COMP-05 | 强 | 强 | 有信号 | 健康 | FORBIDDEN | BLOCK/SHADOW |

---

## 测试用例设计

### TC-01: Shadow模式L4拒绝

```
测试ID: TC-01
场景: SR-03（触底1次 < 3次）
预期输出:
  - 日志: [EntryGate][INFO] L4拒绝: touches=1/3...
  - verdict: SHADOW
  - rejected_layers: ["L4"]
  - pair: BTC/USDT
  - direction: LONG
验证方法:
  grep "L4拒绝" /tmp/tianlu_gate_logs/entry_decisions.json
```

### TC-02: Shadow模式综合评分通过

```
测试ID: TC-02
场景: SR-01 + VOL-01（强信号）
预期输出:
  - 日志: [EntryGate][INFO] 评估开始: BTC/USDT LONG
  - 日志: [EntryGate][INFO] L4通过: support @ 95234.56, touches=4
  - 日志: [EntryGate][INFO] 综合评分: 78/50
  - 日志: [EntryGate][INFO] → SHADOW: score=78
  - verdict: SHADOW
  - score: 78
验证方法:
  cat /tmp/tianlu_gate_logs/entry_decisions.json | python3 -c "
    import sys, json
    logs = json.load(sys.stdin)
    latest = logs[-1]
    assert latest['verdict'] == 'SHADOW'
    assert latest['score'] >= 50
    print('TC-02 PASS')
  "
```

### TC-03: Dry模式不调用AI

```
测试ID: TC-03
场景: DRY模式
预期输出:
  - 日志: [天眼AI][DRY] 不调用AI，只用规则检查
  - 无MiniMax API调用
验证方法:
  # 检查网络连接（无实际API调用）
  # 在shadow模式下应该有MiniMax调用记录，dry模式没有
  grep "MiniMax" /tmp/tianlu_gate_logs/*.log
  # 预期: 无匹配
```

### TC-04: 天眼AI shadow模式只记录

```
测试ID: TC-04
场景: 天眼AI verdict=EXECUTE_LONG, confidence=0.85
预期输出:
  - 日志: [天眼AI][SHADOW] verdict=EXECUTE_LONG, confidence=0.85
  - 日志: [天眼AI][SHADOW] speech=...
  - 无交易API调用
验证方法:
  grep "SHADOW" /tmp/tianlu_gate_logs/entry_decisions.json
  # 检查无POST/交易API调用
```

### TC-05: 出山AI只展示不执行

```
测试ID: TC-05
场景: 出山AI action=EXIT_FULL, confidence=0.75
预期输出:
  - 日志: [出山AI][SHADOW] BTC/USDT → action=EXIT_FULL, confidence=0.75
  - 日志: [出山AI][SHADOW] speech=...
  - 无平仓API调用
验证方法:
  grep "EXIT_FULL" /tmp/tianlu_gate_logs/exit_recommendations.json
  # 检查无平仓API调用
```

### TC-06: 反转猎杀shadow模式

```
测试ID: TC-06
场景: action=HUNT_REVERSE
预期输出:
  - 日志: [出山AI][HUNT_REVERSE][SHADOW] BTC/USDT 反转猎杀信号已记录
  - 冷却记录文件存在: /tmp/tianlu_hunt_cooldown_BTC_USDT.json
  - 无实际反手操作
验证方法:
  ls /tmp/tianlu_hunt_cooldown*.json
  # 预期: 存在冷却记录文件（只记录，未实际触发）
```

---

## 自动化测试脚本草案

```python
# tests/test_entry_decision_gate.py  (草案，禁止写入实盘tests目录)

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 设置测试模式
os.environ["TIANLU_ENTRY_GATE_MODE"] = "shadow"
os.environ["TIANLU_EXIT_GATE_MODE"] = "shadow"

from bt_tools.entry_decision_gate import (
    evaluate, EntryVerdictType, COMPOSITE_SCORE_THRESHOLD
)

class TestEntryDecisionGate:
    """EntryDecisionGate 单元测试（草案）"""

    def test_l4_reject_no_sr(self):
        """L4拒绝：没有S/R"""
        # Mock: get_m2_sr_evidence 返回无S/R
        pass

    def test_l4_reject_few_touches(self):
        """L4拒绝：触底次数不足"""
        pass

    def test_l4_reject_distance(self):
        """L4拒绝：距离S/R太远"""
        pass

    def test_l4_pass(self):
        """L4通过：有效S/R + 足够触底次数 + 距离<1%"""
        pass

    def test_shadow_mode_never_blocks(self):
        """Shadow模式永远不返回BLOCK verdict"""
        # 设置 shadow 模式
        pass

    def test_live_mode_can_block(self):
        """Live模式可以返回BLOCK verdict"""
        # 设置 live 模式
        pass

    def test_score_threshold_50(self):
        """置信度门槛 = 50（爸确认）"""
        assert COMPOSITE_SCORE_THRESHOLD == 50

    def test_verdict_has_all_fields(self):
        """EntryVerdict包含所有必需字段"""
        pass
```

---

## 预期输出格式

### Shadow模式日志示例

```
2026-05-04 16:38:00 [EntryGate][INFO] 评估开始: BTC/USDT LONG @ 96500.00 (mode=shadow)
2026-05-04 16:38:00 [EntryGate][INFO]   L4通过: support @ 95234.56, touches=4, dist=-0.45%
2026-05-04 16:38:00 [EntryGate][INFO]   M1-M5 Evidence收集完成: ratio=5.234, sr_touches=4
2026-05-04 16:38:01 [天眼AI][SHADOW] verdict=EXECUTE_LONG, confidence=0.88
2026-05-04 16:38:01 [天眼AI][SHADOW] reason=三所共振做多信号确认...
2026-05-04 16:38:01 [EntryGate][INFO]   综合评分: 78/50
2026-05-04 16:38:01 [EntryGate][INFO]   → SHADOW: score=78
```

### 日志JSON示例

```json
{
  "ts": 1746346680,
  "mode": "shadow",
  "pair": "BTC/USDT",
  "direction": "LONG",
  "verdict": "SHADOW",
  "score": 78,
  "confidence": 0.88,
  "sources": ["L4", "M1", "M2", "M3", "M4", "L5"],
  "rejected_layers": [],
  "ai_verdict": "EXECUTE_LONG",
  "ai_speech": "三所共振做多信号确认..."
}
```

---

## 验证检查清单

每个测试用例完成后：
- [ ] 日志文件存在（`/tmp/tianlu_gate_logs/`）
- [ ] verdict类型正确
- [ ] score在预期范围内
- [ ] 无交易API调用（网络抓包或日志审查）
- [ ] shadow模式不返回BLOCK实际阻止
- [ ] M1-M5 evidence字段完整
- [ ] 天眼AI响应时间 < 5秒
- [ ] 出山AI响应时间 < 5秒

---

## 禁止事项

- **禁止**在测试环境使用live模式执行真实交易
- **禁止**在测试环境修改机器人参数
- **禁止**测试完成后不清除测试日志
