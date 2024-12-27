<script setup lang="ts">
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const router = useRouter();

const logout = () => {
  localStorage.removeItem('token');
  router.push('/login');
};

onMounted(() => {
  logout();
});
</script>

<template>
  <div></div>
</template>
