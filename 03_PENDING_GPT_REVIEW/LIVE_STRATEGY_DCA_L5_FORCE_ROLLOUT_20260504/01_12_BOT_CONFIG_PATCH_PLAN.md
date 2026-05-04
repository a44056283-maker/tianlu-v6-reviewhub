# 12 BOT配置补丁计划 (PATCH_PLAN)
**生成时间**: 2026/05/04 15:00
**PATCH编号**: LIVE_STRATEGY_DCA_L5_FORCE_ROLLOUT_20260504
**执行状态**: 待执行(仅生成补丁,不自动写入)

---

## 执行约束确认
- [x] 不重启任何机器人
- [x] 不调用交易所API
- [x] 不执行force_entry/exit
- [x] API keys已脱敏(仅显示前8字符)
- [x] 备份目录已创建: `~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/`

---

## 补丁内容定义

### P0-1: DOGE冻结 (temporary_pair_freeze)
添加到所有overlay配置的top-level:
```json
"temporary_pair_freeze": {
  "DOGE/USDT:USDT": {
    "enabled": true,
    "duration_hours": 24,
    "reason": "batch_stoploss_loop",
    "block_auto_entry": true,
    "block_auto_dca": true
  }
}
```

### P0-2: SOL DCA暂停 (dca_pause_rules)
添加到所有overlay配置的top-level:
```json
"dca_pause_rules": {
  "SOL/USDT:USDT:SHORT": {
    "enabled": true,
    "reason": "dca_full_layer_roe_negative",
    "block_new_dca": true
  }
}
```

---

## 一、Mac A 补丁 (8个bot)

### 1.1 PATCH: config_9090_overlay.json
**路径**: `/Users/luxiangnan/freqtrade_console/bt_tools/config_9090_overlay.json`
**说明**: 这是9090 bot的FOttStrategy基础配置，由console_server.py直接加载为9090主配置（而非独立的exchange overlay）
**交易所**: Gate.io (key: caa8dc0c...)
**端口**: 9090

**BEFORE** (尾部现有字段):
```json
  "position_stacking": true,
  "short_allowed": true
}
```

**AFTER** (新增字段):
```json
  "position_stacking": true,
  "short_allowed": true,
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true
    }
  }
}
```

**PATCH.diff**:
```diff
--- a/bt_tools/config_9090_overlay.json
+++ b/bt_tools/config_9090_overlay.json
@@ -61,5 +61,17 @@
   "position_stacking": true,
   "timeframe": "15m",
-  "strategy": "FOttStrategy"
+  "strategy": "FOttStrategy",
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade_console/bt_tools/config_9090_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9090_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9090_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade_console/bt_tools/config_9090_overlay.json
```

---

### 1.2 PATCH: config_9091_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9091_overlay.json`
**交易所**: Gate.io (key: eea4664d...)
**端口**: 9091

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true
}
```

**AFTER**:
```json
  "position_stacking": true,
  "short_allowed": true,
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true
    }
  }
}
```

**PATCH.diff**:
```diff
--- a/config_9091_overlay.json
+++ b/config_9091_overlay.json
@@ -83,5 +83,17 @@
   "user_data_dir": "/Users/luxiangnan/freqtrade/user_data_gate85363904550",
   "position_stacking": true,
-  "short_allowed": true
+  "short_allowed": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9091_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9091_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9091_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9091_overlay.json
```

---

### 1.3 PATCH: config_9092_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9092_overlay.json`
**交易所**: Gate.io (key: 2face13e...)
**端口**: 9092

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true,
  "timeframe": "15m"
}
```

**AFTER**:
```json
  "position_stacking": true,
  "short_allowed": true,
  "timeframe": "15m",
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true
    }
  }
}
```

**PATCH.diff**:
```diff
--- a/config_9092_overlay.json
+++ b/config_9092_overlay.json
@@ -84,5 +84,17 @@
   "strategy_path": "user_data_gate15637798222/strategies",
   "position_stacking": true,
   "short_allowed": true,
