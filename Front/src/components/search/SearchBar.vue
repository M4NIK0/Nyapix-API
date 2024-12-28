<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';

const dropdownResults = ref<Array<{ name: string, type: string }>>([]);
const isDropdownVisible = ref(false);

// Data structure to store the search results and query
const structuredQuery = ref({
  tags: [] as string[],
  characters: [] as string[],
  authors: [] as string[],
});

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const searchQuery = ref(''); // Add a ref for the search query

// Extract the current word
const currentWord = computed(() => {
  const words = searchQuery.value.split(' ');
  return words[words.length - 1];
});

// Fetch dropdown suggestions
const fetchResults = async (word: string) => {
  if (!word) {
    dropdownResults.value = [];
    return;
  }
  try {
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

    const tagsResults = tags.data.tags || [];
    const charactersResults = characters.data.characters || [];
    const authorsResults = authors.data.authors || [];

    dropdownResults.value = [
      ...tagsResults.map((item: { name: string }) => ({ name: item.name, type: 'tag' })),
      ...charactersResults.map((item: { name: string }) => ({ name: item.name, type: 'character' })),
      ...authorsResults.map((item: { name: string }) => ({ name: item.name, type: 'author' })),
    ];
    isDropdownVisible.value = dropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching search results:', error);
    dropdownResults.value = [];
  }
};

// Add selected item to structured query
const addToStructuredQuery = (result: { name: string, type: string }) => {
  const typeMap: Record<string, keyof typeof structuredQuery.value> = {
    tag: 'tags',
    character: 'characters',
    author: 'authors',
  };

  const queryKey = typeMap[result.type];
  if (!queryKey) {
    console.error(`Unexpected result type: ${result.type}`);
    return;
  }

  // Prepend the correct prefix before pushing to the structuredQuery
  let prefixedName = result.name;
  if (result.type === 'tag') {
    prefixedName = 'tag:' + result.name;
  } else if (result.type === 'character') {
    prefixedName = 'character:' + result.name;
  } else if (result.type === 'author') {
    prefixedName = 'author:' + result.name;
  }

  // Only add the result if it's not already included
  if (!structuredQuery.value[queryKey].includes(prefixedName)) {
    structuredQuery.value[queryKey].push(prefixedName);
  }
};

// Remove an item from structured query
const removeFromStructuredQuery = (type: string, name: string) => {
  console.log('Removing:', name);
  const typeMap: Record<string, keyof typeof structuredQuery.value> = {
    tag: 'tags',
    character: 'characters',
    author: 'authors',
  };

  const queryKey = typeMap[type];
  if (!queryKey) {
    console.error(`Unexpected type: ${type}`);
    return;
  }

  // Prepend the correct prefix only if the name does not already contain it
  let prefixedName = name;
  if (type === 'tag' && !name.startsWith('tag:')) {
    prefixedName = 'tag:' + name;
  } else if (type === 'character' && !name.startsWith('character:')) {
    prefixedName = 'character:' + name;
  } else if (type === 'author' && !name.startsWith('author:')) {
    prefixedName = 'author:' + name;
  }

  // Remove the item from the array and create a new array to trigger reactivity
  structuredQuery.value[queryKey] = structuredQuery.value[queryKey].filter((item) => item !== prefixedName);
  console.log('Structured query:', structuredQuery.value);
};

// Watch for changes to the current word
watch(currentWord, (word) => {
  if (word.trim()) {
    fetchResults(word);
  } else {
    dropdownResults.value = [];
  }
});

// Close dropdown if user clicks outside
const closeDropdown = (event: MouseEvent) => {
  const searchBar = document.querySelector('.search-bar-container');
  if (searchBar && !searchBar.contains(event.target as Node)) {
    isDropdownVisible.value = false;
  }
};

onMounted(() => {
  document.addEventListener('mousedown', closeDropdown);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', closeDropdown);
});
</script>

<template>
  <div class="search-bar-container">
    <div class="selected-items">
      <span
        v-for="(item, index) in structuredQuery.tags"
        :key="'tag-' + index"
        class="tag-item"
      >
        {{ item }}
        <button @click="removeFromStructuredQuery('tag', item)">x</button>
      </span>
      <span
        v-for="(item, index) in structuredQuery.characters"
        :key="'character-' + index"
        class="character-item"
      >
        {{ item }}
        <button @click="removeFromStructuredQuery('character', item)">x</button>
      </span>
      <span
        v-for="(item, index) in structuredQuery.authors"
        :key="'author-' + index"
        class="author-item"
      >
        {{ item }}
        <button @click="removeFromStructuredQuery('author', item)">x</button>
      </span>
    </div>
    <input
      type="text"
      v-model="searchQuery"
      placeholder="Search..."
      @focus="isDropdownVisible = dropdownResults.length > 0"
    />
    <ul v-if="isDropdownVisible" class="dropdown">
      <li
        v-for="(result, index) in dropdownResults"
        :key="index"
        @click="addToStructuredQuery(result)"
      >
        <span :class="result.type">{{ result.name }} ({{ result.type }})</span>
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

.selected-items {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.tag-item,
.character-item,
.author-item {
  display: inline-flex;
  align-items: center;
  margin: 0 0.5rem 0.5rem 0;
  padding: 0.2rem 0.5rem;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
}

button {
  margin-left: 0.5rem;
  background: none;
  border: none;
  color: red;
  cursor: pointer;
}
</style>
