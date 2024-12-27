<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};
</script>

<template>
  <div>
    <button
      @click="logout"
      class="bg-blue-500 text-white px-4 py-2 rounded transition transform hover:scale-105">
      {{ 'Logout' }}
    </button>
  </div>
</template>
