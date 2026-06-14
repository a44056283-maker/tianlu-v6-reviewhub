<script setup lang="ts">
defineProps<{
  headers: string[];
  rows: Array<Array<string | number>>;
}>();
</script>

<template>
  <div class="cardduel-card overflow-x-auto p-4">
    <table class="cardduel-table min-w-full">
      <thead>
        <tr>
          <th v-for="h in headers" :key="h">
            {{ h }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in rows" :key="i">
          <td v-for="(cell, j) in row" :key="j">
            {{ cell }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