-  "timeframe": "15m"
+  "timeframe": "15m",
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9092_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9092_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9092_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9092_overlay.json
```

---

### 1.4 PATCH: config_9093_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9093_overlay.json`
**交易所**: OKX (key: 4f4c5c02...)
**端口**: 9093

**BEFORE** (尾部):
```json
  "hedging": true,
  "position_stacking": true,
  "short_allowed": true
}
```

**AFTER**:
```json
  "hedging": true,
  "position_stacking": true,
  "short_allowed": true,
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true
    }
  }
}
```

**PATCH.diff**:
```diff
--- a/config_9093_overlay.json
+++ b/config_9093_overlay.json
@@ -107,5 +107,17 @@
   "hedging": true,
   "position_stacking": true,
-  "short_allowed": true
+  "short_allowed": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9093_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9093_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9093_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9093_overlay.json
```

---

### 1.5 PATCH: config_9094_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9094_overlay.json`
**交易所**: OKX (key: 242fcd80...)
**端口**: 9094

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true,
  "hedging": true
}
```

**AFTER**: 在short_allowed后面加逗号,添加两个新字段

**PATCH.diff**:
```diff
--- a/config_9094_overlay.json
+++ b/config_9094_overlay.json
@@ -107,5 +107,17 @@
   "position_stacking": true,
   "short_allowed": true,
-  "hedging": true
+  "hedging": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9094_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9094_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9094_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9094_overlay.json
```

---

### 1.6 PATCH: config_9095_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9095_overlay.json`
**交易所**: OKX (key: b718acf2...)
**端口**: 9095

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true,
  "hedging": true
}
```

**AFTER**: 同1.5结构

**PATCH.diff**:
```diff
--- a/config_9095_overlay.json
+++ b/config_9095_overlay.json
@@ -107,5 +107,17 @@
   "position_stacking": true,
   "short_allowed": true,
-  "hedging": true
+  "hedging": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9095_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9095_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9095_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9095_overlay.json
```

---

### 1.7 PATCH: config_9096_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9096_overlay.json`
**交易所**: OKX (key: 0927c9fa...)
**端口**: 9096

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true,
  "hedging": true
}
```

**AFTER**: 同1.5结构

**PATCH.diff**:
```diff
--- a/config_9096_overlay.json
+++ b/config_9096_overlay.json
@@ -103,5 +103,17 @@
   "position_stacking": true,
   "short_allowed": true,
-  "hedging": true
+  "hedging": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9096_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9096_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9096_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9096_overlay.json
```

---

### 1.8 PATCH: config_9097_overlay.json
**路径**: `/Users/luxiangnan/freqtrade/config_9097_overlay.json`
**交易所**: OKX (key: edb9e15e...)
**端口**: 9097

**BEFORE** (尾部):
```json
  "position_stacking": true,
  "short_allowed": true,
  "hedging": true
}
```

**AFTER**: 同1.5结构

**PATCH.diff**:
```diff
--- a/config_9097_overlay.json
+++ b/config_9097_overlay.json
@@ -103,5 +103,17 @@
   "position_stacking": true,
   "short_allowed": true,
-  "hedging": true
+  "hedging": true,
+  "temporary_pair_freeze": {
+    "DOGE/USDT:USDT": {
+      "enabled": true,
+      "duration_hours": 24,
+      "reason": "batch_stoploss_loop",
+      "block_auto_entry": true,
+      "block_auto_dca": true
+    }
+  },
+  "dca_pause_rules": {
+    "SOL/USDT:USDT:SHORT": {
+      "enabled": true,
+      "reason": "dca_full_layer_roe_negative",
+      "block_new_dca": true
+    }
+  }
 }
