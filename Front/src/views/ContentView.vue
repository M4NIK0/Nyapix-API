<script setup lang="ts">
import { defineProps, ref, onMounted, watch, onBeforeUnmount } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";
import router from "@/router";

const props = defineProps<{ id: number }>();

const content = ref<any>(null);
const isEditOverlayVisible = ref(false);
const editForm = ref({
  title: '',
  description: '',
  sourceId: null as number | null,
  is_private: false,
  tags: '',
  characters: '',
  authors: ''
});

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

const deleteContent = async () => {
  try {
    await axios.delete(`${API_BASE}/content/${props.id}`, {
      headers: getAuthHeader(),
    });
    alert('Content deleted successfully');
    router.push('/');
  } catch (error) {
    console.error('Error deleting content:', error);
    alert('Failed to delete content');
  }
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

    const tagNames = await Promise.all(content.value.tags.map(fetchTagDetails));
    content.value.tagNames = tagNames.filter(name => name !== null);

    const characterNames = await Promise.all(content.value.characters.map(fetchCharacterDetails));
    content.value.characterNames = characterNames.filter(name => name !== null);

    const authorNames = await Promise.all(content.value.authors.map(fetchAuthorDetails));
    content.value.authorNames = authorNames.filter(name => name !== null);

    const mediaResponse = await axios.get(content.value.url, {
      headers: getAuthHeader(),
      responseType: 'blob',
    });

    const mediaBlob = mediaResponse.data;
    content.value.mediaSrc = URL.createObjectURL(mediaBlob);
    content.value.mediaType = mediaResponse.headers['content-type'];
  } catch (error) {
    console.error('Error fetching content:', error);
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
  const tagList = editForm.value.tags.split(',').map(tag => tag.trim());
  tagList[tagList.length - 1] = tag.name;
  editForm.value.tags = tagList.join(', ');
  showTagSuggestions.value = false;
};

const selectCharacterSuggestion = (character: { id: number; name: string }) => {
  const characterList = editForm.value.characters.split(',').map(character => character.trim());
  characterList[characterList.length - 1] = character.name;
  editForm.value.characters = characterList.join(', ');
  showCharacterSuggestions.value = false;
};

