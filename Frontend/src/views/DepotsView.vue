<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import PreviewModal from '../components/documents/PreviewModal.vue'
import Pagination from '../components/shared/Pagination.vue'

const depots = ref([])
const isLoading = ref(true)
const selectedDepot = ref(null)
const activites = ref([])
const isLoadingActivites = ref(false)

const isCreateModalOpen = ref(false)
const newDepot = ref({ nom_dep: '', type_dep: 'Equipe' })
const isCreating = ref(false)

const isInviteModalOpen = ref(false)
const newInvite = ref({ email: '', permission: 'lecture' })
const isInviting = ref(false)

const userDocs = ref([])
const isAddDocModalOpen = ref(false)
const selectedDocId = ref('')
const isAddingDoc = ref(false)

const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)

// Pagination
const depotsPage = ref(1)
const depotsPerPage = 6
const docsPage = ref(1)
const docsPerPage = 10
const activitesPage = ref(1)
const activitesPerPage = 10

const paginatedDepots = computed(() => {
  const start = (depotsPage.value - 1) * depotsPerPage
  return depots.value.slice(start, start + depotsPerPage)
})

const paginatedDocs = computed(() => {
  const docs = selectedDepot.value?.documents || []
  const start = (docsPage.value - 1) * docsPerPage
  return docs.slice(start, start + docsPerPage)
})

const activitesFiltrees = computed(() => {
  if (filtreActivite.value === 'Tous') return activites.value
  return activites.value.filter(a => a.type_action === filtreActivite.value)
})

const paginatedActivites = computed(() => {
  const start = (activitesPage.value - 1) * activitesPerPage
  return activitesFiltrees.value.slice(start, start + activitesPerPage)
})

// Permission de l'utilisateur connecté dans le dépôt sélectionné
const maPermission = computed(() => selectedDepot.value?.permission || 'lecture')
const estAdmin = computed(() => maPermission.value === 'admin')
const peutEcrire = computed(() => maPermission.value === 'admin' || maPermission.value === 'ecriture')

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
    const { data } = await api.get('/api/depots/')
    const updated = data.find(d => d.id_depot === selectedDepot.value.id_depot)
    if (updated) selectedDepot.value = { ...updated, activeTab: 'Documents' }
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || "Erreur lors de l'ajout du document")
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

const fetchActivites = async () => {
  if (!selectedDepot.value) return
  try {
    isLoadingActivites.value = true
    const { data } = await api.get(`/api/depots/${selectedDepot.value.id_depot}/activites`)
    activites.value = data
  } catch (err) {
    console.error('Erreur activités', err)
  } finally {
    isLoadingActivites.value = false
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
  docsPage.value = 1
  activitesPage.value = 1
}

const closeDepot = () => {
  selectedDepot.value = null
  activites.value = []
  fetchDepots()
}

const filtreActivite = ref('Tous')

const typesActivite = [
  { label: 'Tous', value: 'Tous', icon: 'ti-list' },
  { label: 'Téléversements', value: 'upload', icon: 'ti-upload' },
  { label: 'Consultations', value: 'consultation', icon: 'ti-eye' },
  { label: 'Téléchargements', value: 'telechargement', icon: 'ti-download' },
  { label: 'Invitations', value: 'invitation', icon: 'ti-user-plus' },
  { label: 'Adhésions', value: 'adhesion', icon: 'ti-user-check' },
]

const onTabChange = (tab) => {
  selectedDepot.value.activeTab = tab
  if (tab === 'Activité') {
    activitesPage.value = 1
    fetchActivites()
  }
  if (tab === 'Documents') docsPage.value = 1
}

const updatePermission = async (membre) => {
  try {
    await api.patch(`/api/depots/${selectedDepot.value.id_depot}/membres/${membre.user.id_user}/permission?permission=${membre.permission}`)
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || 'Erreur lors de la modification de la permission')
    fetchDepots()
  }
}

