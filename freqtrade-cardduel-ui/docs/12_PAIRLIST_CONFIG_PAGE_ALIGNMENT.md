# 12 交易对配置对照：Pairlist Config / 牌组规则工坊

## 官方版本锁定

- 后端：`freqtrade/freqtrade`
- 分支：`develop`
- Commit：`9aa5a628d891ca13f11d6647963dd413736fbb8c`
- 前端：`freqtrade/frequi`
- 分支：`main`
- Commit：`1745a9f77e4a9a7ae2386815ec6c56330b95cdce`

## 官方页面定位

### 路由

`src/router/index.ts`

- `/pairlist_config` 指向 `src/views/PairlistConfigView.vue`。
- 该入口在 `NavBar.vue` 中只有当 Bot 处于 Webserver 模式且 `botFeatures.pairlistConfig` 为真时显示。
- 页面用于配置 Pairlist 规则链、黑名单和预览结果，不直接执行交易。

### 页面容器

`src/views/PairlistConfigView.vue`

官方当前页面只有：

```vue
<PairlistConfigurator class="pt-4" />
```

### 主配置器

`src/components/ftbot/PairlistConfigurator.vue`

必须保留：

- `availablePairlists`
- `pairlistConfigsEl`
- `availablePairlistsEl`
- `selectedView: 'Config' | 'Results'`
- `configEmpty`
- `useSortable(availablePairlistsEl, availablePairlists.value, ...)`
- `useSortable(pairlistConfigsEl, pairlistStore.config.pairlists, ...)`
- `moveArrayElement(pairlistStore.config.pairlists, e.oldIndex, e.newIndex)`
- `pairlistStore.addToConfig(pairlist, e.newIndex)`
- `getPairlists()` 后按 `is_pairlist_generator` 和名称排序
- `pairlistStore.selectOrCreateConfig(...)`
- `watch(pairlistStore.whitelist)` 后切换到 Results
- `PairlistConfigActions`
- `PairlistConfigBlacklist`
- `PairlistConfigItem`
- `CopyableTextfield` 的 config JSON 和 whitelist 输出

### 操作栏

`src/components/ftbot/PairlistConfigActions.vue`

必须保留：

- `pairlistStore.saveConfig(pairlistStore.config.name)`
- `EditValue`
- `pairlistStore.deleteConfig`
- `pairlistStore.duplicateConfig(newName)`
- `pairlistStore.newConfig(name)`
- `pairlistStore.saveConfig(newName)`
- `pairlistStore.selectOrCreateConfig(config as string)`
- `pairlistStore.startPairlistEvaluation()`
- `pairlistStore.evaluating`
- `pairlistStore.pairlistValid`
- 按钮标题 `Save configuration`
- 按钮文本 `Evaluate`

### 黑名单配置

`src/components/ftbot/PairlistConfigBlacklist.vue`

必须保留：

- `copyFromConfig`
- `configNames`
- `pairlistStore.duplicateBlacklist(copyFromConfig)`
- `pairlistStore.config.blacklist`
- `pairlistStore.removeFromBlacklist(i)`
- `pairlistStore.addToBlacklist()`
- `BaseCollapsible title="Blacklist"`
- `Copy from:`
- `Blacklisted Pairs`
- `Add`

### 规则链条目

`src/components/ftbot/PairlistConfigItem.vue`

必须保留：

- `defineModel<Pairlist>`
- `hasParameters`
- `toggleVisible()`
- 拖拽 handle class：`handle`
- `pairlistStore.removeFromConfig(index)`
- `PairlistConfigParameter`
- `pairlist.showParameters`

### 参数编辑

`src/components/ftbot/PairlistConfigParameter.vue`

必须保留：

- `PairlistParamType.string`
- `PairlistParamType.number`
- `PairlistParamType.boolean`
- `PairlistParamType.option`
- `PairlistParamType.list`
- `param.description`
- `param.help`
- `BaseCheckbox`
- `BaseStringList`
- `UInput`
- `USelect`

## 设计目标

页面风格命名：`牌组规则工坊 / Pairlist Rule Forge`

视觉元素：

