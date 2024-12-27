<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';

const searchQuery = ref('');
const dropdownResults = ref<Array<{ name: string, type: string }>>([]); // Store both name and type
const isDropdownVisible = ref(false);

// API Base URL
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';

// Retrieve the token dynamically from localStorage
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Extract the current word being typed
const currentWord = computed(() => {
  const words = searchQuery.value.split(' ');
  return words[words.length - 1];
});

// Fetch data from endpoints
const fetchResults = async (word: string) => {
  if (!word) {
    dropdownResults.value = [];
    return;
  }

  try {
    // Parallel API calls
    const [tags, characters, authors] = await Promise.all([
      axios.get(`${API_BASE}/tags/search`, {
        params: { tag_name: word, max_results: 15 },
        headers: getAuthHeader(),
      }),
      axios.get(`${API_BASE}/characters/search`, {
        params: { character_name: word, max_results: 15 },
        headers: getAuthHeader(),
      }),
      axios.get(`${API_BASE}/authors/search`, {
        params: { author_name: word, max_results: 15 },
        headers: getAuthHeader(),
      }),
    ]);

    // Extract results from the correct property
    const tagsResults = tags.data.tags || [];
    const charactersResults = characters.data.characters || [];
    const authorsResults = authors.data.authors || [];

    // Combine and limit results
    const combined = [
      ...tagsResults.slice(0, 7).map((item: { name: string }) => ({ name: item.name, type: 'tag' })),
      ...charactersResults.slice(0, 7).map((item: { name: string }) => ({ name: item.name, type: 'character' })),
      ...authorsResults.slice(0, 6).map((item: { name: string }) => ({ name: item.name, type: 'author' })),
    ].slice(0, 20);

    dropdownResults.value = combined;
    isDropdownVisible.value = dropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching search results:', error);
    dropdownResults.value = [];
  }
};

const getResultClass = (result: { type: string }) => {
  return result.type;
};

// Watch for changes to the current word
watch(currentWord, (word) => {
  if (word.trim()) {
    fetchResults(word);
  } else {
    dropdownResults.value = [];
  }
});

// Autocomplete word
const autocompleteWord = (result: { name: string, type: string }) => {
  const words = searchQuery.value.split(' ');
  words[words.length - 1] = result.name; // Set the name
  searchQuery.value = words.join(' ');
  isDropdownVisible.value = false; // Hide dropdown
};

// Close dropdown if user clicks outside
const closeDropdown = (event: MouseEvent) => {
  const searchBar = document.querySelector('.search-bar-container');
  if (searchBar && !searchBar.contains(event.target as Node)) {
    isDropdownVisible.value = false;
  }
};

// Add event listener to close dropdown on outside click
onMounted(() => {
  document.addEventListener('mousedown', closeDropdown);
});

// Remove event listener on component unmount
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', closeDropdown);
});
</script>

<template>
  <div class="search-bar-container">
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search..."
      @input="fetchResults(currentWord)"
      @focus="isDropdownVisible = dropdownResults.length > 0"
    />
    <ul v-if="isDropdownVisible" class="dropdown">
      <li v-for="(result, index) in dropdownResults" :key="index" @click="autocompleteWord(result)">
        <span :class="getResultClass(result)">
          {{ result.name }}
          <span v-if="result.type === 'character'">(character)</span>
          <span v-if="result.type === 'author'">(author)</span>
        </span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.search-bar-container {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  color: black; /* Text inside the search bar will be black */
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-top: none;
  background: white;
  list-style: none;
  padding: 0;
  margin: 0;
  z-index: 1000;
}

.dropdown li {
  padding: 0.5rem;
  cursor: pointer;
}

.dropdown li:hover {
  background-color: #f0f0f0;
}

.dropdown span {
  font-size: 0.9rem;
}

.character {
  color: green; /* Characters will be green */
}

.author {
  color: blue; /* Authors will be blue */
}

.tag {
  color: black; /* Regular tags will be black */
}
</style>
