# 前端院 · m2_sr.html 补丁：过期判断 + 实时价格重算 + 数据年龄展示

**草案文件** | **禁止直接写入实盘**

---

## 1. 问题定位

### 1.1 前端无数据年龄展示

**位置**: `m2_sr.html:176-178`（topbar）

```html
<!-- 当前代码（无年龄展示）-->
<span class="status-dot yellow pulse" id="status-dot"></span>
<span style="font-size:11px;color:var(--muted)" id="status-text">就绪</span>
<span style="font-size:11px;color:var(--gold)" id="scan-ts">--</span>
```

**问题**: 无论数据多老，始终显示"就绪"，用户无法判断数据是否过期。

### 1.2 实时价格覆盖后未重算 S/R 距离

**位置**: `m2_sr.html:1379-1388`（天眼AI更新 current_price）

天眼AI更新了 `_m2Data[pair].current_price`，但没有重新计算：
- `nearest_support`
- `nearest_resistance`
- `dist_to_support_pct`
- `dist_to_resistance_pct`

**影响**: 显示"新价格 + 旧支撑/压力位"，造成距离数据不准确。

---

## 2. 补丁一：topbar 显示数据年龄和来源

### 修改位置: `m2_sr.html` topbar 区段（约第176行）

```javascript
// 修改前:
<span class="status-dot yellow pulse" id="status-dot"></span>
<span style="font-size:11px;color:var(--muted)" id="status-text">就绪</span>
<span style="font-size:11px;color:var(--gold)" id="scan-ts">--</span>

// 修改后（Stage B 新增）:
<span class="status-dot yellow pulse" id="status-dot"></span>
<span style="font-size:11px;color:var(--muted)" id="status-text">就绪</span>
<span style="font-size:11px;color:var(--gold)" id="scan-ts">--</span>
<!-- Stage B 新增: 数据年龄和来源 -->
<span id="m2-cache-indicator" style="font-size:10px;color:var(--dimmer);margin-left:4px"
      title="数据新鲜度"></span>
```

---

## 3. 补丁二：`_updateStatus()` 显示缓存年龄

### 修改位置: `m2_sr.html` 约第1420-1500行 `_updateStatus()` 函数

```javascript
// 在 _updateStatus() 函数末尾（状态更新后）添加:

// ── Stage B 新增: 数据年龄和来源展示 ────────────────────────
function _updateCacheIndicator() {
  const el = document.getElementById('m2-cache-indicator');
  if (!el) return;

  // 从 srR._cache 获取 API 缓存年龄（90s TTL）
  const apiAge = window._m2ApiCacheAge || 0; // 秒
  // 从任意一个 pair 的 timestamp 计算 triple 缓存年龄
  const pairs = window._m2Data || {};
  let cacheAgeStr = '';
  let staleLevel = 'fresh'; // fresh | aging | stale

  const pairKeys = Object.keys(pairs);
  if (pairKeys.length > 0) {
    const firstPair = pairs[pairKeys[0]];
    const ts = firstPair?.timestamp;
    if (ts) {
      // 尝试解析 ISO 时间
      let ageMs;
      try {
        const d = new Date(ts);
        if (!isNaN(d.getTime())) {
          ageMs = Date.now() - d.getTime();
        } else if (typeof ts === 'number' && ts > 1e12) {
          ageMs = Date.now() - ts;
        }
      } catch(e) {}
      if (ageMs !== undefined) {
        const ageMin = ageMs / 60000;
        const ageH = ageMin / 60;
        if (ageMin < 2) {
          cacheAgeStr = `🟢 ${Math.round(ageMin)}分钟前`;
          staleLevel = 'fresh';
        } else if (ageMin < 15) {
          cacheAgeStr = `🟡 ${Math.round(ageMin)}分钟前`;
          staleLevel = 'aging';
        } else if (ageH < 2) {
          cacheAgeStr = `🟠 ${Math.round(ageMin)}分钟前`;
          staleLevel = 'stale';
        } else {
          cacheAgeStr = `🔴 ${ageH.toFixed(1)}小时前`;
          staleLevel = 'stale';
        }
      }
    }
    // data_source
    const src = firstPair?.data_source || '';
    const srcLabel = src.includes('triple') ? '三所' :
                     src.includes('single') ? '单所' :
                     src.includes('fallback') ? '回退' :
                     src ? src.slice(0, 8) : '未知';
    el.textContent = cacheAgeStr ? `${cacheAgeStr} | ${srcLabel}` : '';
    el.style.color = staleLevel === 'fresh' ? 'var(--green)' :
                     staleLevel === 'aging' ? 'var(--yellow)' : 'var(--red)';
    el.title = `数据源: ${src}\nAPI缓存: ${apiAge.toFixed(0)}秒`;
  }
}

// 修改 _updateStatus 末尾，调用新增的缓存指示器
// 在 dot.className = 'status-dot green'; 后添加:
_updateCacheIndicator();
```

