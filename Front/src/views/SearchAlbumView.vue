<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import SearchBar from '@/components/album/AlbumSearchBar.vue';
import AddButton from "@/components/search/AddButton.vue";
import NavBar from "@/components/NavBar.vue";

const searchResults = ref<Array<{ id: number, title: string, description: string, source: number, tags: number[], characters: number[], authors: number[], is_private: boolean, url: string }>>([]);
const updateSearchResults = (results: any[]) => {
  searchResults.value = results;
};

</script>

<template>
  <div class="album-view">
    <header class="navbar">
      <NavBar />
    </header>

    <main class="main-content">
      <div class="searchbar">
        <SearchBar @update:searchResults="updateSearchResults" />
      </div>
    </main>
  </div>
</template>

<style scoped>
.album-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  margin: 0;
  padding: 0;
}

.navbar {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.main-content {
  display: flex;
  flex: 1;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.sidebar {
  flex: 0 0 20%;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}
</style>
