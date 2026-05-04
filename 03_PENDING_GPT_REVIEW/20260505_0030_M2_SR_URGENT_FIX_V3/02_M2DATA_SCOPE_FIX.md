# 02_M2DATA_SCOPE_FIX.md
# V3 修正 #2: `_updateCacheIndicator` 改用局部 `_m2Data`

---

## 根因分析

### V2 代码

```javascript
function _updateCacheIndicator() {
  const el = document.getElementById('m2-cache-indicator');
  if (!el) return;
  const pairs = window._m2Data || {};   // ← V2 使用 window._m2Data
  ...
}
```

### 问题

`_m2Data` 在 m2_sr.html 中定义为：
```javascript
let _m2Data = {};   // line 330 — script 全局作用域，非 window
```

在浏览器 JavaScript 中，`let` 声明的变量**不在 window 对象上**：
```javascript
let x = 1;
window.x  // undefined
```

因此 `window._m2Data` **始终为 undefined**，`|| {}` 永远触发，
导致函数在 `_m2Data` 未初始化时静默返回空（不显示任何内容）。

### 何时调用

`_updateCacheIndicator()` 在 `loadM2All()` 结束时调用（line ~1492），
此时 `_m2Data` 已由 `_loadBlock1_SR()` 填充（line 1347），**理论上不会为空**。
但防御性编程原则：若函数被提前调用，应能正确处理。

---

## V3 修正

```javascript
function _updateCacheIndicator() {
  const el = document.getElementById('m2-cache-indicator');
  if (!el) return;
  // V3: 直接使用 script 全局变量 _m2Data（let 声明，不在 window 上）
  const pairs = typeof _m2Data !== 'undefined' ? _m2Data : {};
  ...
}
```

**修正点**:
- 移除 `window._m2Data || {}`（window 上根本不存在）
- 改用 `typeof _m2Data !== 'undefined' ? _m2Data : {}`（检查变量是否已初始化）
- 同时兼容：正常调用时使用真实数据，提前调用时返回空对象（不报错）

---

## 补充：`_loadBlock1_SR()` 中的 cacheStale 检测

该函数内直接访问 `srR.pairs`，不涉及 `_m2Data`，**无需修改**。

---

## 影响范围

| 位置 | 函数 | 修正 |
|------|------|------|
| m2_sr.html | `_updateCacheIndicator()` | ✅ 移除 window._m2Data |
