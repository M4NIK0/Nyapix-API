<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import NavBar from '@/components/NavBar.vue';

interface User {
  id: number;
  username: string;
  nickname: string;
  type: number;
  tags: number;
  creators: number;
  characters: number;
  favorites: number;
  content: number;
  albums: number;
  creation_date: string;
}

const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const user = ref<User | null>(null);
const isEditProfilePopupVisible = ref(false);
const editedUsername = ref('');
const editedNickname = ref('');
const editedPassword = ref('');
const router = useRouter();

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
  } catch (error: any) {
    console.log(`Error fetching user data: ${error.response?.data?.message || error.message}`);
  }
};

const updateUserProfile = async () => {
  if (user.value) {
    const updatedFields: { [key: string]: string } = {};
    if (editedUsername.value !== user.value.username) {
      updatedFields.username = editedUsername.value;
    }
    if (editedNickname.value !== user.value.nickname) {
      updatedFields.nickname = editedNickname.value;
    }
    if (editedPassword.value) {
      updatedFields.password = editedPassword.value;
    }

    if (Object.keys(updatedFields).length > 0) {
      try {
        await axios.put(`${API_BASE}/users/me`, updatedFields, {
          headers: {
            ...getAuthHeader(),
            'Content-Type': 'application/json',
          },
        });
        await fetchUserData();
        isEditProfilePopupVisible.value = false;
        router.push('/logout');
      } catch (error: any) {
        alert(`Error updating user profile: ${error.response?.data?.message || error.message}`);
      }
    } else {
      alert('No changes detected.');
    }
  }
};

const openEditProfilePopup = () => {
  if (user.value) {
    editedUsername.value = user.value.username;
    editedNickname.value = user.value.nickname;
    editedPassword.value = '';
    isEditProfilePopupVisible.value = true;
  }
};

const deleteUserAccount = async () => {
  if (confirm('Are you sure you want to delete your account?') &&
    confirm('This action is irreversible. Do you really want to delete your account?') &&
    confirm('Please confirm one last time: Do you want to delete your account?')) {
    try {
      await axios.delete(`${API_BASE}/users/me`, {
        headers: getAuthHeader(),
      });
      alert('Your account has been deleted.');
      router.push('/logout');
    } catch (error: any) {
      alert(`Error deleting account: ${error.response?.data?.message || error.message}`);
    }
  }
};

onMounted(() => {
  fetchUserData();
});
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div v-if="user" class="profile-container">
    <h1>{{ user.username }}</h1>
    <p>Nickname: {{ user.nickname }}</p>
    <p>Type: {{ user.type }}</p>
    <p>Tags: {{ user.tags }}</p>
    <p>Creators: {{ user.creators }}</p>
    <p>Characters: {{ user.characters }}</p>
    <p>Favorites: {{ user.favorites }}</p>
    <p>Content: {{ user.content }}</p>
    <p>Albums: {{ user.albums }}</p>
    <p>Creation Date: {{ new Date(user.creation_date).toLocaleString() }}</p>
    <button @click="openEditProfilePopup">Edit Profile</button>
    <button @click="deleteUserAccount">Delete Account</button>
  </div>
  <div v-else>
    <p>Loading...</p>
  </div>

  <div v-if="isEditProfilePopupVisible" class="edit-popup">
    <div class="edit-popup-content">
      <h3>Edit Profile</h3>
      <input v-model="editedUsername" placeholder="Username" />
      <input v-model="editedNickname" placeholder="Nickname" />
      <input v-model="editedPassword" type="password" placeholder="Password" />
      <button @click="updateUserProfile">Save</button>
      <button @click="isEditProfilePopupVisible = false">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
/* Ensure the whole page takes full height */
body, html {
  height: 100%;
  margin: 0;
}

.profile-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Make the profile container take the full height of the viewport */
}

.profile-container h1, .profile-container p, .profile-container button {
  margin: 5px 0;
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
