<script setup lang="ts">
defineProps<{ danger?: boolean }>();
</script>

<template>
  <button class="cardduel-button px-4 py-2" :class="danger ? 'cardduel-button-danger' : ''">
    <slot />
  </button>
</template>
