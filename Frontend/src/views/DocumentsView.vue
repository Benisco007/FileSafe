<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../api'
import StatusBadge from '../components/shared/StatusBadge.vue'
import UploadModal from '../components/documents/UploadModal.vue'
import ShareModal from '../components/documents/ShareModal.vue'
import PreviewModal from '../components/documents/PreviewModal.vue'

const documents = ref([])
const isLoading = ref(true)
const searchQuery = ref('')
const activeCategory = ref('Tous')
const isUploadModalOpen = ref(false)
const isShareModalOpen = ref(false)
const selectedDocToShare = ref(null)

const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)

const categories = ['Tous', 'Identité', 'Diplômes', 'Santé', 'Contrats', 'Divers']

const fetchDocuments = async () => {
  try {
    isLoading.value = true
    const params = {}
    if (searchQuery.value) params.recherche = searchQuery.value
    if (activeCategory.value !== 'Tous') params.categorie = activeCategory.value

    const { data } = await api.get('/api/documents/', { params })
    documents.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des documents', err)
  } finally {
    isLoading.value = false
  }
}

let timeoutId = null
watch(searchQuery, () => {
  clearTimeout(timeoutId)
  timeoutId = setTimeout(() => {
    fetchDocuments()
  }, 300)
})

watch(activeCategory, () => {
  fetchDocuments()
})

onMounted(() => {
  fetchDocuments()
})

const getFileIcon = (mimeType) => {
  if (!mimeType) return 'ti-file'
  if (mimeType.includes('pdf')) return 'ti-file-type-pdf text-danger'
  if (mimeType.includes('image')) return 'ti-photo text-primary'
  if (mimeType.includes('word')) return 'ti-file-type-doc text-info'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'ti-file-type-xls text-success'
  return 'ti-file'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).format(new Date(dateString))
}

const toggleCritique = async (doc) => {
  try {
    await api.patch(`/api/documents/${doc.id_doc}/marquer-critique`)
    doc.est_critique = !doc.est_critique
  } catch (err) {
    console.error(err)
  }
}

const toggleIA = async (doc) => {
  try {
    await api.patch(`/api/documents/${doc.id_doc}/autoriser-ia`)
    doc.autorise_ia = !doc.autorise_ia
  } catch (err) {
    console.error(err)
  }
}

const downloadDoc = async (id) => {
  try {
    const { data, headers } = await api.get(`/api/documents/${id}/telecharger`, { responseType: 'blob' })
    
    // Récupérer le vrai type MIME depuis les headers
    const mimeType = headers['content-type'] || 'application/octet-stream'
    const blob = new Blob([data], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    let fileName = 'document'
    const contentDisposition = headers['content-disposition']
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/i)
      if (match && match[1]) fileName = decodeURIComponent(match[1])
    }

    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error(err)
  }
}

const deleteDoc = async (id) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer ce document ? Cette action est irréversible.')) {
    try {
      await api.delete(`/api/documents/${id}`)
      fetchDocuments()
    } catch (err) {
      console.error(err)
    }
  }
}

const openShareModal = (doc) => {
  selectedDocToShare.value = doc
  isShareModalOpen.value = true
}

const previewDoc = async (doc) => {
  try {
    const { data, headers } = await api.get(`/api/documents/${doc.id_doc}/telecharger?inline=true`, { responseType: 'blob' })
    const type = doc.type_mime || doc.type_doc || headers['content-type'] || 'application/pdf'
    const blob = new Blob([data], { type })
    
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    
    previewBlob.value = blob
    previewUrl.value = URL.createObjectURL(blob)
    previewName.value = doc.nom_doc
    previewMime.value = type
    isPreviewModalOpen.value = true
  } catch (err) {
    console.error('Erreur lors de la prévisualisation', err)
    alert("Impossible de charger l'aperçu de ce document.")
  }
}
</script>

