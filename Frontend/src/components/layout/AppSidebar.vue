<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Récupérer le nom de l'utilisateur connecté depuis le localStorage.
// Reste vide tant qu'aucune donnée réelle n'est disponible (pas de valeur
// factice) : la vraie valeur viendra de la base de données / du backend.
const user = JSON.parse(localStorage.getItem('user') || '{}')
const userName = ref(user.name || '')

// TODO backend : remplacer par le compteur réel de notifications non lues
const unreadNotifications = ref(0)

const navItems = [
  { label: 'Accueil', icon: 'ti-home', route: '/' },
  { label: 'Mes documents', icon: 'ti-files', route: '/documents' },
  { label: 'Dépôts partagés', icon: 'ti-users', route: '/depots' },
  { label: 'Partages', icon: 'ti-share', route: '/shares' }
]

const secondaryItems = [
  { label: 'Hors ligne', icon: 'ti-wifi-off', route: '/hors-ligne' },
  { label: 'Notifications', icon: 'ti-bell', route: '/notifications' }
]

const isActive = (itemRoute) => route.path === itemRoute
const navigate = (itemRoute) => router.push(itemRoute)

const logout = () => {
  localStorage.removeItem('user')
  router.push('/login')
  window.location.reload()
}
</script>

<template>
  <aside class="sidebar">
    <!-- LOGO -->
    <div class="logo">
      <div class="logo-icon">
        <i class="ti ti-lock"></i>
      </div>
      <span class="logo-name">CoffreDoc</span>
    </div>

    <!-- NAVIGATION PRINCIPALE -->
    <nav class="nav-main">
      <div
        v-for="item in navItems"
        :key="item.route"
        :class="['nav-item', isActive(item.route) ? 'active' : '']"
        @click="navigate(item.route)"
      >
        <i :class="['ti', item.icon]"></i>
        <span>{{ item.label }}</span>
      </div>
    </nav>

    <!-- SÉPARATEUR -->
    <div class="separator"></div>

    <!-- NAVIGATION SECONDAIRE -->
    <nav class="nav-secondary">
      <div
        v-for="item in secondaryItems"
        :key="item.route"
        :class="['nav-item', isActive(item.route) ? 'active' : '']"
        @click="navigate(item.route)"
      >
        <i :class="['ti', item.icon]"></i>
        <span>{{ item.label }}</span>
        <span v-if="item.route === '/notifications' && unreadNotifications > 0" class="nav-badge">
          {{ unreadNotifications }}
        </span>
      </div>
    </nav>

    <!-- BAS DE SIDEBAR -->
    <div class="sidebar-bottom">
      <div
        :class="['nav-item', isActive('/settings') ? 'active' : '']"
        @click="navigate('/settings')"
      >
        <i class="ti ti-settings"></i>
        <span>Paramètres</span>
      </div>
      <div class="user-row">
        <div class="avatar">{{ userName ? userName.charAt(0).toUpperCase() : '' }}</div>
        <span class="user-name">{{ userName }}</span>
        <i class="ti ti-logout logout-icon" title="Déconnexion" @click="logout"></i>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ============================================
   TAILLES — modifie uniquement ici
   ============================================ */
.sidebar {
  --font-logo:    22px;
  --font-nav:     20px;
  --font-user:    20px;
  --icon-nav:     20px;
  --icon-logo:    20px;
}
/* ============================================ */

.sidebar {
  width: 220px;
  min-height: 100vh;
  background-color: var(--bg-secondary);
  border-right: 0.5px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  margin-bottom: 28px;
}
.logo-icon {
  width: 34px;
  height: 34px;
  background: var(--primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #121212;
  font-size: var(--icon-logo);
}
.logo-name {
  font-size: var(--font-logo);
  font-weight: 500;
  color: var(--text-primary);
}

/* NAVIGATION */
.nav-main,
.nav-secondary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: var(--font-nav);
  transition: all 0.2s;
  position: relative;
}
.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.nav-item.active {
  background: rgba(244, 180, 0, 0.12);
  color: var(--primary);
  border-left: 3px solid var(--primary);
}
.nav-item i {
  font-size: var(--icon-nav);
  flex-shrink: 0;
}

.nav-badge {
  margin-left: auto;
  background: var(--primary);
  color: #121212;
  font-size: 11px;
  font-weight: 600;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* SÉPARATEUR */
.separator {
  height: 0.5px;
  background: var(--border-color);
  margin: 16px 0;
}

/* BAS DE SIDEBAR */
.sidebar-bottom {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.user-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 4px;
}
.avatar {
  width: 28px;
  height: 28px;
  background: var(--primary);
  color: #121212;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}
.user-name {
  font-size: var(--font-user);
  color: var(--text-secondary);
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.logout-icon {
  font-size: 16px;
  color: var(--text-secondary);
  cursor: pointer;
}
.logout-icon:hover {
  color: #EF4444;
}
</style>
