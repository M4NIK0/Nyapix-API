import { createRouter, createWebHistory } from 'vue-router';
import LoginForm from '@/components/login/LoginForm.vue';
import LogoutComponent from "@/components/logout/LogoutComponent.vue";
import HomeView from '@/views/HomeView.vue';
import AlbumView from '@/views/AlbumView.vue';
import ContentView from '@/views/ContentView.vue';
import NewContentView from "@/views/NewContentView.vue";
import SearchAlbumView from '@/views/SearchAlbumView.vue';
import TagView from '@/views/TagView.vue';
import RegisterForm from "@/components/register/RegisterForm.vue";
import SourceView from "@/views/SourceView.vue";
import ProfileView from "@/views/ProfileView.vue";
import AdminView from "@/views/AdminView.vue";

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
      path: '/new/content',
      name: 'NewContentView',
      component: NewContentView,
    },
    {
      path: '/album/:id',
      name: 'AlbumView',
      component: AlbumView,
      props: route => ({ id: Number(route.params.id) }),
    },
    {
      path: '/albums',
      name: 'albums',
      component: SearchAlbumView,
    },
    {
      path: '/tags',
      name: 'tags',
      component: TagView,
    },
    {
      path: '/sources',
      name: 'sources',
      component: SourceView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginForm
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterForm
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
