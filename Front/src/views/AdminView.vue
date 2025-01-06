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
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div>
    <input v-model="searchQuery" placeholder="Search users..." />
    <button @click="searchUsers">Search</button>
    <ul>
      <li v-for="user in searchResults" :key="user.id">
        {{ user.username }}
        <button @click="editUser(user.id)">Edit</button>
        <button @click="deleteUser(user.id)" style="color: red;">X</button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
input {
  margin-right: 10px;
  padding: 5px;
}

button {
  padding: 5px 10px;
}

ul {
  margin-top: 20px;
  list-style-type: none;
  padding: 0;
}

li {
  margin-bottom: 10px;
}
</style>
