<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import NavBar from "@/components/NavBar.vue";

interface Tag {
  id: number;
  name: string;
}

interface Character {
  id: number;
  name: string;
}

interface Author {
  id: number;
  name: string;
}

const tags = ref<Tag[]>([]);
const characters = ref<Character[]>([]);
const authors = ref<Author[]>([]);
const currentPage = ref(1);
const pageSize = ref(10);
const searchQuery = ref('');
const totalPages = ref(1);
const API_BASE = import.meta.env.VITE_BACKEND_URL + '/v1';
const isEditTagPopupVisible = ref(false);
const isEditCharacterPopupVisible = ref(false);
const isEditAuthorPopupVisible = ref(false);
const tagToEdit = ref<Tag | null>(null);
const characterToEdit = ref<Character | null>(null);
const authorToEdit = ref<Author | null>(null);
const newTagName = ref('');
const newCharacterName = ref('');
const newAuthorName = ref('');

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const fetchTags = async () => {
  try {
    const response = await axios.get(`${API_BASE}/tags`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    tags.value = response.data.tags;
    totalPages.value = Math.max(totalPages.value, response.data.total_pages);
  } catch (error) {
    console.error('Error fetching tags:', error);
  }
};

const fetchCharacters = async () => {
  try {
    const response = await axios.get(`${API_BASE}/characters`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    characters.value = response.data.characters;
    totalPages.value = Math.max(totalPages.value, response.data.total_pages);
  } catch (error) {
    console.error('Error fetching characters:', error);
  }
};

const fetchAuthors = async () => {
  try {
    const response = await axios.get(`${API_BASE}/authors`, {
      headers: getAuthHeader(),
      params: { page: currentPage.value, size: pageSize.value }
    });
    authors.value = response.data.authors;
    totalPages.value = Math.max(totalPages.value, response.data.total_pages);
  } catch (error) {
    console.error('Error fetching authors:', error);
  }
};

const search = async () => {
  try {
    const [tagsResponse, charactersResponse, authorsResponse] = await Promise.all([
      axios.get(`${API_BASE}/tags/search`, {
        headers: getAuthHeader(),
        params: { tag_name: searchQuery.value, max_results: pageSize.value }
      }),
      axios.get(`${API_BASE}/characters/search`, {
        headers: getAuthHeader(),
        params: { character_name: searchQuery.value, max_results: pageSize.value }
      }),
      axios.get(`${API_BASE}/authors/search`, {
        headers: getAuthHeader(),
        params: { author_name: searchQuery.value, max_results: pageSize.value }
      })
    ]);
    tags.value = tagsResponse.data.tags;
    characters.value = charactersResponse.data.characters;
    authors.value = authorsResponse.data.authors;
  } catch (error) {
    console.error('Error searching:', error);
  }
};

const deleteTag = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/tags/${id}`, {
      headers: getAuthHeader()
    });
    fetchTags();
  } catch (error) {
    console.error('Error deleting tag:', error);
  }
};

const deleteCharacter = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/characters/${id}`, {
      headers: getAuthHeader()
    });
    fetchCharacters();
  } catch (error) {
    console.error('Error deleting character:', error);
  }
};

const deleteAuthor = async (id: number) => {
  try {
    await axios.delete(`${API_BASE}/authors/${id}`, {
      headers: getAuthHeader()
    });
    fetchAuthors();
  } catch (error) {
    console.error('Error deleting author:', error);
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
      fetchTags();
    } catch (error) {
      console.error('Error adding tag:', error);
    }
  }
};

const addCharacter = async () => {
  const charName = prompt('Enter the character name:');
  if (charName) {
    try {
      await axios.post(`${API_BASE}/characters`, null, {
        headers: getAuthHeader(),
        params: { character_name: charName }
      });
      fetchCharacters();
    } catch (error) {
      console.error('Error adding character:', error);
    }
  }
};

const addAuthor = async () => {
  const authName = prompt('Enter the author name:');
  if (authName) {
    try {
      await axios.post(`${API_BASE}/authors`, null, {
        headers: getAuthHeader(),
        params: { author_name: authName }
      });
      fetchAuthors();
    } catch (error) {
      console.error('Error adding author:', error);
    }
  }
};

