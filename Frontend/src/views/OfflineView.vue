<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from '@/composables/useTheme'
import api from '../api'
import PreviewModal from '../components/documents/PreviewModal.vue'

const { isDark, toggleTheme } = useTheme()

// ─── État de chargement ───────────────────────────────────────────
const isLoading = ref(true)

// ─── Documents hors ligne ─────────────────────────────────────────
const offlineDocs = ref([])

// ─── Prévisualisation ──────────────────────────────────────────────
const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)

const previewDoc = async (doc) => {
  try {
    const { data, headers } = await api.get(`/api/documents/${doc.id_doc}/telecharger?inline=true`, { responseType: 'blob' })
    const type = doc.type_doc || headers['content-type'] || 'application/pdf'
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

// ─── Helpers ──────────────────────────────────────────────────────
const documentIconClass = (mimeType) => {
  if (!mimeType) return 'ti-file-text'
  if (mimeType.includes('pdf')) return 'ti-file-type-pdf'
  if (mimeType.includes('image')) return 'ti-photo'
  if (mimeType.includes('word')) return 'ti-file-type-doc'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'ti-file-spreadsheet'
  return 'ti-file-text'
}

const removeDocument = async (id) => {
  try {
    await api.patch(`/api/documents/${id}/marquer-critique`)
    offlineDocs.value = offlineDocs.value.filter((doc) => doc.id_doc !== id)
  } catch (error) {
    console.error('Erreur lors du retrait du document hors ligne :', error)
  }
}

// ─── Chargement des données ───────────────────────────────────────
const fetchOfflineDocs = async () => {
  const { data } = await api.get('/api/documents/')
  offlineDocs.value = data.filter((d) => d.est_critique)
}

// ─── Déclenchement au montage ─────────────────────────────────────
onMounted(async () => {
  try {
    await fetchOfflineDocs()
  } catch (error) {
    console.error('Erreur chargement documents hors ligne :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="offline">
    <!-- EN-TÊTE -->
    <div class="header">
      <div class="header-left">
        <h1>Hors ligne</h1>
        <p class="subtitle">Vos documents accessibles sans connexion internet</p>
      </div>
      <div class="header-right">
        <button class="btn-icon" :title="isDark ? 'Mode clair' : 'Mode sombre'" @click="toggleTheme">
          <i :class="isDark ? 'ti ti-sun' : 'ti ti-moon'"></i>
        </button>
        <button class="btn-icon" title="Paramètres" @click="$router.push('/settings')">
          <i class="ti ti-settings"></i>
        </button>
      </div>
    </div>

    <!-- SKELETON -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton skeleton-header"></div>
      <div class="skeleton skeleton-list"></div>
    </div>

    <!-- CONTENU -->
    <div v-else class="offline-content">
      <!-- Explication -->
      <div class="card info-card">
        <div class="info-icon">
          <i class="ti ti-wifi-off"></i>
        </div>
        <div class="info-text">
          <h3>Fonctionnement hors ligne</h3>
          <p>
            Les documents que tu ajoutes ici restent disponibles même sans connexion.
            Ils sont conservés de façon sécurisée sur ton appareil et synchronisés
            automatiquement dès le retour du réseau.
          </p>
        </div>
      </div>

      <!-- Liste des documents -->
      <div class="card documents-card">
        <h2 class="section-title">Documents disponibles hors ligne</h2>

        <div v-if="offlineDocs.length === 0" class="empty-state">
          <i class="ti ti-wifi-off empty-icon"></i>
          <p>Aucun document hors ligne</p>
          <span>Ajoute tes documents les plus importants pour y accéder sans internet.</span>
        </div>

        <div v-else class="offline-list">
          <div
            v-for="doc in offlineDocs"
            :key="doc.id_doc"
            class="offline-row"
          >
            <div class="doc-preview">
              <i :class="'ti ' + documentIconClass(doc.type_doc)"></i>
            </div>
            <div class="doc-info">
              <p class="doc-name">{{ doc.nom_doc }}</p>
              <p class="doc-desc">{{ doc.categorie }}</p>
            </div>
            <div class="doc-actions">
              <button class="btn-edit" @click="previewDoc(doc)">
                <i class="ti ti-eye"></i> Aperçu
              </button>
              <button class="btn-remove" @click="removeDocument(doc.id_doc)">
                <i class="ti ti-trash"></i> Retirer
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de prévisualisation -->
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
.offline {
  padding: 24px 32px;
  background-color: var(--bg-primary);
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

/* EN-TÊTE */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.header h1 {
  font-size: 22px;
  font-weight: 500;
}

.subtitle {
  font-size: 13px;
  color: #888;
  margin-top: 4px;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-icon {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 0.5px solid var(--border-color);
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  font-size: 16px;
  transition: color 0.2s, border-color 0.2s;
}
.btn-icon:hover {
  color: var(--primary);
  border-color: var(--primary);
}

/* SKELETON */
.loading-state {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skeleton {
  background: linear-gradient(90deg, #1E1E1E 25%, #2a2a2a 50%, #1E1E1E 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 18px;
}

.skeleton-header {
  height: 100px;
}

.skeleton-list {
  height: 360px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* CARTES */
.card {
  background: #1E1E1E;
  border-radius: 18px;
  padding: 20px;
  border: 0.5px solid #2a2a2a;
}

.offline-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 900px;
}

/* INFO CARD */
.info-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.info-text h3 {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 6px;
}

.info-text p {
  font-size: 13px;
  color: #888;
  line-height: 1.6;
}

/* DOCUMENTS CARD */
.documents-card {
  padding: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 20px;
}

.offline-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.offline-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  transition: background 0.15s ease;
}

.offline-row:hover {
  background: rgba(244, 180, 0, 0.06);
}

.doc-preview {
  width: 52px;
  height: 52px;
  border-radius: 10px;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.doc-info {
  flex: 1;
  min-width: 0;
}

.doc-name {
  font-size: 14px;
  font-weight: 500;
  color: white;
  margin-bottom: 3px;
}

.doc-desc {
  font-size: 12px;
  color: #888;
}

.doc-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-edit {
  background: transparent;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-edit:hover {
  border-color: #F4B400;
  color: #F4B400;
}

.btn-remove {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-remove:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* ÉTAT VIDE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
  gap: 8px;
  color: #555;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 4px;
  color: #444;
}

.empty-state p {
  font-size: 14px;
  font-weight: 500;
  color: #666;
}

.empty-state span {
  font-size: 12px;
  color: #444;
  text-align: center;
  max-width: 320px;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .offline {
    padding: 20px;
  }

  .info-card {
    flex-direction: column;
  }

  .offline-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .doc-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
