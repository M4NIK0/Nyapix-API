<script setup lang="ts">
import { defineProps } from 'vue';
import { onMounted, ref } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";
import router from "@/router";

const props = defineProps<{ id: number }>();

const content = ref<any>(null);
const isEditOverlayVisible = ref(false);
const editForm = ref({
  title: '',
  description: '',
  source_id: 0,
  is_private: false,
  tags: '',
  characters: '',
  authors: ''
});

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const deleteContent = async () => {
  try {
    const response = await axios.delete(`${API_BASE}/content/${props.id}`, {
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
    console.log('Content:', content.value);

    const tagNames = await Promise.all(content.value.tags.map(fetchTagDetails));
    content.value.tagNames = tagNames.filter(name => name !== null);

    const characterNames = await Promise.all(content.value.characters.map(fetchCharacterDetails));
    content.value.characterNames = characterNames.filter(name => name !== null);

    const authorNames = await Promise.all(content.value.authors.map(fetchAuthorDetails));
    content.value.authorNames = authorNames.filter(name => name !== null);

    const imageResponse = await axios.get(content.value.url, {
      headers: getAuthHeader(),
      responseType: 'blob',
    });

    const imageBlob = imageResponse.data;
    content.value.imageSrc = URL.createObjectURL(imageBlob);
  } catch (error) {
    console.error('Error fetching content:', error);
  }
};

const showEditOverlay = () => {
  editForm.value = {
    title: content.value.title,
    description: content.value.description,
    source_id: content.value.source,
    is_private: content.value.is_private,
    tags: content.value.tags.join(', '),
    characters: content.value.characters.join(', '),
    authors: content.value.authors.join(', ')
  };
  isEditOverlayVisible.value = true;
};

const hideEditOverlay = () => {
  isEditOverlayVisible.value = false;
};

const updateContent = async () => {
  try {
    const updatedContent = {
      title: editForm.value.title,
      description: editForm.value.description,
      source_id: editForm.value.source_id,
      is_private: editForm.value.is_private,
      tags: editForm.value.tags.split(',').map(tag => parseInt(tag.trim())),
      characters: editForm.value.characters.split(',').map(character => parseInt(character.trim())),
      authors: editForm.value.authors.split(',').map(author => parseInt(author.trim()))
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

onMounted(() => {
  fetchContent();
});
</script>

<template>
  <div class="content-view">
    <header>
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
          <button @click="deleteContent" class="delete-button">Delete</button>
          <button @click="showEditOverlay" class="edit-button">Edit</button>
          <h1>{{ content.title }}</h1>
          <p>{{ content.description }}</p>
          <img v-if="content.imageSrc" :src="content.imageSrc" alt="Content Image" class="responsive-image" />
        </div>
      </div>
    </div>
    <div v-else>
      <p>Loading...</p>
    </div>
    <div v-if="isEditOverlayVisible" class="overlay">
      <div class="overlay-content">
        <h2>Edit Content</h2>
        <label>
          Title:
          <input v-model="editForm.title" type="text" />
        </label>
        <label>
          Description:
          <textarea v-model="editForm.description"></textarea>
        </label>
        <label>
          Source ID:
          <input v-model="editForm.source_id" type="number" />
        </label>
        <label>
          Is Private:
          <input v-model="editForm.is_private" type="checkbox" />
        </label>
        <label>
          Tags:
          <input v-model="editForm.tags" type="text" placeholder="Comma separated tags" />
        </label>
        <label>
          Characters:
          <input v-model="editForm.characters" type="text" placeholder="Comma separated characters" />
        </label>
        <label>
          Authors:
          <input v-model="editForm.authors" type="text" placeholder="Comma separated authors" />
        </label>
        <button @click="updateContent" class="save-button">Save</button>
        <button @click="hideEditOverlay" class="cancel-button">Cancel</button>
      </div>
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

.responsive-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.delete-button, .edit-button {
  background-color: red;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  margin-bottom: 20px;
  border-radius: 4px;
}

.edit-button {
  background-color: blue;
}

.delete-button:hover {
  background-color: darkred;
}

.edit-button:hover {
  background-color: darkblue;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay-content {
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 500px;
}

.overlay-content label {
  display: block;
  margin-bottom: 10px;
}

.overlay-content input[type="text"],
.overlay-content input[type="number"],
.overlay-content textarea {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  margin-bottom: 15px;
}

.save-button, .cancel-button {
  background-color: green;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  margin-right: 10px;
  border-radius: 4px;
}

.cancel-button {
  background-color: gray;
}

.save-button:hover {
  background-color: darkgreen;
}

.cancel-button:hover {
  background-color: darkgray;
}
</style>
