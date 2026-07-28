<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import StatusBadge from '../components/shared/StatusBadge.vue'
import ShareModal from '../components/documents/ShareModal.vue'
import Pagination from '../components/shared/Pagination.vue'

const shares = ref([])
const documents = ref([]) // Pour le dropdown du journal
const selectedDocForJournal = ref('')
const journal = ref([])
const isLoadingShares = ref(true)
const isLoadingJournal = ref(false)
const isShareModalOpen = ref(false)

const currentPage = ref(1)
const perPage = 10

const paginatedShares = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return shares.value.slice(start, start + perPage)
})

const fetchShares = async () => {
  try {
    isLoadingShares.value = true
    // Note: l'endpoint /api/shares/ n'est pas explicitement dans la liste, 
    // on suppose qu'il retourne la liste des partages actifs de l'utilisateur.
    const { data } = await api.get('/api/shares/mes-partages')
    shares.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des partages', err)
  } finally {
    isLoadingShares.value = false
  }
}

const fetchDocuments = async () => {
  try {
    const { data } = await api.get('/api/documents/')
    documents.value = data
    if (data.length > 0) {
      selectedDocForJournal.value = data[0].id_doc
      fetchJournal()
    }
  } catch (err) {
    console.error('Erreur lors de la récupération des documents pour le journal', err)
  }
}

const fetchJournal = async () => {
  if (!selectedDocForJournal.value) return
  
  try {
    isLoadingJournal.value = true
    const { data } = await api.get(`/api/shares/${selectedDocForJournal.value}/journal`)
    journal.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération du journal', err)
  } finally {
    isLoadingJournal.value = false
  }
}

onMounted(() => {
  fetchShares()
  fetchDocuments()
})

const revokeShare = async (id_part) => {
  if (confirm('Êtes-vous sûr de vouloir révoquer ce partage ?')) {
    try {
      await api.patch(`/api/shares/${id_part}/revoquer`)
      fetchShares()
    } catch (err) {
      console.error(err)
    }
  }
}

const copySuccess = ref(null) // id du partage dont le lien vient d'être copié

const copyLink = async (token, id_part) => {
  // Pointe vers le téléchargement direct sur le BACKEND
  const url = `https://file-safe.vercel.app/share/${token}`
  try {
    await navigator.clipboard.writeText(url)
    copySuccess.value = id_part
    setTimeout(() => copySuccess.value = null, 2000)
  } catch (err) {
    console.error('Erreur copie:', err)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Jamais'
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(dateString))
}

const getJournalIcon = (type) => {
  return type === 'Téléchargement' ? 'ti-download text-primary' : 'ti-eye text-info'
}
</script>

