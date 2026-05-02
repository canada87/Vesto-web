import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/',
      name: 'wardrobe',
      component: () => import('@/views/WardrobeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/today',
      name: 'today',
      component: () => import('@/views/TodayView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/discovery',
      name: 'discovery',
      component: () => import('@/views/DiscoveryView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/history',
      name: 'history',
      component: () => import('@/views/HistoryView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/trips',
      name: 'trips',
      component: () => import('@/views/TripView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/UsersView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.token) {
    return '/login'
  }

  if (to.meta.requiresAuth && auth.token && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAdmin && auth.user?.role !== 'admin') {
    return '/'
  }

  if (to.path === '/login' && auth.token) {
    return '/'
  }
})

export default router
