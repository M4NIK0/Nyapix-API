<script setup lang="ts">
import {defineProps, ref, watch} from "vue";
import axios from "axios";

const props = defineProps<{
  searchResults: Array<{
    id: number,
    title: string,
    description: string,
    source: number,
    tags: number[],
    characters: number[],
    authors: number[],
    is_private: boolean,
    url: string
  }>
}>();

const images = ref<{ [key: number]: string }>({});

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchImage = async (id: number) => {
  try {
    const imageUrl = `${API_BASE}/content/${id}/thumb`;
    const response = await axios.get(imageUrl, {
      headers: getAuthHeader(),
      responseType: 'blob'
    });

    // Convert the Blob to a URL and store it
    const imageBlob = response.data;
    images.value[id] = URL.createObjectURL(imageBlob);
  } catch (error) {
    console.error("Error fetching image for:", id, error);
    images.value[id] = '';
  }
};

// Function to fetch images for all results
const fetchImagesForAllResults = () => {
  props.searchResults.forEach((result) => {
    fetchImage(result.id);
  });
};

watch(() => props.searchResults, () => {
  images.value = {};
  fetchImagesForAllResults();
}, { immediate: true });

import { useRouter } from 'vue-router';

const router = useRouter();

const handleClick = (result: { id: number, title: string }) => {
  router.push({ name: 'ContentView', params: { id: result.id } });
};
</script>

<template>
  <div class="search-result-container">
    <div v-for="result in props.searchResults"
         :key="result.id"
         class="result-item"
         @click="handleClick(result)">

      <!-- Display image if it is fetched -->
      <div class="image-wrapper" v-if="images[result.id]">
        <img :src="images[result.id]" alt="Content Image" class="result-image" />
      </div>

      <!-- Display fallback or placeholder if no image is available -->
      <div class="image-wrapper" v-else>
        <span>No Image</span>
      </div>

      <div class="result-info">
        <h3>{{ result.title }}</h3>
        <p>{{ result.description }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-result-container {
  display: flex;
  flex-wrap: wrap; /* Allow items to wrap */
  gap: 20px; /* Space between items */
  justify-content: center; /* Center the items if there's extra space */
}

.result-item {
  flex: 1 1 250px; /* Minimum width of 250px */
  max-width: 300px; /* Limit maximum width to ensure uniformity */
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease-in-out;
  box-sizing: border-box; /* Include padding and borders in size */
  background: #444444;
}

.result-item:hover {
  transform: scale(1.05); /* Slight zoom effect on hover */
  color: #ffffff;
}

.image-wrapper {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: black;
}

.result-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;

}

.result-info {
  padding: 10px;
  color: #ffffff;
}

.result-info h3 {
  margin: 0;
  font-size: 1.2rem;
}

.result-info p {
  font-size: 0.9rem;
}
</style>
