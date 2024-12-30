<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const nickname = ref('');
const password = ref('');
const passwordError = ref('');
const formError = ref('');
const apiRegisterUrl = import.meta.env.VITE_BACKEND_URL + '/v1/register';

const register = async () => {
  passwordError.value = '';
  formError.value = '';

  const requestBody = {
    username: username.value,
    nickname: nickname.value,
    password: password.value,
  };

  try {
    const response = await fetch(apiRegisterUrl, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (response.status === 200) {
      await router.push('/login');
    } else {
      const errorData = await response.json();
      formError.value = errorData.message || 'Registration failed';
    }
  } catch (error) {
    console.error('Registration failed:', error);
    formError.value = error.message || 'Registration failed';
  }
};

onMounted(async () => {
  document.title = "Register"
});
</script>

<template>
  <div class="flex justify-center items-center h-[80vh]">
    <div class="max-w-sm mx-auto p-4">
      <h2 class="text-center text-white text-2xl">{{ 'Register' }}</h2>
      <form @submit.prevent="register" class="mt-8 mb-8">
        <p v-if="formError" class="text-red-500 text-sm">{{ formError }}</p>
        <div class="mb-4">
          <input type="text" id="username_register" v-model="username" placeholder="username" required class="w-full p-2 box-border text-black placeholder-neutral-950" />
        </div>
        <div class="mb-4">
          <input type="text" id="nickname_register" v-model="nickname" placeholder="nickname" required class="w-full p-2 box-border text-black placeholder-neutral-950" />
        </div>
        <div class="mb-4">
          <input type="password" id="password_register" v-model="password" placeholder="password" required class="w-full p-2 box-border text-black placeholder-neutral-950" />
          <p v-if="passwordError" class="text-red-500 text-sm">{{ passwordError }}</p>
        </div>
        <button type="submit" id="submit_register" class="w-full p-2 text-black bg-green-300 rounded cursor-pointer">{{ 'Register' }}</button>
      </form>
      <div class="login-link">
        <p>Already have an account? <router-link to="/login" class="text-white">Click here to login</router-link></p>
      </div>
    </div>
  </div>
</template>
