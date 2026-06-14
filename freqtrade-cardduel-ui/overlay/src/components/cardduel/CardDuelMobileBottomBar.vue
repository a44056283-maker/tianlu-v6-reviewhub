<script setup lang="ts">
const items = [
  { label: '首页', to: '/dashboard' },
  { label: '交易', to: '/trade' },
  { label: '策略', to: '/strategies' },
  { label: '订单', to: '/orders' },
  { label: '我的', to: '/settings' },
];
</script>

<template>
  <nav
    class="cardduel-mobile-only fixed inset-x-3 bottom-3 z-50 grid grid-cols-5 rounded-2xl border border-[rgba(201,150,61,.55)] bg-[#070d18]/95 p-2 shadow-2xl"
  >
    <RouterLink
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="text-center text-xs text-[#f0cf7a]"
    >
      {{ item.label }}
    </RouterLink>
  </nav>
</template>
