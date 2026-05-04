# 03_V2_FRONTEND_PATCH.md
# M2 S/R 紧急修复 V2 — 前端补丁（m2_sr.html）
# 修正：timestamp兼容性、_m2Data作用域、插入位置

---

## 补丁位置总览

| 区域 | 文件 | 插入位置 | 内容 |
|------|------|---------|------|
| A | m2_sr.html | topbar HTML (line ~178) | 缓存年龄指示器 `<span>` |
| B | m2_sr.html | `_loadBlock1_SR()` 内 (line ~1319) | Triple 缓存过期自动 force_live |
| C | m2_sr.html | `_loadBlock2_AI()` 内 (line ~1392) | 实时价格覆盖后重算 S/R |
| D | m2_sr.html | `loadM2All()` 结束前 (line ~1492) | `_updateCacheIndicator()` 调用 |
| E | m2_sr.html | 文件末尾 (line ~1496后) | 函数定义 |

---

## 补丁 A：Topbar 缓存年龄指示器

**插入位置**: `m2_sr.html` line 178（`<span style="font-size:11px;color:var(--gold)" id="scan-ts">--</span>` 之后）

**V1 问题**: V1 正确插入，无需修正

```html
      <!-- V2: 数据年龄和来源指示器 -->
      <span id="m2-cache-indicator" style="font-size:10px;color:var(--dimmer);margin-left:4px"
            title="数据新鲜度"></span>
```

---

## 补丁 B：Triple 缓存过期自动 force_live（修复 timestamp 兼容性）

**插入位置**: `m2_sr.html` line 1319（`let rawPairs = srR.pairs || {};` 之前）

**V1 问题**:
- `ts > 1e12` 无法区分秒级和毫秒级字符串 timestamp
- 字符串 `"1777910404" > 1e12` → `false`（误判为毫秒）

**V2 修正**:

```javascript
    // ── V2: Triple 缓存过期检测（修复 timestamp 兼容性）───────────────
    let cacheStale = false;
    if (!forceLive && srR.pairs) {
      const firstPair = Object.values(srR.pairs)[0];
      const ts = firstPair?.timestamp;
      if (ts !== undefined && ts !== null) {
        try {
          let ageMs;
          const d = new Date(ts);
          if (!isNaN(d.getTime())) {
            // ISO 字符串或 Date 对象
            ageMs = Date.now() - d.getTime();
          } else if (typeof ts === 'number' && ts > 0) {
            // 纯数字：统一转为毫秒
            // 秒级 (1e9–1e12): ×1000 → 毫秒
            // 毫秒级 (>1e12): 直接使用
            ageMs = ts > 1e12 ? Date.now() - ts : Date.now() - ts * 1000;
          }
          if (ageMs !== undefined && ageMs >= 0 && ageMs / 3600000 >= 2) {
            log('⚠️ Triple缓存超过2小时，自动触发强制刷新', 'warn');
            cacheStale = true;
          }
        } catch(e) {}
      }
      // 额外兜底：_cache.age_sec ≥ 90s 也视为过期
      if ((srR._cache?.age_sec || 0) >= 90) cacheStale = true;
    }
    if (cacheStale && !forceLive) {
      const liveR = await _fetchJsonFast('/api/bt2/sr_levels?force_live=1', 25000).catch(() => ({}));
      if (liveR && liveR.ok && liveR.pairs && Object.keys(liveR.pairs).length > 0) {
        srR = liveR;
        log('✅ 强制刷新成功，S/R数据已更新', 'ok');
      }
    }
```

**关键修复**:
1. ✅ 统一处理 ISO 字符串、数字秒、数字毫秒三种格式
2. ✅ `ageMs >= 0` 防止 `NaN` 导致误判
3. ✅ 秒级判断：`ts > 1e12` → 毫秒直接用；否则 ×1000 转毫秒

---

## 补丁 C：天眼 AI 更新后重算 S/R 距离

**插入位置**: `m2_sr.html` line 1391（`if (_m2Data[pair]) { ... }` 块内，在 `_m2Data[pair].scene_short = td.scene_short;` 之后）

**V1 问题**: V1 正确插入，无需修正（V1 和 V2 相同）

