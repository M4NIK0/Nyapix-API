<script setup lang="ts">
import TagManager from '@/components/tags/TagManager.vue';
import AuthorManager from '@/components/tags/AuthorManager.vue';
import CharacterManager from "@/components/tags/CharacterManager.vue";
import NavBar from "@/components/NavBar.vue";
</script>

<template>
  <header class="navbar">
    <NavBar />
  </header>
  <div class="main-container">
    <div class="manager-wrapper">
      <TagManager />
    </div>
    <div class="manager-wrapper">
      <AuthorManager />
    </div>
    <div class="manager-wrapper">
      <CharacterManager />
    </div>
  </div>
</template>

<style scoped>
.navbar {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.main-container {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: stretch;
  width: 100%;
  padding: 20px;
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0%);
  margin-top: 80px;
}

.manager-wrapper {
  flex-grow: 1; /* Ensure each manager takes up equal space */
  margin: 0 10px; /* Add margin between managers */
  display: flex;
  justify-content: center;
}
</style>
