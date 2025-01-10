<script setup lang="ts">
import {onMounted, ref} from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const username = ref('');
const password = ref('');
const passwordError = ref('');
const formError = ref('');
const apiLoginUrl = import.meta.env.VITE_BACKEND_URL + '/v1/login';

const login = async () => {
  passwordError.value = '';
  formError.value = '';

  const requestBody = {
    username: username.value,
    password: password.value,
  };

  try {
    const response = await fetch(apiLoginUrl, {
      method: 'POST',
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorData = await response.json();
      formError.value = errorData.message || 'Login failed';
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    console.log('Login successful:', data);

    // Set JWT token as a local storage item
    localStorage.setItem('token', data.access_token);

    // Redirect to home page
    await router.push('/');
  } catch (error) {
    console.error('Login failed:', error);
  }
};

onMounted(async () => {
  document.title = "Login"
});
</script>

<template>
  <div class="flex justify-center items-center h-[80vh]">
    <div class="max-w-sm mx-auto p-4">
      <h2 class="text-center text-white text-2xl">{{ 'Login' }}</h2>
      <form @submit.prevent="login" class="mt-8 mb-8">
        <p v-if="formError" class="text-red-500 text-sm">{{ formError }}</p>
        <div class="mb-4">
          <input type="text" id="email_login" v-model="username" placeholder="username" required class="w-full p-2 box-border text-black placeholder-neutral-950" />
        </div>
        <div class="mb-4">
          <input type="password" id="password_login" v-model="password" placeholder="password" required class="w-full p-2 box-border text-black placeholder-neutral-950" />
          <p v-if="passwordError" class="text-red-500 text-sm">{{ passwordError }}</p>
        </div>
        <button type="submit" id="submit_login" class="w-full p-2 text-black bg-green-300 rounded cursor-pointer">{{ 'Login' }}</button>
      </form>
      <div class="register-link">
        <p>Don't have an account yet? <router-link to="/register" class="text-white">Click here to get started</router-link></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-link, .register-link {
  margin-top: 1rem;
  text-align: center;
}

.flex {
  display: flex;
}

.justify-center {
  justify-content: center;
}

.items-center {
  align-items: center;
}

.login-link a, .register-link a {
  color: #fff;
}

.login-link a:hover, .register-link a:hover {
  text-decoration: underline;
}
</style>
