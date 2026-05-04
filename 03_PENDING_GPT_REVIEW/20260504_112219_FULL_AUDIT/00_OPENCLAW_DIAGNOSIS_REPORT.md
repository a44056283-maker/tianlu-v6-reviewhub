# OpenClaw 飞书/微信/子代理无响应诊断报告
生成时间: 2026-05-04
诊断执行时间戳: 20260504_095443

---

## 一、故障根因判断

**结论：部分修复，已识别需要额外修改的根因**

诊断覆盖5个维度，确认：
1. ✅ Gateway 正在运行，18789 端口正常监听
2. ✅ MiniMax 不再走 /v1/responses（主会话 HEARTBEAT 正常）
3. ✅ openclaw.json JSON 结构正常
4. ✅ 所有 agent 和 cron 使用 minimax2-7/MiniMax-M2.7-highspeed
5. ❌ 孤立会话（cron、embedded agent）仍然调用 /v1/responses

---

## 二、Gateway 运行状态

| 检查项 | 结果 |
|--------|------|
| Gateway 进程 | ✅ 运行中 (pid=55441) |
| 18789 端口监听 | ✅ 127.0.0.1:18789 |
| launchctl 状态 | ✅ running (runs=3) |
| 飞书消息接收 | ✅ 日志显示消息正常接收 |
| HEARTBEAT | ✅ minimax2-7/MiniMax-M2.7-highspeed 成功响应 |
| Feishu 回复 | ❌ timeout of 30000ms exceeded |

---

## 三、配置 JSON 检查

| 文件 | JSON 状态 |
|------|----------|
| openclaw.json | ✅ JSON_OK |
| agents/*/models.json | ✅ 结构正确 (models.providers) |
| agents/*/auth-profiles.json | ✅ 存在 |
| cron/jobs.json | ✅ 22个任务使用 minimax2-7/MiniMax-M2.7-highspeed |

---

## 四、/v1/responses 问题

**gateway.log 中：0 次 /v1/responses**
**gateway.err.log 中：3014 次 /v1/responses**（历史累积）

**关键发现：**

主会话（gateway 直接处理的会话）已修复：
```
[gateway] agent model: minimax2-7/MiniMax-M2.7-highspeed
[plugins] [lcm] Compaction summarization model: minimax2-7/MiniMax-M2.7-highspeed
```

孤立会话（embedded agent / cron）仍然失败：
```
unexpected status 404 Not Found: 404 page not found, 
url: https://api.minimaxi.com/v1/responses
```

**根因分析（详细）：**

`model-D_zg2j4m.js` 的 API 解析链（第377行）：
```javascript
api: resolvedTransport.api 
    ?? normalizeResolvedTransportApi(discoveredModel.api) 
    ?? resolveConfiguredProviderDefaultApi(providerConfig) 
    ?? "openai-responses"
```

孤立会话的问题：
- 传入的 `cfg` 没有 `models.providers`（孤立会话用最小化配置）
- `providerConfig = undefined`
- `resolveConfiguredProviderDefaultApi(undefined)` → 返回 `undefined`
- 最终落到 `?? "openai-responses"` — 这是 /v1/responses 的来源

但 `baseUrl` 却正确（`https://api.minimaxi.com/v1`），说明有部分 cfg 被传进来了。

`normalizeTransport` hook 只在 `providerConfig` 存在且 `providerConfig.api === undefined` 时才触发将 `anthropic-messages` 转为 `openai-completions`。

我们的 `minimax2-7` provider 有明确的 `api: "openai-completions"`，所以 hook 根本不触发。

---

## 五、MiniMax Provider 当前配置

| 项目 | 值 |
|------|-----|
| Provider ID | minimax2-7（自定义） |
| baseUrl | https://api.minimaxi.com/v1 |
| api | openai-completions |
| 模型 | MiniMax-M2.7-highspeed |
| 主会话状态 | ✅ 正常（HEARTBEAT 成功） |
| 孤立会话状态 | ❌ 失败（/v1/responses） |

**为什么主会话正常但孤立会话失败：**