<template>
  <div class="documents-view">
    <div class="page-header">
      <h1>Mes documents</h1>
      <button class="btn-primary" @click="isUploadModalOpen = true">
        <i class="ti ti-plus"></i> Nouveau document
      </button>
    </div>

    <div class="filters-bar">
      <div class="search-box">
        <i class="ti ti-search"></i>
        <input type="text" v-model="searchQuery" placeholder="Rechercher un document...">
      </div>

      <div class="pills-container">
        <button 
          v-for="cat in categories" 
          :key="cat"
          :class="['pill', { active: activeCategory === cat }]"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="skeleton-list">
      <div class="skeleton-item" v-for="i in 5" :key="i"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="documents.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="ti ti-folder-off"></i>
      </div>
      <h2>Aucun document trouvé</h2>
      <p>Essayez de modifier vos filtres ou ajoutez un nouveau document.</p>
    </div>

    <!-- Documents List -->
    <div v-else class="documents-list">
      <div class="document-card" v-for="doc in documents" :key="doc.id_doc">
        <div class="doc-main-info">
          <div class="doc-icon">
            <i :class="['ti', getFileIcon(doc.type_mime)]"></i>
          </div>
          <div class="doc-text">
            <h3 class="doc-title">{{ doc.nom_doc }}</h3>
            <div class="doc-meta">
              <span class="category">{{ doc.categorie }}</span>
              <span class="dot">•</span>
              <span class="date">Ajouté le {{ formatDate(doc.date_ajout) }}</span>
            </div>
          </div>
        </div>

        <div class="doc-status">
          <StatusBadge :statut="doc.statut" :date_exp="doc.date_exp" />
        </div>

        <div class="doc-actions">
          <button class="action-btn" title="Aperçu" @click="previewDoc(doc)">
            <i class="ti ti-eye"></i>
          </button>
          <button class="action-btn" title="Télécharger" @click="downloadDoc(doc.id_doc)">
            <i class="ti ti-download"></i>
          </button>
          <button class="action-btn" title="Partager" @click="openShareModal(doc)">
            <i class="ti ti-share"></i>
          </button>
          <button 
            :class="['action-btn', { active: doc.est_critique }]" 
            title="Marquer critique / Hors ligne"
            @click="toggleCritique(doc)"
          >
            <i class="ti ti-wifi-off"></i>
          </button>
          <button 
            :class="['action-btn', { active: doc.autorise_ia }]" 
            title="Autoriser l'analyse IA"
            @click="toggleIA(doc)"
          >
            <i class="ti ti-robot"></i>
          </button>
          <button class="action-btn text-danger hover-danger" title="Supprimer" @click="deleteDoc(doc.id_doc)">
            <i class="ti ti-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Action Button pour Mobile -->
    <button class="fab" @click="isUploadModalOpen = true">
      <i class="ti ti-plus"></i>
    </button>

    <UploadModal 
      :isOpen="isUploadModalOpen" 
      @close="isUploadModalOpen = false"
      @uploaded="fetchDocuments"
    />

    <ShareModal
      v-if="isShareModalOpen"
      :document="selectedDocToShare"
      @close="isShareModalOpen = false"
    />

    <PreviewModal
      :isOpen="isPreviewModalOpen"
      :fileUrl="previewUrl"
      :fileName="previewName"
      :mimeType="previewMime"
      :fileBlob="previewBlob"
      @close="isPreviewModalOpen = false"
    />
  </div>
</template>

<style scoped>
.documents-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
  min-height: calc(100vh - 100px);
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

/* Filtres */
.filters-bar {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: var(--bg-card);
  padding: 16px;
  border-radius: 12px;
}

@media (min-width: 768px) {
  .filters-bar {
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

/* Liste de documents */
.documents-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.document-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-card);
  padding: 16px 20px;
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.document-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.doc-main-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 2;
}

.doc-icon {
  width: 48px;
  height: 48px;
  background-color: var(--bg-primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.text-danger { color: var(--danger) !important; }
.text-primary { color: var(--primary) !important; }
.text-info { color: #3B82F6 !important; }
.text-success { color: var(--success) !important; }

.doc-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doc-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
}

.category {
  background-color: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
}

.doc-status {
  flex: 1;
  display: flex;
  justify-content: center;
}

.doc-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: flex-end;
}

.action-btn {
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.action-btn.active {
  color: var(--primary);
  background-color: rgba(244, 180, 0, 0.1);
}

.hover-danger:hover {
  color: var(--danger);
  background-color: rgba(239, 68, 68, 0.1);
}

/* Skeleton */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 80px;
  background-color: var(--bg-card);
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--text-secondary);
}

.empty-icon {
  width: 80px;
  height: 80px;
  background-color: var(--bg-card);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-state h2 {
  color: var(--text-primary);
  margin-bottom: 8px;
}

/* FAB */
.fab {
  display: none;
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: var(--primary);
  color: var(--bg-primary);
  border: none;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(244, 180, 0, 0.3);
  cursor: pointer;
  z-index: 99;
}

@media (max-width: 768px) {
  .page-header .btn-primary {
    display: none;
  }
  .fab {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .document-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .doc-status {
    justify-content: flex-start;
  }
  .doc-actions {
    justify-content: flex-start;
    width: 100%;
    border-top: 1px solid var(--border-color);
    padding-top: 12px;
  }
}
</style>