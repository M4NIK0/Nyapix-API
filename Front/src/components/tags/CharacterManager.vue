<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

interface Character {
  id: number;
  name: string;
}

interface User {
  user_type: number;
}

const characters = ref<Character[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref('');
const totalPages = ref(1);
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const isEditCharacterPopupVisible = ref(false);
const characterToEdit = ref<Character | null>(null);
const newCharacterName = ref('');
const user = ref<User | null>(null);

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchUserData = async () => {
  try {
    const response = await axios.get(`${API_BASE}/users/me`, {
      headers: getAuthHeader(),
    });
    user.value = response.data;
  } catch (error) {
    console.error('Error fetching user data:', error);
  }
};

const search = async () => {
  try {
    const response = await axios.get(`${API_BASE}/characters/search`, {
      headers: getAuthHeader(),
      params: { character_name: searchQuery.value, max_results: pageSize.value }
    });
    characters.value = response.data.characters;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error searching:', error);
  }
};

const deleteCharacter = async (id: number) => {
  if (confirm(`Are you sure you want to delete character n°${id}?`)) {
    try {
      await axios.delete(`${API_BASE}/characters/${id}`, {
        headers: getAuthHeader()
      });
      await search();
    } catch (error) {
      console.error('Error deleting character:', error);
    }
  }
};

const addCharacter = async () => {
  const characterName = prompt('Enter the character name:');
  if (characterName) {
    try {
      await axios.post(`${API_BASE}/characters`, null, {
        headers: getAuthHeader(),
        params: { character_name: characterName }
      });
      await search();
    } catch (error) {
      console.error('Error adding character:', error);
    }
  }
};

const editCharacter = async (character: Character) => {
  try {
    const response = await axios.get(`${API_BASE}/characters/${character.id}`, {
      headers: getAuthHeader()
    });
    characterToEdit.value = response.data;
    newCharacterName.value = response.data.name;
    isEditCharacterPopupVisible.value = true;
  } catch (error) {
    console.error('Error fetching character:', error);
  }
};

const updateCharacter = async () => {
  if (characterToEdit.value && newCharacterName.value) {
    try {
      await axios.put(`${API_BASE}/characters/${characterToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { character_name: newCharacterName.value }
      });
      await search();
      isEditCharacterPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating character:', error);
    }
  }
};

onMounted(async () => {
  await fetchUserData();
  await search();
});

watch(searchQuery, async () => {
  currentPage.value = 1;
  await search();
});
</script>

<template>
  <div class="character-container">
    <h2 class="character_title">Characters</h2>
    <button v-if="user?.user_type === 1" @click="addCharacter" class="add-character">Add a Character</button>
    <input v-model="searchQuery" placeholder="Search..." />
    <ul>
      <li v-for="character in characters" :key="character.id" class="list-item character">
        {{ character.name }}
        <div class="button-group">
          <button v-if="user?.user_type === 1" class="edit-button" @click="editCharacter(character)">Edit</button>
          <button v-if="user?.user_type === 1" class="delete-button" @click="deleteCharacter(character.id)">X</button>
        </div>
      </li>
    </ul>
  </div>

  <div v-if="isEditCharacterPopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Edit Character</h3>
      <input v-model="newCharacterName" placeholder="Character Name" />
      <button @click="updateCharacter">Save</button>
      <button @click="isEditCharacterPopupVisible = false">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.add-character {
  margin-bottom: 10px;
}

.character-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 800px;
  width: 100%;
  max-height: 100vh;
  overflow-y: auto; /* Allow scrolling within the container if content overflows */
  background: #2c2c2c;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.character, .character_title {
  color: green;
}

input {
  margin-bottom: 10px;
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.list-item .character {
  flex-grow: 1;
  margin-right: 10px;
}

.button-group {
  display: flex;
  gap: 5px;
}

.edit-button {
  cursor: pointer;
  margin-left: 10px;
}

.delete-button {
  color: red;
  cursor: pointer;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 10px;
}

.pagination button {
  cursor: pointer;
}

/* Edit popup */
.edit-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.edit-popup-content {
  background: #333;
  color: #fff;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
}

.edit-popup-content input {
  margin-bottom: 10px;
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
}
</style>
