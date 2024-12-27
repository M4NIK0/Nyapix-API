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