- 顶部工坊 HUD：Available Rules、Config Chain、Blacklist、Result Pairs。
- Available pairlists 改成“规则卡库”。
- 中央配置区改成“规则链熔炉”，拖拽规则仍然使用官方 `useSortable`。
- Stake currency / Custom Exchange 改成基础铸造参数卡。
- Blacklist 改成“放逐名单工坊”。
- Config / Results 输出改成 JSON/结果卷轴。
- Evaluate 和 Save 改成工坊技能按钮，但行为不变。

## 官方字段到设计字段映射

| 设计表现 | 官方字段/行为 | 是否保留 |
| --- | --- | --- |
| 可用规则数 | `availablePairlists.length` | 保留 |
| 生成器数量 | `availablePairlists.filter(p => p.is_pairlist_generator)` | 保留 |
| 规则链长度 | `pairlistStore.config.pairlists.length` | 保留 |
| 黑名单数量 | `pairlistStore.config.blacklist.length` | 保留 |
| 结果数量 | `pairlistStore.whitelist.length` | 保留 |
| 拖入规则 | `pairlistStore.addToConfig(...)` | 保留 |
| 重排规则 | `moveArrayElement(...)` | 保留 |
| 删除规则 | `removeFromConfig(index)` | 保留 |
| 保存配置 | `saveConfig(...)` | 保留 |
| 评估配置 | `startPairlistEvaluation()` | 保留 |
| 输出配置 | `configJSON` | 保留 |
| 输出结果 | `whitelist` | 保留 |

## 建议补丁范围

新增 / 覆盖：

```text
src/views/PairlistConfigView.vue
src/components/ftbot/PairlistConfigurator.vue
src/components/ftbot/PairlistConfigActions.vue
src/components/ftbot/PairlistConfigBlacklist.vue
src/components/ftbot/PairlistConfigItem.vue
src/components/ftbot/PairlistConfigParameter.vue
src/components/ftbot/PairlistConfigResults.vue
src/styles/cardduel-pairlist-config.css
```

其中：

- `PairlistConfigView.vue`：新增页面舞台 class 和样式入口。
- `PairlistConfigurator.vue`：保留 sortable、配置、结果输出和 watch 逻辑，只新增 HUD 与三栏工坊布局。
- `PairlistConfigActions.vue`：保留保存、编辑、复制、新建、重命名、删除、评估逻辑，只改按钮皮肤。
- `PairlistConfigBlacklist.vue`：保留复制、增删黑名单逻辑，只改放逐名单工坊皮肤。
- `PairlistConfigItem.vue`：保留拖拽 handle、参数展开、删除规则逻辑。
- `PairlistConfigParameter.vue`：保留所有参数类型组件。
- `PairlistConfigResults.vue`：保留结果 whitelist、ChartView 和 CopyableTextfield，只改预览外观。
- `cardduel-pairlist-config.css`：新增工坊布局、规则卡、参数卡、输出卷轴和响应式样式。

## E2E / 功能兼容锚点

必须保留：

- `Stake currency:`
- `Custom Exchange`
- `Invalid configuration`
- `The first entry in the pairlist must be a Generating pairlist`
- `Drag pairlist here`
- `Save configuration`
- `Evaluate`
- `Config`
- `Results`
- `Blacklist`
- `Copy from:`
- `Blacklisted Pairs`
- `Add`
- `.handle`
- `CopyableTextfield` 的 config JSON 与 whitelist 输出

## 移动端行为

- `> 1280px`：左侧规则卡库 + 中央规则链熔炉 + 右侧输出卷轴。
- `<= 1280px`：规则卡库在上，配置和输出两列。
- `<= 900px`：全部单列，规则条目参数区单列。
- `<= 640px`：操作按钮全宽，Config/Results 横向滚动或单列显示。
- 拖拽不可用时仍可通过箭头按钮添加规则。
- Save / Evaluate / Blacklist Add 不隐藏。

## 安全边界

禁止改动：

- `useSortable` 拖拽与 clone/add 逻辑
- `pairlistStore.addToConfig` / `removeFromConfig` / `moveArrayElement` 逻辑
- 配置保存、重命名、复制、新建、删除逻辑
- Pairlist 评估 API 调用逻辑
- 黑名单复制、添加、删除逻辑
- Custom Exchange 选择逻辑
- Config JSON / whitelist 输出逻辑
- 后端 API 调用

只允许改视觉、布局、class、非业务 summary computed 和响应式 CSS。
