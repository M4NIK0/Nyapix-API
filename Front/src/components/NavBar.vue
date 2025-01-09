<template>
  <nav class="navbar">
    <div class="navbar-container">
      <router-link to="/" class="navbar-logo">Nyapix</router-link>
      <ul class="navbar-menu">
        <li class="navbar-item">
          <router-link to="/" class="navbar-link">Search</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/albums" class="navbar-link">Albums</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/tags" class="navbar-link">Tags</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/sources" class="navbar-link">Sources</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/profile" class="navbar-link">My Profile</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/admin" class="navbar-link">Admin</router-link>
        </li>
        <li class="navbar-item">
          <router-link to="/logout" class="navbar-link">Logout</router-link>
        </li>
      </ul>
      <ThemeDropdown />
    </div>
  </nav>
</template>

<script setup lang="ts">
import ThemeDropdown from './theme/ThemeDropdown.vue';
</script>

<style scoped>
.navbar {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  border-bottom: 2px solid var(--border-color);
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}

.navbar-logo {
  text-decoration: none;
  font-size: 1.5rem;
  color: var(--text-color);
}

.navbar-menu {
  list-style: none;
  display: flex;
  margin: 0;
  padding: 0;
}

.navbar-item {
  margin-left: 1rem;
}

.navbar-link {
  text-decoration: none;
  font-size: 1rem;
}

.navbar-link:hover {
  text-decoration: underline;
}
</style>