### 在 `_loadBlock1_SR` 函数中保存 api cache age

```javascript
// 在 _loadBlock1_SR 函数中，API 响应后保存缓存年龄:
const srR = await _fetchJsonFast(srUrl, forceLive ? 20000 : 6000);
// 新增: 保存 API 缓存年龄
if (srR._cache) {
  window._m2ApiCacheAge = srR._cache.age_sec || 0;
}
```

---

## 4. 补丁三：实时价格覆盖后重算 S/R 距离

### 修改位置: `m2_sr.html` 约第1379行

```javascript
// 当前代码（天眼AI更新 current_price）:
if (_m2Data[pair]) {
  _m2Data[pair].current_price = td.current_price;
  _m2Data[pair].current_price_gate = td.current_price_gate;
  _m2Data[pair].current_price_okx = td.current_price_okx;
  _m2Data[pair].current_price_bnb = td.current_price_bnb;
  // ... 更多字段
}

// 修改后（Stage B 新增: 实时价格覆盖后重算 S/R 距离）:
if (_m2Data[pair]) {
  _m2Data[pair].current_price = td.current_price;
  _m2Data[pair].current_price_gate = td.current_price_gate;
  _m2Data[pair].current_price_okx = td.current_price_okx;
  _m2Data[pair].current_price_bnb = td.current_price_bnb;
  // ... 更多字段

  // ── Stage B 新增: 实时价格覆盖后重算 S/R 距离 ─────────────
  _recomputeSRDistances(pair, _m2Data[pair]);
}

// 新增辅助函数:
function _recomputeSRDistances(pair, data) {
  if (!data || !data.levels || !data.current_price) return;
  const price = Number(data.current_price);
  if (!price || price <= 0) return;

  const levels = data.levels;
  if (!levels || levels.length === 0) return;

  // 找最近的支撑和压力
  let nearest_support = null, nearest_resistance = null;
  let min_support_dist = Infinity, min_resist_dist = Infinity;

  for (const lvl of levels) {
    const p = Number(lvl.price);
    if (!p || p <= 0) continue;
    const dist = (price - p) / p * 100;  // 正=价格在上（支撑在下方），负=价格在下（压力在上方）
    if (dist > 0 && dist < min_support_dist) {
      min_support_dist = dist;
      nearest_support = p;
    }
    if (dist < 0 && Math.abs(dist) < min_resist_dist) {
      min_resist_dist = Math.abs(dist);
      nearest_resistance = p;
    }
  }

  data.nearest_support = nearest_support;
  data.nearest_resistance = nearest_resistance;
  data.dist_to_support_pct = min_support_dist < Infinity ? min_support_dist : null;
  data.dist_to_resistance_pct = min_resist_dist < Infinity ? min_resist_dist : null;
}
```

---

## 5. 补丁四：过期自动触发 force_live

### 修改位置: `m2_sr.html` 约第1319行 `_loadBlock1_SR` 函数

