<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const title = ref('');
const description = ref('');
const source = ref('');
const sources = ref<{ id: number, name: string }[]>([]);
const searchQuery = ref('');
const tagSearchQuery = ref('');
const characterSearchQuery = ref('');
const authorSearchQuery = ref('');
const dropdownResults = ref<Array<{ name: string, id: number }>>([]);
const characterDropdownResults = ref<Array<{ name: string, id: number }>>([]);
const authorDropdownResults = ref<Array<{ name: string, id: number }>>([]);
const isDropdownVisible = ref(false);
const isCharacterDropdownVisible = ref(false);
const isAuthorDropdownVisible = ref(false);
const maxResultsToShow = 10;
const isPrivate = ref(false);
const selectedFile = ref<File | null>(null); // New state variable for the selected file

const structuredQuery = ref({
  tags: [] as Array<{ id: number, name: string }>,
  characters: [] as Array<{ id: number, name: string }>,
  authors: [] as Array<{ id: number, name: string }>,
});

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchSources = async () => {
  try {
    const response = await axios.get(`${API_BASE}/sources`, {
      headers: getAuthHeader(),
    });
    sources.value = response.data.sources.sort((a: { id: number, name: string }, b: { id: number, name: string }) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error('Error fetching sources:', error);
  }
};

onMounted(() => {
  fetchSources();
});

const filteredSources = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return sources.value
    .filter(source => source.name.toLowerCase().includes(query))
    .slice(0, maxResultsToShow);
});

const updateDropdown = () => {
  // This function is called on input event to update the dropdown options
};

const fetchTagResults = async (tag_name: string) => {
  if (!tag_name) {
    dropdownResults.value = [];
    return;
  }
  try {
    const response = await axios.get(`${API_BASE}/tags/search`, {
      params: { tag_name, max_results: 15 },
      headers: getAuthHeader(),
    });
    const results = response.data.tags || [];
    dropdownResults.value = results.filter((tag: { id: number, name: string }) =>
      !structuredQuery.value.tags.some(selectedTag => selectedTag.id === tag.id)
    );
    isDropdownVisible.value = dropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching tag results:', error);
    dropdownResults.value = [];
  }
};

const fetchCharacterResults = async (character_name: string) => {
  if (!character_name) {
    characterDropdownResults.value = [];
    return;
  }
  try {
    const response = await axios.get(`${API_BASE}/characters/search`, {
      params: { character_name, max_results: 15 },
      headers: getAuthHeader(),
    });
    const results = response.data.characters || [];
    characterDropdownResults.value = results.filter((character: { id: number, name: string }) =>
      !structuredQuery.value.characters.some(selectedCharacter => selectedCharacter.id === character.id)
    );
    isCharacterDropdownVisible.value = characterDropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching character results:', error);
    characterDropdownResults.value = [];
  }
};

const fetchAuthorResults = async (author_name: string) => {
  if (!author_name) {
    authorDropdownResults.value = [];
    return;
  }
  try {
    const response = await axios.get(`${API_BASE}/authors/search`, {
      params: { author_name, max_results: 15 },
      headers: getAuthHeader(),
    });
    const results = response.data.authors || [];
    authorDropdownResults.value = results.filter((author: { id: number, name: string }) =>
      !structuredQuery.value.authors.some(selectedAuthor => selectedAuthor.id === author.id)
    );
    isAuthorDropdownVisible.value = authorDropdownResults.value.length > 0;
  } catch (error) {
    console.error('Error fetching author results:', error);
    authorDropdownResults.value = [];
  }
};

const addToStructuredQuery = (result: { name: string, id: number }, type: 'tag' | 'character' | 'author') => {
  if (type === 'tag' && !structuredQuery.value.tags.some(tag => tag.id === result.id)) {
    structuredQuery.value.tags.push(result);
    fetchTagResults(tagSearchQuery.value); // Refresh suggestions
  } else if (type === 'character' && !structuredQuery.value.characters.some(character => character.id === result.id)) {
    structuredQuery.value.characters.push(result);
    fetchCharacterResults(characterSearchQuery.value); // Refresh suggestions
  } else if (type === 'author' && !structuredQuery.value.authors.some(author => author.id === result.id)) {
    structuredQuery.value.authors.push(result);
    fetchAuthorResults(authorSearchQuery.value); // Refresh suggestions
  }
};

