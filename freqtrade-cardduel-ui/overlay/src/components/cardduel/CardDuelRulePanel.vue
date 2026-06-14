<script setup lang="ts">
defineProps<{
  title: string;
  rules: string[];
}>();
</script>

<template>
  <article class="cardduel-card p-4 text-left">
    <h3 class="cardduel-card-title text-lg">
      {{ title }}
    </h3>
    <div class="mt-4 grid gap-2">
      <label
        v-for="rule in rules"
        :key="rule"
        class="flex items-center justify-between gap-3 rounded-xl border border-[rgba(201,150,61,.25)] bg-black/20 px-3 py-2"
      >
        <span>{{ rule }}</span>
        <span class="cardduel-pill text-xs">ON</span>
      </label>
    </div>
  </article>
</template>
