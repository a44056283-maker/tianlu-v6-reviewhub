<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  delta?: string;
  negative?: boolean;
}>();
</script>

<template>
  <article class="cardduel-card p-4 text-left">
    <p class="cardduel-muted text-sm">
      {{ label }}
    </p>
    <div class="mt-2 text-3xl font-bold">
      {{ value }}
    </div>
    <p v-if="delta" class="mt-1 text-sm" :class="negative ? 'cardduel-loss' : 'cardduel-profit'">
      {{ delta }}
    </p>
  </article>
</template>
