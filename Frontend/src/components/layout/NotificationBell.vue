<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()
const alertCount = ref(0)

const fetchAlerts = async () => {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const { data } = await api.get('/api/notifications/')
    alertCount.value = data.filter(n => !n.lue).length
  } catch (err) {
    console.error('Erreur récupération notifications', err)
  }
}

onMounted(() => {
  fetchAlerts()
  // Rafraîchir toutes les 30 secondes
  setInterval(fetchAlerts, 30000)
})

const goToNotifications = () => {
  router.push('/notifications')
}

</script>

<template>
  <div class="notification-bell" @click="goToNotifications">
    <i class="ti ti-bell"></i>
    <span v-if="alertCount > 0" class="badge">{{ alertCount }}</span>
  </div>
</template>

<style scoped>
.notification-bell {
  position: relative;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-card);
  color: var(--text-primary);
  transition: background-color 0.2s;
}

.notification-bell:hover {
  background-color: var(--border-color);
}

.notification-bell i {
  font-size: 24px;
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background-color: var(--danger);
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
</style>