const retirerMembre = async (membre) => {
  if (!confirm(`Retirer ${membre.user.prenom} ${membre.user.nom} du dépôt ?`)) return
  try {
    await api.delete(`/api/depots/${selectedDepot.value.id_depot}/membres/${membre.user.id_user}`)
    const { data } = await api.get('/api/depots/')
    const updated = data.find(d => d.id_depot === selectedDepot.value.id_depot)
    if (updated) selectedDepot.value = { ...updated, activeTab: 'Membres' }
    else closeDepot()
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || 'Erreur lors du retrait du membre')
  }
}

const inviteMember = async () => {
  try {
    isInviting.value = true
    await api.post(`/api/depots/${selectedDepot.value.id_depot}/inviter?mail_invite=${encodeURIComponent(newInvite.value.email)}&permission=${newInvite.value.permission || 'lecture'}`)
    isInviteModalOpen.value = false
    newInvite.value = { email: '', permission: 'lecture' }
    fetchDepots()
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || "Erreur lors de l'invitation")
  } finally {
    isInviting.value = false
  }
}

const previewDoc = async (doc) => {
  try {
    const { data, headers } = await api.get(
      `/api/depots/${selectedDepot.value.id_depot}/documents/${doc.id_doc}/telecharger?inline=true`,
      { responseType: 'blob' }
    )
    const type = headers['content-type'] || doc.type_doc || 'application/pdf'
    const blob = new Blob([data], { type })
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewBlob.value = blob
    previewUrl.value = URL.createObjectURL(blob)
    previewName.value = doc.nom_doc
    previewMime.value = type
    isPreviewModalOpen.value = true
  } catch (err) {
    console.error('Erreur prévisualisation', err)
    alert("Impossible de charger l'aperçu.")
  }
}

