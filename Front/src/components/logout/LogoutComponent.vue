<script setup lang="ts">
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const router = useRouter();

const logout = async () => {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      await axios.delete(`${API_BASE}/logout`, {
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
