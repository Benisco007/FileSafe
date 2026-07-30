import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/Auth/LoginView.vue'
import RegisterView from '../views/Auth/RegisterView.vue'
import TwoFAView from '../views/Auth/TwoFAView.vue'
import TwoFALoginView from '../views/Auth/TwoFALoginView.vue'
import ShareAccessView from '../views/ShareAccessView.vue'
import DocumentsView from '../views/DocumentsView.vue'
import SharesView from '../views/SharesView.vue'
import DepotsView from '../views/DepotsView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import SettingsView from '../views/SettingsView.vue'
import AdminView from '../views/AdminView.vue'
import OfflineView from '../views/OfflineView.vue'
import AIView from '../views/AIView.vue'
import ForgotPasswordView from '../views/Auth/ForgotPasswordView.vue'
import ResetPasswordView from '../views/Auth/ResetPasswordView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Public Share Access (No Auth)
    { path: '/share/:token', name: 'share-access', component: ShareAccessView },

    // Auth
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/2fa', name: '2fa', component: TwoFAView },
    { path: '/2fa-login', name: '2fa-login', component: TwoFALoginView },

    // App
    { path: '/', name: 'home', component: HomeView, meta: { requiresAuth: true } },
    { path: '/documents', name: 'documents', component: DocumentsView, meta: { requiresAuth: true } },
    { path: '/shares', name: 'shares', component: SharesView, meta: { requiresAuth: true } },
    { path: '/depots', name: 'depots', component: DepotsView, meta: { requiresAuth: true } },
    { path: '/offline', name: 'offline', component: OfflineView, meta: { requiresAuth: true } },
    { path: '/notifications', name: 'notifications', component: NotificationsView, meta: { requiresAuth: true } },
    { path: '/settings', name: 'settings', component: SettingsView, meta: { requiresAuth: true } },
    { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } },

    { path: '/ai', name: 'ai', component: AIView, meta: { requiresAuth: true } },
    // Redirect par défaut
    { path: '/:pathMatch(.*)*', redirect: '/login' },
    { path: '/forgot-password', name: 'forgot-password', component: ForgotPasswordView },
    { path: '/reset-password', name: 'reset-password', component: ResetPasswordView },
  ]
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  // Routes publiques : pas de vérification d'auth
  const publicRoutes = ['share-access', 'login', 'register', '2fa', '2fa-login', 'forgot-password', 'reset-password']
  if (publicRoutes.includes(to.name)) return

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/login'
  }

  // Redirection automatique des admins vers /admin s'ils tentent d'accéder à la racine '/'
  if (authStore.user?.role === 'admin' && to.path === '/') {
    return '/admin'
  }

  if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
    return '/'
  }
})

export default router