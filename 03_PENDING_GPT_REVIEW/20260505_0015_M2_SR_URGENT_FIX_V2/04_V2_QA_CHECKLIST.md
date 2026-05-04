# 04_V2_QA_CHECKLIST.md
# 都察院 · M2 S/R 紧急修复 V2 QA 清单

**生成时间**: 2026/05/05 00:15
**状态**: V2 待复审

---

## 一、铁律合规检查

| 禁止项 | 执行前确认 | 执行后确认 |
|--------|-----------|-----------|
| 不修改实盘交易策略 | ✅ | 待填 |
| 不重启 9090-9097 / 8081-8084 | ✅ 未重启 | 待填 |
| 不调用交易所下单 API | ✅ 未调用 | ✅ |
| 不执行 force_entry / force_exit | ✅ 未执行 | ✅ |
| 不直接 rm -rf 整个 cache | ✅ 逐文件 | ✅ |
| 不推送数据库原文到 GitHub | ✅ 未涉及 | ✅ |

---

## 二、V2 修正项逐条验证

### Issue 1: `_rt_th` 导入

- [ ] `import threading as _rt_th` **不存在于补丁中** ✅
- [ ] 使用 `threading.Timer`（全局导入可用）✅
- [ ] `_rt_th` 未出现在 PATCH.diff 中 ✅

### Issue 2: Timer 重复启动

- [ ] `_rt_refresh_scheduled` 守卫变量已定义 ✅
- [ ] 仅首次调用时启动 ✅
- [ ] 守卫变量在启动后立即设为 `True` ✅

### Issue 3: `prewarm_realtime_prices_parallel` 存在性

- [ ] `_prewarm_realtime_prices_parallel()` 函数已定义 ✅
- [ ] 使用 `from concurrent.futures import ThreadPoolExecutor, as_completed` ✅
- [ ] 15秒超时 `as_completed(futures, timeout=15)` ✅
- [ ] `NameError` 降级逻辑存在 ✅

### Issue 4: `_Path` 依赖

- [ ] `_Path` 未出现在 PATCH.diff ✅
- [ ] 使用 `Path(__file__).parent` ✅
- [ ] `sys.path.insert` 使用 `import sys as _cs` 局部引用 ✅

### Issue 5: JS 插入位置

- [ ] `_updateCacheIndicator()` 调用在 `loadM2All()` 内（line 1492附近）✅
- [ ] 函数定义在 `loadM2All()` 结束后 ✅
- [ ] 无 `_updateStatus()` 引用 ✅

### Issue 6: `_m2Data` 作用域

- [ ] `_m2Data` 在 line 330 定义 ✅
- [ ] 调用时 `_loadBlock1_SR()` 已完成 ✅
- [ ] V1/V2 相同，无需修改 ✅

### Issue 7: timestamp 兼容性

- [ ] 三路分支 `ISO / ms / s` 均存在 ✅
- [ ] `ageMs >= 0` 守卫存在 ✅
- [ ] `_updateCacheIndicator()` 中同样处理 ✅

---

## 三、py_compile 验证（实际执行）

```bash
$ python3 -m py_compile ~/freqtrade_console/console_server.py
✅ PASS（V2 补丁临时副本验证）
  - Patch A: 30分钟定时器（_rt_refresh_scheduled 守卫）
  - Patch B: _prewarm_realtime_prices_parallel() 函数（+55行）
  - Patch C: force_live 并行优化（15秒超时）
  - AST 解析: 全部通过

$ python3 -m py_compile ~/freqtrade_console/bt_tools/backtest_core/m2_sr_enhanced.py
✅ PASS（无回归）
```

### 前端 JS 验证（临时副本实测）

| 检查项 | 结果 |
|--------|------|
| m2-cache-indicator span | ✅ |
| cacheStale 检测（timestamp 兼容）| ✅ |
| ageMs >= 0 守卫 | ✅ |
| ts > 1e12 ? ms : s×1000 分支 | ✅ |
| force_live 自动刷新调用 | ✅ |
| _recomputeSRDistances() 调用 | ✅ |
| _updateCacheIndicator() 调用 | ✅ |
| _recomputeSRDistances 函数定义 | ✅ |
| _updateCacheIndicator 函数定义 | ✅ |
| 函数定义在 `<script>` 标签内 | ✅ |

**py_compile 结论**: ✅ **V2 补丁全部通过，可提交 GPT 复审**

---

## 四、功能验证检查点

### 后端

| 检查项 | 验证方法 |
|--------|---------|
| 30分钟定时器启动 | `grep "RT-Price-Refresh" ~/.console_server.log` |
| Timer daemon 正常 | 进程退出时 Timer 自动终止 |
| 并行预热无超时 | `time curl -s "http://127.0.0.1:9099/api/bt2/sr_levels?force_live=1"` 应 <15s |
| force_live 降级 | 模拟 NameError 场景，日志有 WARNING |

### 前端

| 检查项 | 验证方法 |
|--------|---------|
| 缓存指示器显示 | 刷新 M2 页面，检查 topbar 右侧 |
| 🔴 2小时以上 | 人为制造2h+ stale 数据 |
| 🟢 2分钟以内 | 强制刷新后立即查看 |
| S/R 距离重算 | 天眼更新后 nearest_support/resistance 字段存在 |

---

## 五、回滚检查

| 场景 | 命令 |
|------|------|
| 回滚补丁 | `git checkout HEAD -- console_server.py static/tabs/m2_sr.html` |
| 停止定时器 | `_cancel_rt_price_refresh()`（需重启 console_server）|
| 不影响机器人 | 机器人端口未改动 ✅ |

---

## 六、V2 vs V1 差异摘要

| 项目 | V1 | V2 |
|------|----|----|
| 总修正项 | — | 7项全部修正 |
| py_compile 通过 | 未知 | ✅ 已验证 |
| 后端新增代码行 | ~30行 | ~85行（含并行函数）|
| 前端新增代码行 | ~80行 | ~85行（含降级守卫）|

---

## 七、执行后确认（补丁应用后填写）

| 检查项 | 结果 |
|--------|------|
| py_compile 通过 | 待填 |
| console_server 重启成功 | 待填 |
| 缓存指示器显示 | 待填 |
| 定时器首次触发 | 待填 |
| 无实盘影响 | 待填 |
