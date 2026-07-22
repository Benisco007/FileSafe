<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'

const users = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const activeFilter = ref('Tous')
const currentPage = ref(1)
const itemsPerPage = 10

const filters = ['Tous', 'Actifs', 'Bloqués']

const stats = computed(() => {
  return {
    total: users.value.length,
    actifs: users.value.filter(u => !u.is_blocked).length,
    bloques: users.value.filter(u => u.is_blocked).length,
    admins: users.value.filter(u => u.role === 'admin').length
  }
})

const fetchUsers = async () => {
  try {
    isLoading.value = true
    const { data } = await api.get('/api/admin/utilisateurs')
    users.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des utilisateurs', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})

const toggleBlockUser = async (user) => {
  try {
    const action = user.is_blocked ? 'debloquer' : 'bloquer'
    await api.patch(`/api/admin/utilisateurs/${user.id_user}/${action}`)
    user.is_blocked = !user.is_blocked
  } catch (err) {
    console.error(`Erreur lors de l'action sur l'utilisateur`, err)
  }
}

const filteredUsers = computed(() => {
  let result = users.value

  if (activeFilter.value === 'Actifs') {
    result = result.filter(u => !u.is_blocked)
  } else if (activeFilter.value === 'Bloqués') {
    result = result.filter(u => u.is_blocked)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(u => 
      (u.nom && u.nom.toLowerCase().includes(query)) ||
      (u.prenom && u.prenom.toLowerCase().includes(query)) ||
      (u.email && u.email.toLowerCase().includes(query))
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage))

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filteredUsers.value.slice(start, end)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}
</script>

<template>
  <div class="admin-view">
    <div class="page-header">
      <h1>Administration</h1>
    </div>

    <!-- Stats Rapides -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><i class="ti ti-users"></i></div>
        <div class="stat-info">
          <span class="stat-label">Total Utilisateurs</span>
          <span class="stat-value">{{ stats.total }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon text-success"><i class="ti ti-user-check"></i></div>
        <div class="stat-info">
          <span class="stat-label">Utilisateurs Actifs</span>
          <span class="stat-value">{{ stats.actifs }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon text-danger"><i class="ti ti-user-x"></i></div>
        <div class="stat-info">
          <span class="stat-label">Comptes Bloqués</span>
          <span class="stat-value">{{ stats.bloques }}</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon text-primary"><i class="ti ti-shield-check"></i></div>
        <div class="stat-info">
          <span class="stat-label">Administrateurs</span>
          <span class="stat-value">{{ stats.admins }}</span>
        </div>
      </div>
    </div>

    <!-- Filtres et Recherche -->
    <div class="controls-bar">
      <div class="search-box">
        <i class="ti ti-search"></i>
        <input type="text" v-model="searchQuery" placeholder="Rechercher par nom ou email...">
      </div>
      <div class="pills-container">
        <button 
          v-for="filter in filters" 
          :key="filter"
          :class="['pill', { active: activeFilter === filter }]"
          @click="activeFilter = filter; currentPage = 1"
        >
          {{ filter }}
        </button>
      </div>
    </div>

    <!-- Tableau des utilisateurs -->
    <div class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Rôle</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="isLoading" v-for="i in 5" :key="'skel'+i">
            <td colspan="4">
              <div class="skeleton-row"></div>
            </td>
          </tr>
          <tr v-else-if="paginatedUsers.length === 0">
            <td colspan="4" class="empty-state">
              <p>Aucun utilisateur trouvé.</p>
            </td>
          </tr>
          <tr v-else v-for="user in paginatedUsers" :key="user.id_user">
            <td>
              <div class="user-info">
                <div class="user-avatar">{{ user.prenom?.charAt(0) || 'U' }}</div>
                <div class="user-details">
                  <span class="user-name">{{ user.prenom }} {{ user.nom }}</span>
                  <span class="user-email">{{ user.email }}</span>
                </div>
              </div>
            </td>
            <td>
              <span class="role-badge" :class="user.role === 'admin' ? 'admin' : 'user'">
                {{ user.role || 'user' }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="user.is_blocked ? 'blocked' : 'active'">
                {{ user.is_blocked ? 'Bloqué' : 'Actif' }}
              </span>
            </td>
            <td>
              <button 
                class="btn-action" 
                :class="user.is_blocked ? 'btn-success' : 'btn-danger'"
                @click="toggleBlockUser(user)"
                :disabled="user.role === 'admin'"
              >
                <i :class="user.is_blocked ? 'ti ti-user-check' : 'ti ti-user-x'"></i>
                {{ user.is_blocked ? 'Débloquer' : 'Bloquer' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1" 
          @click="goToPage(currentPage - 1)"
        >
          <i class="ti ti-chevron-left"></i>
        </button>
        <span class="page-info">Page {{ currentPage }} sur {{ totalPages }}</span>
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages" 
          @click="goToPage(currentPage + 1)"
        >
          <i class="ti ti-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background-color: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.text-success { color: var(--success); background-color: rgba(34, 197, 94, 0.1); }
.text-danger { color: var(--danger); background-color: rgba(239, 68, 68, 0.1); }
.text-primary { color: var(--primary); background-color: rgba(244, 180, 0, 0.1); }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Contrôles */
.controls-bar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: var(--bg-card);
  padding: 16px;
  border-radius: 12px;
}

@media (min-width: 768px) {
  .controls-bar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 18px;
}

.search-box input {
  width: 100%;
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 10px 16px 10px 40px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--primary);
}

.pills-container {
  display: flex;
  gap: 8px;
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

/* Tableau */
.table-container {
  background-color: var(--bg-card);
  border-radius: 12px;
  overflow-x: auto;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table th, .users-table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.users-table th {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  text-transform: uppercase;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background-color: var(--primary);
  color: var(--bg-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  color: var(--text-primary);
  font-weight: 500;
}

.user-email {
  color: var(--text-secondary);
  font-size: 13px;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.role-badge.admin {
  background-color: rgba(244, 180, 0, 0.1);
  color: var(--primary);
}

.role-badge.user {
  background-color: rgba(255, 255, 255, 0.05);
  color: #aaa;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.status-badge.blocked {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.btn-danger:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.2);
}

.btn-success {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success);
}

.btn-success:hover:not(:disabled) {
  background-color: rgba(34, 197, 94, 0.2);
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.page-btn {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--primary);
  color: var(--primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.skeleton-row {
  height: 20px;
  background-color: var(--bg-primary);
  border-radius: 4px;
  animation: pulse 1.5s infinite;
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: 32px !important;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