```javascript
      // ── V2: 实时价格覆盖后重算 S/R 距离 ───────────────────────
      _recomputeSRDistances(pair, _m2Data[pair]);
```

---

## 补丁 D：`_updateCacheIndicator()` 调用点

**插入位置**: `m2_sr.html` line 1492（`loadM2All()` 结束前的日志行）

**V1 问题**: V1 在末尾注释 "// 在 _updateStatus() 函数末尾添加"，但该函数不存在

**V2 修正**: 改为在 `loadM2All()` 完成后调用

```javascript
  // V2: 更新缓存年龄指示器
  _updateCacheIndicator();

  dot.className = 'status-dot green';
```

---

## 补丁 E：函数定义（文件末尾 line 1496 后）

**V1 问题**: V1 在文件末尾注释插入位置不明确

**V2 修正**: 在 `loadM2All()` 结束后的文件末尾添加

```javascript
// ── V2: S/R 距离重算函数 ────────────────────────────────────────────
function _recomputeSRDistances(pair, data) {
  if (!data || !data.levels || !data.current_price) return;
  const price = Number(data.current_price);
  if (!price || price <= 0) return;
  const levels = data.levels;
  let nearest_support = null, nearest_resistance = null;
  let min_support_dist = Infinity, min_resist_dist = Infinity;
  for (const lvl of levels) {
    const p = Number(lvl.price);
    if (!p || p <= 0) continue;
    const dist = (price - p) / p * 100;
    if (dist > 0 && dist < min_support_dist) { min_support_dist = dist; nearest_support = p; }
    if (dist < 0 && Math.abs(dist) < min_resist_dist) { min_resist_dist = Math.abs(dist); nearest_resistance = p; }
  }
  data.nearest_support = nearest_support;
  data.nearest_resistance = nearest_resistance;
  data.dist_to_support_pct = min_support_dist < Infinity ? min_support_dist : null;
  data.dist_to_resistance_pct = min_resist_dist < Infinity ? min_resist_dist : null;
}

// ── V2: 缓存年龄指示器更新 ──────────────────────────────────────────
function _updateCacheIndicator() {
  const el = document.getElementById('m2-cache-indicator');
  if (!el) return;
  const pairs = window._m2Data || {};
  const pairKeys = Object.keys(pairs);
  if (!pairKeys.length) return;
  const firstPair = pairs[pairKeys[0]];
  const ts = firstPair?.timestamp;
  if (!ts) return;
  let ageMs;
  try {
    const d = new Date(ts);
    if (!isNaN(d.getTime())) {
      ageMs = Date.now() - d.getTime();
    } else if (typeof ts === 'number' && ts > 0) {
      ageMs = ts > 1e12 ? Date.now() - ts : Date.now() - ts * 1000;
    }
  } catch(e) {}
  if (ageMs === undefined || ageMs < 0) return;
  const ageMin = ageMs / 60000, ageH = ageMin / 60;
  const src = firstPair?.data_source || '';
  const srcLabel = src.includes('triple') ? '三所' :
                   src.includes('single') ? '单所' :
                   src.includes('fallback') ? '回退' :
                   src ? src.slice(0,8) : '未知';
  const label = ageMin < 2   ? `🟢 ${Math.round(ageMin)}分钟前 | ${srcLabel}` :
                 ageMin < 15 ? `🟡 ${Math.round(ageMin)}分钟前 | ${srcLabel}` :
                 ageH < 2    ? `🟠 ${Math.round(ageMin)}分钟前 | ${srcLabel}` :
                               `🔴 ${ageH.toFixed(1)}小时前 | ${srcLabel}`;
  el.textContent = label;
  el.style.color = ageMin < 2   ? 'var(--green)'  :
                   ageMin < 15 ? 'var(--yellow)' :
                   'var(--red)';
  el.title = `数据源: ${src}`;
}
```

---

## V2 vs V1 对比

| 问题 | V1 | V2 |
|------|----|----|
| 6. _m2Data 作用域 | 作用域正确，V1/V2 相同 | ✅ 无需修改 |
| 7. timestamp 兼容性 | `ts > 1e12` 无法处理秒级数字 | 统一处理 ISO/秒/毫秒三种格式 |
| 5. JS 插入位置 | 末尾注释不明确 | 精确指定5个插入点 |
