<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

interface User {
  id: number;
  username: string;
  nickname: string;
  type: number;
}

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const searchQuery = ref('');
const searchResults = ref<User[]>([]);
const currentPage = ref(0);
const maxResults = ref(10);
const isEditPopupVisible = ref(false);
const editedUserId = ref<number | null>(null);
const editedUsername = ref('');
const editedNickname = ref('');
const editedPassword = ref('');
const contentId = ref('');
const userData = ref<User | null>(null);
const albumId = ref('');
const albumUserData = ref<User | null>(null);

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const searchUsers = async () => {
  try {
    const response = await axios.get(`${API_BASE}/users/search`, {
      headers: getAuthHeader(),
      params: {
        user_query: searchQuery.value,
        max_results: maxResults.value,
        page: currentPage.value,
      },
    });
    searchResults.value = response.data.users;
    console.log('Search results:', searchResults.value);
  } catch (error) {
    console.error('Error searching users:', error);
  }
};

const deleteUser = async (userId: number) => {
  if (confirm('Are you sure you want to delete this user?')) {
    try {
      await axios.delete(`${API_BASE}/users/${userId}`, {
        headers: getAuthHeader(),
      });
      searchUsers(); // Refresh the user list after deletion
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  }
};

const openEditPopup = (user: User) => {
  editedUserId.value = user.id;
  editedUsername.value = user.username;
  editedNickname.value = user.nickname;
  editedPassword.value = '';
  isEditPopupVisible.value = true;
};

const updateUser = async () => {
  if (editedUserId.value !== null) {
    try {
      await axios.put(`${API_BASE}/users/${editedUserId.value}`, {
        username: editedUsername.value,
        nickname: editedNickname.value,
        password: editedPassword.value,
      }, {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      });
      searchUsers();
      isEditPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating user:', error);
    }
  }
};

const previousPage = () => {
  if (currentPage.value > 0) {
    currentPage.value--;
    searchUsers();
  }
};

const nextPage = () => {
  currentPage.value++;
  searchUsers();
};

const fetchUserData = async () => {
  if (contentId.value) {
    try {
      const response = await axios.get(`${API_BASE}/content/${contentId.value}/who`, {
        headers: getAuthHeader(),
      });
      userData.value = response.data;
    } catch (error) {
      alert('Error fetching user data : ' + error);
      console.error('Error fetching user data:', error);
      userData.value = null;
    }
  }
};

const fetchAlbumUserData = async () => {
  if (albumId.value) {
    try {
      const response = await axios.get(`${API_BASE}/albums/${albumId.value}/who`, {
        headers: getAuthHeader(),
        params: {
          album_id: albumId.value,
        },
      });
      albumUserData.value = response.data;
    } catch (error) {
      alert('Error fetching album user data : ' + error);
      console.error('Error fetching album user data:', error);
      albumUserData.value = null;
    }
  }
};
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div class="container">
    <div class="search-container">
      <div class="search-section">
        <input v-model="searchQuery" placeholder="Search users..." />
        <button @click="searchUsers">Search</button>
      </div>
      <ul>
        <li v-for="user in searchResults" :key="user.id" class="user-item">
          <span>{{ user.username }}</span>
          <div class="user-actions">
            <button @click="openEditPopup(user)">Edit</button>
            <button @click="deleteUser(user.id)" style="color: red;">X</button>
          </div>
        </li>
      </ul>
      <div class="pagination">
        <button @click="previousPage" :disabled="currentPage === 0">Previous</button>
        <button @click="nextPage">Next</button>
      </div>
    </div>

    <div class="search-container">
      <div class="search-section">
        <input v-model="contentId" placeholder="Enter content ID" />
        <button @click="fetchUserData">Fetch User Data</button>
      </div>
      <div v-if="userData">
        <p>Username: {{ userData.username }}</p>
        <p>User ID: {{ userData.id }}</p>
      </div>
    </div>

    <div class="search-container">
      <div class="search-section">
        <input v-model="albumId" placeholder="Enter album ID" />
        <button @click="fetchAlbumUserData">Fetch Album User Data</button>
      </div>
      <div v-if="albumUserData">
        <p>Username: {{ albumUserData.username }}</p>
        <p>User ID: {{ albumUserData.id }}</p>
      </div>
    </div>

    <div v-if="isEditPopupVisible" class="edit-popup">
      <div class="edit-popup-content">
        <h3>Edit User</h3>
        <input v-model="editedUsername" placeholder="Username" />
        <input v-model="editedNickname" placeholder="Nickname" />
        <input v-model="editedPassword" type="password" placeholder="Password" />
        <button @click="updateUser">Save</button>
        <button @click="isEditPopupVisible = false">Cancel</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
html, body {
  margin: 0;
  padding: 0;
  height: 100%; /* Full height */
  display: flex;
  justify-content: center; /* Center horizontally */
  align-items: center; /* Center vertically */
  background-color: #f4f4f4; /* Optional background color */
}

.container {
  width: 100%;
  max-width: 900px; /* Max width for the container */
  margin-top: 50%;
  max-height: 50%;
  flex-direction: column; /* Stack content vertically */
  align-items: center; /* Center horizontally */
  padding: 20px; /* Padding to prevent elements from touching edges */
  box-sizing: border-box; /* Include padding and borders in width/height calculation */
  vertical-align: middle;
  background-color: #2d2d2d;
}

.search-container {
  width: 100%;
  margin-bottom: 20px;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
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
</style>
