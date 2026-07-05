import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/Auth/LoginView.vue'
import RegisterView from '../views/Auth/RegisterView.vue'
import TwoFAView from '../views/Auth/TwoFAView.vue'
import DocumentsView from '../views/DocumentsView.vue'
import SharesView from '../views/SharesView.vue'
import DepotsView from '../views/DepotsView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import SettingsView from '../views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // Auth
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/2fa', name: '2fa', component: TwoFAView },

    // App
    { path: '/', name: 'home', component: HomeView },
    { path: '/documents', name: 'documents', component: DocumentsView },
    { path: '/shares', name: 'shares', component: SharesView },
    { path: '/depots', name: 'depots', component: DepotsView },
    { path: '/notifications', name: 'notifications', component: NotificationsView },
    { path: '/settings', name: 'settings', component: SettingsView },

    // Redirect par défaut
    { path: '/:pathMatch(.*)*', redirect: '/login' }
  ]
})

export default router