<script setup lang="ts">
import LogoutComponent from '@/components/logout/LogoutComponent.vue'
</script>

<template>
  <nav class="fixed top-0 left-0 w-full bg-gray-800 p-4 flex items-center justify-between text-white z-50">

    <div class="flex-1 ml-14 flex justify-center">
      <h1 class="text-xl font-bold">Dashboard</h1>
    </div>

    <LogoutComponent />
  </nav>
  <br>
  <br>
</template>
