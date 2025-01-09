<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

interface Tag {
  id: number;
  name: string;
}

interface Character {
  id: number;
  name: string;
}

interface Author {
  id: number;
  name: string;
}

interface Content {
  id: number;
  title: string;
  description: string;
  source: number;
  tags: Tag[];
  characters: Character[];
  authors: Author[];
  is_private: boolean;
  url: string;
}

interface AlbumInfo {
  id: number;
  name: string;
  description: string;
}

const route = useRoute();
const albumId = route.params.id;

const albumInfo = ref<AlbumInfo>({
  id: 0,
  name: '',
  description: ''
});
const albumContents = ref<Content[]>([]);

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchAlbumDetails = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/v1/albums/${albumId}`, {
      headers: getAuthHeader()
    });
    albumInfo.value = response.data.info;
    albumContents.value = response.data.contents;
  } catch (error) {
    console.error('Error fetching album details:', error);
  }
};

onMounted(() => {
  fetchAlbumDetails();
});
</script>

<template>
  <div class="album-view">
    <div class="album-info">
      <h1>{{ albumInfo.name }}</h1>
      <p>{{ albumInfo.description }}</p>
    </div>
    <div class="album-contents">
      <h2>Contents</h2>
      <ul>
        <li v-for="content in albumContents" :key="content.id">
          <h3>{{ content.title }}</h3>
          <p>{{ content.description }}</p>
          <p>Source: {{ content.source }}</p>
          <p>Tags: <span v-for="tag in content.tags" :key="tag.id">{{ tag.name }}</span></p>
          <p>Characters: <span v-for="character in content.characters" :key="character.id">{{ character.name }}</span></p>
          <p>Authors: <span v-for="author in content.authors" :key="author.id">{{ author.name }}</span></p>
          <p v-if="content.is_private">Private</p>
          <a :href="content.url" target="_blank">View Content</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.album-view {
  padding: 20px;
}

.album-info {
  margin-bottom: 20px;
}

.album-contents ul {
  list-style-type: none;
  padding: 0;
}

.album-contents li {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.album-contents h3 {
  margin: 0 0 10px 0;
}

.album-contents p {
  margin: 5px 0;
}
</style>
