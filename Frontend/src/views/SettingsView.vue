<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import PreviewModal from '../components/documents/PreviewModal.vue'

const authStore = useAuthStore()
const activeTab = ref('Profil')

const user = ref({ ...authStore.user } || {})
const isDarkMode = ref(true)
const offlineDocs = ref([])
const isLoadingOffline = ref(false)
const is2FAEnabled = ref(authStore.user?.deux_fa_active || false)

const saveSuccess = ref(false)
const isPasswordModalOpen = ref(false)
const pwdForm = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const pwdMsg = ref('')

// Données de connexion
const lastIp = ref(localStorage.getItem('last_ip') || 'Non disponible')
const lastLogin = ref(localStorage.getItem('last_login') || 'Non disponible')
const currentIp = ref('Chargement...') // Pour afficher l'IP actuelle de l'utilisateur

const isPreviewModalOpen = ref(false)
const previewUrl = ref('')
const previewName = ref('')
const previewMime = ref('')
const previewBlob = ref(null)

onMounted(async () => {
  isDarkMode.value = localStorage.getItem('theme') !== 'light'

  // Récupérer l'IP via une API publique gratuite
  try {
    const response = await fetch('https://api.ipify.org?format=json')
    const data = await response.json()
    currentIp.value = data.ip
  } catch (err) {
    currentIp.value = lastIp.value || 'Non disponible'
  }

  if (activeTab.value === 'Hors ligne') {
    fetchOfflineDocs()

  }
})

const fetchOfflineDocs = async () => {
  try {
    isLoadingOffline.value = true
    const { data } = await api.get('/api/documents/')
    offlineDocs.value = data.filter(d => d.est_critique).slice(0, 3)
  } catch (err) {
    console.error('Erreur lors de la récupération des documents hors ligne', err)
  } finally {
    isLoadingOffline.value = false
  }
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.remove('light-mode')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.add('light-mode')
    localStorage.setItem('theme', 'light')
  }
}

const tabs = ['Profil', 'Sécurité', 'Hors ligne', 'Apparence']

const handleTabChange = (tab) => {
  activeTab.value = tab
  if (tab === 'Hors ligne') {
    fetchOfflineDocs()
  }
}

const saveProfile = () => {
  if (authStore.user) {
    authStore.user.prenom = user.value.prenom
    authStore.user.nom = user.value.nom
    localStorage.setItem('user', JSON.stringify(authStore.user))
    saveSuccess.value = true
    setTimeout(() => saveSuccess.value = false, 2000)
  }
}

