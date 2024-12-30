<script setup lang="ts">
import { defineProps } from 'vue';
import { onMounted, ref } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

const props = defineProps<{ id: number }>();

const content = ref<any>(null);

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchContent = async () => {
  try {
    const response = await axios.get(`${API_BASE}/content/${props.id}`, {
      headers: getAuthHeader(),
    });
    content.value = response.data;
    console.log('Content:', content.value);

    const imageUrl = content.value.url.replace('/v1', '/v1/content');
    const imageResponse = await axios.get(imageUrl, {
      headers: getAuthHeader(),
      responseType: 'blob',
    });

    const imageBlob = imageResponse.data;
    content.value.imageSrc = URL.createObjectURL(imageBlob);
  } catch (error) {
    console.error('Error fetching content:', error);
  }
};

onMounted(() => {
  fetchContent();
});
</script>

<template>
  <div class="content-view">
    <header class="navbar">
      <NavBar />
    </header>
    <div v-if="content">
      <h1>{{ content.title }}</h1>
      <p>{{ content.description }}</p>
      <img v-if="content.imageSrc" :src="content.imageSrc" alt="Content Image" />
    </div>
    <div v-else>
      <p>Loading...</p>
    </div>
  </div>
</template>

<style scoped>

</style>
