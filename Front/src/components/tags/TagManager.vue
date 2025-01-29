<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

interface Tag {
  id: number;
  name: string;
}

interface User {
  user_type: number;
}

const tags = ref<Tag[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref('');
const totalPages = ref(1);
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const isEditTagPopupVisible = ref(false);
const tagToEdit = ref<Tag | null>(null);
const newTagName = ref('');
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
    const response = await axios.get(`${API_BASE}/tags/search`, {
      headers: getAuthHeader(),
      params: { tag_name: searchQuery.value, max_results: pageSize.value }
    });
    tags.value = response.data.tags;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error searching:', error);
  }
};

const deleteTag = async (id: number) => {
  if (confirm(`Are you sure you want to delete tag n°${id}?`)) {
    try {
      await axios.delete(`${API_BASE}/tags/${id}`, {
        headers: getAuthHeader()
      });
      await search();
    } catch (error) {
      console.error('Error deleting tag:', error);
    }
  }
};

const addTag = async () => {
  const tagName = prompt('Enter the tag name:');
  if (tagName) {
    try {
      await axios.post(`${API_BASE}/tags`, null, {
        headers: getAuthHeader(),
        params: { tag_name: tagName }
      });
      await search();
    } catch (error) {
      console.error('Error adding tag:', error);
    }
  }
};

const editTag = async (tag: Tag) => {
  try {
    const response = await axios.get(`${API_BASE}/tags/${tag.id}`, {
      headers: getAuthHeader()
    });
    tagToEdit.value = response.data;
    newTagName.value = response.data.name;
    isEditTagPopupVisible.value = true;
  } catch (error) {
    console.error('Error fetching tag:', error);
  }
};

const updateTag = async () => {
  if (tagToEdit.value && newTagName.value) {
    try {
      await axios.put(`${API_BASE}/tags/${tagToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { tag_name: newTagName.value }
      });
      await search();
      isEditTagPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating tag:', error);
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
  <div class="tag-container">
    <h2 class="tag_title">Tags</h2>
    <button v-if="user?.user_type === 1" @click="addTag" class="add-tag">Add a Tag</button>
    <input v-model="searchQuery" placeholder="Search..." />
    <ul>
      <li v-for="tag in tags" :key="tag.id" class="list-item tag">
        {{ tag.name }}
        <div class="button-group">
          <button v-if="user?.user_type === 1" class="edit-button" @click="editTag(tag)">Edit</button>
          <button v-if="user?.user_type === 1" class="delete-button" @click="deleteTag(tag.id)">X</button>
        </div>
      </li>
    </ul>
  </div>

  <div v-if="isEditTagPopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Edit Tag</h3>
      <input v-model="newTagName" placeholder="Tag Name" />
      <button @click="updateTag">Save</button>
      <button @click="isEditTagPopupVisible = false">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.add-tag {
  margin-bottom: 10px;
}

.tag-container {
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

.tag, .tag_title {
  color: #ff9100;
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

.list-item .tag {
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