const removeFromStructuredQuery = (name: string, type: 'tag' | 'character' | 'author') => {
  if (type === 'tag') {
    structuredQuery.value.tags = structuredQuery.value.tags.filter(tag => tag.name !== name);
    fetchTagResults(tagSearchQuery.value); // Refresh suggestions
  } else if (type === 'character') {
    structuredQuery.value.characters = structuredQuery.value.characters.filter(character => character.name !== name);
    fetchCharacterResults(characterSearchQuery.value); // Refresh suggestions
  } else if (type === 'author') {
    structuredQuery.value.authors = structuredQuery.value.authors.filter(author => author.name !== name);
    fetchAuthorResults(authorSearchQuery.value); // Refresh suggestions
  }
};

const clearAllTags = () => {
  structuredQuery.value.tags = [];
  tagSearchQuery.value = '';
  fetchTagResults(tagSearchQuery.value);
};

const clearAllCharacters = () => {
  structuredQuery.value.characters = [];
  characterSearchQuery.value = '';
  fetchCharacterResults(characterSearchQuery.value);
};

const clearAllAuthors = () => {
  structuredQuery.value.authors = [];
  authorSearchQuery.value = '';
  fetchAuthorResults(authorSearchQuery.value);
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target && target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  } else {
    selectedFile.value = null;
  }
};

const submitForm = async () => {
  const payload = {
    title: title.value,
    description: description.value,
    source_id: sources.value.find(sourceItem => sourceItem.name === source.value)?.id,
    tags: structuredQuery.value.tags.map(tag => tag.id),
    characters: structuredQuery.value.characters.map(character => character.id),
    authors: structuredQuery.value.authors.map(author => author.id),
    is_private: isPrivate.value,
  };

  const formData = new FormData();
  formData.append('content', JSON.stringify(payload));
  if (selectedFile.value) {
    formData.append('file', selectedFile.value);
  }

  try {
    const response = await axios.post(`${API_BASE}/content`, formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      },
    });
    if (response.status === 200) {
      alert('Content submitted successfully!');
    }
  } catch (error) {
    if (error) {
      alert(`Error submitting content: ${error}`);
    }
    console.error('Error submitting content:', error);
  }
};

watch(tagSearchQuery, (query) => {
  if (query.trim()) {
    fetchTagResults(query);
  } else {
    dropdownResults.value = [];
  }
});

watch(characterSearchQuery, (query) => {
  if (query.trim()) {
    fetchCharacterResults(query);
  } else {
    characterDropdownResults.value = [];
  }
});

watch(authorSearchQuery, (query) => {
  if (query.trim()) {
    fetchAuthorResults(query);
  } else {
    authorDropdownResults.value = [];
  }
});
</script>