const selectAuthorSuggestion = (author: { id: number; name: string }) => {
  const authorList = editForm.value.authors.split(',').map(author => author.trim());
  authorList[authorList.length - 1] = author.name;
  editForm.value.authors = authorList.join(', ');
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

const updateContent = async () => {
  try {
    const tagIds = await Promise.all(editForm.value.tags.split(',').map(tag => getOrCreateId(tag.trim(), 'tags')));
    const characterIds = await Promise.all(editForm.value.characters.split(',').map(character => getOrCreateId(character.trim(), 'characters')));
    const authorIds = await Promise.all(editForm.value.authors.split(',').map(author => getOrCreateId(author.trim(), 'authors')));

    const updatedContent = {
      title: editForm.value.title,
      description: editForm.value.description,
      source_id: editForm.value.sourceId,
      is_private: editForm.value.is_private,
      tags: tagIds,
      characters: characterIds,
      authors: authorIds
    };
    await axios.put(`${API_BASE}/content/${props.id}`, updatedContent, {
      headers: {
        'accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      }
    });
    alert('Content updated successfully');
    hideEditOverlay();
    fetchContent();
  } catch (error) {
    console.error('Error updating content:', error);
    alert('Failed to update content');
  }
};

const showEditOverlay = () => {
  editForm.value = {
    title: content.value.title,
    description: content.value.description,
    sourceId: content.value.source_id,
    is_private: content.value.is_private,
    tags: content.value.tagNames.join(', '),
    characters: content.value.characterNames.join(', '),
    authors: content.value.authorNames.join(', ')
  };
  isEditOverlayVisible.value = true;
};

const hideEditOverlay = () => {
  isEditOverlayVisible.value = false;
};

watch(() => editForm.value.tags, (newTags: string) => {
  const lastTag = newTags.split(',').pop()?.trim();
  if (lastTag) {
    fetchTagSuggestions(lastTag);
  } else {
    showTagSuggestions.value = false;
  }
});

watch(() => editForm.value.characters, (newCharacters: string) => {
  const lastCharacter = newCharacters.split(',').pop()?.trim();
  if (lastCharacter) {
    fetchCharacterSuggestions(lastCharacter);
  } else {
    showCharacterSuggestions.value = false;
  }
});

watch(() => editForm.value.authors, (newAuthors: string) => {
  const lastAuthor = newAuthors.split(',').pop()?.trim();
  if (lastAuthor) {
    fetchAuthorSuggestions(lastAuthor);
  } else {
    showAuthorSuggestions.value = false;
  }
});

const closeDropdown = (event: MouseEvent) => {
  const overlayContent = document.querySelector('.overlay-content');
  if (overlayContent && !overlayContent.contains(event.target as Node)) {
    showTagSuggestions.value = false;
    showCharacterSuggestions.value = false;
    showAuthorSuggestions.value = false;
  }
};

onMounted(() => {
  fetchContent();
  fetchSources();
  document.addEventListener('mousedown', closeDropdown);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', closeDropdown);
});
</script>

<template>
  <div class="content-view">
    <header>
      <NavBar />
    </header>
    <div v-if="content" class="content-container">
      <div class="content-header">
        <h1>{{ content.title }}</h1>
        <p>{{ content.description }}</p>
      </div>
      <div class="content-body">
        <aside class="info-section">
          <h2>Information</h2>
          <section>
            <h3>Tags</h3>
            <ul>
              <li v-for="tag in content.tagNames" :key="tag">{{ tag }}</li>
            </ul>
          </section>
          <section>
            <h3>Characters</h3>
            <ul>
              <li v-for="character in content.characterNames" :key="character">{{ character }}</li>
            </ul>
          </section>
          <section>
            <h3>Authors</h3>
            <ul>
              <li v-for="author in content.authorNames" :key="author">{{ author }}</li>
            </ul>
          </section>
          <div class="action-buttons">
            <button @click="deleteContent" class="delete-button">Delete</button>
            <button @click="showEditOverlay" class="edit-button">Edit</button>
          </div>
        </aside>
        <div class="media-section">
          <div v-if="content.mediaSrc">
            <img v-if="content.mediaType.startsWith('image/')" :src="content.mediaSrc" alt="Content Image" class="responsive-image" />
            <video v-else-if="content.mediaType.startsWith('video/')" :src="content.mediaSrc" controls class="responsive-media"></video>
            <audio v-else-if="content.mediaType.startsWith('audio/')" :src="content.mediaSrc" controls class="responsive-media"></audio>
            <span v-else>No media available</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <p>Loading...</p>
    </div>
    <div v-if="isEditOverlayVisible" class="overlay">
      <div class="overlay-content">
        <h2>Edit Content</h2>
        <!-- Edit Form -->
        <button @click="hideEditOverlay" class="cancel-button">Cancel</button>
      </div>
    </div>
  </div>
</template>


<style scoped>
.content-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.content-main {
  display: flex;
  flex-direction: row-reverse;
  gap: 20px;
  width: 80%;
  max-width: 1200px;
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.info-section {
  flex: 1;
  max-width: 300px;
}

.media-section {
  flex: 2;
}

.content-details h1 {
  margin-top: 0;
}

.responsive-image,
.responsive-media {
  width: 100%;
  height: auto;
  margin-top: 20px;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.overlay-content {
  background: grey;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.overlay-content input,
.overlay-content select,
.overlay-content textarea {
  margin-bottom: 10px;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
  border-radius: 4px;
  border: 1px solid #ccc;
  color: black;
}

.delete-button,
.edit-button,
.save-button,
.cancel-button {
  margin-top: 10px;
}
</style>
