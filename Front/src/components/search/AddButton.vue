<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const isPopupVisible = ref(false);
const title = ref('');
const description = ref('');
const sourceId = ref(0);
const tags = ref('');
const characters = ref('');
const authors = ref('');
const isPrivate = ref(false);
const selectedFile = ref<File | null>(null);

const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const openPopup = () => {
  isPopupVisible.value = true;
};

const closePopup = () => {
  isPopupVisible.value = false;
};

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  }
};

const getOrCreateId = async (name: string, type: 'tags' | 'characters' | 'authors') => {
  try {
    const searchResponse = await axios.get(`http://localhost:5000/v1/${type}/search`, {
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
        const createResponse = await axios.post(`http://localhost:5000/v1/${type}`, null, {
          headers: getAuthHeader(),
          params: {
            [`${type.slice(0, -1)}_name`]: name,
          },
        });
        return createResponse.data.id;
      } catch (createError) {
        if (createError.response && createError.response.status === 409) {
          const retrySearchResponse = await axios.get(`http://localhost:5000/v1/${type}/search`, {
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

const submitForm = async () => {
  if (!selectedFile.value) {
    alert('Please select a file.');
    return;
  }

  try {
    const tagIds = await Promise.all(tags.value.split(',').map(tag => getOrCreateId(tag.trim(), 'tags')));
    const characterIds = await Promise.all(characters.value.split(',').map(character => getOrCreateId(character.trim(), 'characters')));
    const authorIds = await Promise.all(authors.value.split(',').map(author => getOrCreateId(author.trim(), 'authors')));

    const formData = new FormData();
    formData.append('content', JSON.stringify({
      title: title.value,
      description: description.value,
      source_id: sourceId.value,
      tags: tagIds,
      characters: characterIds,
      authors: authorIds,
      is_private: isPrivate.value,
    }));
    formData.append('file', selectedFile.value);

    // Log FormData entries
    for (let pair of formData.entries()) {
      console.log(pair[0] + ': ' + pair[1]);
    }

    await axios.post('http://localhost:5000/v1/content', formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      },
    });
    alert('Content added successfully!');
    closePopup();
  } catch (error) {
    console.error('Error adding content:', error);
    alert('Error adding content.');
  }
};
</script>

<template>
  <button @click="openPopup" class="theme-button">Add Content</button>

  <div v-if="isPopupVisible" class="popup">
    <div class="popup-content">
      <h3>Add Content</h3>
      <input v-model="title" placeholder="Title" />
      <input v-model="description" placeholder="Description" />
      <input v-model="sourceId" type="number" placeholder="Source ID" />
      <input v-model="tags" placeholder="Tags (comma separated names)" />
      <input v-model="characters" placeholder="Characters (comma separated names)" />
      <input v-model="authors" placeholder="Authors (comma separated names)" />
      <label>
        <input type="checkbox" v-model="isPrivate" />
        Private
      </label>
      <input type="file" @change="handleFileChange" />
      <button @click="submitForm" class="theme-button">Submit</button>
      <button @click="closePopup" class="theme-button">Cancel</button>
    </div>
  </div>
</template>

<style scoped>
.theme-button {
  padding: 10px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.popup {
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

.popup-content {
  background: grey;
  padding: 20px;
  border-radius: 4px;
  text-align: center;
}

.popup-content input {
  margin-bottom: 10px;
  padding: 5px;
  width: 100%;
  box-sizing: border-box;
  color: black;
}
</style>
