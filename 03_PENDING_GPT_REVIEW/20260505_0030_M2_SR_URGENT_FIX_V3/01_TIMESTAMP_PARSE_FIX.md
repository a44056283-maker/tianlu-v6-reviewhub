# 01_TIMESTAMP_PARSE_FIX.md
# V3 修正 #1: Timestamp 秒级/毫秒级解析逻辑

---

## 根因分析

### V2 的 bug

V2 代码：
```javascript
const d = new Date(ts);
if (!isNaN(d.getTime())) {
  ageMs = Date.now() - d.getTime();              // ISO 字符串
} else if (typeof ts === 'number' && ts > 0) {
  ageMs = ts > 1e12 ? Date.now() - ts : Date.now() - ts * 1000;  // 数字
}
```

**问题**: `new Date(ts)` 对任何正数都返回有效 Date（不触发 `isNaN`），
但 Unix 秒级数字（如 `1777910404`）会被 `new Date()` 错误解释为毫秒，
得到 `1970/01/21` 的日期。

此时 `Date.now() - d.getTime()` 结果巨大（≈当前时间戳），必然 `≥ 2h`，
条件"意外"通过，但实际上 ageMs 根本不是真实年龄。

### 边界值分析

| ts 值 | 类型 | new Date(ts) 解释 | 实际应为 |
|--------|------|------------------|---------|
| `1777910404` | 秒（10位数）| 1777910404ms = 1970年 | ×1000 → 2026年 |
| `1777910404000` | 毫秒（13位数）| 1777910404000ms = 2026年 | 直接用 |
| `"1777910404"` | 秒字符串 | 1970年（触发 isNaN false）| 先 parseInt 再×1000 |
| `"2026-05-05T..."` | ISO 字符串 | 正确 | 直接用 |

**关键结论**: 数字秒（10位数 < 1e10）< 数字毫秒（13位数 > 1e12）。
1e12（12位数）以下是秒级，统一 ×1000。

---

## V3 修正

```javascript
let ageMs;
if (typeof ts === 'string' && ts.trim()) {
  // ISO 字符串或带空格的秒字符串
  const d = new Date(ts);
  if (!isNaN(d.getTime())) {
    ageMs = Date.now() - d.getTime();
  } else {
    // 纯数字字符串秒 → parseInt 后 ×1000
    const numeric = parseInt(ts, 10);
    if (!isNaN(numeric) && numeric > 0) {
      ageMs = numeric < 1e12 ? Date.now() - numeric * 1000 : Date.now() - numeric;
    }
  }
} else if (typeof ts === 'number' && ts > 0) {
  // 纯数字
  // < 1e12 → 秒级 → ×1000
  // ≥ 1e12 → 毫秒级 → 直接用
  ageMs = ts < 1e12 ? Date.now() - ts * 1000 : Date.now() - ts;
}
```

**核心修复**: 去掉 `new Date(ts)` 作为数字解析路径，
改为显式判断 `ts < 1e12` → 秒级 → ×1000。

---

## 影响范围

| 位置 | 函数 | 修正 |
|------|------|------|
| m2_sr.html | `_loadBlock1_SR()` 内 cacheStale 检测 | ✅ |
| m2_sr.html | `_updateCacheIndicator()` 内 | ✅ |
| PATCH.diff | 两处 timestamp 解析 | ✅ |
