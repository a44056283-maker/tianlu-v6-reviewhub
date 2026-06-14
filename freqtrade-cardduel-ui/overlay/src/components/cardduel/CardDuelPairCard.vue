<script setup lang="ts">
defineProps<{
  pair: string;
  price?: string | number;
  change?: string;
  negative?: boolean;
}>();
</script>

<template>
  <article class="cardduel-card p-4 text-left">
    <div class="flex items-start justify-between gap-3">
      <div>
        <h3 class="cardduel-card-title text-lg">
          {{ pair }}
        </h3>
        <p class="cardduel-muted text-xs">
          交易对卡牌
        </p>
      </div>
      <span class="cardduel-pill text-xs" :class="negative ? 'cardduel-loss' : 'cardduel-profit'">
        {{ change }}
      </span>
    </div>
    <div class="mt-8 text-2xl font-bold">
      {{ price }}
    </div>
    <slot />
  </article>
</template>
