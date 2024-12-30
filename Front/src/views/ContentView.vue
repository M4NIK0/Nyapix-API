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

const fetchTagDetails = async (tagId: number) => {
  try {
    const response = await axios.get(`${API_BASE}/tags/${tagId}`, {
      headers: getAuthHeader(),
    });
    return response.data.name;
  } catch (error) {
    console.error(`Error fetching tag details for tag ID ${tagId}:`, error);
    return null;
  }
};

const fetchCharacterDetails = async (characterId: number) => {
  try {
    const response = await axios.get(`${API_BASE}/characters/${characterId}`, {
      headers: getAuthHeader(),
    });
    return response.data.name;
  } catch (error) {
    console.error(`Error fetching character details for character ID ${characterId}:`, error);
    return null;
  }
};

const fetchAuthorDetails = async (authorId: number) => {
  try {
    const response = await axios.get(`${API_BASE}/authors/${authorId}`, {
      headers: getAuthHeader(),
    });
    return response.data.name;
  } catch (error) {
    console.error(`Error fetching author details for author ID ${authorId}:`, error);
    return null;
  }
};

const fetchContent = async () => {
  try {
    const response = await axios.get(`${API_BASE}/content/${props.id}`, {
      headers: getAuthHeader(),
    });
    content.value = response.data;
    console.log('Content:', content.value);

    const tagNames = await Promise.all(content.value.tags.map(fetchTagDetails));
    content.value.tagNames = tagNames.filter(name => name !== null);

    const characterNames = await Promise.all(content.value.characters.map(fetchCharacterDetails));
    content.value.characterNames = characterNames.filter(name => name !== null);

    const authorNames = await Promise.all(content.value.authors.map(fetchAuthorDetails));
    content.value.authorNames = authorNames.filter(name => name !== null);

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
      <div class="content-main">
        <aside class="tags">
          <h2>Tags</h2>
          <ul>
            <li v-for="tag in content.tagNames" :key="tag">{{ tag }}</li>
            <li v-for="character in content.characterNames" :key="character" class="character">{{ character }} (character)</li>
            <li v-for="author in content.authorNames" :key="author" class="author">{{ author }} (author)</li>
          </ul>
        </aside>
        <div class="content-details">
          <h1>{{ content.title }}</h1>
          <p>{{ content.description }}</p>
          <img v-if="content.imageSrc" :src="content.imageSrc" alt="Content Image" />
        </div>
      </div>
    </div>
    <div v-else>
      <p>Loading...</p>
    </div>
  </div>
</template>

<style scoped>
.content-view {
  display: flex;
  flex-direction: column;
}

.content-main {
  display: flex;
}

.tags {
  flex: 0 0 10%;
  padding: 10px;
}

.content-details {
  flex: 1;
  padding: 10px;
}

.tags h3 {
  margin-top: 0;
}

.tags ul {
  list-style-type: none;
  padding: 0;
}

.tags li {
  margin: 5px 0;
  padding: 5px;
  border-radius: 4px;
}

.character {
  color: green;
}

.author {
  color: blue;
}
</style>