<template>
  <header class="navbar">
    <NavBar />
  </header>
  <div class="new-content-container">
    <h1>Add New Content</h1>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="title">Title</label>
        <input id="title" v-model="title" placeholder="Enter title" />
      </div>
      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" v-model="description" placeholder="Enter description"></textarea>
      </div>
      <div class="form-group">
        <label for="source-search">Source</label>
        <div class="source-input-container">
          <input id="source-search" v-model="searchQuery" @input="updateDropdown" placeholder="Search for a source" />
          <select id="source" v-model="source" class="source-dropdown">
            <option v-for="(sourceItem) in filteredSources" :key="sourceItem.id" :value="sourceItem.name">
              {{ sourceItem.name }}
            </option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label for="tag-search">Tags</label>
        <div class="selected-tags">
          <span v-for="(tag, index) in structuredQuery.tags" :key="index" class="tag-item">
            {{ tag.name }}
            <button type="button" @click="removeFromStructuredQuery(tag.name, 'tag')" class="remove-button">x</button>
          </span>
        </div>
        <div class="tag-input-container">
          <input id="tag-search" v-model="tagSearchQuery" placeholder="Search for tags" />
          <button type="button" @click="clearAllTags" class="clear-tags-button">Clear</button>
          <ul v-if="isDropdownVisible" class="dropdown">
            <li v-for="(result, index) in dropdownResults" :key="index" @click="addToStructuredQuery(result, 'tag')">
              {{ result.name }}
            </li>
          </ul>
        </div>
      </div>
      <div class="form-group">
        <label for="character-search">Characters</label>
        <div class="selected-characters">
          <span v-for="(character, index) in structuredQuery.characters" :key="index" class="character-item">
            {{ character.name }}
            <button type="button" @click="removeFromStructuredQuery(character.name, 'character')" class="remove-button">x</button>
          </span>
        </div>
        <div class="character-input-container">
          <input id="character-search" v-model="characterSearchQuery" placeholder="Search for characters" />
          <button type="button" @click="clearAllCharacters" class="clear-characters-button">Clear</button>
          <ul v-if="isCharacterDropdownVisible" class="dropdown">
            <li v-for="(result, index) in characterDropdownResults" :key="index" @click="addToStructuredQuery(result, 'character')">
              {{ result.name }}
            </li>
          </ul>
        </div>
      </div>
      <div class="form-group">
        <label for="author-search">Authors</label>
        <div class="selected-authors">
          <span v-for="(author, index) in structuredQuery.authors" :key="index" class="author-item">
            {{ author.name }}
            <button type="button" @click="removeFromStructuredQuery(author.name, 'author')" class="remove-button">x</button>
          </span>
        </div>
        <div class="author-input-container">
          <input id="author-search" v-model="authorSearchQuery" placeholder="Search for authors" />
          <button type="button" @click="clearAllAuthors" class="clear-authors-button">Clear</button>
          <ul v-if="isAuthorDropdownVisible" class="dropdown">
            <li v-for="(result, index) in authorDropdownResults" :key="index" @click="addToStructuredQuery(result, 'author')">
              {{ result.name }}
            </li>
          </ul>
        </div>
      </div>
      <div class="form-group">
        <label for="is-private">Privacy</label>
        <label for="is-private">
          <input type="checkbox" id="is-private" v-model="isPrivate" />
          is Private?
        </label>
      </div>
      <div class="form-group">
        <label for="file-upload">Upload File</label>
        <input type="file" id="file-upload" @change="handleFileChange" />
      </div>
      <div class="submit-button-container">
        <button type="submit" class="submit-button">Submit</button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.new-content-container {
  max-width: 80%;
  margin: 0 auto;
  padding: 20px;
  background: #2f2f2f;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

input,
textarea,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

textarea {
  resize: none;
}

.source-input-container {
  display: flex;
  gap: 10px;
}

#source-search,
.source-dropdown {
  flex: 1;
}

.tag-input-container,
.character-input-container,
.author-input-container {
  display: flex;
  gap: 10px;
  position: relative;
}

#tag-search,
#character-search,
#author-search {
  flex: 4;
}

.clear-tags-button,
.clear-characters-button,
.clear-authors-button {
  flex: 1;
  padding: 10px;
  background-color: #ff0000;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid;
  border-top: none;
  list-style: none;
  padding: 0;
  margin: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.8);
}

.dropdown li {
  display: flex;
  align-items: center;
  padding: 0.7rem 1rem;
  cursor: pointer;
  font-size: 1rem;
  color: #ffffff;
}

.dropdown span {
  font-size: 1rem;
  color: #000;
}

.remove-button {
  margin-left: 10px;
  color: red;
  font-size: large;
}

.selected-tags,
.selected-characters,
.selected-authors {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 10px;
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
  background-color: rgba(255, 145, 0, 0.30);
  color: #ff9100;
}

.character-item {
  background-color: rgba(0, 128, 0, 0.30);
  color: green;
}

.author-item {
  background-color: rgba(0, 166, 255, 0.30);
  color: #00a6ff;
}

.submit-button-container {
  display: flex;
  justify-content: center;
}

.submit-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
