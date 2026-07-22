<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navItems = [
  { label: 'Accueil', icon: 'ti-home', route: '/' },
  { label: 'Mes documents', icon: 'ti-files', route: '/documents' },
  { label: 'Dépôts partagés', icon: 'ti-users', route: '/depots' },
  { label: 'Partages', icon: 'ti-share', route: '/shares' },
  { label: 'Hors ligne', icon: 'ti-wifi-off', route: '/offline' }
]

const isActive = (itemRoute) => route.path === itemRoute
const navigate = (itemRoute) => router.push(itemRoute)

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <aside class="sidebar">

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
      <div class="nav-item" @click="navigate('/settings')">
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
/* ============================================
   TAILLES — modifie uniquement ici
   ============================================ */
.sidebar {
  --font-logo:    22px;   /* Nom "Filsafe"         */
  --font-nav:     18px;   /* Items de navigation     */
  --font-badge:   18px;   /* Badge "3"               */
  --font-user:    20px;   /* Nom utilisateur bas      */
  --icon-nav:     20px;   /* Taille icônes navigation */
  --icon-logo:    20px;   /* Taille icône logo        */
}
/* ============================================ */

.sidebar {
  width: 220px;
  min-height: 100vh;
  background-color: var(--bg-primary);
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
  color: var(--bg-primary);
  font-size: var(--icon-logo);
}
.logo-name {
  font-size: var(--font-logo);
  font-weight: 500;
  color: var(--text-primary);
}

/* NAVIGATION */
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

/* BADGE */
.badge {
  margin-left: auto;
  background: var(--primary);
  color: var(--bg-primary);
  font-size: var(--font-badge);
  font-weight: 500;
  padding: 2px 7px;
  border-radius: 20px;
}

/* SÉPARATEUR */
.separator {
  height: 0.5px;
  background: var(--border-color);
  margin: 16px 0;
}

/* NAVIGATION SECONDAIRE */
.nav-secondary {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
</style>