```javascript
// 在 srR 获取后（约 line 1319）添加过期检查:
let srR = await _fetchJsonFast(srUrl, forceLive ? 20000 : 6000);

// ── Stage B 新增: 检测 triple 缓存过期，自动触发 force_live ──
let cacheStale = false;
if (!forceLive && srR.pairs) {
  const firstPair = Object.values(srR.pairs)[0];
  const ts = firstPair?.timestamp;
  if (ts) {
    try {
      let ageMs;
      const d = new Date(ts);
      if (!isNaN(d.getTime())) ageMs = Date.now() - d.getTime();
      else if (typeof ts === 'number' && ts > 1e12) ageMs = Date.now() - ts;
      if (ageMs !== undefined) {
        const ageH = ageMs / 3600000;
        if (ageH >= 2) {
          log(`⚠️ Triple缓存超过2小时(${ageH.toFixed(1)}h)，自动触发强制刷新`, 'warn');
          cacheStale = true;
        }
      }
    } catch(e) {}
  }
  // API cache 过期也触发
  if ((srR._cache?.age_sec || 0) >= 90) {
    cacheStale = true;
  }
}

// 如果缓存过期，尝试强制刷新
if (cacheStale && !forceLive) {
  const liveR = await _fetchJsonFast('/api/bt2/sr_levels?force_live=1', 25000).catch(() => ({}));
  if (liveR && liveR.ok && liveR.pairs && Object.keys(liveR.pairs).length > 0) {
    srR = liveR;
    log('✅ 强制刷新成功，S/R数据已更新', 'ok');
  }
}
```

---

## 6. PATCH.diff 片段（前端）

```diff
diff --git a/static/tabs/m2_sr.html b/static/tabs/m2_sr.html
--- a/static/tabs/m2_sr.html
+++ b/static/tabs/m2_sr.html
@@ -176,6 +176,9 @@
       <span style="font-size:11px;color:var(--muted)" id="status-text">就绪</span>
       <span style="font-size:11px;color:var(--gold)" id="scan-ts">--</span>
+      <!-- Stage B 新增: 数据年龄和来源 -->
+      <span id="m2-cache-indicator" style="font-size:10px;color:var(--dimmer);margin-left:4px"
+            title="数据新鲜度"></span>
     </div>
   </div>

@@ -1319,6 +1322,26 @@ async function _loadBlock1_SR(forceLive=false) {
     }
     });
     if (srR.error) { ... }
+
+    // ── Stage B: 检测 triple 缓存过期 ────────────────────────
+    let cacheStale = false;
+    if (!forceLive && srR.pairs) {
+      const firstPair = Object.values(srR.pairs)[0];
+      const ts = firstPair?.timestamp;
+      if (ts) {
+        try {
+          let ageMs;
+          const d = new Date(ts);
+          if (!isNaN(d.getTime())) ageMs = Date.now() - d.getTime();
+          else if (typeof ts === 'number' && ts > 1e12) ageMs = Date.now() - ts;
+          if (ageMs !== undefined && ageMs / 3600000 >= 2) cacheStale = true;
+        } catch(e) {}
+      }
+      if ((srR._cache?.age_sec || 0) >= 90) cacheStale = true;
+    }
+
     let rawPairs = srR.pairs || {};
     let fallbackUsed = false;
@@ -1379,6 +1402,12 @@ async function _loadBlock2_AI() {
       _m2Data[pair].current_price = td.current_price;
       _m2Data[pair].current_price_gate = td.current_price_gate;
       // ...
+
+      // ── Stage B: 实时价格覆盖后重算 S/R 距离 ──────────────
+      _recomputeSRDistances(pair, _m2Data[pair]);
     });
```

---

## 7. 验证命令

```bash
# 验证 HTML 语法（无脚本执行）
python3 -c "
from html.parser import HTMLParser
with open('~/freqtrade_console/static/tabs/m2_sr.html') as f:
    parser = HTMLParser()
    parser.feed(f.read())
print('✅ HTML 解析通过')
"

# 验证 JS 语法（无执行）
node --check ~/freqtrade_console/static/tabs/m2_sr.html 2>&1 || true
```
