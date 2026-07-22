<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const notifications = ref([])
const isLoading = ref(true)
const activeFilter = ref('Toutes')

const filters = ['Toutes', 'Alertes expiration', 'Accès extérieurs']

const fetchNotifications = async () => {
  try {
    isLoading.value = true
    const { data } = await api.get('/api/notifications/')
    notifications.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des notifications', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchNotifications()
})

const getTitreAlerte = (message) => {
  if (message.toLowerCase().includes('expire')) return 'Expiration proche'
  if (message.toLowerCase().includes('accès')) return 'Nouvel accès'
  return 'Alerte'
}

const getTypeAlerte = (message) => {
  if (message.toLowerCase().includes('expire')) return 'Alertes expiration'
  if (message.toLowerCase().includes('accès')) return 'Accès extérieurs'
  return 'Toutes'
}

const getIcon = (type) => {
  if (type === 'Alertes expiration') return 'ti-alert-triangle text-warning'
  if (type === 'Accès extérieurs') return 'ti-shield-check text-success'
  return 'ti-bell text-primary'
}

const formatRelativeTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return 'À l\'instant'
  if (diffMins < 60) return `Il y a ${diffMins} min`
  if (diffHours < 24) return `Il y a ${diffHours}h`
  if (diffDays === 1) return 'Hier'
  return `Il y a ${diffDays} jours`
}

const filteredNotifications = computed(() => {
  if (activeFilter.value === 'Toutes') return notifications.value
  return notifications.value.filter(n => n.type === activeFilter.value)
})

const markAllAsRead = async () => {
  try {
    await api.patch('/api/notifications/marquer-lues')
    notifications.value.forEach(n => n.lue = true)
  } catch (err) {
    console.error('Erreur lors du marquage des notifications', err)
  }
}
</script>

<template>
  <div class="notifications-view">
    <div class="page-header">
      <h1>Notifications</h1>
      <button class="btn-outline" @click="markAllAsRead" v-if="notifications.length > 0">
        <i class="ti ti-check-all"></i> Tout marquer comme lu
      </button>
    </div>

    <div class="filters-bar">
      <div class="pills-container">
        <button 
          v-for="filter in filters" 
          :key="filter"
          :class="['pill', { active: activeFilter === filter }]"
          @click="activeFilter = filter"
        >
          {{ filter }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="skeleton-list">
      <div class="skeleton-item" v-for="i in 4" :key="i"></div>
    </div>

    <div v-else-if="filteredNotifications.length === 0" class="empty-state">
      <i class="ti ti-bell-off"></i>
      <h2>Aucune notification</h2>
      <p>Vous êtes à jour !</p>
    </div>

    <div v-else class="notifications-list">
      <div 
        v-for="notif in filteredNotifications" 
        :key="notif.id" 
        :class="['notif-card', { unread: !notif.lue }]"
        @click="notif.lue = true"
      >
        <div class="notif-icon">
          <i :class="['ti', getIcon(notif.type)]"></i>
        </div>
        <div class="notif-content">
          <div class="notif-header">
            <h3>{{ notif.titre }}</h3>
            <span class="notif-time">{{ formatRelativeTime(notif.horodatage) }}</span>
          </div>
          <p class="notif-desc">{{ notif.description }}</p>
        </div>
        <div class="unread-dot" v-if="!notif.lue"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-outline:hover {
  background-color: var(--bg-card);
  border-color: var(--text-muted);
}

/* Filtres */
.filters-bar {
  display: flex;
  background-color: var(--bg-card);
  padding: 16px;
  border-radius: 12px;
}

.pills-container {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pill {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: #aaa;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.pill:hover {
  border-color: var(--text-muted);
  color: var(--text-primary);
}

.pill.active {
  background-color: rgba(244, 180, 0, 0.15);
  border-color: var(--primary);
  color: var(--primary);
}

/* Liste Notifications */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notif-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background-color: var(--bg-card);
  padding: 20px;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s;
}

.notif-card:hover {
  background-color: #242424;
  transform: translateY(-2px);
}

.notif-card.unread {
  background-color: rgba(244, 180, 0, 0.05);
  border: 1px solid rgba(244, 180, 0, 0.2);
}

.notif-icon {
  width: 48px;
  height: 48px;
  background-color: var(--bg-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.text-primary { color: var(--primary); }
.text-warning { color: #F59E0B; }
.text-success { color: #10B981; }

.notif-content {
  flex: 1;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.notif-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.notif-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.notif-desc {
  font-size: 14px;
  color: #aaa;
  margin: 0;
  line-height: 1.4;
}

.unread-dot {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 10px;
  height: 10px;
  background-color: var(--primary);
  border-radius: 50%;
}

/* Skeletons & Empty States */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 90px;
  background-color: var(--bg-card);
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: var(--text-secondary);
  background-color: var(--bg-card);
  border-radius: 18px;
}

.empty-state i {
  font-size: 64px;
  color: var(--input-border);
  margin-bottom: 16px;
}

.empty-state h2 {
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  margin-bottom: 0;
}
</style>
