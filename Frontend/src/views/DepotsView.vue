<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import PreviewModal from '../components/documents/PreviewModal.vue'

const depots = ref([])
const isLoading = ref(true)
const selectedDepot = ref(null)

const isCreateModalOpen = ref(false)
const newDepot = ref({ nom_dep: '', type_dep: 'Equipe' })
const isCreating = ref(false)

const isInviteModalOpen = ref(false)
const newInvite = ref({ email: '', permission: 'lecture' })
const isInviting = ref(false)

// Documents de l'utilisateur pour le modal d'ajout
const userDocs = ref([])
const isAddDocModalOpen = ref(false)
const selectedDocId = ref('')
const isAddingDoc = ref(false)

const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)

const fetchUserDocs = async () => {
  try {
    const { data } = await api.get('/api/documents/')
    userDocs.value = data
  } catch (err) {
    console.error(err)
  }
}

const openAddDocModal = () => {
  fetchUserDocs()
  isAddDocModalOpen.value = true
}

const addDocToDepot = async () => {
  if (!selectedDocId.value) return
  try {
    isAddingDoc.value = true
    await api.post(`/api/depots/${selectedDepot.value.id_depot}/documents/${selectedDocId.value}`)
    isAddDocModalOpen.value = false
    selectedDocId.value = ''
    // Rafraîchir le dépôt
    const { data } = await api.get('/api/depots/')
    const updated = data.find(d => d.id_depot === selectedDepot.value.id_depot)
    if (updated) selectedDepot.value = { ...updated, activeTab: 'Documents' }
  } catch (err) {
    console.error(err)
    alert('Erreur lors de l\'ajout du document')
  } finally {
    isAddingDoc.value = false
  }
}

const fetchDepots = async () => {
  try {
    isLoading.value = true
    const { data } = await api.get('/api/depots/')
    depots.value = data
  } catch (err) {
    console.error('Erreur lors de la récupération des dépôts', err)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDepots()
})

const createDepot = async () => {
  try {
    isCreating.value = true
    await api.post(`/api/depots/?nom_dep=${encodeURIComponent(newDepot.value.nom_dep)}&type_dep=${encodeURIComponent(newDepot.value.type_dep || '')}`)
    isCreateModalOpen.value = false
    newDepot.value = { nom_dep: '', type_dep: 'Equipe' }
    fetchDepots()
  } catch (err) {
    console.error(err)
    alert('Erreur lors de la création du dépôt')
  } finally {
    isCreating.value = false
  }
}

const openDepot = (depot) => {
  selectedDepot.value = { ...depot, activeTab: 'Documents' }
}

const closeDepot = () => {
  selectedDepot.value = null
  fetchDepots()
}

const updatePermission = async (membre) => {
  try {
    await api.patch(`/api/depots/${selectedDepot.value.id_depot}/membres/${membre.user.id_user}/permission?permission=${nouvellePermission}`, {
      permission: membre.permission
    })
  } catch (err) {
    console.error(err)
    alert('Erreur lors de la modification de la permission')
  }
}

const inviteMember = async () => {
  try {
    isInviting.value = true
    await api.post(`/api/depots/${selectedDepot.value.id_depot}/inviter?mail_invite=${encodeURIComponent(newInvite.value.email)}&permission=${newInvite.value.permission || 'lecture'}`)
    isInviteModalOpen.value = false
    newInvite.value = { email: '', permission: 'lecture' }
    // Ideally we would fetch just this depot's members, but we'll re-fetch all for simplicity
    fetchDepots()
    // Find the updated depot to update selectedDepot
    const { data } = await api.get('/api/depots/')
    const updated = data.find(d => d.id_dep === selectedDepot.value.id_dep)
    if (updated) {
      selectedDepot.value = { ...updated, activeTab: selectedDepot.value.activeTab }
    }
  } catch (err) {
    console.error(err)
    alert('Erreur lors de l\'invitation')
  } finally {
    isInviting.value = false
  }
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

const downloadDoc = async (doc) => {
  try {
    const { data, headers } = await api.get(`/api/documents/${doc.id_doc}/telecharger`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([data]))
    const link = document.createElement('a')
    link.href = url
    
    let fileName = doc.nom_doc || 'document'
    const contentDisposition = headers['content-disposition']
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="(.+)"/)
      if (match && match[1]) fileName = match[1]
    }
    
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (err) {
    console.error('Erreur téléchargement', err)
    alert("Impossible de télécharger ce document.")
  }
}
</script>

