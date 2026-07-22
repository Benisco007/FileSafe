<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import PreviewModal from '../components/documents/PreviewModal.vue'

const route = useRoute()
const token = route.params.token

const isLoading = ref(true)
const errorMsg = ref('')
const documentData = ref(null)

const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)
const isLoadingPreview = ref(false)

const fetchShareData = async () => {
  try {
    isLoading.value = true
    const { data } = await api.get(`/api/shares/acces/${token}`)
    documentData.value = data
  } catch (err) {
    if (err.response?.status === 404) {
      errorMsg.value = "Ce lien de partage n'existe pas ou est invalide."
    } else if (err.response?.status === 403) {
      errorMsg.value = err.response.data.detail || "Vous n'avez pas accès à ce document."
    } else {
      errorMsg.value = "Une erreur est survenue lors de la récupération du document."
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchShareData()
})

const handleDownload = async () => {
  if (!documentData.value?.lien_telechargement) return
  try {
    const { data, headers } = await api.get(`/api/shares/telecharger/${token}`, { responseType: 'blob' })

    // Récupérer le vrai type MIME depuis les headers pour que le fichier soit reconnu à l'ouverture
    const mimeType = headers['content-type'] || documentData.value.type_doc || 'application/octet-stream'
    const url = window.URL.createObjectURL(new Blob([data], { type: mimeType }))

    const link = document.createElement('a')
    link.href = url

    let fileName = documentData.value.nom_doc || 'document'
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
    console.error('Erreur lors du téléchargement:', err)
    alert("Impossible de télécharger ce document.")
  }
}

const handlePreview = async () => {
  if (!documentData.value?.lien_telechargement) return
  
  try {
    isLoadingPreview.value = true
    const { data, headers } = await api.get(`/api/shares/telecharger/${token}?inline=true`, {
      responseType: 'blob'
    })
    
    // Priorité aux headers du serveur (source de vérité), puis fallback sur les métadonnées du doc
    const type = headers['content-type'] || documentData.value.type_doc || 'application/octet-stream'
    const blob = new Blob([data], { type })
    
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    
    previewBlob.value = blob
    previewUrl.value = URL.createObjectURL(blob)
    previewName.value = documentData.value.nom_doc
    previewMime.value = type
    isPreviewModalOpen.value = true
  } catch (err) {
    console.error('Erreur lors du chargement de l\'aperçu:', err)
    alert("Impossible de charger l'aperçu du document.")
  } finally {
    isLoadingPreview.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Intl.DateTimeFormat('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(new Date(dateString))
}
</script>

<template>
  <div class="share-access-view">
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement du document sécurisé...</p>
    </div>

    <div v-else-if="errorMsg" class="error-state">
      <div class="error-icon">
        <i class="ti ti-lock-x"></i>
      </div>
      <h2>Accès refusé</h2>
      <p>{{ errorMsg }}</p>
    </div>

    <div v-else-if="documentData" class="document-card-container">
      <div class="brand-header">
        <i class="ti ti-shield-lock"></i>
        <h2>FileSafe Partage</h2>
      </div>
      
      <div class="document-card">
        <div class="doc-header">
          <div class="doc-icon">
            <i class="ti ti-file-text"></i>
          </div>
          <div class="doc-title">
            <h3>{{ documentData.nom_doc }}</h3>
            <span class="doc-badge">{{ documentData.categorie }}</span>
          </div>
        </div>

        <div class="doc-details">
          <div class="detail-item">
            <span class="detail-label">Partagé par</span>
            <span class="detail-value">
              <strong>{{ documentData.expediteur_nom }}</strong>
              <span class="text-muted" v-if="documentData.expediteur_email">({{ documentData.expediteur_email }})</span>
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Date d'ajout</span>
            <span class="detail-value">{{ formatDate(documentData.date_ajout) }}</span>
          </div>
        </div>

        <div class="doc-actions">
          <button class="btn-primary" @click="handleDownload">
            <i class="ti ti-download"></i>
            Télécharger le document
          </button>
          
          <button class="btn-secondary" @click="handlePreview" :disabled="isLoadingPreview">
            <i class="ti ti-eye"></i>
            {{ isLoadingPreview ? 'Chargement...' : 'Aperçu du document' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- Modale de prévisualisation -->
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
.share-access-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #121212;
  color: var(--text-primary);
  padding: 20px;
}

.loading-state, .error-state {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  background-color: var(--bg-card);
  padding: 40px;
  border-radius: 16px;
  max-width: 400px;
  width: 100%;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--input-border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-icon {
  width: 64px;
  height: 64px;
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--danger);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.error-state h2 {
  margin: 0;
  font-size: 24px;
}

.error-state p {
  margin: 0;
  color: var(--text-secondary);
}

.document-card-container {
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.brand-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--primary);
}

.brand-header i {
  font-size: 32px;
}

.brand-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.document-card {
  background-color: var(--bg-card);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.doc-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.doc-icon {
  width: 56px;
  height: 56px;
  background-color: var(--bg-primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: var(--primary);
}

.doc-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  word-break: break-word;
}

.doc-badge {
  background-color: rgba(244, 180, 0, 0.15);
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.doc-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.detail-value {
  font-size: 15px;
}

.text-muted {
  color: var(--text-secondary);
  font-size: 13px;
  margin-left: 6px;
}

.doc-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background-color: var(--primary);
  color: #121212;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--bg-primary);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>