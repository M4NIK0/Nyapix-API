<script setup lang="ts">
import { ref, onMounted } from 'vue';

const themes = ref(['dark', 'pastel-pink', 'pastel-green', 'pastel-blue']);
const selectedTheme = ref('dark');

const createThemeLinkElement = () => {
  let themeLink = document.getElementById('theme-link') as HTMLLinkElement;
  if (!themeLink) {
    themeLink = document.createElement('link');
    themeLink.id = 'theme-link';
    themeLink.rel = 'stylesheet';
    document.head.appendChild(themeLink);
  }
  return themeLink;
};

const setTheme = (theme: string) => {
  const themeLink = createThemeLinkElement();
  themeLink.href = `/src/assets/styles/theme-${theme}.css`;
  selectedTheme.value = theme;
};

const handleThemeChange = (event: Event) => {
  const target = event.target as HTMLSelectElement;
  setTheme(target.value);
};

onMounted(() => {
  setTheme(selectedTheme.value);
});
</script>

<template>
  <div class="theme-dropdown">
    <label for="theme-select">Select Theme:</label>
    <select id="theme-select" v-model="selectedTheme" @change="handleThemeChange">
      <option v-for="theme in themes" :key="theme" :value="theme">{{ theme }}</option>
    </select>
  </div>
</template>

<style scoped>
.theme-dropdown {
  margin: 1rem;
}

label {
  margin-right: 0.5rem;
}

select {
  padding: 0.5rem;
}
</style>
