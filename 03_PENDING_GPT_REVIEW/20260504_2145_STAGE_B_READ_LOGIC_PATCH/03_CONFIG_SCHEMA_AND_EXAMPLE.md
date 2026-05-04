# 03_CONFIG_SCHEMA_AND_EXAMPLE.md

## 配置 Schema + DOGE/SOL 示例

**草案文件** | **禁止直接写入实盘**

---

## 1. overlay config 扩展字段

在现有 `config_XXXX_overlay.json` 根级别新增两个字段：

```json
{
  "exchange": { ... },
  "entry_pricing": { ... },
  "api_server": { ... },
  "leverage": { ... },

  "temporary_pair_freeze": { ... },   // ← 新增
  "dca_pause_rules": { ... }           // ← 新增
}
```

---

## 2. temporary_pair_freeze Schema

```json
"temporary_pair_freeze": {
  "<pair>": {
    "enabled": true,                    // 必需：开关
    "reason": "string",                 // 必需：冻结原因（供监控展示）
    "block_auto_entry": true,           // 必需：阻断自动驾驶首次入场
    "block_auto_dca": false,             // 可选：阻断新仓位的初始 DCA（默认 false）
    "duration_hours": 24,               // 可选：持续时长（小时），与 until_ts 二选一
    "until_ts": null,                   // 可选：Unix 时间戳（秒），null=无过期时间
    "created_by": "claude",             // 可选：操作者标识
    "created_at": "2026-05-04T21:45:00+08:00"  // 可选：创建时间
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | bool | ✅ | 开关，false = 忽略此规则 |
| `reason` | string | ✅ | 冻结原因，会出现在日志和监控中 |
| `block_auto_entry` | bool | ✅ | 是否阻断自动驾驶首次入场 |
| `block_auto_dca` | bool | ❌ | 是否阻断该仓位的首次 DCA（默认 false）|
| `duration_hours` | int | ❌ | 持续小时数（与 until_ts 二选一）|
| `until_ts` | float | ❌ | Unix 时间戳秒（与 duration_hours 二选一），null=永不过期 |
| `created_by` | string | ❌ | 操作者标识 |
| `created_at` | string | ❌ | ISO 格式时间 |

### 兼容 key 格式

系统会尝试以下 key 格式（第一个匹配生效）：
1. `DOGE/USDT:USDT`
2. `DOGE/USDT`
3. `DOGE`

---

## 3. dca_pause_rules Schema

```json
"dca_pause_rules": {
  "<pair:direction>": {
    "enabled": true,                     // 必需：开关
    "reason": "string",                 // 必需：暂停原因（供监控展示）
    "block_new_dca": true,              // 必需：阻断 DCA 新增仓位
    "allow_exit_review": true,          // 可选：是否允许出山AI回测出场（默认 true）
    "duration_hours": 48,               // 可选：持续时长（小时）
    "until_ts": null,                   // 可选：Unix 时间戳秒
    "created_by": "claude",
    "created_at": "2026-05-04T21:45:00+08:00"
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `enabled` | bool | ✅ | 开关 |
| `reason` | string | ✅ | 暂停原因 |
| `block_new_dca` | bool | ✅ | 是否阻断 DCA 新增仓位 |
| `allow_exit_review` | bool | ❌ | 是否允许出山AI出场（不影响风控止损）|
| `duration_hours` | int | ❌ | 持续小时数 |
| `until_ts` | float | ❌ | Unix 时间戳秒 |
| `created_by` | string | ❌ | 操作者标识 |
| `created_at` | string | ❌ | ISO 格式时间 |

### 兼容 key 格式

1. `SOL/USDT:USDT:LONG`
2. `SOL:LONG`
3. `SOL/USDT:USDT`
4. `SOL`

---

## 4. DOGE 冻结示例（config_9090_overlay.json）

```json
{
  "exchange": {
    "name": "gateio",
    "key": "...",
    "secret": "...",
    "ccxt_config": { "timeout": 120000, "proxies": {} },
    "ccxt_async_config": { "proxies": {} },
    "pair_whitelist": [
      "BTC/USDT:USDT",
      "ETH/USDT:USDT",
      "SOL/USDT:USDT",
      "BNB/USDT:USDT",
      "DOGE/USDT:USDT"
    ],
    "pair_blacklist": [...]
  },
  "entry_pricing": { ... },
  "api_server": { ... },
  "leverage": { ... },

  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true,
      "duration_hours": 24,
      "until_ts": null,
      "created_by": "claude-stage-b",
      "created_at": "2026-05-04T21:45:00+08:00"
    }
  }
}
```

**注意**: DOGE 仍在 whitelist 中，但自动驾驶会跳过入场。这确保：
- 监控仍可看到 DOGE
- 已有仓位不受影响
- 解冻时只需 `enabled: false` 或等 `until_ts` 过期

---

## 5. SOL DCA 暂停示例（config_9093_overlay.json）

```json
{
  "exchange": {
    "name": "okx",
    "key": "...",
    "secret": "...",
    "ccxt_config": { "timeout": 120000, "proxies": {} },
    "ccxt_async_config": { "proxies": {} },
    "pair_whitelist": [
      "BTC/USDT:USDT",
      "ETH/USDT:USDT",
      "SOL/USDT:USDT",
      "BNB/USDT:USDT"
    ],
    "pair_blacklist": [...]
  },
  "entry_pricing": { ... },
  "api_server": { ... },
  "leverage": { ... },

  "dca_pause_rules": {
    "SOL/USDT:USDT:LONG": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true,
      "allow_exit_review": true,
      "duration_hours": 48,
      "until_ts": null,
      "created_by": "claude-stage-b",
      "created_at": "2026-05-04T21:45:00+08:00"
    }
  }
}
```

---

## 6. Python 辅助函数（写入 overlay 工具）

```python
import json, time
from pathlib import Path

def add_freeze_rule(overlay_path: str, pair: str, reason: str,
                    duration_hours: int = 24, block_auto_dca: bool = False):
    """给指定 overlay 添加 temporary_pair_freeze 规则"""
    path = Path(overlay_path).expanduser()
    cfg = json.loads(path.read_text())

    cfg.setdefault("temporary_pair_freeze", {})
    cfg["temporary_pair_freeze"][pair] = {
        "enabled": True,
        "reason": reason,
        "block_auto_entry": True,
        "block_auto_dca": block_auto_dca,
        "duration_hours": duration_hours,
        "until_ts": time.time() + duration_hours * 3600,
        "created_by": "claude-stage-b",
        "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
    }
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
    print(f"✅ 已写入 {overlay_path}: 冻结 {pair} {duration_hours}h")

def remove_freeze_rule(overlay_path: str, pair: str):
    """解除冻结（不删除配置，只关闭开关）"""
    path = Path(overlay_path).expanduser()
    cfg = json.loads(path.read_text())
    if "temporary_pair_freeze" in cfg and pair in cfg["temporary_pair_freeze"]:
        cfg["temporary_pair_freeze"][pair]["enabled"] = False
        path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))
        print(f"✅ 已解除冻结 {pair}")
```

---

## 7. JSON Schema 验证（draft，非实盘）

```json
// temporary_pair_freeze schema
{
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "required": ["enabled", "reason", "block_auto_entry"],
    "properties": {
      "enabled":       { "type": "boolean" },
      "reason":        { "type": "string" },
      "block_auto_entry": { "type": "boolean" },
      "block_auto_dca": { "type": "boolean" },
      "duration_hours": { "type": "number" },
      "until_ts":      { "type": ["number", "null"] },
      "created_by":    { "type": "string" },
      "created_at":    { "type": "string" }
    }
  }
}

// dca_pause_rules schema
{
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "required": ["enabled", "reason", "block_new_dca"],
    "properties": {
      "enabled":       { "type": "boolean" },
      "reason":        { "type": "string" },
      "block_new_dca": { "type": "boolean" },
      "allow_exit_review": { "type": "boolean" },
      "duration_hours": { "type": "number" },
      "until_ts":      { "type": ["number", "null"] },
      "created_by":    { "type": "string" },
      "created_at":    { "type": "string" }
    }
  }
}
```

---

## 8. 与现有字段不冲突

| 现有字段 | 说明 | 兼容性 |
|----------|------|--------|
| `exchange.pair_whitelist` | whitelist 管理 | freeze 不删除，只阻断自动驾驶 |
| `exchange.pair_blacklist` | blacklist 管理 | freeze 不操作 blacklist |
| `position_stacking` | 持仓堆叠 | 不受影响 |
| `hedging` | 对冲模式 | 不受影响 |

---

## 9. 验证命令

```bash
# 验证 overlay JSON 语法
python3 -m json.tool ~/freqtrade/config_9090_overlay.json >/dev/null && echo "9090 JSON OK"
python3 -m json.tool ~/freqtrade/config_9093_overlay.json >/dev/null && echo "9093 JSON OK"

# 验证 freeze 字段存在
python3 -c "
import json, sys
cfg = json.load(open('$HOME/freqtrade/config_9090_overlay.json'))
freeze = cfg.get('temporary_pair_freeze', {})
print(f'9090 freeze rules: {len(freeze)} 个')
for pair, rule in freeze.items():
    print(f'  {pair}: enabled={rule.get(\"enabled\")} reason={rule.get(\"reason\")}')
"
```
