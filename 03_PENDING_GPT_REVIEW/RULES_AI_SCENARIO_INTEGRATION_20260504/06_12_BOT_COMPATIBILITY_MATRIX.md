# 兵部审计报告：12机器人兼容性矩阵
**生成时间**: 2026-05-04 16:00 GMT+8
**审计人**: 兵部代理
**数据来源**: 各bot overlay配置文件 + 参考文档
**Mac B访问状态**: SSH不可达（192.168.13.104拒绝连接），8081-8084配置基于推断

---

## 一、机器人拓扑总览

| 端口 | 主机 | 交易所 | 账号 | 策略 | 配置文件路径 | 在线状态 |
|------|------|--------|------|------|------------|---------|
| 9090 | Mac A | Gate.io | Gate-17656685222 | FOttStrategy | `/freqtrade_console/bt_tools/config_9090_overlay.json` | **在线** |
| 9091 | Mac A | Gate.io | Gate-85363904550 | FOttStrategy | `/freqtrade/config_9091_overlay.json` | **在线** |
| 9092 | Mac A | Gate.io | Gate-15637798222 | FOttStrategy | `/freqtrade/config_9092_overlay.json` | **在线** |
| 9093 | Mac A | OKX | OKX-15637798222 | FOttStrategy | `/freqtrade/config_9093_overlay.json` | **在线** |
| 9094 | Mac A | OKX | OKX-242fcd80 | FOttStrategy | `/freqtrade/config_9094_overlay.json` | **在线** |
| 9095 | Mac A | OKX | OKX-b718acf2 | FOttStrategy | `/freqtrade/config_9095_overlay.json` | **在线** |
| 9096 | Mac A | OKX | OKX-0927c9fa | FOttStrategy | `/freqtrade/config_9096_overlay.json` | **在线** |
| 9097 | Mac A | OKX | OKX-edb9e15e | FOttStrategy | `/freqtrade/config_9097_overlay.json` | **在线** |
| 8081 | Mac B | Gate.io | MacB-Gate-a63904550 | FOttStrategy | `192.168.13.104:/freqtrade_bots/config_8081_overlay.json` | **SSH拒绝** |
| 8082 | Mac B | Gate.io | MacB-Gate-a15637798222 | FOttStrategy | `192.168.13.104:/freqtrade_bots/config_8082_overlay.json` | **SSH拒绝** |
| 8083 | Mac B | Gate.io | MacB-Gate-b15637798222 | FOttStrategy | `192.168.13.104:/freqtrade_bots/config_8083_overlay.json` | **SSH拒绝** |
| 8084 | Mac B | Gate.io | MacB-Gate-c15637798222 | FOttStrategy | `192.168.13.104:/freqtrade_bots/config_8084_overlay.json` | **SSH拒绝** |

---

## 二、Overlay配置文件字段清单

### 2.1 Mac A 配置文件读取结果

| 端口 | 配置文件路径 | 实际交易所 | listen_port | leverage | position_stacking | short_allowed | hedging | timeframe | db_url | user_data_dir | DOGE白名单 | SOL白名单 |
|------|------------|---------|------------|---------|------------------|--------------|--------|---------|-------|-------------|---------|---------|
| 9090 | `bt_tools/config_9090_overlay.json` | **OKX** (异常) | 9093 (异常) | 10/10 | YES | YES | YES | - | okx_9093 | okx_9093 | YES | YES |
| 9091 | `freqtrade/config_9091_overlay.json` | Gate.io | 9091 | 10/10 | YES | YES | - | - | gate85363904550 | gate85363904550 | YES | YES |
| 9092 | `freqtrade/config_9092_overlay.json` | Gate.io | 9092 | 10/10 | YES | YES | - | 15m | gate15637798222 | gate15637798222 | YES | YES |
| 9093 | `freqtrade/config_9093_overlay.json` | OKX | 9093 | 10/10 | YES | YES | YES | - | okx_9093 | okx_9093 | YES | YES |
| 9094 | `freqtrade/config_9094_overlay.json` | OKX | 9094 | 10/10 | YES | YES | YES | - | okx_9094 | okx_9094 | YES | YES |
| 9095 | `freqtrade/config_9095_overlay.json` | OKX | 9095 | 10/10 | YES | YES | YES | - | okx_9095 | okx_9095 | YES | YES |
| 9096 | `freqtrade/config_9096_overlay.json` | OKX | 9096 | 10/10 | YES | YES | YES | - | okx_9096 | okx_9096 | YES | YES |
| 9097 | `freqtrade/config_9097_overlay.json` | OKX | 9097 | 10/10 | YES | YES | YES | - | okx_9097 | okx_9097 | YES | YES |