主会话走 gateway 进程，gateway 的 `cfg` 有完整的 `models.providers`，所以 `normalizeTransport` hook 正确触发。

孤立会话走 embedded agent，它们的 `cfg` 对象是孤立化的，没有 `models.providers` 部分，导致 `providerConfig` 为 undefined。

---

## 六、第三方模型残留

✅ **无第三方模型残留** — 所有 agent、cron、默认配置均使用 `minimax2-7/MiniMax-M2.7-highspeed`。

---

## 七、Doctor 警告项

| 警告 | 影响 | 建议 |
|------|------|------|
| openclaw-weixin channelConfigs metadata 缺失 | 非致命 | 可忽略 |
| device-pair / claude-mem disabled but config present | 非致命 | 可忽略 |
| commands.ownerAllowFrom 未设置 | 安全 | 可忽略（内网） |
| PATH 包含过多版本管理器 | 性能 | 建议清理 |
| 2个 orphan agent dirs（main, tianfu） | 非致命 | 可忽略 |
| 813个 orphan transcripts | 存储 | 可清理 |
| 1个 session lock | 正常 | 无需处理 |
| Feishu reply timeout | **致命** | 需要修复 |

---

## 八、需要修改的文件

### 方案：重命名 Provider 为 minimax（利用内置 hook）

孤立会话的 `cfg` 有 `agents` 部分但没有 `models.providers`。内置 `minimax` provider 的 `normalizeTransport` hook 会在 `providerConfig.api === undefined` 时自动将 CN endpoint 的 API 从 `anthropic-messages` 转换为 `openai-completions`。

需要修改：

1. **openclaw.json** — 将 `minimax2-7` provider 改名为 `minimax`（覆盖内置），保留 baseUrl 和 apiKey
2. **cron/jobs.json** — 所有22个 cron job 的 model 从 `minimax2-7/MiniMax-M2.7-highspeed` 改为 `minimax/MiniMax-M2.7-highspeed`
3. **agents/*/models.json** — provider 从 `minimax2-7` 改为 `minimax`（所有子代理）

### 或者：不变 provider 名，添加 normalizeTransport hook

在 `models.providers.minimax2-7` 中添加 `normalizeTransport` 函数：
```json
"minimax2-7": {
  "baseUrl": "https://api.minimaxi.com/v1",
  "api": "anthropic-messages",
  "normalizeTransport": { ... },
  ...
}
```
（但 OpenClaw 是否支持在 provider config 中加 hook 需验证）

---

## 九、备份路径

本次诊断为纯诊断，未做修改。
备份路径：已在之前修复时创建：
- `~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/openclaw_minimax_unified_fix_20260504_090943/`
- `~/Desktop/Tianlu_V6_5_Workspace/04_BACKUPS/openclaw_models_struct_fix_20260504_091711/`

---

## 十、是否建议重启 Gateway

**暂不重启。** 需要先执行上述修复方案，然后再重启验证。

---

## 十一、是否需要回滚

本次诊断未做修改，无需回滚。

---

## 十二、后续修复步骤（待用户确认后执行）

1. 备份 openclaw.json、cron/jobs.json、所有 agents/*/models.json
2. 修改 openclaw.json 中的 provider 名称（或添加 normalizeTransport hook）
3. 修改 cron/jobs.json 中的 model 引用
4. 修改所有 agents/*/models.json 中的 provider 引用
5. 验证 JSON 正确性
6. 生成修改报告
7. 询问用户是否重启 gateway
8. 用户确认后执行 `openclaw gateway restart`
9. 飞书/微信发送测试消息验证

---

## 十三、诊断文件清单

- `openclaw_no_response_diagnosis_20260504_095443/01_openclaw_status.txt` — 基础状态
- `openclaw_no_response_diagnosis_20260504_095443/02_config_check.txt` — JSON 和配置文件
- `openclaw_no_response_diagnosis_20260504_095443/03_model_provider_scan.txt` — 模型/provider 扫描
- `openclaw_no_response_diagnosis_20260504_095443/04_gateway_logs.txt` — Gateway 日志

