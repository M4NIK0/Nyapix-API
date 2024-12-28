<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';

const emit = defineEmits<{
  (event: 'update:searchResults', searchResults: any): void;
}>();

const dropdownResults = ref<Array<{ name: string, type: string, id: number }>>([]);
const isDropdownVisible = ref(false);

// Data structure to store the search results and query
const structuredQuery = ref({
  tags: [] as Array<{ id: number, name: string }>,
  characters: [] as Array<{ id: number, name: string }>,
  authors: [] as Array<{ id: number, name: string }>,
});

const searchResults = ref<Array<{ id: number, title: string, description: string, source: number, tags: number[], characters: number[], authors: number[], is_private: boolean, url: string }>>([]);

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const searchQuery = ref('');

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
      ...tagsResults.map((item: { name: string, id: number }) => ({
        name: item.name,
        type: 'tag',
        id: item.id,
      })),
      ...charactersResults.map((item: { name: string, id: number }) => ({
        name: item.name,
        type: 'character',
        id: item.id,
      })),
      ...authorsResults.map((item: { name: string, id: number }) => ({
        name: item.name,
        type: 'author',
        id: item.id,
      })),
    ];

    isDropdownVisible.value = dropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching search results:', error);
    dropdownResults.value = [];
  }
};

// Add selected item to structured query
const addToStructuredQuery = (result: { name: string, type: string, id: number }) => {
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

  // Store both name and id in the structured query
  let prefixedName = result.name;
  if (result.type === 'tag') {
    prefixedName = 'tag:' + result.name;
  } else if (result.type === 'character') {
    prefixedName = 'character:' + result.name;
  } else if (result.type === 'author') {
    prefixedName = 'author:' + result.name;
  }

  // Store both name and ID in the structuredQuery
  structuredQuery.value[queryKey].push({ id: result.id, name: prefixedName });
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

  // Find the item by name and remove it from the corresponding category
  structuredQuery.value[queryKey] = structuredQuery.value[queryKey].filter((item) => item.name !== name);
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

// Function to validate the search result (empty for now)
const validateSearchResults = async () => {
  try {
    // Extract the IDs of tags, characters, and authors from the structuredQuery
    const tags = structuredQuery.value.tags.filter(tag => tag.id).map(tag => tag.id);
    const characters = structuredQuery.value.characters.filter(character => character.id).map(character => character.id);
    const authors = structuredQuery.value.authors.filter(author => author.id).map(author => author.id);

    // Prepare the query parameters
    const params: Record<string, string | string[]> = {
      page: '1',
      max_results: '25',
    };

    // Add multiple `needed_tags` if there are tags
    if (tags.length > 0) {
      tags.forEach(tagId => {
        params['needed_tags'] = params['needed_tags'] ? [...(params['needed_tags'] as string[]), tagId.toString()] : [tagId.toString()];
      });
    }

    // Add multiple `needed_characters` if there are characters
    if (characters.length > 0) {
      characters.forEach(characterId => {
        params['needed_characters'] = params['needed_characters'] ? [...(params['needed_characters'] as string[]), characterId.toString()] : [characterId.toString()];
      });
    }

    // Add multiple `needed_authors` if there are authors
    if (authors.length > 0) {
      authors.forEach(authorId => {
        params['needed_authors'] = params['needed_authors'] ? [...(params['needed_authors'] as string[]), authorId.toString()] : [authorId.toString()];
      });
    }

    // Custom query string serializer to avoid the [] in the query parameters
    const customParamsSerializer = (params: Record<string, string | string[]>) => {
      const queryString = Object.keys(params)
        .map(key => {
          const value = params[key];
          if (Array.isArray(value)) {
            return value.map(val => `${key}=${val}`).join('&');
          }
          return `${key}=${value}`;
        })
        .join('&');
      return queryString;
    };

    // Send the request to the API
    const response = await axios.get(`${API_BASE}/content/search`, {
      params,
      paramsSerializer: customParamsSerializer, // Using custom serializer
      headers: getAuthHeader(),
    });

    // Handle the response
    if (response.data && response.data.contents) {
      console.log('Search results:', response.data.contents);
      searchResults.value = response.data.contents;
      emit('update:searchResults', searchResults.value);
    } else {
      console.log('No search results found');
      searchResults.value = [];
      emit('update:searchResults', searchResults.value);
    }
  } catch (error) {
    console.error('Error validating search results:', error);
  }
};
</script>

<template>
  <div class="search-bar-container">
    <div class="selected-items">
      <span
        v-for="(item, index) in structuredQuery.tags"
        :key="'tag-' + index"
        class="tag-item"
      >
        {{ item.name }}
        <button @click="removeFromStructuredQuery('tag', item.name)">x</button>
      </span>
      <span
        v-for="(item, index) in structuredQuery.characters"
        :key="'character-' + index"
        class="character-item"
      >
        {{ item.name }}
        <button @click="removeFromStructuredQuery('character', item.name)">x</button>
      </span>
      <span
        v-for="(item, index) in structuredQuery.authors"
        :key="'author-' + index"
        class="author-item"
      >
        {{ item.name }}
        <button @click="removeFromStructuredQuery('author', item.name)">x</button>
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
    <button @click="validateSearchResults" class="validate_button">Search</button>
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
  color: black;
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

.tag-item {
  color: black;
}

.character-item {
  color: green;
}

.author-item {
  color: blue;
}

button {
  margin-left: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
}

/* Style for the "x" buttons */
button {
  color: red;
}

.validate_button {
  margin-top: 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.validate_button:hover {
  background-color: #45a049;
}

button:hover {
  background-color: #45a049;
}
</style>