```

**备份命令**:
```bash
cp /Users/luxiangnan/freqtrade/config_9097_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9097_overlay.json.bak_20260504_150000
```

**回滚命令**:
```bash
cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_9097_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_9097_overlay.json
```

---

## 二、Mac B 补丁 (4个bot - 需SSH执行)

> **WARNING**: SSH到192.168.13.104被拒绝，以下补丁需手动在Mac B上执行或通过其他方式推送

### 2.1 PATCH: config_8081_overlay.json
**远程路径**: `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8081_overlay.json`
**Bot名称**: MacB-Gate-a63904550

**JSON补丁内容** (需追加到文件末尾,替换最后一行}):
```json
  "temporary_pair_freeze": {
    "DOGE/USDT:USDT": {
      "enabled": true,
      "duration_hours": 24,
      "reason": "batch_stoploss_loop",
      "block_auto_entry": true,
      "block_auto_dca": true
    }
  },
  "dca_pause_rules": {
    "SOL/USDT:USDT:SHORT": {
      "enabled": true,
      "reason": "dca_full_layer_roe_negative",
      "block_new_dca": true
    }
  }
}
```

**SSH备份命令**:
```bash
ssh luxiangnan@192.168.13.104 "cp /Users/luxiangnan/freqtrade_bots/config_8081_overlay.json ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_8081_overlay.json.bak_20260504_150000" 2>/dev/null || echo "SSH failed - manual backup required"
```

**SSH回滚命令**:
```bash
ssh luxiangnan@192.168.13.104 "cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_8081_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade_bots/config_8081_overlay.json"
```

### 2.2 PATCH: config_8082_overlay.json
**远程路径**: `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8082_overlay.json`
**Bot名称**: MacB-Gate-a15637798222

同2.1结构

### 2.3 PATCH: config_8083_overlay.json
**远程路径**: `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8083_overlay.json`
**Bot名称**: MacB-Gate-b15637798222

同2.1结构

### 2.4 PATCH: config_8084_overlay.json
**远程路径**: `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8084_overlay.json`
**Bot名称**: MacB-Gate-c15637798222

同2.1结构

---

## 三、执行检查清单

### 阶段0: 备份 (执行补丁前必须完成)
- [ ] 创建备份目录
- [ ] 备份Mac A 8个overlay配置
- [ ] (Mac B) 通过SSH备份4个overlay配置

### 阶段1: Mac A补丁执行
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9090_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9090
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9091_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9091
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9092_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9092
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9093_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9093
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9094_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9094
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9095_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9095
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9096_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9096
- [ ] 备份 `/Users/luxiangnan/freqtrade/config_9097_overlay.json`
- [ ] 写入 P0-1+P0-2 到 9097

### 阶段2: Mac B补丁执行 (需先解决SSH访问)
- [ ] SSH到192.168.13.104
- [ ] 备份并写入 8081-8084

### 阶段3: 验证
- [ ] JSON语法验证 (python3 -c "import json; json.load(open('config_9090_overlay.json'))")
- [ ] 确认机器人无需重启即可加载新配置 (overlay在启动时加载)
- [ ] 确认配置通过API可见: `curl http://127.0.0.1:9090/api/v1/show_config`

---

## 四、回滚指南

如需回滚,在备份目录中执行:
```bash
# Mac A回滚
for port in 9090 9091 9092 9093 9094 9095 9096 9097; do
  cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_${port}_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade/config_${port}_overlay.json
done

# Mac B回滚 (需SSH)
for port in 8081 8082 8083 8084; do
  ssh luxiangnan@192.168.13.104 "cp ~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/live_rollout_20260504_150000/config_${port}_overlay.json.bak_20260504_150000 /Users/luxiangnan/freqtrade_bots/config_${port}_overlay.json"
done
```

---

## 五、注意事项

1. **Overlay生效时机**: Freqtrade的overlay配置在bot启动时读取,修改后需重启对应bot才会生效
2. **统一性**: Mac A 8个bot全部使用相同的P0-1+P0-2规则,Mac B 4个bot也应保持一致
3. **DCA支持确认**: 请确认FOttStrategy.py中实现了对`dca_pause_rules`和`temporary_pair_freeze`配置项的读取逻辑,否则补丁不会生效
4. **JSON逗号**: 每个文件最后一个字段后面原来是`}`,补丁后变为`,}`,需确保格式正确
5. **Mac B SSH**: 建议在Mac A上先测试SSH连接: `ssh -o ConnectTimeout=5 luxiangnan@192.168.13.104 echo ok`
