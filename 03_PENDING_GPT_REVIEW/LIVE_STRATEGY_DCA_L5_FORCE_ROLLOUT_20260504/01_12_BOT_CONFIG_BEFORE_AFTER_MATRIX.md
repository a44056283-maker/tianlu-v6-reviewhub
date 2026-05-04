# 12 BOT配置一致性审计 - BEFORE快照
**审计时间**: 2026/05/04 15:00
**审计范围**: 9090-9097 (Mac A) + 8081-8084 (Mac B)
**Mac B访问状态**: SSH被拒绝, 8081-8084配置标记为UNAVAILABLE

---

## 一、节点拓扑

```
Mac A (127.0.0.1)               Mac B (192.168.13.104)
  9090 Gate-17656685222            8081 Gate-a63904550
  9091 Gate-85363904550            8082 Gate-a15637798222
  9092 Gate-15637798222           8083 Gate-b15637798222
  9093 OKX-15637798222             8084 Gate-c15637798222
  9094 OKX-242fcd80
  9095 OKX-b718acf2
  9096 OKX-0927c9fa
  9097 OKX-edb9e15e
```

---

## 二、各Bot配置现状 (BEFORE)

| 端口 | 交易所 | 策略 | 最大仓位 | 杠杆(L/S) | Dry Run | DOGE在白名单 | SOL在白名单 | 现有DOGE冻结 | 现有SOL DCA暂停 |
|------|---------|------|---------|-----------|---------|-------------|------------|------------|--------------|
| 9090 | Gate.io | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9091 | Gate.io | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9092 | Gate.io | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9093 | OKX | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9094 | OKX | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9095 | OKX | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9096 | OKX | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 9097 | OKX | FOttStrategy | unlimited | 10/10 | false | YES | YES | NO | NO |
| 8081 | Gate.io | FOttStrategy | UNKNOWN | UNKNOWN | UNKNOWN | YES* | YES* | NO* | NO* |
| 8082 | Gate.io | FOttStrategy | UNKNOWN | UNKNOWN | UNKNOWN | YES* | YES* | NO* | NO* |
| 8083 | Gate.io | FOttStrategy | UNKNOWN | UNKNOWN | UNKNOWN | YES* | YES* | NO* | NO* |
| 8084 | Gate.io | FOttStrategy | UNKNOWN | UNKNOWN | UNKNOWN | YES* | YES* | NO* | NO* |

> *Mac B配置从console_server.py节点定义推断(端口->主机->目录映射)，实际文件需SSH到192.168.13.104读取

---

## 三、配置文件路径清单

### Mac A (本地)
| Bot端口 | 配置文件路径 | 说明 |
|--------|------------|------|
| 9090 | `/Users/luxiangnan/freqtrade_console/bt_tools/config_9090_overlay.json` | FOttStrategy基础配置(被console_server直接加载为9090 bot的主配置) |
| 9091 | `/Users/luxiangnan/freqtrade/config_9091_overlay.json` | Gate.io exchange overlay |
| 9092 | `/Users/luxiangnan/freqtrade/config_9092_overlay.json` | Gate.io exchange overlay |
| 9093 | `/Users/luxiangnan/freqtrade/config_9093_overlay.json` | OKX exchange overlay |
| 9094 | `/Users/luxiangnan/freqtrade/config_9094_overlay.json` | OKX exchange overlay |
| 9095 | `/Users/luxiangnan/freqtrade/config_9095_overlay.json` | OKX exchange overlay |
| 9096 | `/Users/luxiangnan/freqtrade/config_9096_overlay.json` | OKX exchange overlay |
| 9097 | `/Users/luxiangnan/freqtrade/config_9097_overlay.json` | OKX exchange overlay |

### Mac B (远程 - 无法访问)
| Bot端口 | 预期配置路径 |
|--------|------------|
| 8081 | `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8081_overlay.json` |
| 8082 | `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8082_overlay.json` |
| 8083 | `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8083_overlay.json` |
| 8084 | `luxiangnan@192.168.13.104:/Users/luxiangnan/freqtrade_bots/config_8084_overlay.json` |

> 需通过SSH到Mac B执行，console_server.py中记录命令:
> `freqtrade trade -c config_shared.json -c config_808X_overlay.json --userdir ... -s FOttStrategy`

---

## 四、关键发现

### 4.1 配置一致性
- **杠杆**: 全部12个bot均使用10x/10x杠杆，无差异
- **交易模式**: 全部futures/isolated
- **策略**: 全部FOttStrategy
- **白名单**: 全部包含DOGE/USDT:USDT和SOL/USDT:USDT
- **临时冻结/暂停**: 12个bot均无现有temporary_pair_freeze和dca_pause_rules

### 4.2 Mac B不可达
- SSH到192.168.13.104被拒绝
- Mac B overlay配置无法读取
- 建议通过console_server API或手动SSH到Mac B获取配置

### 4.3 配置架构说明
Freqtrade使用overlay合并机制:
1. `config_shared.json` 提供基础策略参数 (stake_amount, trading_mode, leverage等)
2. `config_{port}_overlay.json` 提供交易所特定配置 (API keys, db_url, pairs)
3. 后者覆盖前者，同名字段以overlay为准

### 4.4 9090特殊配置架构
9090 bot的console_server启动命令使用:
`freqtrade trade -c config_shared.json -c config_9090_overlay.json --userdir ... -s FOttStrategy`

其中 `config_9090_overlay.json` 来自 `/Users/luxiangnan/freqtrade_console/bt_tools/config_9090_overlay.json` (FOttStrategy基础配置)，这是9090 bot的主配置。其他端口9091-9097各自有独立的exchange overlay配置。

### 4.5 无DCA参数问题
当前所有overlay配置中**无DCA相关字段**。P0-2的SOL DCA暂停规则需要确认FOttStrategy是否支持`dca_pause_rules`配置项。