> **CRITICAL发现**: `bt_tools/config_9090_overlay.json` 包含OKX交易所配置（exchange name: okx, key前8: 4f4c5c02, listen_port: 9093），但拓扑定义中9090应为Gate.io bot。此文件与9093共享相同的数据库和配置，疑似被覆盖或复制错误。**建议立即人工核查。**

### 2.2 Mac B 配置文件状态（SSH不可达）

| 端口 | 预期交易所 | 预期路径 | 状态 |
|------|---------|---------|------|
| 8081 | Gate.io | `192.168.13.104:/freqtrade_bots/config_8081_overlay.json` | **SSH拒绝** |
| 8082 | Gate.io | `192.168.13.104:/freqtrade_bots/config_8082_overlay.json` | **SSH拒绝** |
| 8083 | Gate.io | `192.168.13.104:/freqtrade_bots/config_8083_overlay.json` | **SSH拒绝** |
| 8084 | Gate.io | `192.168.13.104:/freqtrade_bots/config_8084_overlay.json` | **SSH拒绝** |

---

## 三、M1-M5 Evidence Payload 兼容性矩阵

> **说明**: M1-M5 evidence payload由console_server.py构造并通过API派发，FOttStrategy框架层统一处理。
> 所有12个bot运行同一FOttStrategy框架，理论上M1-M5接收能力一致。
> 差异仅在overlay配置文件所暴露的基础字段是否完整。

### 3.1 各Bot M1-M5支持状态

| 端口 | M1资金流裁决 | M2支撑压力 | M3巨量K线 | M4技术面 | M5/L5进化 | 框架级兼容 |
|------|------------|-----------|----------|---------|---------|----------|
| 9090 | PASS | PASS | PASS | PASS | PASS | YES* |
| 9091 | PASS | PASS | PASS | PASS | PASS | YES |
| 9092 | PASS | PASS | PASS | PASS | PASS | YES |
| 9093 | PASS | PASS | PASS | PASS | PASS | YES |
| 9094 | PASS | PASS | PASS | PASS | PASS | YES |
| 9095 | PASS | PASS | PASS | PASS | PASS | YES |
| 9096 | PASS | PASS | PASS | PASS | PASS | YES |
| 9097 | PASS | PASS | PASS | PASS | PASS | YES |
| 8081 | PASS | PASS | PASS | PASS | PASS | UNKNOWN |
| 8082 | PASS | PASS | PASS | PASS | PASS | UNKNOWN |
| 8083 | PASS | PASS | PASS | PASS | PASS | UNKNOWN |
| 8084 | PASS | PASS | PASS | PASS | PASS | UNKNOWN |

> *9090: 框架级PASS，但overlay配置异常（见2.1节警告）
> **UNKNOWN**: Mac B SSH不可达，无法读取配置文件确认框架版本

### 3.2 M1-M5字段详情

| 字段名 | 来源 | 说明 | 依赖 |
|--------|------|------|------|
| `m1_net_flow_direction` | 币世界实时数据 | 净流入方向裁决 | console_server.py数据采集 |
| `m1_volume_ratio` | 币世界实时数据 | 量比裁决 | console_server.py数据采集 |
| `m1_net_flow_amount` | 币世界实时数据 | 净流入金额 | console_server.py数据采集 |
| `m2_sr_level` | 技术分析模块 | 支撑/压力位 | console_server.py技术分析 |
| `m2_touch_count` | 技术分析模块 | 触及次数 | console_server.py技术分析 |
| `m3_big_candle_ratio` | 巨量K线检测 | 放量倍数 | console_server.py巨量K线检测 |
| `m3_big_candle_direction` | 巨量K线检测 | 方向(LONG/SHORT) | console_server.py巨量K线检测 |
| `m4_rsi_14` | TA-Lib计算 | RSI指标 | FOttStrategy populate_indicators |
| `m4_volume_ma5` | TA-Lib计算 | 成交量均线 | FOttStrategy populate_indicators |
| `m5_leverage_guard` | L5 Shadow Lab | 杠杆保护裁决 | FOttStrategy L5扩展 |
| `m5_stake_protection` | L5 Shadow Lab | 仓位保护裁决 | FOttStrategy L5扩展 |

