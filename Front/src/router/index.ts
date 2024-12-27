import { createRouter, createWebHistory } from 'vue-router'
import LoginForm from '@/components/login/LoginForm.vue'
import HomeView from './HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
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
