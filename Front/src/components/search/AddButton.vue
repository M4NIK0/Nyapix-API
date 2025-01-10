<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

const isPopupVisible = ref(false);
const title = ref('');
const description = ref('');
const sourceId = ref<number | null>(null);
const tags = ref('');
const characters = ref('');
const authors = ref('');
const isPrivate = ref(false);
const selectedFile = ref<File | null>(null);
const sources = ref<{ id: number; name: string }[]>([]);
const tagSuggestions = ref<{ id: number; name: string }[]>([]);
const characterSuggestions = ref<{ id: number; name: string }[]>([]);
const authorSuggestions = ref<{ id: number; name: string }[]>([]);
const showTagSuggestions = ref(false);
const showCharacterSuggestions = ref(false);
const showAuthorSuggestions = ref(false);

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const openPopup = () => {
  isPopupVisible.value = true;
};

const closePopup = () => {
  isPopupVisible.value = false;
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  }
};

const fetchSources = async () => {
  try {
    const response = await axios.get(`${API_BASE}/sources`, {
      headers: getAuthHeader(),
    });
    sources.value = response.data;
  } catch (error) {
    console.error('Error fetching sources:', error);
  }
};

const fetchTagSuggestions = async (query: string) => {
  try {
    const response = await axios.get(`${API_BASE}/tags/search`, {
      headers: getAuthHeader(),
      params: {
        tag_name: query,
        max_results: 5,
      },
    });
    tagSuggestions.value = response.data.tags;
    showTagSuggestions.value = true;
  } catch (error) {
    console.error('Error fetching tag suggestions:', error);
  }
};

const fetchCharacterSuggestions = async (query: string) => {
  try {
    const response = await axios.get(`${API_BASE}/characters/search`, {
      headers: getAuthHeader(),
      params: {
        character_name: query,
        max_results: 5,
      },
    });
    characterSuggestions.value = response.data.characters;
    showCharacterSuggestions.value = true;
  } catch (error) {
    console.error('Error fetching character suggestions:', error);
  }
};

const fetchAuthorSuggestions = async (query: string) => {
  try {
    const response = await axios.get(`${API_BASE}/authors/search`, {
      headers: getAuthHeader(),
      params: {
        author_name: query,
        max_results: 5,
      },
    });
    authorSuggestions.value = response.data.authors;
    showAuthorSuggestions.value = true;
  } catch (error) {
    console.error('Error fetching author suggestions:', error);
  }
};

const selectTagSuggestion = (tag: { id: number; name: string }) => {
  const tagList = tags.value.split(',').map(tag => tag.trim());
  tagList[tagList.length - 1] = tag.name;
  tags.value = tagList.join(', ');
  showTagSuggestions.value = false;
};

const selectCharacterSuggestion = (character: { id: number; name: string }) => {
  const characterList = characters.value.split(',').map(character => character.trim());
  characterList[characterList.length - 1] = character.name;
  characters.value = characterList.join(', ');
  showCharacterSuggestions.value = false;
};

const selectAuthorSuggestion = (author: { id: number; name: string }) => {
  const authorList = authors.value.split(',').map(author => author.trim());
  authorList[authorList.length - 1] = author.name;
  authors.value = authorList.join(', ');
  showAuthorSuggestions.value = false;
};

const getOrCreateId = async (name: string, type: 'tags' | 'characters' | 'authors') => {
  try {
    const searchResponse = await axios.get(`${API_BASE}/${type}/search`, {
      headers: getAuthHeader(),
      params: {
        [`${type.slice(0, -1)}_name`]: name,
        max_results: 10,
      },
    });

    if (searchResponse.data[type].length > 0) {
      return searchResponse.data[type][0].id;
    } else {
      try {
        const createResponse = await axios.post(`${API_BASE}/${type}`, null, {
          headers: getAuthHeader(),
          params: {
            [`${type.slice(0, -1)}_name`]: name,
          },
        });
        return createResponse.data.id;
      } catch (createError: any) {
        if (createError.response && createError.response.status === 409) {
          const retrySearchResponse = await axios.get(`${API_BASE}/${type}/search`, {
            headers: getAuthHeader(),
            params: {
              [`${type.slice(0, -1)}_name`]: name,
              max_results: 10,
            },
          });
          if (retrySearchResponse.data[type].length > 0) {
            return retrySearchResponse.data[type][0].id;
          }
        }
        throw createError;
      }
    }
  } catch (error) {
    console.error(`Error fetching or creating ${type.slice(0, -1)}:`, error);
    throw error;
  }
};