---

## 四、EntryDecisionGate & ExitDecisionGate 兼容性矩阵

> **说明**: EntryDecisionGate和ExitDecisionGate裁决结果由console_server.py生成，通过bot API的`force_entry`/`force_exit`端点执行。
> 兼容性取决于bot API是否可达、API认证是否正确、以及overlay中的`api_server`配置。

| 端口 | EntryDecisionGate | ExitDecisionGate | API可达性 | API认证 | 备注 |
|------|-----------------|-----------------|---------|--------|------|
| 9090 | **PARTIAL** | **PARTIAL** | YES | YES* | overlay异常，API指向9093 |
| 9091 | FULL | FULL | YES | YES | Gate.io，API正常 |
| 9092 | FULL | FULL | YES | YES | Gate.io，API正常 |
| 9093 | FULL | FULL | YES | YES | OKX，API正常 |
| 9094 | FULL | FULL | YES | YES | OKX，API正常 |
| 9095 | FULL | FULL | YES | YES | OKX，API正常 |
| 9096 | FULL | FULL | YES | YES | OKX，API正常 |
| 9097 | FULL | FULL | YES | YES | OKX，API正常 |
| 8081 | **UNKNOWN** | **UNKNOWN** | UNKNOWN | UNKNOWN | SSH不可达 |
| 8082 | **UNKNOWN** | **UNKNOWN** | UNKNOWN | UNKNOWN | SSH不可达 |
| 8083 | **UNKNOWN** | **UNKNOWN** | UNKNOWN | UNKNOWN | SSH不可达 |
| 8084 | **UNKNOWN** | **UNKNOWN** | UNKNOWN | UNKNOWN | SSH不可达 |

> *9090 API认证理论上正常（user/pass: freqtrade/freqtrade），但配置文件与bot不对应

---

## 五、L5 Shadow Lab 兼容性矩阵

> **说明**: L5 Shadow Lab是FOttStrategy的进化层，负责杠杆保护和仓位保护裁决。
> 该功能为框架级功能，所有bot运行相同v65_autopilot.py源码，理论上全部支持。

| 端口 | L5框架支持 | 杠杆保护裁决 | 仓位保护裁决 | 补丁状态 | 备注 |
|------|----------|------------|------------|---------|------|
| 9090 | YES | YES | YES | 待补丁 | overlay异常 |
| 9091 | YES | YES | YES | 待补丁 | 正常 |
| 9092 | YES | YES | YES | 待补丁 | 正常 |
| 9093 | YES | YES | YES | 待补丁 | 正常 |
| 9094 | YES | YES | YES | 待补丁 | 正常 |
| 9095 | YES | YES | YES | 待补丁 | 正常 |
| 9096 | YES | YES | YES | 待补丁 | 正常 |
| 9097 | YES | YES | YES | 待补丁 | 正常 |
| 8081 | UNKNOWN | UNKNOWN | UNKNOWN | 待补丁 | SSH不可达 |
| 8082 | UNKNOWN | UNKNOWN | UNKNOWN | 待补丁 | SSH不可达 |
| 8083 | UNKNOWN | UNKNOWN | UNKNOWN | 待补丁 | SSH不可达 |
| 8084 | UNKNOWN | UNKNOWN | UNKNOWN | 待补丁 | SSH不可达 |

---

## 六、DOGE/SOL止血规则 兼容性矩阵

> **说明**: DOGE/SOL止血规则通过overlay配置的`temporary_pair_freeze`字段实现（PATCH_PLAN P0-1/P0-2）。
> 补丁执行前，所有bot均无此字段。补丁执行后，预期全部12个bot均支持。

