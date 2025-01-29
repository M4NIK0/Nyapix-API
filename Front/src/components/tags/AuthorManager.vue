<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';

interface Author {
  id: number;
  name: string;
}

interface User {
  user_type: number;
}

const authors = ref<Author[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref('');
const totalPages = ref(1);
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const isEditAuthorPopupVisible = ref(false);
const authorToEdit = ref<Author | null>(null);
const newAuthorName = ref('');
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
    const response = await axios.get(`${API_BASE}/authors/search`, {
      headers: getAuthHeader(),
      params: { author_name: searchQuery.value, max_results: pageSize.value }
    });
    authors.value = response.data.authors;
    totalPages.value = response.data.total_pages;
  } catch (error) {
    console.error('Error searching:', error);
  }
};

const deleteAuthor = async (id: number) => {
  if (confirm(`Are you sure you want to delete author n°${id}?`)) {
    try {
      await axios.delete(`${API_BASE}/authors/${id}`, {
        headers: getAuthHeader()
      });
      await search();
    } catch (error) {
      console.error('Error deleting author:', error);
    }
  }
};

const addAuthor = async () => {
  const authorName = prompt('Enter the author name:');
  if (authorName) {
    try {
      await axios.post(`${API_BASE}/authors`, null, {
        headers: getAuthHeader(),
        params: { author_name: authorName }
      });
      await search();
    } catch (error) {
      console.error('Error adding author:', error);
    }
  }
};

const editAuthor = async (author: Author) => {
  try {
    const response = await axios.get(`${API_BASE}/authors/${author.id}`, {
      headers: getAuthHeader()
    });
    authorToEdit.value = response.data;
    newAuthorName.value = response.data.name;
    isEditAuthorPopupVisible.value = true;
  } catch (error) {
    console.error('Error fetching author:', error);
  }
};

const updateAuthor = async () => {
  if (authorToEdit.value && newAuthorName.value) {
    try {
      await axios.put(`${API_BASE}/authors/${authorToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { author_name: newAuthorName.value }
      });
      await search();
      isEditAuthorPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating author:', error);
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
  <div class="author-container">
    <h2 class="author_title">Authors</h2>
    <button v-if="user?.user_type === 1" @click="addAuthor" class="add-author">Add an Author</button>
    <input v-model="searchQuery" placeholder="Search..." />
    <ul>
      <li v-for="author in authors" :key="author.id" class="list-item author">
        {{ author.name }}
        <div class="button-group">
          <button v-if="user?.user_type === 1" class="edit-button" @click="editAuthor(author)">Edit</button>
          <button v-if="user?.user_type === 1" class="delete-button" @click="deleteAuthor(author.id)">X</button>
        </div>
      </li>
    </ul>
  </div>

  <div v-if="isEditAuthorPopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Edit Author</h3>
      <input v-model="newAuthorName" placeholder="Author Name" />
      <button @click="updateAuthor">Save</button>
      <button @click="isEditAuthorPopupVisible = false">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.add-author {
  margin-bottom: 10px;
}

.author-container {
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

.author, .author_title {
  color: #00a6ff;
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

.list-item .author {
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
