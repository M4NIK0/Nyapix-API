<script setup lang="ts">
import { ref, onMounted } from 'vue';
import ErrorPopup from './components/ErrorPopup.vue';

const errorMessage = ref<string | null>(null);

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  const error = urlParams.get('error');
  if (error) {
    errorMessage.value = error;
  }
});

const closePopup = () => {
  errorMessage.value = null;
};
</script>

<template>
  <router-view />
  <ErrorPopup v-if="errorMessage" :message="errorMessage" @close="closePopup" />
</template>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