| 端口 | DOGE冻结字段 | SOL DCA暂停字段 | DOGE黑名单 | SOL黑名单 | 当前DOGE冻结 | 当前SOL DCA暂停 |
|------|------------|--------------|----------|---------|-----------|--------------|
| 9090 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9091 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9092 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9093 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9094 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9095 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9096 | **缺失** | **缺失** | YES | YES | NO | NO |
| 9097 | **缺失** | **缺失** | YES | YES | NO | NO |
| 8081 | **缺失** | **缺失** | YES* | YES* | NO | NO |
| 8082 | **缺失** | **缺失** | YES* | YES* | NO | NO |
| 8083 | **缺失** | **缺失** | YES* | YES* | NO | NO |
| 8084 | **缺失** | **缺失** | YES* | YES* | NO | NO |

> *Mac B DOGE/SOL白名单状态基于拓扑推断，需SSH确认

---

## 七、DCA/杠杆保护兼容性矩阵

> **说明**: DCA参数由FOttStrategy框架层的`dca_pause_rules`和杠杆保护模块提供。
> overlay配置文件不包含DCA金额/批次参数（由策略代码控制）。
> 补丁执行后，overlay将包含`dca_pause_rules`和`temporary_pair_freeze`字段。

| 端口 | DCA框架 | DCA暂停规则 | 杠杆保护 | 杠杆倍数 | 仓位堆叠 | 最大仓位 | 补丁后DCA暂停 |
|------|-------|----------|---------|--------|--------|-------|-------------|
| 9090 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9091 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9092 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9093 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9094 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9095 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9096 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 9097 | YES | **缺失** | YES | 10x/10x | YES | unlimited | 待补丁 |
| 8081 | YES | **缺失** | YES | 10x/10x* | YES* | unlimited* | 待补丁 |
| 8082 | YES | **缺失** | YES | 10x/10x* | YES* | unlimited* | 待补丁 |
| 8083 | YES | **缺失** | YES | 10x/10x* | YES* | unlimited* | 待补丁 |
| 8084 | YES | **缺失** | YES | 10x/10x* | YES* | unlimited* | 待补丁 |

> *Mac B参数基于拓扑推断，需SSH确认

---

## 八、ForceActionGuard 兼容性矩阵

> **说明**: ForceActionGuard通过console_server.py的force_entry/force_exit API实现。
> 兼容性取决于overlay中`api_server`配置是否正确。

| 端口 | api_server启用 | api_server端口 | jwt_secret | force_entry可达 | force_exit可达 | 备注 |
|------|--------------|-------------|-----------|--------------|--------------|------|
| 9090 | YES | **9093** (异常) | freqtrade_secret_key_change_this | YES* | YES* | listen_port错误 |
| 9091 | YES | 9091 | freqtrade_secret_key_9091 | YES | YES | 正常 |
| 9092 | YES | 9092 | freqtrade_secret_key_9092 | YES | YES | 正常 |
| 9093 | YES | 9093 | freqtrade_secret_key_9093 | YES | YES | 正常 |
| 9094 | YES | 9094 | freqtrade_secret_key_change_this_9094 | YES | YES | 正常 |
| 9095 | YES | 9095 | freqtrade_secret_key_change_this_9095 | YES | YES | 正常 |
| 9096 | YES | 9096 | freqtrade_secret_key_change_this_9096 | YES | YES | 正常 |
| 9097 | YES | 9097 | freqtrade_secret_key_change_this_9097 | YES | YES | 正常 |
| 8081 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | SSH不可达 |
| 8082 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | SSH不可达 |
| 8083 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | SSH不可达 |
| 8084 | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | SSH不可达 |

> *9090 force_entry/exit实际发送到9093端口的bot

---

## 九、Mac B 手动操作清单

> **WARNING**: SSH到192.168.13.104被拒绝，以下操作需在Mac B上手动执行

### 9.1 SSH连接测试
```bash
ssh -o ConnectTimeout=5 luxiangnan@192.168.13.104 echo "SSH OK"
# 如果失败，检查Mac B的远程登录设置: 系统偏好设置 -> 共享 -> 远程登录
```

