<script setup lang="ts">
import NavBar from "@/components/NavBar.vue";
import SearchBar from "@/components/search/SearchBar.vue";
import {ref} from "vue";

const searchResults = ref<Array<{ id: number, title: string, description: string, source: number, tags: number[], characters: number[], authors: number[], is_private: boolean, url: string }>>([]);
const updateSearchResults = (results: any[]) => {
  searchResults.value = results;
};
</script>

<template>
  <div class="home-view">
    <!-- Navbar -->
    <header class="navbar">
      <NavBar />
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <aside class="sidebar">
        <div class="searchbar">
          <SearchBar @update:searchResults="updateSearchResults" />
        </div>
      </aside>
      <section class="content">
        <h1>Search Results</h1>
        <ul>
          <li v-for="result in searchResults" :key="result.id" class="result-item">
            <h2>{{ result.title }}</h2>
            <p><strong>Description:</strong> {{ result.description }}</p>
            <p><strong>Source:</strong> {{ result.source }}</p>
            <p><strong>Tags:</strong> {{ result.tags.join(', ') }}</p>
            <p><strong>Characters:</strong> {{ result.characters.join(', ') }}</p>
            <p><strong>Authors:</strong> {{ result.authors.join(', ') }}</p>
            <p><strong>Private:</strong> {{ result.is_private ? 'Yes' : 'No' }}</p>
            <a :href="result.url" target="_blank">View Content</a>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>

<style>
/* Ensure the container spans the full viewport */
.home-view {
  display: flex;
  flex-direction: column;
  height: 100vh; /* Full viewport height */
  width: 100%;  /* Full viewport width */
  margin: 0;    /* Ensure no spacing issues */
  padding: 0;
}

/* Navbar at the top */
.navbar {
  height: 60px; /* Set fixed height for the navbar */
  flex-shrink: 0; /* Prevents shrinking */
  display: flex;
  padding: 0 20px; /* Optional padding for content inside the navbar */
}

/* Main content area */
.main-content {
  display: flex;
  flex: 1; /* Takes up remaining space below the navbar */
  width: 100%;
  height: 100%;
  overflow: hidden; /* Prevents overflow issues */
}

/* Sidebar styling */
.sidebar {
  flex: 0 0 20%;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1); /* Optional shadow */
  overflow-y: auto; /* Enable vertical scroll if needed */
}

/* Content styling */
.content {
  flex: 1;
  padding: 10px;
  overflow-y: auto;
}
</style>
