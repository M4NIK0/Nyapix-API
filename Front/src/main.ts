import './assets/main.css'
import './assets/styles/theme-dark.css';

import { createApp } from 'vue'
import App from './App.vue'
import router from './router';

const app = createApp(App)

app.config.globalProperties.$setTheme = (theme: string) => {
  const themeLink = document.getElementById('theme-link') as HTMLLinkElement;
  themeLink.href = `./assets/styles/theme-${theme}.css`;
};

app.use(router)
  .use(router)
  .mount('#app');