const submitForm = async () => {
  if (!selectedFile.value) {
    alert('Please select a file.');
    return;
  }

  try {
    const tagIds = await Promise.all(tags.value.split(',').map(tag => getOrCreateId(tag.trim(), 'tags')));
    const characterIds = await Promise.all(characters.value.split(',').map(character => getOrCreateId(character.trim(), 'characters')));
    const authorIds = await Promise.all(authors.value.split(',').map(author => getOrCreateId(author.trim(), 'authors')));

    const formData = new FormData();
    formData.append('content', JSON.stringify({
      title: title.value,
      description: description.value,
      source_id: sourceId.value,
      tags: tagIds,
      characters: characterIds,
      authors: authorIds,
      is_private: isPrivate.value,
    }));
    formData.append('file', selectedFile.value);

    await axios.post(`${API_BASE}/content`, formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      },
    });
    alert('Content added successfully!');
    closePopup();
  } catch (error) {
    console.error('Error adding content:', error);
    alert('Error adding content.');
  }
};

watch(tags, (newTags) => {
  const lastTag = newTags.split(',').pop()?.trim();
  if (lastTag) {
    fetchTagSuggestions(lastTag);
  } else {
    showTagSuggestions.value = false;
  }
});

watch(characters, (newCharacters) => {
  const lastCharacter = newCharacters.split(',').pop()?.trim();
  if (lastCharacter) {
    fetchCharacterSuggestions(lastCharacter);
  } else {
    showCharacterSuggestions.value = false;
  }
});

watch(authors, (newAuthors) => {
  const lastAuthor = newAuthors.split(',').pop()?.trim();
  if (lastAuthor) {
    fetchAuthorSuggestions(lastAuthor);
  } else {
    showAuthorSuggestions.value = false;
  }
});

onMounted(() => {
  fetchSources();
});
</script>

<template>
  <button @click="openPopup" class="theme-button">Add Content</button>

  <div v-if="isPopupVisible" class="popup">
    <div class="popup-content">
      <h3>Add Content</h3>
      <input v-model="title" placeholder="Title" />
      <input v-model="description" placeholder="Description" />
      <select v-model="sourceId">
        <option v-for="source in sources" :key="source.id" :value="source.id">{{ source.name }}</option>
      </select>
      <div class="tag-input">
        <input v-model="tags" placeholder="Tags (comma separated names)" />
        <ul v-if="showTagSuggestions" class="suggestions">
          <li v-for="suggestion in tagSuggestions" :key="suggestion.id" @click="selectTagSuggestion(suggestion)">
            {{ suggestion.name }}
          </li>
        </ul>
      </div>
      <div class="character-input">
        <input v-model="characters" placeholder="Characters (comma separated names)" />
        <ul v-if="showCharacterSuggestions" class="suggestions">
          <li v-for="suggestion in characterSuggestions" :key="suggestion.id" @click="selectCharacterSuggestion(suggestion)">
            {{ suggestion.name }}
          </li>
        </ul>
      </div>
      <div class="author-input">
        <input v-model="authors" placeholder="Authors (comma separated names)" />
        <ul v-if="showAuthorSuggestions" class="suggestions">
          <li v-for="suggestion in authorSuggestions" :key="suggestion.id" @click="selectAuthorSuggestion(suggestion)">
            {{ suggestion.name }}
          </li>
        </ul>
      </div>
      <label>
        <input type="checkbox" v-model="isPrivate" />
        Private
      </label>
      <input type="file" @change="handleFileChange" />
      <button @click="submitForm" class="theme-button">Submit</button>
      <button @click="closePopup" class="theme-button">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.theme-button {
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.popup-content {
  background: grey;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
}

.popup-content input,
.popup-content select {
  margin-bottom: 10px;
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
  color: black;
}

.tag-input,
.character-input,
.author-input {
  position: relative;
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 150px;
  overflow-y: auto;
}

.suggestions li {
  padding: 5px;
  cursor: pointer;
  color: black;
}

.suggestions li:hover {
  background: #eee;
}
</style>