const downloadDoc = async (doc) => {
  try {
    const { data, headers } = await api.get(
      `/api/depots/${selectedDepot.value.id_depot}/documents/${doc.id_doc}/telecharger`,
      { responseType: 'blob' }
    )
    const mimeType = headers['content-type'] || doc.type_doc || 'application/octet-stream'
    const blob = new Blob([data], { type: mimeType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    let fileName = doc.nom_doc || 'document'
    const cd = headers['content-disposition']
    if (cd) {
      const m = cd.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)["']?/i)
      if (m && m[1]) fileName = decodeURIComponent(m[1])
    }
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err) {
    console.error('Erreur téléchargement', err)
    alert("Impossible de télécharger ce document.")
  }
}

const getActionIcon = (type) => {
  const icons = {
    upload: 'ti-upload text-success',
    consultation: 'ti-eye text-primary',
    telechargement: 'ti-download text-warning',
    invitation: 'ti-user-plus text-primary',
    adhesion: 'ti-user-check text-success',
    retrait_membre: 'ti-user-minus text-danger',
    modification_role: 'ti-pencil text-warning',
    creation_depot: 'ti-folder-plus text-primary',
  }
  return icons[type] || 'ti-activity text-secondary'
}

const formatDate = (d) => {
  if (!d) return ''
  return new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(d))
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

      <div v-else class="depots-grid-wrapper">
        <div class="depots-grid">
          <div class="depot-card" v-for="depot in paginatedDepots" :key="depot.id_depot">
            <div class="depot-header">
              <div class="depot-icon"><i class="ti ti-folder-shared"></i></div>
              <span class="depot-type">{{ depot.type_dep }}</span>
            </div>
            <h3 class="depot-name">{{ depot.nom_dep }}</h3>
            
            <div class="depot-stats">
              <div class="stat-item"><i class="ti ti-file"></i><span>{{ depot.documents?.length || 0 }} documents</span></div>
              <div class="stat-item"><i class="ti ti-users"></i><span>{{ depot.nb_membres || 0 }} membres</span></div>
            </div>

            <div class="members-stack">
              <div 
                class="member-avatar" 
                v-for="(membre, idx) in (depot.membres || []).filter(m => m.statut === 'accepte').slice(0, 3)" 
                :key="idx"
                :title="membre.user?.prenom + (membre.permission === 'admin' ? ' (Admin)' : '')"
              >
                {{ membre.user?.prenom?.charAt(0).toUpperCase() || 'U' }}
                <span v-if="membre.permission === 'admin'" class="crown">👑</span>
              </div>
              <div class="member-avatar more" v-if="(depot.nb_membres || 0) > 3">+{{ depot.nb_membres - 3 }}</div>
            </div>

            <button class="btn-outline" @click="openDepot(depot)">Accéder</button>
          </div>
        </div>
        <Pagination :total="depots.length" :perPage="depotsPerPage" v-model:currentPage="depotsPage" />
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
            <span class="my-role-badge">Mon rôle : {{ maPermission }}</span>
          </div>
        </div>
        <button class="btn-primary" @click="isInviteModalOpen = true" v-if="estAdmin && selectedDepot.activeTab === 'Membres'">
          <i class="ti ti-user-plus"></i> Inviter
        </button>
      </div>

      <div class="tabs">
        <button :class="['tab', { active: selectedDepot.activeTab === 'Documents' }]" @click="onTabChange('Documents')">
          <i class="ti ti-files"></i> Documents
        </button>
        <button :class="['tab', { active: selectedDepot.activeTab === 'Membres' }]" @click="onTabChange('Membres')">
          <i class="ti ti-users"></i> Membres
        </button>
        <button :class="['tab', { active: selectedDepot.activeTab === 'Activité' }]" @click="onTabChange('Activité')">
          <i class="ti ti-activity"></i> Activité
        </button>
      </div>

      <div class="tab-content">
        <!-- Onglet Documents -->
        <div v-if="selectedDepot.activeTab === 'Documents'" class="tab-pane">
          <div class="tab-actions" v-if="peutEcrire">
            <button class="btn-primary" @click="openAddDocModal">
              <i class="ti ti-plus"></i> Ajouter un document
            </button>
          </div>

          <div v-if="!selectedDepot.documents || selectedDepot.documents.length === 0" class="empty-state">
            <i class="ti ti-file-off"></i>
            <p>Aucun document dans ce dépôt</p>
            <span v-if="peutEcrire">Ajoutez des documents depuis votre coffre personnel</span>
          </div>

          <div v-else class="docs-list-wrapper">
            <div class="docs-list">
              <div class="doc-item" v-for="doc in paginatedDocs" :key="doc.id_doc">
                <i class="ti ti-file-text doc-icon"></i>
                <div class="doc-info">
                  <span class="doc-name">{{ doc.nom_doc }}</span>
                  <span class="doc-meta">{{ doc.categorie }} • {{ new Date(doc.date_ajout).toLocaleDateString('fr-FR') }}</span>
                </div>

                <span :class="['badge', doc.status === 'Valide' ? 'badge-valide' : 'badge-expire']">{{ doc.status }}</span>
                <div class="doc-actions-inline">
                  <button class="action-btn" title="Aperçu" @click="previewDoc(doc)"><i class="ti ti-eye"></i></button>
                  <button class="action-btn" title="Télécharger" @click="downloadDoc(doc)" v-if="peutEcrire"><i class="ti ti-download"></i></button>
                </div>
              </div>
            </div>
            <Pagination :total="(selectedDepot.documents || []).length" :perPage="docsPerPage" v-model:currentPage="docsPage" />
          </div>
        </div>

        <!-- Onglet Membres -->
        <div v-if="selectedDepot.activeTab === 'Membres'" class="tab-pane">
          <div class="table-responsive">
          <table class="members-table">
            <thead>
              <tr>
                <th>Utilisateur</th>
                <th>Rôle</th>
                <th v-if="estAdmin">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="membre in selectedDepot.membres" :key="membre.id">
                <td>
                  <div class="user-info">
                    <div class="member-avatar">{{ membre.user?.prenom?.charAt(0).toUpperCase() || 'U' }}</div>
                    <div class="user-details">
                      <span class="user-name">
                        {{ membre.user?.prenom }} {{ membre.user?.nom }}
                        <span v-if="membre.permission === 'admin'" class="admin-badge">Admin</span>
                        <span v-if="membre.statut === 'en_attente'" class="pending-badge">En attente</span>
                      </span>
                      <span class="user-email">{{ membre.user?.mail }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <select 
                    v-if="estAdmin && membre.user?.id_user !== selectedDepot.id_createur"
                    v-model="membre.permission" 
                    @change="updatePermission(membre)" 
                    class="permission-select"
                  >
                    <option value="admin">Admin</option>
                    <option value="ecriture">Écriture</option>
                    <option value="lecture">Lecture</option>
                  </select>
                  <span v-else class="role-label">{{ membre.permission }}</span>
                </td>
                <td v-if="estAdmin">
                  <button 
                    class="btn-icon text-danger" 
                    title="Retirer"
                    @click="retirerMembre(membre)"
                    v-if="membre.user?.id_user !== selectedDepot.id_createur"
                  >
                    <i class="ti ti-user-minus"></i>
                  </button>
                  <span v-else class="role-label" title="Le créateur ne peut pas être retiré">—</span>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>

              <!-- Onglet Activité -->
        <div v-if="selectedDepot.activeTab === 'Activité'" class="tab-pane">
          <div v-if="isLoadingActivites" class="skeleton-list">
            <div class="skeleton-item" v-for="i in 4" :key="i"></div>
          </div>
          <div v-else class="activites-container">
            <!-- Filtres par type -->
            <div class="activite-filters">
              <button
                v-for="type in typesActivite"
                :key="type.value"
                :class="['pill', { active: filtreActivite === type.value }]"
                @click="filtreActivite = type.value; activitesPage = 1"
              >
                <i :class="['ti', type.icon]"></i> {{ type.label }}
              </button>
            </div>

            <div v-if="activitesFiltrees.length === 0" class="empty-state">
              <i class="ti ti-activity"></i>
              <p>Aucune activité pour ce filtre</p>
            </div>

            <div v-else class="activites-list-wrapper">
              <div class="activites-list">
                <div class="activite-item" v-for="(log, idx) in paginatedActivites" :key="idx">
                  <div class="activite-icon">
                    <i :class="['ti', getActionIcon(log.type_action)]"></i>
                  </div>
                  <div class="activite-content">
                    <span class="activite-detail">{{ log.detail || log.type_action }}</span>
                    <span class="activite-doc" v-if="log.nom_document">📄 {{ log.nom_document }}</span>
                    <span class="activite-meta">
                      {{ log.user?.prenom }} {{ log.user?.nom }} • {{ formatDate(log.date_action) }}
                    </span>
                  </div>
                </div>
              </div>
              <Pagination
                :total="activitesFiltrees.length"
                :perPage="activitesPerPage"
                v-model:currentPage="activitesPage"
              />
            </div>
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
          <label>Rôle</label>
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

    <!-- Modal Ajouter Document -->
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
.depots-view { display: flex; flex-direction: column; gap: 24px; height: calc(100vh - 108px); overflow: hidden; }
.depots-list-view { display: flex; flex-direction: column; flex: 1; min-height: 0; overflow: hidden; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-shrink: 0; }
.page-header h1 { font-size: 24px; font-weight: 600; color: var(--text-primary); }

.btn-primary { background-color: var(--primary); color: var(--bg-primary); border: none; padding: 10px 20px; border-radius: 8px; font-size: 15px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background-color 0.2s; }
.btn-primary:hover:not(:disabled) { background-color: var(--primary-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.depots-grid-wrapper { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.depots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; flex: 1; overflow-y: auto; min-height: 0; }
.depot-card { background-color: var(--bg-card); border-radius: 18px; padding: 24px; display: flex; flex-direction: column; gap: 16px; transition: transform 0.2s, box-shadow 0.2s; }
.depot-card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }

.depot-header { display: flex; justify-content: space-between; align-items: flex-start; }
.depot-icon { width: 48px; height: 48px; background-color: rgba(244,180,0,0.1); color: var(--primary); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.depot-icon.large { width: 64px; height: 64px; font-size: 32px; }
.depot-type { background-color: var(--bg-primary); padding: 4px 10px; border-radius: 20px; font-size: 12px; color: var(--text-secondary); }
.depot-name { font-size: 18px; font-weight: 600; color: var(--text-primary); margin: 0; }
.depot-stats { display: flex; gap: 16px; font-size: 13px; color: #aaa; }
.stat-item { display: flex; align-items: center; gap: 6px; }

.members-stack { display: flex; align-items: center; margin-top: auto; position: relative; }
.member-avatar { width: 32px; height: 32px; border-radius: 50%; background-color: var(--input-border); color: var(--text-primary); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; border: 2px solid var(--bg-card); margin-left: -8px; position: relative; }
.member-avatar:first-child { margin-left: 0; }
.member-avatar:nth-child(1) { background-color: var(--danger); z-index: 3; }
.member-avatar:nth-child(2) { background-color: #3B82F6; z-index: 2; }
.member-avatar:nth-child(3) { background-color: #10B981; z-index: 1; }
.member-avatar.more { background-color: var(--bg-primary); color: var(--text-secondary); z-index: 0; }
.crown { position: absolute; top: -6px; right: -4px; font-size: 10px; }

.btn-outline { background-color: transparent; border: 1px solid var(--primary); color: var(--primary); padding: 10px; border-radius: 8px; font-weight: 500; cursor: pointer; margin-top: 8px; transition: all 0.2s; }
.btn-outline:hover { background-color: var(--primary); color: var(--bg-primary); }

.depot-inner-view { display: flex; flex-direction: column; flex: 1; min-height: 0; overflow: hidden; }
.inner-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; flex-wrap: wrap; gap: 16px; flex-shrink: 0; }
.btn-back { background: none; border: none; color: var(--text-secondary); font-size: 15px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: color 0.2s; width: 100%; margin-bottom: -10px; }
.btn-back:hover { color: var(--text-primary); }
.depot-title-area { display: flex; align-items: center; gap: 16px; }
.depot-title-area h1 { font-size: 28px; margin: 0 0 4px 0; }
.my-role-badge { display: inline-block; background-color: rgba(244,180,0,0.15); color: var(--primary); padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-left: 8px; }

.tabs { display: flex; border-bottom: 1px solid var(--border-color); margin-bottom: 24px; }
.tab { background: none; border: none; color: var(--text-secondary); padding: 12px 24px; font-size: 15px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid transparent; transition: all 0.2s; }
.tab:hover { color: var(--text-primary); }
.tab.active { color: var(--primary); border-bottom-color: var(--primary); }

.tab-content { flex: 1; min-height: 0; overflow: hidden; display: flex; flex-direction: column; }
.tab-pane { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.activites-container { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.tab-actions { margin-bottom: 16px; flex-shrink: 0; }
.docs-list-wrapper { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.docs-list { display: flex; flex-direction: column; gap: 8px; flex: 1; overflow-y: auto; min-height: 0; }
.doc-item { display: flex; align-items: center; gap: 12px; background-color: var(--bg-card); padding: 16px; border-radius: 12px; }
.doc-item i.doc-icon { font-size: 24px; color: var(--primary); }
.doc-info { display: flex; flex-direction: column; flex: 1; }
.doc-name { font-weight: 500; color: var(--text-primary); }
.doc-meta { font-size: 13px; color: var(--text-secondary); }
.doc-actions-inline { display: flex; gap: 8px; margin-left: auto; }
.action-btn { background: none; border: none; width: 36px; height: 36px; border-radius: 8px; color: var(--text-secondary); display: flex; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; transition: all 0.2s; }
.action-btn:hover { background-color: rgba(255,255,255,0.05); color: var(--text-primary); }

.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
.badge-valide { background-color: rgba(16,185,129,0.1); color: #10B981; }
.badge-expire { background-color: rgba(239,68,68,0.1); color: var(--danger); }

.members-table { width: 100%; border-collapse: collapse; background-color: var(--bg-card); border-radius: 12px; overflow: hidden; }
.members-table th, .members-table td { padding: 16px; text-align: left; border-bottom: 1px solid var(--border-color); }
.members-table th { color: var(--text-secondary); font-size: 13px; font-weight: 500; text-transform: uppercase; }
.user-info { display: flex; align-items: center; gap: 12px; }
.user-details { display: flex; flex-direction: column; }
.user-name { color: var(--text-primary); font-weight: 500; display: flex; align-items: center; gap: 8px; }
.user-email { color: var(--text-secondary); font-size: 13px; }
.admin-badge { background-color: rgba(244,180,0,0.15); color: var(--primary); padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; }
.pending-badge { background-color: rgba(156,163,175,0.15); color: #9CA3AF; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
.role-label { color: var(--text-secondary); font-size: 14px; }
.permission-select { background-color: var(--bg-primary); border: 1px solid var(--input-border); color: var(--text-primary); padding: 8px 12px; border-radius: 6px; outline: none; }
.btn-icon { background: none; border: none; cursor: pointer; font-size: 18px; padding: 8px; border-radius: 8px; transition: background-color 0.2s; }
.btn-icon.text-danger { color: var(--danger); }
.btn-icon.text-danger:hover { background-color: rgba(239,68,68,0.1); }

.activites-list-wrapper { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.activites-list { display: flex; flex-direction: column; gap: 8px; flex: 1; overflow-y: auto; min-height: 0; }
.activite-item { display: flex; align-items: flex-start; gap: 12px; background-color: var(--bg-card); padding: 16px; border-radius: 12px; }
.activite-icon { width: 40px; height: 40px; background-color: var(--bg-primary); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0; }
.activite-content { display: flex; flex-direction: column; gap: 4px; }
.activite-detail { color: var(--text-primary); font-size: 15px; }
.activite-doc { color: var(--primary); font-size: 13px; }
.activite-meta { color: var(--text-secondary); font-size: 12px; }
.text-success { color: #10B981; }
.text-primary { color: var(--primary); }
.text-warning { color: #F59E0B; }
.text-danger { color: var(--danger); }
.text-secondary { color: var(--text-secondary); }
.activite-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 30px;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill:hover {
  background-color: rgba(244, 180, 0, 0.05);
  color: var(--text-primary);
  border-color: rgba(244, 180, 0, 0.3);
}

.pill.active {
  background-color: rgba(244, 180, 0, 0.15);
  color: var(--primary);
  border-color: var(--primary);
}

.pill i {
  font-size: 16px;
}

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px); }
.modal-content { background-color: var(--bg-card); padding: 32px; border-radius: 18px; width: 100%; max-width: 450px; }
.modal-content h2 { margin-top: 0; margin-bottom: 24px; }
.form-group { margin-bottom: 16px; display: flex; flex-direction: column; gap: 8px; }
.form-group label { color: #aaa; font-size: 14px; }
.form-group input, .form-group select { background-color: var(--bg-primary); border: 1px solid var(--input-border); color: var(--text-primary); padding: 12px; border-radius: 8px; outline: none; }
.form-group input:focus, .form-group select:focus { border-color: var(--primary); }
.modal-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 32px; }
.btn-cancel { background: none; border: none; color: var(--text-secondary); cursor: pointer; padding: 10px 16px; }
.btn-cancel:hover { color: var(--text-primary); }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center; color: var(--text-secondary); background-color: var(--bg-card); border-radius: 18px; }
.empty-state i { font-size: 64px; color: var(--input-border); margin-bottom: 16px; }
.empty-state h2 { color: var(--text-primary); margin-bottom: 8px; }
.empty-state p { margin-bottom: 24px; }

.skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 24px; }
.skeleton-card { height: 200px; background-color: var(--bg-card); border-radius: 18px; animation: pulse 1.5s infinite; }
.skeleton-list { display: flex; flex-direction: column; gap: 8px; }
.skeleton-item { height: 70px; background-color: var(--bg-card); border-radius: 12px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

/* Responsive — Mobile */
@media (max-width: 767px) {
  .depots-view { height: auto; min-height: calc(100vh - 108px); }
  .depots-grid { grid-template-columns: 1fr; }
  .depot-title-area { flex-direction: column; align-items: flex-start; gap: 8px; }
  .depot-title-area h1 { font-size: 22px; }
  .tabs { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .tab { padding: 12px 16px; font-size: 14px; white-space: nowrap; }
  .doc-item { flex-wrap: wrap; gap: 8px; }
  .doc-actions-inline { width: 100%; justify-content: flex-end; }
  .inner-header { flex-direction: column; align-items: flex-start; }
  .activite-item { flex-direction: column; }
}

/* Responsive — Tablet */
@media (min-width: 768px) and (max-width: 1024px) {
  .depots-grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }
}
</style>