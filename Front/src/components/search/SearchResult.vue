<script setup lang="ts">
import { defineProps, ref, onMounted, watch } from "vue";
import axios from "axios";

// Define the type of the search results prop
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

// Store the images for each result
const images = ref<{ [key: number]: string }>({});

// Function to retrieve the bearer token from localStorage
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Fetch the image for a specific result using its `url` field
const fetchImage = async (url: string, id: number) => {
  try {
    // Replace `/v1/image` with `/v1/content/image` in the URL
    const imageUrl = url.replace('/v1/image', '/v1/content/image');
    const response = await axios.get(imageUrl, {
      headers: getAuthHeader(),
    });
    images.value[id] = response.data.imageUrl || '';
  } catch (error) {
    console.error("Error fetching image for:", id, error);
    images.value[id] = '';
  }
};

// Function to fetch images for all results
const fetchImagesForAllResults = () => {
  props.searchResults.forEach((result) => {
    fetchImage(result.url, result.id);
  });
};

// Watch for changes in the `searchResults` prop and trigger image fetching
watch(() => props.searchResults, () => {
  // Clear images to avoid stale data
  images.value = {};
  // Fetch images for the updated results
  fetchImagesForAllResults();
}, { immediate: true });

// Handle click event for each result
const handleClick = (result: { id: number, title: string }) => {
  console.log(`Clicked on result with ID: ${result.id}, Title: ${result.title}`);
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
  flex-wrap: wrap; /* Allow items to wrap when they exceed the screen width */
  gap: 20px; /* Space between items */
}

.result-item {
  width: calc(20% - 20px);
  cursor: pointer;
  background-color: #f4f4f4;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease-in-out;
}

.result-item:hover {
  transform: scale(1.05); /* Slight zoom effect on hover */
}

.image-wrapper {
  width: 100%;
  height: 200px;
  background-color: #ddd; /* Light gray background if no image is found */
  display: flex;
  justify-content: center;
  align-items: center;
}

.result-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.result-info {
  padding: 10px;
  color: black;
}

.result-info h3 {
  margin: 0;
  font-size: 1.2rem;
}

.result-info p {
  font-size: 0.9rem;
  color: #555;
}
</style>
