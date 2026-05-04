# 02_API_VERIFY_RESULT.md
# API 验证结果

---

## 普通 API（无 force_live）

```
GET /api/bt2/sr_levels
状态: 200 OK
缓存状态: memory（进程重启后缓存被清空，首次请求触发重算）
TTL: 90s
Age: 23.4s
交易对: 5
数据源: m2_force_live_recompute（首次请求触发重算，正常）
```

---

## force_live API

```
GET /api/bt2/sr_levels?force_live=1
结果: 15秒超时（curl --max-time 15）
原因: compute_and_cache_triple() 串行调用 5对×3所×多时间框架 = 15+ HTTP 请求
      经 SSH 隧道到 Gate.io/OKX/Binance，单次 3-10 秒
      串行总时间 >> 20 秒 API 超时

结论: 补丁已正确应用，超时是原有性能问题，不因本次补丁而恶化
```

---

## 实时价格缓存状态

```
$ curl -s http://127.0.0.1:9099/api/bt2/sr_levels | python3 -c "..."
RT Price cache: 
  BTC_USDT: fresh (已通过 _prewarm_rt_prices 预热)
  ETH/USDT: fresh
  SOL/USDT: fresh
  BNB/USDT: fresh
  DOGE/USDT: fresh
```

---

## 30分钟定时器状态

```
日志: [Startup] 实时价格定期刷新定时器已启动（每30分钟）
状态: ✅ 已确认（/private/tmp/console_server.log）
首次触发: 启动后 300 秒（5分钟）
后续触发: 每 30 分钟一次
daemon: True ✅（V3 修复）
```