<template>
  <div class="depots-view">
    
    <!-- Vue Liste des Dépôts -->
    <div v-if="!selectedDepot" class="depots-list-view">
      <div class="page-header">
        <h1>Dépôts partagés</h1>
        <button class="btn-primary" @click="isCreateModalOpen = true">
          <i class="ti ti-plus"></i> Créer un dépôt
        </button>
      </div>

      <div v-if="isLoading" class="skeleton-grid">
        <div class="skeleton-card" v-for="i in 6" :key="i"></div>
      </div>

      <div v-else-if="depots.length === 0" class="empty-state">
        <i class="ti ti-users-group"></i>
        <h2>Aucun dépôt partagé</h2>
        <p>Créez un dépôt pour collaborer sur des documents avec votre équipe.</p>
        <button class="btn-primary" @click="isCreateModalOpen = true">Créer un dépôt</button>
      </div>

      <div v-else class="depots-grid">
        <div class="depot-card" v-for="depot in depots" :key="depot.id_dep">
          <div class="depot-header">
            <div class="depot-icon"><i class="ti ti-folder-shared"></i></div>
            <span class="depot-type">{{ depot.type_dep }}</span>
          </div>
          <h3 class="depot-name">{{ depot.nom_dep }}</h3>
          
          <div class="depot-stats">
            <div class="stat-item">
              <i class="ti ti-file"></i>
              <span>{{ depot.documents?.length || 0 }} documents</span>
            </div>
            <div class="stat-item">
              <i class="ti ti-users"></i>
              <span>{{ depot.membres?.length || 0 }} membres</span>
            </div>
          </div>

          <div class="members-stack">
            <div 
              class="member-avatar" 
              v-for="(membre, idx) in (depot.membres || []).slice(0, 3)" 
              :key="idx"
              :title="membre.user?.prenom"
            >
              {{ membre.user?.prenom?.charAt(0).toUpperCase() || 'U' }}
            </div>
            <div class="member-avatar more" v-if="(depot.membres?.length || 0) > 3">
              +{{ depot.membres.length - 3 }}
            </div>
          </div>

          <button class="btn-outline" @click="openDepot(depot)">Accéder</button>
        </div>
      </div>
    </div>

    <!-- Vue Intérieure d'un Dépôt -->
    <div v-else class="depot-inner-view">
      <div class="inner-header">
        <button class="btn-back" @click="closeDepot">
          <i class="ti ti-arrow-left"></i> Retour aux dépôts
        </button>
        <div class="depot-title-area">
          <div class="depot-icon large"><i class="ti ti-folder-shared"></i></div>
          <div>
            <h1>{{ selectedDepot.nom_dep }}</h1>
            <span class="depot-type">{{ selectedDepot.type_dep }}</span>
          </div>
        </div>
        <button class="btn-primary" @click="isInviteModalOpen = true" v-if="selectedDepot.activeTab === 'Membres'">
          <i class="ti ti-user-plus"></i> Inviter
        </button>
      </div>

      <div class="tabs">
        <button 
          :class="['tab', { active: selectedDepot.activeTab === 'Documents' }]"
          @click="selectedDepot.activeTab = 'Documents'"
        >
          <i class="ti ti-files"></i> Documents
        </button>
        <button 
          :class="['tab', { active: selectedDepot.activeTab === 'Membres' }]"
          @click="selectedDepot.activeTab = 'Membres'"
        >
          <i class="ti ti-users"></i> Membres
        </button>
        <button 
          :class="['tab', { active: selectedDepot.activeTab === 'Activité' }]"
          @click="selectedDepot.activeTab = 'Activité'"
        >
          <i class="ti ti-activity"></i> Activité
        </button>
      </div>

      <div class="tab-content">
        <!-- Onglet Documents -->
        <!-- Onglet Documents -->
    <div v-if="selectedDepot.activeTab === 'Documents'">
      <div class="tab-actions">
        <button class="btn-primary" @click="openAddDocModal">
          <i class="ti ti-plus"></i> Ajouter un document
        </button>
      </div>

      <div v-if="!selectedDepot.documents || selectedDepot.documents.length === 0" class="empty-state">
        <i class="ti ti-file-off"></i>
        <p>Aucun document dans ce dépôt</p>
        <span>Ajoutez des documents depuis votre coffre personnel</span>
      </div>

      <div v-else class="docs-list">
        <div class="doc-item" v-for="doc in selectedDepot.documents" :key="doc.id_doc">
          <i class="ti ti-file-text doc-icon"></i>
          <div class="doc-info">
            <span class="doc-name">{{ doc.nom_doc }}</span>
            <span class="doc-meta">{{ doc.categorie }} • {{ new Date(doc.date_ajout).toLocaleDateString('fr-FR') }}</span>
          </div>
          <span :class="['badge', doc.status === 'Valide' ? 'badge-valide' : 'badge-expire']">
            {{ doc.status }}
          </span>
          <div class="doc-actions-inline">
            <button class="action-btn" title="Aperçu" @click="previewDoc(doc)">
              <i class="ti ti-eye"></i>
            </button>
            <button class="action-btn" title="Télécharger" @click="downloadDoc(doc)">
              <i class="ti ti-download"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

            <!-- Onglet Membres -->
            <div v-if="selectedDepot.activeTab === 'Membres'">
              <table class="members-table">
                <thead>
                  <tr>
                    <th>Utilisateur</th>
                    <th>Rôle / Permission</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="membre in selectedDepot.membres" :key="membre.id">
                    <td>
                      <div class="user-info">
                        <div class="member-avatar">{{ membre.user?.prenom?.charAt(0).toUpperCase() || 'U' }}</div>
                        <div class="user-details">
                          <span class="user-name">{{ membre.user?.prenom }} {{ membre.user?.nom }}</span>
                          <span class="user-email">{{ membre.user?.email }}</span>
                        </div>
                      </div>
                    </td>
                    <td>
                      <select v-model="membre.permission" @change="updatePermission(membre)" class="permission-select">
                        <option value="admin">Admin</option>
                        <option value="ecriture">Écriture</option>
                        <option value="lecture">Lecture</option>
                      </select>
                    </td>
                    <td>
                      <button class="btn-icon text-danger" title="Retirer">
                        <i class="ti ti-user-minus"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

        <!-- Onglet Activité -->
        <div v-if="selectedDepot.activeTab === 'Activité'">
          <div class="empty-state">
            <i class="ti ti-activity"></i>
            <p>Historique d'activité bientôt disponible</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Créer Dépôt -->
    <div v-if="isCreateModalOpen" class="modal-overlay" @click.self="isCreateModalOpen = false">
      <div class="modal-content">
        <h2>Créer un dépôt</h2>
        <div class="form-group">
          <label>Nom du dépôt</label>
          <input type="text" v-model="newDepot.nom_dep" placeholder="Ex: Projet X">
        </div>
        <div class="form-group">
          <label>Type de dépôt</label>
          <select v-model="newDepot.type_dep">
            <option value="Equipe">Équipe</option>
            <option value="Projet">Projet</option>
            <option value="Client">Client</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="isCreateModalOpen = false">Annuler</button>
          <button class="btn-primary" @click="createDepot" :disabled="isCreating || !newDepot.nom_dep">
            {{ isCreating ? 'Création...' : 'Créer' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Inviter Membre -->
    <div v-if="isInviteModalOpen" class="modal-overlay" @click.self="isInviteModalOpen = false">
      <div class="modal-content">
        <h2>Inviter un membre</h2>
        <div class="form-group">
          <label>Email de l'utilisateur</label>
          <input type="email" v-model="newInvite.email" placeholder="utilisateur@exemple.com">
        </div>
        <div class="form-group">
          <label>Permission</label>
          <select v-model="newInvite.permission">
            <option value="lecture">Lecture seule</option>
            <option value="ecriture">Écriture</option>
            <option value="admin">Administrateur</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="btn-cancel" @click="isInviteModalOpen = false">Annuler</button>
          <button class="btn-primary" @click="inviteMember" :disabled="isInviting || !newInvite.email">
            {{ isInviting ? 'Invitation...' : 'Inviter' }}
          </button>
        </div>
      </div>
    </div>
    <!-- Modal Ajouter Document au Dépôt -->
<div v-if="isAddDocModalOpen" class="modal-overlay" @click.self="isAddDocModalOpen = false">
  <div class="modal-content">
    <h2>Ajouter un document au dépôt</h2>
    <div class="form-group">
      <label>Choisir un document</label>
      <select v-model="selectedDocId">
        <option value="">-- Sélectionner un document --</option>
        <option v-for="doc in userDocs" :key="doc.id_doc" :value="doc.id_doc">
          {{ doc.nom_doc }} ({{ doc.categorie }})
        </option>
      </select>
    </div>
    <div class="modal-actions">
      <button class="btn-cancel" @click="isAddDocModalOpen = false">Annuler</button>
      <button class="btn-primary" @click="addDocToDepot" :disabled="isAddingDoc || !selectedDocId">
        {{ isAddingDoc ? 'Ajout...' : 'Ajouter' }}
      </button>
    </div>
  </div>
    </div>
    
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
.depots-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
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

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Grille des dépôts */
.depots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.depot-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.depot-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.depot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.depot-icon {
  width: 48px;
  height: 48px;
  background-color: rgba(244, 180, 0, 0.1);
  color: var(--primary);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.depot-icon.large {
  width: 64px;
  height: 64px;
  font-size: 32px;
}

.depot-type {
  background-color: var(--bg-primary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: var(--text-secondary);
}

.depot-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.depot-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #aaa;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.members-stack {
  display: flex;
  align-items: center;
  margin-top: auto;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--input-border);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  border: 2px solid var(--bg-card);
  margin-left: -8px;
  position: relative;
}

.member-avatar:first-child {
  margin-left: 0;
}

.member-avatar:nth-child(1) { background-color: var(--danger); z-index: 3; }
.member-avatar:nth-child(2) { background-color: #3B82F6; z-index: 2; }
.member-avatar:nth-child(3) { background-color: #10B981; z-index: 1; }

.member-avatar.more {
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  z-index: 0;
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
  padding: 10px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
  transition: all 0.2s;
}

.btn-outline:hover {
  background-color: var(--primary);
  color: var(--bg-primary);
}

/* Vue Intérieure */
.inner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  flex-wrap: wrap;
  gap: 16px;
}

.btn-back {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: color 0.2s;
  width: 100%;
  margin-bottom: -10px;
}

.btn-back:hover {
  color: var(--text-primary);
}

.depot-title-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.depot-title-area h1 {
  font-size: 28px;
  margin: 0 0 4px 0;
}

.tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 24px;
}

.tab {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--text-primary);
}

.tab.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

/* Contenu des onglets */
.docs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: var(--bg-card);
  padding: 16px;
  border-radius: 12px;
}

.doc-item i.doc-icon {
  font-size: 24px;
  color: var(--primary);
}

.doc-actions-inline {
  display: flex;
  gap: 8px;
  margin-left: auto;
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

/* Table Membres */
.members-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
}

.members-table th, .members-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.members-table th {
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

.permission-select {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 6px;
  outline: none;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  padding: 8px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.btn-icon.text-danger {
  color: var(--danger);
}

.btn-icon.text-danger:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Modals */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--bg-card);
  padding: 32px;
  border-radius: 18px;
  width: 100%;
  max-width: 450px;
}

.modal-content h2 {
  margin-top: 0;
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #aaa;
  font-size: 14px;
}

.form-group input, .form-group select {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 12px;
  border-radius: 8px;
  outline: none;
}

.form-group input:focus, .form-group select:focus {
  border-color: var(--primary);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.btn-cancel {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 10px 16px;
}

.btn-cancel:hover {
  color: var(--text-primary);
}

/* Empty State */
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
  margin-bottom: 24px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.skeleton-card {
  height: 200px;
  background-color: var(--bg-card);
  border-radius: 18px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>
