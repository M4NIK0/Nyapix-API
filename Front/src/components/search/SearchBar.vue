<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import AddButton from '@/components/search/AddButton.vue'

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
  tagsToExclude: [] as Array<{ id: number, name: string }>,
  charactersToExclude: [] as Array<{ id: number, name: string }>,
  authorsToExclude: [] as Array<{ id: number, name: string }>,
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
    // Remove the negative sign for autocomplete
    const searchWord = word.startsWith('-') ? word.slice(1) : word;

    const [tags, characters, authors] = await Promise.all([
      axios.get(`${API_BASE}/tags/search`, {
        params: { tag_name: searchWord, max_results: 15 },
        headers: getAuthHeader(),
      }),
      axios.get(`${API_BASE}/characters/search`, {
        params: { character_name: searchWord, max_results: 15 },
        headers: getAuthHeader(),
      }),
      axios.get(`${API_BASE}/authors/search`, {
        params: { author_name: searchWord, max_results: 15 },
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

  const negativeTypeMap: Record<string, keyof typeof structuredQuery.value> = {
    tag: 'tagsToExclude',
    character: 'charactersToExclude',
    author: 'authorsToExclude',
  };

  const queryKey = typeMap[result.type];
  const excludeQueryKey = negativeTypeMap[result.type];

  if (!queryKey || !excludeQueryKey) {
    console.error(`Unexpected result type: ${result.type}`);
    return;
  }

  const isNegative = result.name.startsWith('-');
  const normalizedName = isNegative ? result.name.slice(1) : result.name;

  // Check for duplicates between normal and negative inputs
  const existingNormal = structuredQuery.value[queryKey].some(item => item.name === result.name);
  const existingNegative = structuredQuery.value[excludeQueryKey].some(item => item.name === normalizedName);

  // Prevent adding the same input as both normal and negative
  if (isNegative) {
    if (!existingNegative && !existingNormal) {
      structuredQuery.value[excludeQueryKey].push({ id: result.id, name: result.name });
    }
  } else {
    if (!existingNormal && !existingNegative) {
      structuredQuery.value[queryKey].push({ id: result.id, name: result.name });
    }
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

  const excludeTypeMap: Record<string, keyof typeof structuredQuery.value> = {
    tag: 'tagsToExclude',
    character: 'charactersToExclude',
    author: 'authorsToExclude',
  };

  const queryKey = typeMap[type];
  const excludeQueryKey = excludeTypeMap[type];

  if (!queryKey || !excludeQueryKey) {
    console.error(`Unexpected type: ${type}`);
    return;
  }

  // Remove from the relevant query list
  structuredQuery.value[queryKey] = structuredQuery.value[queryKey].filter((item) => item.name !== name);
  structuredQuery.value[excludeQueryKey] = structuredQuery.value[excludeQueryKey].filter((item) => item.name !== name);
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
    const tags = structuredQuery.value.tags.map(tag => tag.id);
    const characters = structuredQuery.value.characters.map(character => character.id);
    const authors = structuredQuery.value.authors.map(author => author.id);
    const tagsToExclude = structuredQuery.value.tagsToExclude.map(tag => tag.id);
    const charactersToExclude = structuredQuery.value.charactersToExclude.map(character => character.id);
    const authorsToExclude = structuredQuery.value.authorsToExclude.map(author => author.id);

    // Prepare the query parameters
    const params: Record<string, string | string[]> = {
      page: '1',
      max_results: '25',
    };

    // Add multiple `needed_tags` if there are tags
    if (tags.length > 0) {
      params['needed_tags'] = tags.map(tagId => tagId.toString());
    }

    // Add multiple `needed_characters` if there are characters
    if (characters.length > 0) {
      params['needed_characters'] = characters.map(characterId => characterId.toString());
    }

    // Add multiple `needed_authors` if there are authors
    if (authors.length > 0) {
      params['needed_authors'] = authors.map(authorId => authorId.toString());
    }

    // Add exclusion parameters
    if (tagsToExclude.length > 0) {
      params['tags_to_exclude'] = tagsToExclude.map(tagId => tagId.toString());
    }
    if (charactersToExclude.length > 0) {
      params['characters_to_exclude'] = charactersToExclude.map(characterId => characterId.toString());
    }
    if (authorsToExclude.length > 0) {
      params['authors_to_exclude'] = authorsToExclude.map(authorId => authorId.toString());
    }

    // Send the request to the API with custom serialization for arrays
    const response = await axios.get(`${API_BASE}/content/search`, {
      params,
      headers: getAuthHeader(),
      paramsSerializer: (params) => {
        const queryStrings: string[] = [];
        Object.keys(params).forEach((key) => {
          const value = params[key];
          if (Array.isArray(value)) {
            value.forEach((val) => {
              queryStrings.push(`${key}=${val}`);
            });
          } else {
            queryStrings.push(`${key}=${value}`);
          }
        });
        return queryStrings.join('&');
      },
    });

    const results = response.data.contents;
    searchResults.value = results;
    emit('update:searchResults', results); // Emit the results to the parent component
  } catch (error) {
    console.error('Error fetching search results:', error);
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
    <AddButton />
  </div>
</template>

<style scoped>
.search-bar-container {
  position: relative;
  width: 100%;
  max-width: 600px; /* Increase the container width */
  margin: 0 auto;
}

input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid;
  border-radius: 6px;
  font-size: 1rem;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px; /* Allow more space for dropdown items */
  overflow-y: auto;
  border: 1px solid;
  border-top: none;
  list-style: none;
  padding: 0;
  margin: 0;
  z-index: 1000;
}

.dropdown li {
  display: flex;
  align-items: center;
  padding: 0.7rem 1rem; /* Adjust padding for larger clickable area */
  cursor: pointer;
  font-size: 1rem; /* Larger font for better readability */
}

.dropdown span {
  font-size: 1rem; /* Adjust size for uniformity */
}

.character {
  color: green;
}

.author {
  color: #00a6ff;
}

.tag {
  color: #ff9100;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
  gap: 0.5rem; /* Add consistent spacing between selected items */
}

.tag-item,
.character-item,
.author-item {
  display: inline-flex;
  align-items: center;
  padding: 0.4rem 0.8rem;
  border: 1px solid;
  border-radius: 6px;
  font-size: 0.95rem;
}

.tag-item {
  color: #ff9100;
}

.character-item {
  color: green;
}

.author-item {
  color: #00a6ff;
}

.validate_button {
  margin-top: 1rem;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
}

.center-container {
  display: flex;
  justify-content: flex-end; /* Align content to the right */
  align-items: center;
  height: 100vh; /* Full viewport height */
  padding: 20px; /* Optional: Add padding */
  box-sizing: border-box;
}

.center-container > div {
  max-width: 800px; /* Set a maximum width for content */
  width: 100%; /* Allow it to shrink for smaller screens */
  background: #2c2c2c; /* Optional: White background for contrast */
  border-radius: 8px; /* Optional: Rounded corners */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: Add a shadow */
  padding: 20px;
}

</style>
