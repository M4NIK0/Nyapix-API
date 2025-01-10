<script setup lang="ts">
import NavBar from "@/components/NavBar.vue";
import SearchBar from "@/components/search/SearchBar.vue";
import {ref} from "vue";
import SearchResult from "@/components/search/SearchResult.vue";

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
      <!-- Search Bar Section -->
      <div class="searchbar">
        <SearchBar @update:searchResults="updateSearchResults" />
      </div>

      <!-- Search Results Section -->
      <section class="content">
        <h1>Search Results</h1>
        <SearchResult :searchResults="searchResults" />
      </section>
    </main>
  </div>
</template>


<style>
/* Reset margins and padding for body and html */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box; /* Include padding/borders in size calculations */
}

/* General Layout */
.home-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw; /* Ensure full viewport width */
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Navbar */
.navbar {
  height: 60px;
  flex-shrink: 0;
  display: flex;
  padding: 0 20px;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column; /* Stack items vertically */
  width: 100%;
}

/* Search Bar */
.searchbar {
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  width: 100%; /* Ensure full width */
}

/* Search Results */
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  width: 100%; /* Ensure full width */
}

#app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

</style>
