import { createRouter, createWebHistory } from 'vue-router';
import LoginForm from '@/components/login/LoginForm.vue';
import LogoutComponent from "@/components/logout/LogoutComponent.vue";
import HomeView from '@/views/HomeView.vue';
import ContentView from '@/views/ContentView.vue';
import TagView from '@/views/TagView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/content/:id',
      name: 'ContentView',
      component: ContentView,
      props: route => ({ id: Number(route.params.id) }),
    },
    {
      path: '/tags',
      name: 'tags',
      component: TagView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
    },
    {
      path: '/logout',
      name: 'logout',
      component: LogoutComponent
    },
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!token && to.name !== 'login' && to.name !== 'register') {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
