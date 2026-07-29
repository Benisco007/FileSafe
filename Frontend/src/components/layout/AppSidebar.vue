<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const props = defineProps({
  isOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isAdmin = authStore.user?.role === 'admin'

const navItems = isAdmin ? [
  { label: 'Administration', icon: 'ti-shield', route: '/admin' }
] : [
  { label: 'Accueil', icon: 'ti-home', route: '/' },
  { label: 'Mes documents', icon: 'ti-files', route: '/documents' },
  { label: 'Dépôts partagés', icon: 'ti-users', route: '/depots' },
  { label: 'Partages', icon: 'ti-share', route: '/shares' },
  { label: 'Hors ligne', icon: 'ti-wifi-off', route: '/offline' },
  { label: 'Assistant IA', icon: 'ti-sparkles', route: '/ai' },
]

const isActive = (itemRoute) => route.path === itemRoute
const navigate = (itemRoute) => {
  router.push(itemRoute)
  emit('close')
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <aside :class="['sidebar', { open: isOpen }]">

    <!-- LOGO -->
    <div class="logo">
      <div class="logo-icon">
        <i class="ti ti-lock"></i>
      </div>
      <span class="logo-name">FileSafe</span>
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

    <!-- BAS DE SIDEBAR -->
    <div class="sidebar-bottom">
      <div class="nav-item" @click="navigate('/settings')" v-if="!isAdmin">
        <i class="ti ti-settings"></i>
        <span>Paramètres</span>
      </div>
      <div class="user-row">
        <div class="avatar">{{ authStore.user?.prenom?.[0]?.toUpperCase() || 'U' }}</div>
        <span class="user-name">{{ authStore.user?.nom || 'Utilisateur' }}</span>
        <i class="ti ti-logout logout-icon" @click="handleLogout" title="Se déconnecter"></i>
      </div>
    </div>

  </aside>
</template>

<style scoped>
.sidebar {
  --font-logo:    22px;
  --font-nav:     18px;
  --font-badge:   18px;
  --font-user:    20px;
  --icon-nav:     20px;
  --icon-logo:    20px;
}

.sidebar {
  width: 220px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background-color: var(--bg-primary);
  border-right: 0.5px solid var(--border-color);
  display: flex;
  flex-direction: column;
  padding: 20px 12px;
  flex-shrink: 0;
  overflow-y: auto;
  z-index: 1000;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
  color: var(--bg-primary);
  font-size: var(--icon-logo);
}
.logo-name {
  font-size: var(--font-logo);
  font-weight: 500;
  color: var(--text-primary);
}

.nav-main {
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
  min-height: 44px;
}
.nav-item:hover {
  background: var(--bg-card);
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

.badge {
  margin-left: auto;
  background: var(--primary);
  color: var(--bg-primary);
  font-size: var(--font-badge);
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 20px;
}

.separator {
  height: 0.5px;
  background: var(--border-color);
  margin: 16px 0;
}

.nav-secondary {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

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
  color: var(--bg-primary);
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
  color: #aaa;
  flex: 1;
}
.logout-icon {
  font-size: 16px;
  color: var(--text-muted);
  cursor: pointer;
}
.logout-icon:hover {
  color: var(--danger);
}

/* Mobile: hidden by default, slides in when open */
@media (max-width: 767px) {
  .sidebar {
    transform: translateX(-100%);
    box-shadow: none;
  }

  .sidebar.open {
    transform: translateX(0);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4);
  }
}
</style>