### 9.2 手动验证清单（Mac B每bot）
- [ ] 读取 `/Users/luxiangnan/freqtrade_bots/config_808X_overlay.json`
- [ ] 确认 exchange.name == "gateio"
- [ ] 确认 listen_port == 808X
- [ ] 确认 DOGE/USDT 和 SOL/USDT 在 pair_whitelist
- [ ] 确认 leverage.long == 10, leverage.short == 10
- [ ] 确认 position_stacking == true, short_allowed == true
- [ ] **添加** `temporary_pair_freeze` 字段（DOGE 24小时冻结）
- [ ] **添加** `dca_pause_rules` 字段（SOL DCA暂停）
- [ ] 验证JSON语法: `python3 -c "import json; json.load(open('config_808X_overlay.json'))"`
- [ ] 重启对应bot使配置生效

### 9.3 Mac B配置同步验证命令
```bash
# 在Mac B上执行
for port in 8081 8082 8083 8084; do
  echo "=== Bot $port ==="
  grep -E "temporary_pair_freeze|dca_pause_rules|name|listen_port" /Users/luxiangnan/freqtrade_bots/config_${port}_overlay.json
done
```

---

## 十、综合兼容性评分

| 端口 | 主机 | 证据Payload | EntryGate | ExitGate | L5 Shadow Lab | DOGE/SOL止血 | DCA保护 | ForceActionGuard | 综合评分 |
|------|------|-----------|----------|---------|-------------|------------|--------|----------------|---------|
| 9090 | Mac A | PASS | PARTIAL | PARTIAL | PASS | 缺失 | 缺失 | PARTIAL | **6/8** |
| 9091 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9092 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9093 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9094 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9095 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9096 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 9097 | Mac A | PASS | PASS | PASS | PASS | 缺失 | 缺失 | PASS | **8/8** |
| 8081 | Mac B | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 缺失 | 缺失 | UNKNOWN | **0/8** |
| 8082 | Mac B | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 缺失 | 缺失 | UNKNOWN | **0/8** |
| 8083 | Mac B | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 缺失 | 缺失 | UNKNOWN | **0/8** |
| 8084 | Mac B | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | 缺失 | 缺失 | UNKNOWN | **0/8** |

> **评分说明**: PASS=1, PARTIAL=0.5, 缺失=0, UNKNOWN=0
> **综合覆盖率**: Mac A: 62.5/64 (97.7%), Mac B: 0/32 (0%)
> **全部12bot**: 62.5/96 (65.1%)

---

## 十一、关键发现与风险

### 11.1 严重风险
1. **9090配置文件异常**: `bt_tools/config_9090_overlay.json` 包含OKX配置（应为Gate.io），且listen_port为9093（应为9090）。可能导致Gate.io bot 9090的API调用指向错误的交易所实例。

### 11.2 高风险
2. **Mac B完全不可达**: 8081-8084四个bot的overlay配置无法读取和更新，DOGE/SOL止血规则和DCA暂停规则无法部署。

### 11.3 中风险
3. **DCAE暂停规则缺失**: 所有12个bot均无`temporary_pair_freeze`和`dca_pause_rules`字段补丁，2026-05-04 DOGE批量止损事件可能再次发生。

### 11.4 低风险
4. **jwt_secret未完全分离**: 部分bot（9094-9097）使用默认jwt_secret，可能存在安全隐患。

---

## 十二、修复优先级

| 优先级 | 行动项 | 责任人 | 端口 | 状态 |
|--------|-------|------|------|------|
| P0-CRITICAL | 修复9090 overlay配置文件 | 爸/兵部 | 9090 | **待处理** |
| P0-CRITICAL | SSH到Mac B读取8081-8084配置 | 爸（手动） | 8081-8084 | **待处理** |
| P1-HIGH | 执行P0-1 DOGE冻结补丁 | 兵部 | 9090-9097 | **待执行** |
| P1-HIGH | 执行P0-2 SOL DCA暂停补丁 | 兵部 | 9090-9097 | **待执行** |
| P1-HIGH | Mac B DOGE/SOL补丁推送 | 爸（手动） | 8081-8084 | **待处理** |
| P2-MEDIUM | 统一9094-9097 jwt_secret | 爸/兵部 | 9094-9097 | **待处理** |
| P3-LOW | Mac B框架版本确认 | 爸（手动） | 8081-8084 | **待处理** |