<template>
  <div class="shares-view">
    <div class="page-header">
      <h1>Mes partages</h1>
      <button class="btn-primary" @click="isShareModalOpen = true">
        <i class="ti ti-share"></i> Nouveau partage
      </button>
    </div>

    <div class="shares-layout">
      <!-- Colonne Gauche : Liste des partages -->
      <div class="shares-column">
        <h2>Partages actifs</h2>
        
        <div v-if="isLoadingShares" class="skeleton-list">
          <div class="skeleton-item" v-for="i in 3" :key="i"></div>
        </div>

        <div v-else-if="shares.length === 0" class="empty-state">
          <i class="ti ti-share-off"></i>
          <p>Aucun partage actif</p>
        </div>

        <div v-else class="shares-list-wrapper">
          <div class="shares-list">
            <div class="share-card" v-for="share in paginatedShares" :key="share.id_part">
            <div class="share-header">
              <h3 class="doc-name"><i class="ti ti-file-text"></i> {{ share.document?.nom_doc || 'Document' }}</h3>
              <StatusBadge :date_exp="share.date_expiration" />
            </div>
            
            <div class="share-details">
              <div class="detail-item">
                <i class="ti ti-clock"></i> Expire le: {{ formatDate(share.date_expiration) }}
              </div>
              <div class="detail-item">
                <i class="ti ti-download"></i> Téléchargements: {{ share.nb_telechargements }} / {{ share.max_telechargements || '∞' }}
              </div>
            </div>

            <div class="share-actions">
              <div class="link-box">
                <input type="text" readonly :value="`https://file-safe.vercel.app/share/${share.token}`">
                <button 
                  class="btn-icon" 
                  :class="{ 'copied': copySuccess === share.id_part }"
                  @click="copyLink(share.token, share.id_part)" 
                  :title="copySuccess === share.id_part ? 'Copié !' : 'Copier le lien'"
                >
                  <i :class="copySuccess === share.id_part ? 'ti ti-check' : 'ti ti-copy'"></i>
                </button>
              </div>
              <button class="btn-revoke" @click="revokeShare(share.id_part)">
                <i class="ti ti-trash"></i> Révoquer
              </button>
            </div>
          </div>
          </div>
          <Pagination :total="shares.length" :perPage="perPage" v-model:currentPage="currentPage" />
        </div>
      </div>

      <!-- Colonne Droite : Journal d'accès -->
      <div class="journal-column">
        <h2>Journal d'accès</h2>
        
        <div class="journal-card">
          <div class="journal-filter">
            <label>Sélectionner un document :</label>
            <select v-model="selectedDocForJournal" @change="fetchJournal">
              <option v-for="doc in documents" :key="doc.id_doc" :value="doc.id_doc">
                {{ doc.nom_doc }}
              </option>
            </select>
          </div>

          <div v-if="isLoadingJournal" class="skeleton-list">
            <div class="skeleton-item small" v-for="i in 4" :key="i"></div>
          </div>

          <div v-else-if="journal.length === 0" class="empty-state">
            <i class="ti ti-history"></i>
            <p>Aucun historique pour ce document</p>
          </div>

          <div v-else class="timeline">
            <div class="timeline-item" v-for="(entry, index) in journal" :key="index">
              <div class="timeline-icon">
                <i :class="['ti', getJournalIcon(entry.type_action)]"></i>
              </div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="action-type">{{ entry.type_action }}</span>
                  <span class="action-time">{{ formatDate(entry.horodatage) }}</span>
                </div>
                <div class="action-details">
                  <span class="ip-address"><i class="ti ti-network"></i> IP: {{ entry.ip_masquee }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <ShareModal
      v-if="isShareModalOpen"
      @close="isShareModalOpen = false"
      @share-created="fetchShares"
    />
  </div>
</template>

<style scoped>
.shares-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: calc(100vh - 108px);
  overflow: hidden;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-primary {
  background-color: var(--primary);
  color: #121212;
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

.shares-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

@media (min-width: 992px) {
  .shares-layout {
    grid-template-columns: 3fr 2fr;
  }
}

h2 {
  font-size: 18px;
  color: var(--text-primary);
  margin-bottom: 16px;
}

/* Shares List */
.shares-list-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.shares-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.share-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.doc-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.doc-name i {
  color: var(--primary);
}

.share-details {
  display: flex;
  gap: 24px;
  color: var(--text-secondary);
  font-size: 13px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.share-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.link-box {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  border-radius: 8px;
  overflow: hidden;
}

.link-box input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 10px 12px;
  font-size: 13px;
  outline: none;
}

.btn-icon {
  background: none;
  border: none;
  color: var(--primary);
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-icon:hover {
  background-color: rgba(244, 180, 0, 0.1);
}

.btn-icon.copied {
  color: var(--success);
}

.btn-revoke {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.btn-revoke:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

/* Journal */
.journal-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 20px;
  height: 100%;
}

.journal-filter {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.journal-filter label {
  font-size: 13px;
  color: var(--text-secondary);
}

.journal-filter select {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.journal-filter select:focus {
  border-color: var(--primary);
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 16px;
  width: 2px;
  background-color: var(--border-color);
}

.timeline-item {
  display: flex;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.timeline-icon {
  width: 34px;
  height: 34px;
  background-color: var(--bg-primary);
  border: 2px solid var(--border-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.text-primary { color: var(--primary); }
.text-info { color: #3B82F6; }

.timeline-content {
  flex: 1;
  background-color: var(--bg-primary);
  padding: 12px 16px;
  border-radius: 12px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.action-type {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.action-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-details {
  font-size: 13px;
  color: #aaa;
}

.ip-address {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Skeletons & Empty States */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-item {
  height: 120px;
  background-color: var(--bg-card);
  border-radius: 18px;
  animation: pulse 1.5s infinite;
}

.skeleton-item.small {
  height: 60px;
  background-color: var(--bg-primary);
  border-radius: 12px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary);
  text-align: center;
  background-color: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
}

.empty-state i {
  font-size: 48px;
  color: var(--text-muted);
  margin-bottom: 12px;
}
</style>