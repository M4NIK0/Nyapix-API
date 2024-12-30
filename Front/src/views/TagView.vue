<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

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

const tags = ref<Tag[]>([]);
const characters = ref<Character[]>([]);
const authors = ref<Author[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref('');
const totalPages = ref(1);
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchTags = async () => {
  try {
    const response = await axios.get(`${API_BASE}/tags`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    tags.value = response.data.tags;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error fetching tags:', error);
  }
};

const fetchCharacters = async () => {
  try {
    const response = await axios.get(`${API_BASE}/characters`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    characters.value = response.data.characters;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error fetching characters:', error);
  }
};

const fetchAuthors = async () => {
  try {
    const response = await axios.get(`${API_BASE}/authors`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    authors.value = response.data.authors;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error fetching authors:', error);
  }
};

const search = async () => {
  try {
    const [tagsResponse, charactersResponse, authorsResponse] = await Promise.all([
      axios.get(`${API_BASE}/tags/search`, {
        headers: getAuthHeader(),
        params: { tag_name: searchQuery.value, max_results: pageSize.value }
      }),
      axios.get(`${API_BASE}/characters/search`, {
        headers: getAuthHeader(),
        params: { character_name: searchQuery.value, max_results: pageSize.value }
      }),
      axios.get(`${API_BASE}/authors/search`, {
        headers: getAuthHeader(),
        params: { author_name: searchQuery.value, max_results: pageSize.value }
      })
    ]);
    tags.value = tagsResponse.data.tags;
    characters.value = charactersResponse.data.characters;
    authors.value = authorsResponse.data.authors;
  } catch (error) {
    console.error('Error searching:', error);
  }
};

const deleteTag = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/tags/${id}`, {
      headers: getAuthHeader()
    });
    fetchTags();
  } catch (error) {
    console.error('Error deleting tag:', error);
  }
};

const deleteCharacter = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/characters/${id}`, {
      headers: getAuthHeader()
    });
    fetchCharacters();
  } catch (error) {
    console.error('Error deleting character:', error);
  }
};

const deleteAuthor = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/authors/${id}`, {
      headers: getAuthHeader()
    });
    fetchAuthors();
  } catch (error) {
    console.error('Error deleting author:', error);
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    fetchTags();
    fetchCharacters();
    fetchAuthors();
  }
};

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    fetchTags();
    fetchCharacters();
    fetchAuthors();
  }
};

onMounted(() => {
  fetchTags();
  fetchCharacters();
  fetchAuthors();
});
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div>
    <input v-model="searchQuery" @input="search" placeholder="Search..." />
    <div>
      <h2>Tags</h2>
      <ul>
        <li v-for="tag in tags" :key="tag.id">
          {{ tag.name }}
          <button class="delete-button" @click="deleteTag(tag.id)">X</button>
        </li>
      </ul>
    </div>
    <div>
      <h2>Characters</h2>
      <ul>
        <li v-for="character in characters" :key="character.id" class="character">
          {{ character.name }}
          <button class="delete-button" @click="deleteCharacter(character.id)">X</button>
        </li>
      </ul>
    </div>
    <div>
      <h2>Authors</h2>
      <ul>
        <li v-for="author in authors" :key="author.id" class="author">
          {{ author.name }}
          <button class="delete-button" @click="deleteAuthor(author.id)">X</button>
        </li>
      </ul>
    </div>
    <button class="page-button" @click="prevPage" :disabled="currentPage === 1">Previous</button>
    <button class="page-button" @click="nextPage" :disabled="currentPage === totalPages">Next</button>
  </div>
</template>

<style scoped>
.character {
  color: green;
}

.author {
  color: blue;
  margin-bottom: 20px;
}

.delete-button {
  color: red;
  background: none;
  border: none;
  cursor: pointer;
}

.page-button {
  margin-bottom: 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.page-button:hover {
  background-color: #45a049;
}
</style>
