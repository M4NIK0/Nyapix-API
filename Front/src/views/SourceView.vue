<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';

interface Source {
  id: number;
  name: string;
}

const sources = ref<Source[]>([]);
const newSourceName = ref('');
const isAddSourcePopupVisible = ref(false);
const sourceToEdit = ref<Source | null>(null);
const isEditSourcePopupVisible = ref(false);

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
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

const addSource = async () => {
  if (newSourceName.value) {
    try {
      await axios.post(`${API_BASE}/sources`, '', {
        headers: getAuthHeader(),
        params: {
          source_name: newSourceName.value,
        },
      });
      fetchSources();
      newSourceName.value = '';
      isAddSourcePopupVisible.value = false;
    } catch (error) {
      console.error('Error adding source:', error);
    }
  }
};

const updateSource = async () => {
  if (sourceToEdit.value && newSourceName.value) {
    try {
      await axios.put(`${API_BASE}/sources/${sourceToEdit.value.id}?source_name=${newSourceName.value}`, null, {
        headers: {
          ...getAuthHeader(),
        },
      });
      fetchSources();
      isEditSourcePopupVisible.value = false;
    } catch (error) {
      console.error('Error updating source:', error);
    }
  }
};

const deleteSource = async (sourceId: number) => {
  try {
    await axios.delete(`${API_BASE}/sources/${sourceId}`, {
      headers: getAuthHeader(),
    });
    fetchSources();
  } catch (error) {
    console.error('Error deleting source:', error);
  }
};

const editSource = (source: Source) => {
  sourceToEdit.value = source;
  newSourceName.value = source.name;
  isEditSourcePopupVisible.value = true;
};

onMounted(() => {
  fetchSources();
});
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div class="sources-container">
  <div>
    <div class="button-container">
      <button @click="isAddSourcePopupVisible = true">Add Source</button>
    </div>
    <div>
      <h2>Sources</h2>
      <ul>
        <li v-for="source in sources" :key="source.id" class="list-item">
          {{ source.name }}
          <div class="button-group">
            <button class="edit-button" @click="editSource(source)">Edit</button>
            <button class="delete-button" @click="deleteSource(source.id)">X</button>
          </div>
        </li>
      </ul>
    </div>
  </div>

  <div v-if="isAddSourcePopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Add Source</h3>
      <input v-model="newSourceName" placeholder="New source name" />
      <button @click="addSource">Save</button>
      <button @click="isAddSourcePopupVisible = false">Cancel</button>
    </div>
  </div>

  <div v-if="isEditSourcePopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Edit Source</h3>
      <input v-model="newSourceName" placeholder="New source name" />
      <button @click="updateSource">Save</button>
      <button @click="isEditSourcePopupVisible = false">Cancel</button>
    </div>
  </div>
  </div>
</template>

<style scoped>
.delete-button {
  color: red;
  cursor: pointer;
}

.edit-button {
  cursor: pointer;
}

.button-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.button-container button {
  cursor: pointer;
  padding: 10px;
}

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
}

.edit-popup-content {
  background: white;
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

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.button-group {
  display: flex;
  gap: 5px;
}

.sources-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* Ensure it takes full viewport height */
  padding: 20px;
}
</style>
