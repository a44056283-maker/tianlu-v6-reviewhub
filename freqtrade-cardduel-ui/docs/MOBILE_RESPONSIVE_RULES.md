# 移动端自适应规则

## 断点

- `< 768px`：移动端卡牌单列；顶部导航收起为 Slideover；底部显示 5 个核心入口。
- `768px - 1199px`：平板端两列卡牌；保留顶部导航，但隐藏非关键状态项。
- `>= 1200px`：桌面端左侧导航 + 顶部 HUD + 多列卡牌/表格。

## 页面适配

1. Dashboard：指标卡从 4 列变单列，资产曲线保留全宽。
2. Trade：交易对卡牌从 4 列变单列，详情按钮保留。
3. Pair Detail：K 线图全宽，订单簿和操作区下移。
4. Open Trades：每个持仓变独立卡牌，平仓按钮保留二次确认。
5. Strategy Editor：规则区变手风琴/单列；代码编辑器移动端只读预览，编辑建议桌面端。
6. Orders / History / Logs：表格在移动端变为卡片列表，保留状态和操作按钮。
7. Settings：页签变为顶部横向滑动胶囊按钮。
8. 风险按钮：移动端仍需要二次确认，不允许一键危险操作。

## CSS 建议

```css
.cardduel-grid {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: 16px;
}
.cardduel-span-3 { grid-column: span 3; }
.cardduel-span-4 { grid-column: span 4; }
.cardduel-span-6 { grid-column: span 6; }
.cardduel-span-8 { grid-column: span 8; }
.cardduel-span-12 { grid-column: span 12; }

@media (max-width: 767px) {
  .cardduel-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  .cardduel-span-3,
  .cardduel-span-4,
  .cardduel-span-6,
  .cardduel-span-8,
  .cardduel-span-12 {
    grid-column: span 1;
  }
  .cardduel-page {
    padding: 12px;
    padding-bottom: 76px;
  }
}
```

## 移动端底栏

底栏只放 5 个核心入口：

- 首页 / Dashboard
- 交易 / Trade
- 策略 / Strategy
- 订单 / Orders
- 我的 / Settings

其它入口通过顶部 Slideover 进入，避免底栏过载。
