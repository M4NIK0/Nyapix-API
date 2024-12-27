<script setup lang="ts">
defineProps<{
  size?: string;
}>();
</script>

<template>
  <img :src="`/assets/logo.svg`" :alt="`Nyapix Logo`" :style="{ width: size, height: size }" />
</template>

<style scoped>
img {
  display: block;
  margin: 0 auto;
}
</style>
