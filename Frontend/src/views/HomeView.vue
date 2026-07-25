<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import StatusBadge from '../components/shared/StatusBadge.vue'
import UploadModal from '../components/documents/UploadModal.vue'

const authStore = useAuthStore()
const isLoading = ref(true)
const stats = ref(null)
const isUploadModalOpen = ref(false)

const prenom = authStore.user?.prenom || 'Utilisateur'
const dateDuJour = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long',
  year: 'numeric',
  month: 'long',
  day: 'numeric'
}).format(new Date())

const fetchStats = async () => {
  try {
    isLoading.value = true
    const { data } = await api.get('/api/dashboard/stats')
    stats.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des statistiques', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
})

// Reçoit des octets bruts, affiche dans la bonne unité
const formatBytes = (bytes, decimals = 2) => {
  if (!bytes || bytes === 0) return '0 Octets'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Octets', 'Ko', 'Mo', 'Go', 'To']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}
</script>

<template>
  <div class="home-view">
    <div class="header">
      <div class="greeting">
        <h1>Bonjour, {{ prenom }} 👋</h1>
        <p class="date">{{ dateDuJour }}</p>
      </div>
      <button class="btn-primary" @click="isUploadModalOpen = true">
        <i class="ti ti-upload"></i>
        Téléverser un document
      </button>
    </div>

    <div v-if="isLoading" class="skeleton-container">
      <div class="skeleton-card" v-for="i in 4" :key="i"></div>
    </div>

    <template v-else-if="stats">
      <!-- Cartes Métriques -->
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-icon"><i class="ti ti-files"></i></div>
          <div class="metric-info">
            <span class="metric-label">Total Documents</span>
            <span class="metric-value">{{ stats.total_documents }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon"><i class="ti ti-database"></i></div>
          <div class="metric-info">
            <span class="metric-label">Espace Utilisé</span>
            <span class="metric-value">{{ formatBytes(stats.espace_utilise) }} / {{ formatBytes(stats.espace_total) }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon warning"><i class="ti ti-alert-triangle"></i></div>
          <div class="metric-info">
            <span class="metric-label">Documents Expirés</span>
            <span class="metric-value">{{ stats.document_expires }}</span>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon"><i class="ti ti-users"></i></div>
          <div class="metric-info">
            <span class="metric-label">Dépôts Actifs</span>
            <span class="metric-value">{{ stats.depots_actifs }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-content">
        <!-- Colonne principale -->
        <div class="main-column">
          <!-- Score Documentaire -->
          <div class="score-card">
            <h2>Score Documentaire</h2>
            <div class="score-circle">
              <svg viewBox="0 0 36 36" class="circular-chart">
                <path class="circle-bg"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path class="circle"
                  :stroke-dasharray="`${stats.score}, 100`"
                  d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <text x="18" y="20.35" class="percentage">{{ stats.score }}%</text>
              </svg>
            </div>
            <p class="score-text">Documents critiques à jour</p>
          </div>

          <!-- Documents Récents -->
          <div class="recent-docs-card">
            <h2>Documents Récents</h2>
            <div class="doc-list" v-if="stats.documents_recents && stats.documents_recents.length > 0">
              <div class="doc-item" v-for="doc in stats.documents_recents" :key="doc.id_doc">
                <div class="doc-icon">
                  <i class="ti ti-file-text"></i>
                </div>
                <div class="doc-details">
                  <span class="doc-name">{{ doc.nom_doc }}</span>
                  <span class="doc-cat">{{ doc.categorie }}</span>
                </div>
                <StatusBadge :statut="doc.statut" :date_exp="doc.date_exp" />
              </div>
            </div>
            <div class="empty-state" v-else>
              <p>Aucun document récent</p>
            </div>
          </div>
        </div>

        <!-- Colonne latérale (Alertes) -->
        <div class="side-column">
          <div class="alerts-card">
            <h2>Alertes ({{ stats.alertes ? stats.alertes.length : 0 }})</h2>
            <div class="alerts-list" v-if="stats.alertes && stats.alertes.length > 0">
              <div class="alert-item" v-for="(alerte, index) in stats.alertes" :key="index">
                <i class="ti ti-bell-ringing"></i>
                <div class="alert-content">
                  <p>{{ alerte.message }}</p>
                </div>
              </div>
            </div>
            <div class="empty-state" v-else>
              <i class="ti ti-check"></i>
              <p>Aucune alerte</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <UploadModal
      :isOpen="isUploadModalOpen"
      @close="isUploadModalOpen = false"
      @uploaded="fetchStats"
    />
  </div>
</template>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.greeting h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.greeting .date {
  font-size: 14px;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.btn-primary {
  background-color: var(--primary);
  color: var(--bg-primary);
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

/* Skeleton */
.skeleton-container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.skeleton-card {
  height: 100px;
  background-color: var(--bg-card);
  border-radius: 18px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Métriques */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.metric-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: rgba(244, 180, 0, 0.15);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.metric-icon.warning {
  background-color: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Contenu Dashboard */
.dashboard-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.main-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Score Documentaire */
.score-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-card h2 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 20px;
  align-self: flex-start;
}

.score-circle {
  width: 150px;
  height: 150px;
}

.circular-chart {
  display: block;
  margin: 0 auto;
  max-width: 80%;
  max-height: 250px;
}

.circle-bg {
  fill: none;
  stroke: var(--border-color);
  stroke-width: 3.8;
}

.circle {
  fill: none;
  stroke-width: 2.8;
  stroke-linecap: round;
  stroke: var(--primary);
  animation: progress 1s ease-out forwards;
}

@keyframes progress {
  0% { stroke-dasharray: 0 100; }
}

.percentage {
  fill: var(--text-primary);
  font-size: 8px;
  text-anchor: middle;
  font-weight: bold;
}

.score-text {
  margin-top: 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* Documents Récents */
.recent-docs-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 24px;
}

.recent-docs-card h2 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.doc-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: var(--bg-primary);
  border-radius: 12px;
  gap: 16px;
}

.doc-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(244, 180, 0, 0.1);
  color: var(--primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.doc-details {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.doc-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.doc-cat {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Alertes */
.alerts-card {
  background-color: rgba(244, 180, 0, 0.05);
  border-radius: 18px;
  padding: 24px;
  height: 100%;
  border: 1px solid rgba(244, 180, 0, 0.2);
}

.alerts-card h2 {
  font-size: 18px;
  color: var(--primary);
  margin-bottom: 16px;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background-color: rgba(244, 180, 0, 0.1);
  border-radius: 12px;
}

.alert-item i {
  color: var(--primary);
  font-size: 20px;
  margin-top: 2px;
}

.alert-content p {
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.empty-state i {
  font-size: 32px;
  color: var(--primary);
}
</style>