const changePassword = async () => {
  if (pwdForm.value.newPassword !== pwdForm.value.confirmPassword) {
    pwdMsg.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  
  try {
    await api.post('/api/auth/change-password', {
      old_password: pwdForm.value.oldPassword,
      new_password: pwdForm.value.newPassword,
      confirm_password: pwdForm.value.confirmPassword
    })
    pwdMsg.value = 'Mot de passe mis à jour avec succès.'
    setTimeout(() => {
      isPasswordModalOpen.value = false
      pwdForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
      pwdMsg.value = ''
    }, 2000)
  } catch (err) {
    console.error(err)
    pwdMsg.value = err.response?.data?.detail || 'Erreur lors du changement de mot de passe.'
  }
}

const toggle2FA = async () => {
  try {
    const { data } = await api.patch('/api/auth/toggle-2fa')
    is2FAEnabled.value = data.deux_fa_active
    // Mettre à jour le store
    if (authStore.user) {
      authStore.user.deux_fa_active = data.deux_fa_active
      localStorage.setItem('user', JSON.stringify(authStore.user))
    }
  } catch (err) {
    console.error(err)
    alert('Erreur lors de la modification du 2FA')
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
  <div class="settings-view">
    <div class="page-header">
      <h1>Paramètres</h1>
    </div>

    <div class="settings-layout">
      <!-- Navigation latérale des paramètres -->
      <div class="settings-nav">
        <button 
          v-for="tab in tabs" 
          :key="tab"
          :class="['nav-item', { active: activeTab === tab }]"
          @click="handleTabChange(tab)"
        >
          <i v-if="tab === 'Profil'" class="ti ti-user"></i>
          <i v-else-if="tab === 'Sécurité'" class="ti ti-shield-lock"></i>
          <i v-else-if="tab === 'Hors ligne'" class="ti ti-wifi-off"></i>
          <i v-else-if="tab === 'Apparence'" class="ti ti-palette"></i>
          {{ tab }}
        </button>
      </div>

      <!-- Contenu des paramètres -->
      <div class="settings-content">
        
        <!-- Profil -->
        <div v-if="activeTab === 'Profil'" class="settings-section">
          <h2>Profil Utilisateur</h2>
          <div class="profile-card">
            <div class="avatar-large">{{ user.prenom?.charAt(0) || 'U' }}</div>
            <div class="profile-info">
              <div class="form-group">
                <label>Nom</label>
                <input type="text" v-model="user.nom">
              </div>
              <div class="form-group">
                <label>Prénom</label>
                <input type="text" v-model="user.prenom">
              </div>
              <div class="form-group">
                <label>Adresse Email</label>
                <input type="email" :value="user.mail || user.email || 'john@example.com'" readonly disabled>
                <p class="help-text">L'adresse email ne peut pas être modifiée directement.</p>
              </div>
              
              <div class="profile-actions">
                <button class="btn-primary" @click="saveProfile">Enregistrer</button>
                <span v-if="saveSuccess" class="success-text"><i class="ti ti-check"></i> Sauvegardé</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sécurité -->
        <div v-if="activeTab === 'Sécurité'" class="settings-section">
          <h2>Sécurité</h2>
          
          <div class="setting-card">
            <div class="setting-header">
              <div>
                <h3>Authentification à deux facteurs (2FA)</h3>
                <p>Ajoutez une couche de sécurité supplémentaire à votre compte.</p>
              </div>
              <div class="toggle-switch" :class="{ active: is2FAEnabled }" @click="toggle2FA">
                <div class="toggle-knob"></div>
              </div>
            </div>
          </div>

          <div class="setting-card mt-4">
            <div class="setting-header">
              <div>
                <h3>Mot de passe</h3>
                <p>Modifiez votre mot de passe pour sécuriser votre compte.</p>
              </div>
              <button class="btn-secondary" @click="isPasswordModalOpen = true">Changer</button>
            </div>
          </div>

          <div class="setting-card mt-4">
            <h3>Historique de connexion</h3>
            <div class="history-list">
              <div class="history-item">
                <div class="history-icon"><i class="ti ti-device-desktop"></i></div>
                <div class="history-details">
                  <span class="device-name">Windows 11 - Chrome</span>
                  <span class="device-meta">Actuellement connecté • IP: {{ currentIp }}</span>
                </div>
              </div>
              <div class="history-item" v-if="lastIp !== 'Non disponible' || lastLogin !== 'Non disponible'">
                <div class="history-icon"><i class="ti ti-history"></i></div>
                <div class="history-details">
                  <span class="device-name">Dernière connexion</span>
                  <span class="device-meta">IP: {{ lastIp }} • {{ lastLogin }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Hors ligne -->
        <div v-if="activeTab === 'Hors ligne'" class="settings-section">
          <h2>Mode Hors Ligne</h2>
          <p class="section-desc">Ces documents sont marqués comme critiques et sont disponibles même sans connexion internet.</p>
          
          <div v-if="isLoadingOffline" class="skeleton-list">
            <div class="skeleton-item" v-for="i in 3" :key="i"></div>
          </div>
          
          <div v-else-if="offlineDocs.length === 0" class="empty-state">
            <i class="ti ti-wifi-off"></i>
            <h3>Aucun document hors ligne</h3>
            <p>Marquez des documents comme "critiques" pour y accéder hors ligne (max 3).</p>
          </div>
          
          <div v-else class="offline-list">
            <div class="offline-item" v-for="doc in offlineDocs" :key="doc.id_doc">
              <i class="ti ti-file-text"></i>
              <div class="doc-info">
                <span class="doc-name">{{ doc.nom_doc }}</span>
                <span class="doc-cat">{{ doc.categorie }}</span>
              </div>
              <div class="offline-actions">
                <span class="badge-offline">Sauvegardé</span>
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

        <!-- Apparence -->
        <div v-if="activeTab === 'Apparence'" class="settings-section">
          <h2>Apparence</h2>
          
          <div class="setting-card">
            <div class="setting-header">
              <div>
                <h3>Thème de l'application</h3>
                <p>Choisissez entre le thème clair et le thème sombre.</p>
              </div>
            </div>
            
            <div class="theme-options">
              <div class="theme-card" :class="{ active: !isDarkMode }" @click="!isDarkMode ? null : toggleTheme()">
                <div class="theme-preview light-preview">
                  <div class="preview-header"></div>
                  <div class="preview-body">
                    <div class="preview-sidebar"></div>
                    <div class="preview-content"></div>
                  </div>
                </div>
                <span>Thème Clair</span>
              </div>
              
              <div class="theme-card" :class="{ active: isDarkMode }" @click="isDarkMode ? null : toggleTheme()">
                <div class="theme-preview dark-preview">
                  <div class="preview-header"></div>
                  <div class="preview-body">
                    <div class="preview-sidebar"></div>
                    <div class="preview-content"></div>
                  </div>
                </div>
                <span>Thème Sombre</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
    
    <!-- Modal Mot de passe -->
    <div class="modal-overlay" v-if="isPasswordModalOpen" @click.self="isPasswordModalOpen = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Changer le mot de passe</h2>
          <button class="btn-close" @click="isPasswordModalOpen = false"><i class="ti ti-x"></i></button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Ancien mot de passe</label>
            <input type="password" v-model="pwdForm.oldPassword">
          </div>
          <div class="form-group">
            <label>Nouveau mot de passe</label>
            <input type="password" v-model="pwdForm.newPassword">
          </div>
          <div class="form-group">
            <label>Confirmer le nouveau mot de passe</label>
            <input type="password" v-model="pwdForm.confirmPassword">
          </div>
          <p v-if="pwdMsg" class="form-msg">{{ pwdMsg }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="isPasswordModalOpen = false">Annuler</button>
          <button class="btn-primary" @click="changePassword">Enregistrer</button>
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
.settings-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

@media (min-width: 768px) {
  .settings-layout {
    flex-direction: row;
    align-items: flex-start;
  }
}

/* Nav Latérale */
.settings-nav {
  display: flex;
  flex-direction: row;
  overflow-x: auto;
  gap: 8px;
  background-color: var(--bg-card);
  padding: 12px;
  border-radius: 12px;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .settings-nav {
    flex-direction: column;
    width: 250px;
    padding: 16px;
  }
}

.nav-item {
  background: none;
  border: none;
  color: var(--text-secondary);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-item i {
  font-size: 20px;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.nav-item.active {
  background-color: rgba(244, 180, 0, 0.1);
  color: var(--primary);
}

/* Contenu Principal */
.settings-content {
  flex: 1;
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 32px;
  min-height: 500px;
}

.settings-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: 24px;
}

/* Profil */
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

@media (min-width: 640px) {
  .profile-card {
    flex-direction: row;
  }
}

.avatar-large {
  width: 100px;
  height: 100px;
  background-color: var(--primary);
  color: var(--bg-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 600;
  flex-shrink: 0;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 500px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: #aaa;
  font-size: 14px;
}

.form-group input {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--input-border);
  color: var(--text-secondary);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
}

.help-text {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
}

/* Paramètres (Cartes) */
.setting-card {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px;
}

.mt-4 {
  margin-top: 16px;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-header h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.setting-header p {
  color: var(--text-secondary);
  font-size: 13px;
  margin: 0;
}

/* Toggle Switch */
.toggle-switch {
  width: 48px;
  height: 24px;
  background-color: var(--input-border);
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s;
}

.toggle-switch.active {
  background-color: var(--primary);
}

.toggle-knob {
  width: 20px;
  height: 20px;
  background-color: var(--text-primary);
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s;
}

.toggle-switch.active .toggle-knob {
  transform: translateX(24px);
}

/* Historique */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 16px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background-color: rgba(255, 255, 255, 0.02);
  border-radius: 8px;
}

.history-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.history-details {
  display: flex;
  flex-direction: column;
}

.device-name {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 15px;
}

.device-meta {
  color: var(--text-secondary);
  font-size: 13px;
}

/* Thèmes */
.theme-options {
  display: flex;
  gap: 24px;
  margin-top: 24px;
}

.theme-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.theme-card span {
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.theme-card.active span {
  color: var(--primary);
}

.theme-preview {
  width: 140px;
  height: 100px;
  border-radius: 8px;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: border-color 0.2s;
}

.theme-card.active .theme-preview {
  border-color: var(--primary);
}

.light-preview {
  background-color: #f5f5f5;
  border-color: #ddd;
}
.light-preview .preview-header { background-color: var(--text-primary); border-bottom: 1px solid #eee; }
.light-preview .preview-sidebar { background-color: var(--text-primary); border-right: 1px solid #eee; }

.dark-preview {
  background-color: var(--bg-primary);
  border-color: var(--input-border);
}
.dark-preview .preview-header { background-color: var(--bg-card); border-bottom: 1px solid var(--border-color); }
.dark-preview .preview-sidebar { background-color: #1a1a1a; border-right: 1px solid var(--border-color); }

.preview-header {
  height: 20px;
  width: 100%;
}

.preview-body {
  display: flex;
  flex: 1;
}

.preview-sidebar {
  width: 30px;
  height: 100%;
}

.preview-content {
  flex: 1;
}

/* Hors ligne */
.offline-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.offline-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background-color: var(--bg-primary);
  padding: 16px;
  border-radius: 12px;
  border-left: 3px solid var(--primary);
}

.offline-item i.ti-file-text {
  font-size: 24px;
  color: var(--primary);
}

.doc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.doc-name {
  color: var(--text-primary);
  font-weight: 500;
}

.doc-cat {
  color: var(--text-secondary);
  font-size: 13px;
}

.badge-offline {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.offline-actions {
  display: flex;
  align-items: center;
  gap: 8px;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  background-color: var(--bg-primary);
  border-radius: 12px;
}

.empty-state i {
  font-size: 48px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-state h3 {
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  color: var(--text-secondary);
}

.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 60px;
  background-color: var(--bg-primary);
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}

/* Nouvelles classes pour Profil */
.profile-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
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
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-secondary {
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: var(--bg-primary);
}

.success-text {
  color: var(--success);
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Modale */
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
  max-width: 480px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-msg {
  color: var(--primary);
  font-size: 14px;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
