<script setup lang="ts">
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';
import axios from 'axios';

const router = useRouter();

const logout = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      await axios.delete('http://localhost:5000/v1/logout', {
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }
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