const editTag = (tag: Tag) => {
  tagToEdit.value = tag;
  newTagName.value = tag.name;
  isEditTagPopupVisible.value = true;
};

const updateTag = async () => {
  if (tagToEdit.value && newTagName.value) {
    try {
      await axios.put(`${API_BASE}/tags/${tagToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { tag_name: newTagName.value }
      });
      fetchTags();
      isEditTagPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating tag:', error);
    }
  }
};

const editCharacter = (character: Character) => {
  characterToEdit.value = character;
  newCharacterName.value = character.name;
  isEditCharacterPopupVisible.value = true;
};

const updateCharacter = async () => {
  if (characterToEdit.value && newCharacterName.value) {
    try {
      await axios.put(`${API_BASE}/characters/${characterToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { character_name: newCharacterName.value }
      });
      fetchCharacters();
      isEditCharacterPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating character:', error);
    }
  }
};

const editAuthor = (author: Author) => {
  authorToEdit.value = author;
  newAuthorName.value = author.name;
  isEditAuthorPopupVisible.value = true;
};

const updateAuthor = async () => {
  if (authorToEdit.value && newAuthorName.value) {
    try {
      await axios.put(`${API_BASE}/authors/${authorToEdit.value.id}`, null, {
        headers: getAuthHeader(),
        params: { author_name: newAuthorName.value }
      });
      fetchAuthors();
      isEditAuthorPopupVisible.value = false;
    } catch (error) {
      console.error('Error updating author:', error);
    }
  }
};

const nextPage = async () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
    await fetchTags();
    await fetchCharacters();
    await fetchAuthors();
  }
};

const prevPage = async () => {
  if (currentPage.value > 1) {
    currentPage.value--;
    await fetchTags();
    await fetchCharacters();
    await fetchAuthors();
  }
};

onMounted(() => {
  fetchTags();
  fetchCharacters();
  fetchAuthors();
});
</script>

<template>
  <header>
    <NavBar />
  </header>
  <div class="center-container">
    <div>
      <div class="button-container">
        <button @click="addTag">Add Tag</button>
        <button @click="addCharacter">Add Character</button>
        <button @click="addAuthor">Add Author</button>
      </div>
      <input v-model="searchQuery" @input="search" placeholder="Search..." />
      <div>
        <h2>Tags</h2>
        <ul>
          <li v-for="tag in tags" :key="tag.id" class="list-item tag">
            {{ tag.name }}
            <div class="button-group">
              <button class="edit-button" @click="editTag(tag)">Edit</button>
              <button class="delete-button" @click="deleteTag(tag.id)">X</button>
            </div>
          </li>
        </ul>
      </div>
      <div>
        <h2>Characters</h2>
        <ul>
          <li v-for="character in characters" :key="character.id" class="list-item character">
            {{ character.name }}
            <div class="button-group">
              <button class="edit-button" @click="editCharacter(character)">Edit</button>
              <button class="delete-button" @click="deleteCharacter(character.id)">X</button>
            </div>
          </li>
        </ul>
      </div>
      <div>
        <h2>Authors</h2>
        <ul>
          <li v-for="author in authors" :key="author.id" class="list-item author">
            {{ author.name }}
            <div class="button-group">
              <button class="edit-button" @click="editAuthor(author)">Edit</button>
              <button class="delete-button" @click="deleteAuthor(author.id)">X</button>
            </div>
          </li>
        </ul>
      </div>
      <button class="page-button" @click="prevPage" :disabled="currentPage === 1">Previous</button>
      <button class="page-button" @click="nextPage" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>


<style scoped>
.character {
  color: green;
}

.author {
  color: #00a6ff;
}

.tag {
  color: #ff9100;
}

.delete-button {
  color: red;
  cursor: pointer;
}

.edit-button {
  cursor: pointer;
}

.page-button {
  margin-top: 20px;
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

.center-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; /* Full viewport height */
  padding: 20px; /* Optional: Add padding */
  box-sizing: border-box;
  background-color: #f5f5f5; /* Optional: Light background color */
}

.center-container > div {
  max-width: 800px; /* Set a maximum width for content */
  width: 100%; /* Allow it to shrink for smaller screens */
  background: white; /* Optional: White background for contrast */
  border-radius: 8px; /* Optional: Rounded corners */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: Add a shadow */
  padding: 20px;
}

</style>
