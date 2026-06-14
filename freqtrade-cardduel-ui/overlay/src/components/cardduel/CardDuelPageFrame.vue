<script setup lang="ts">
defineProps<{ title?: string; subtitle?: string }>();
</script>

<template>
  <section class="cardduel-page">
    <header v-if="title || subtitle" class="mb-4 flex flex-col gap-1 text-left">
      <h1 v-if="title" class="cardduel-card-title text-2xl">
        {{ title }}
      </h1>
      <p v-if="subtitle" class="cardduel-muted">
        {{ subtitle }}
      </p>
    </header>
    <slot />
  </section>
</template>
