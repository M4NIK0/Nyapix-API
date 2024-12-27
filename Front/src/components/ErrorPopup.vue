<script setup lang="ts">
import { defineProps, defineEmits, ref } from 'vue';

const props = defineProps<{
  message: string;
}>();

const emit = defineEmits(['close']);
const overlayRef = ref<HTMLElement | null>(null);

const handleOverlayClick = (event: MouseEvent) => {
  if (event.target === overlayRef.value) {
    emit('close');
  }
};
</script>

<template>
  <div ref="overlayRef" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50" @click="handleOverlayClick">
    <div class="bg-red-500 text-white p-6 rounded-lg shadow-lg relative">
      <button @click="emit('close')" class="absolute top-2 right-2 text-white">X</button>
      <p>{{ message }}</p>
    </div>
  </div>
</template>
