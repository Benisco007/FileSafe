<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTheme } from '@/composables/useTheme'

// ─── État de chargement ───────────────────────────────────────────
const isLoading = ref(true)

// ─── Onglet actif ─────────────────────────────────────────────────
const activeTab = ref('Profil')
const tabs = ['Profil', 'Sécurité', 'Notifications', 'Hors ligne', 'Apparence']

// ─── Profil ───────────────────────────────────────────────────────
const profile = ref({
  nom: '',
  prenom: '',
  email: ''
})

// ─── Sécurité ─────────────────────────────────────────────────────
const twoFAEnabled = ref(true)
const sessions = ref([])

// ─── Notifications ────────────────────────────────────────────────
const notificationSettings = ref({
  emailAlerts: true,
  shareNotifications: true,
  accountActivity: true
})

// ─── Hors ligne ───────────────────────────────────────────────────
const offlineDocs = ref([])

// ─── Apparence ────────────────────────────────────────────────────
// Même état de thème partagé que le reste de l'application :
// changer le thème ici s'applique donc partout, et inversement.
const { isDark, toggleTheme } = useTheme()

const themeIcon = computed(() => (isDark.value ? 'ti-moon' : 'ti-sun'))

// ─── Helpers ──────────────────────────────────────────────────────
const documentIconClass = (type) => {
  if (type === 'pdf') return 'ti-file-type-pdf'
  if (type === 'image') return 'ti-photo'
  if (type === 'word') return 'ti-file-type-doc'
  if (type === 'excel') return 'ti-file-spreadsheet'
  if (type === 'identity') return 'ti-id-badge'
  if (type === 'passport') return 'ti-passport'
  if (type === 'certificate') return 'ti-certificate'
  return 'ti-file-text'
}

const removeOfflineDoc = async (id) => {
  // TODO: appeler DELETE /api/offline/${id}
  offlineDocs.value = offlineDocs.value.filter((doc) => doc.id !== id)
}

const terminateSession = async (id) => {
  // TODO: appeler DELETE /api/sessions/${id}
  sessions.value = sessions.value.filter((s) => s.id !== id)
}

const tabIconClass = (tab) => {
  const map = {
    Profil: 'ti-user',
    Sécurité: 'ti-shield',
    Notifications: 'ti-bell',
    'Hors ligne': 'ti-wifi-off',
    Apparence: 'ti-palette'
  }
  return map[tab]
}

// ─── Chargement des données ───────────────────────────────────────
const fetchProfile = async () => {
  // TODO: remplacer par → const res = await fetch('/api/me')
  // profile.value = await res.json()
}

const fetchSessions = async () => {
  // TODO: remplacer par → const res = await fetch('/api/sessions')
  // sessions.value = await res.json()
}

const fetchOfflineDocs = async () => {
  // TODO: remplacer par → const res = await fetch('/api/offline')
  // offlineDocs.value = await res.json()
}

// ─── Déclenchement au montage ─────────────────────────────────────
onMounted(async () => {
  try {
    await Promise.all([fetchProfile(), fetchSessions(), fetchOfflineDocs()])
  } catch (error) {
    console.error('Erreur chargement paramètres :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="settings">
    <!-- EN-TÊTE -->
    <div class="header">
      <div class="header-left">
        <h1>Paramètres</h1>
        <p class="subtitle">Personnalisez votre compte et vos préférences</p>
      </div>
      <div class="header-right">
        <button class="btn-icon" :title="isDark ? 'Mode clair' : 'Mode sombre'" @click="toggleTheme">
          <i :class="'ti ' + themeIcon"></i>
        </button>
      </div>
    </div>

    <!-- SKELETON -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton skeleton-nav"></div>
      <div class="skeleton skeleton-content"></div>
    </div>

    <!-- CONTENU -->
    <div v-else class="settings-layout">
      <!-- NAVIGATION LATÉRALE -->
      <nav class="settings-nav card">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="nav-tab"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          <i :class="'ti ' + tabIconClass(tab)"></i>
          <span>{{ tab }}</span>
        </button>
      </nav>

      <!-- PANNEAU DE CONTENU -->
      <div class="settings-panel card">
        <!-- PROFIL -->
        <div v-if="activeTab === 'Profil'" class="panel-section">
          <h2 class="panel-title">Profil</h2>

          <div class="avatar-edit">
            <div class="avatar-large">BH</div>
            <button class="btn-edit">
              <i class="ti ti-camera"></i> Modifier la photo
            </button>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Nom</label>
              <input v-model="profile.nom" type="text" placeholder="Votre nom" />
            </div>
            <div class="form-group">
              <label>Prénom</label>
              <input v-model="profile.prenom" type="text" placeholder="Votre prénom" />
            </div>
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="profile.email" type="email" placeholder="Votre adresse email" />
          </div>

          <button class="btn-save">Enregistrer les modifications</button>
        </div>

        <!-- SÉCURITÉ -->
        <div v-if="activeTab === 'Sécurité'" class="panel-section">
          <h2 class="panel-title">Sécurité</h2>

          <div class="toggle-row">
            <div>
              <p class="toggle-label">Authentification à deux facteurs</p>
              <p class="toggle-sublabel">Protection renforcée de votre compte</p>
            </div>
            <div
              class="toggle-switch"
              :class="{ active: twoFAEnabled }"
              @click="twoFAEnabled = !twoFAEnabled"
            ></div>
          </div>

          <button class="btn-ghost">
            <i class="ti ti-lock"></i> Changer le mot de passe
          </button>

          <h3 class="subsection-title">Connexions récentes</h3>
          <div class="sessions-list">
            <div
              v-for="session in sessions"
              :key="session.id"
              class="session-row"
            >
              <div class="session-info">
                <i class="ti ti-device-desktop session-device-icon"></i>
                <div>
                  <p class="session-device">
                    {{ session.appareil }}
                    <span v-if="session.actuel" class="badge badge-success">Actuel</span>
                  </p>
                  <p class="session-meta">{{ session.ip }} • {{ session.date }}</p>
                </div>
              </div>
              <button
                v-if="!session.actuel"
                class="btn-action"
                @click="terminateSession(session.id)"
              >
                <i class="ti ti-x"></i>
              </button>
            </div>

            <div v-if="sessions.length === 0" class="empty-state small">
              <i class="ti ti-device-desktop empty-icon"></i>
              <p>Aucune connexion récente</p>
            </div>
          </div>
        </div>

        <!-- NOTIFICATIONS -->
        <div v-if="activeTab === 'Notifications'" class="panel-section">
          <h2 class="panel-title">Notifications</h2>

          <div class="toggle-row">
            <div>
              <p class="toggle-label">Alertes par email</p>
              <p class="toggle-sublabel">Recevoir les alertes d'expiration par email</p>
            </div>
            <div
              class="toggle-switch"
              :class="{ active: notificationSettings.emailAlerts }"
              @click="notificationSettings.emailAlerts = !notificationSettings.emailAlerts"
            ></div>
          </div>

          <div class="toggle-row">
            <div>
              <p class="toggle-label">Notifications de partage</p>
              <p class="toggle-sublabel">Être informé lorsqu'un document est consulté</p>
            </div>
            <div
              class="toggle-switch"
              :class="{ active: notificationSettings.shareNotifications }"
              @click="notificationSettings.shareNotifications = !notificationSettings.shareNotifications"
            ></div>
          </div>

          <div class="toggle-row">
            <div>
              <p class="toggle-label">Activité du compte</p>
              <p class="toggle-sublabel">Nouvelles connexions et modifications</p>
            </div>
            <div
              class="toggle-switch"
              :class="{ active: notificationSettings.accountActivity }"
              @click="notificationSettings.accountActivity = !notificationSettings.accountActivity"
            ></div>
          </div>
        </div>

        <!-- HORS LIGNE -->
        <div v-if="activeTab === 'Hors ligne'" class="panel-section">
          <h2 class="panel-title">Documents hors ligne</h2>

          <p class="offline-intro">
            Ces documents sont disponibles même sans connexion internet.
            Ils sont chiffrés sur votre appareil.
          </p>

          <div v-if="offlineDocs.length === 0" class="empty-state small">
            <i class="ti ti-wifi-off empty-icon"></i>
            <p>Aucun document hors ligne</p>
            <span>Ajoutez vos documents critiques pour y accéder hors ligne.</span>
          </div>

          <div v-else class="offline-list">
            <div
              v-for="doc in offlineDocs"
              :key="doc.id"
              class="offline-row"
            >
              <div class="doc-preview">
                <i :class="'ti ' + documentIconClass(doc.type)"></i>
              </div>
              <div class="doc-info">
                <p class="doc-name">{{ doc.nom }}</p>
                <p class="doc-desc">{{ doc.description }}</p>
              </div>
              <div class="doc-actions">
                <button class="btn-edit-small">
                  <i class="ti ti-pencil"></i> Modifier
                </button>
                <button class="btn-remove-small" @click="removeOfflineDoc(doc.id)">
                  <i class="ti ti-trash"></i> Retirer
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- APPARENCE -->
        <div v-if="activeTab === 'Apparence'" class="panel-section">
          <h2 class="panel-title">Apparence</h2>

          <p class="appearance-intro">Choisissez le thème qui vous convient.</p>

          <div class="theme-grid">
            <div
              class="theme-card dark"
              :class="{ active: isDark }"
              @click="isDark = true"
            >
              <i class="ti ti-moon theme-card-icon"></i>
              <p class="theme-card-label">Mode sombre</p>
            </div>

            <div
              class="theme-card light"
              :class="{ active: !isDark }"
              @click="isDark = false"
            >
              <i class="ti ti-sun theme-card-icon"></i>
              <p class="theme-card-label">Mode clair</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings {
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
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
}

.skeleton {
  background: linear-gradient(90deg, #1E1E1E 25%, #2a2a2a 50%, #1E1E1E 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 18px;
}

.skeleton-nav {
  height: 300px;
}

.skeleton-content {
  height: 500px;
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

/* LAYOUT PARAMÈTRES */
.settings-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 24px;
}

/* NAVIGATION */
.settings-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  height: fit-content;
}

.nav-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: #888;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.nav-tab:hover {
  background: rgba(244, 180, 0, 0.06);
  color: white;
}

.nav-tab.active {
  background: rgba(244, 180, 0, 0.12);
  color: #F4B400;
  border-left: 3px solid #F4B400;
}

/* PANNEAU */
.settings-panel {
  min-height: 500px;
}

.panel-section {
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.panel-title {
  font-size: 17px;
  font-weight: 500;
  margin-bottom: 24px;
}

.subsection-title {
  font-size: 15px;
  font-weight: 500;
  margin: 28px 0 16px;
}

/* FORMULAIRES */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.form-group label {
  font-size: 13px;
  color: #888;
}

.form-group input {
  background: rgba(255, 255, 255, 0.04);
  border: 0.5px solid #2a2a2a;
  border-radius: 10px;
  padding: 12px 14px;
  color: white;
  font-size: 14px;
  outline: none;
}

.form-group input:focus {
  border-color: #F4B400;
}

/* AVATAR */
.avatar-edit {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.avatar-large {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #F4B400;
  color: #121212;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 500;
}

/* BOUTONS */
.btn-save {
  background: #F4B400;
  color: #121212;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
}

.btn-save:hover {
  background: #D89E00;
}

.btn-edit {
  background: transparent;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 13px;
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

.btn-ghost {
  background: transparent;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 24px;
}

.btn-ghost:hover {
  border-color: #F4B400;
  color: #F4B400;
}

/* TOGGLES */
.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  margin-bottom: 12px;
}

.toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.toggle-sublabel {
  font-size: 12px;
  color: #888;
  margin-top: 3px;
}

.toggle-switch {
  width: 46px;
  height: 24px;
  background: #333;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
  flex-shrink: 0;
}

.toggle-switch.active {
  background: #F4B400;
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.2s ease;
}

.toggle-switch.active::after {
  transform: translateX(22px);
}

/* SESSIONS */
.sessions-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.session-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.session-device-icon {
  color: #F4B400;
  font-size: 22px;
}

.session-device {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.session-meta {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

.btn-action {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 18px;
  padding: 6px;
  border-radius: 6px;
}

.btn-action:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

/* HORS LIGNE */
.offline-intro {
  font-size: 13px;
  color: #888;
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 600px;
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
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

.doc-preview {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
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
  margin-bottom: 2px;
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

.btn-edit-small,
.btn-remove-small {
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

.btn-edit-small {
  background: transparent;
  color: #aaa;
  border: 0.5px solid #333;
}

.btn-edit-small:hover {
  border-color: #F4B400;
  color: #F4B400;
}

.btn-remove-small {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.btn-remove-small:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* APPARENCE */
.appearance-intro {
  font-size: 13px;
  color: #888;
  margin-bottom: 20px;
}

.theme-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  max-width: 500px;
}

.theme-card {
  padding: 28px;
  border-radius: 16px;
  border: 2px solid transparent;
  cursor: pointer;
  text-align: center;
  transition: all 0.15s ease;
}

.theme-card.active {
  border-color: #F4B400;
}

.theme-card.dark {
  background: #121212;
  color: white;
  border: 0.5px solid #333;
}

.theme-card.light {
  background: #F5F5F5;
  color: #2C2C2C;
  border: 0.5px solid #E0E0E0;
}

.theme-card-icon {
  font-size: 32px;
  margin-bottom: 10px;
  display: block;
}

.theme-card-label {
  font-size: 14px;
  font-weight: 500;
}

/* BADGES */
.badge {
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 20px;
  margin-left: 8px;
}

.badge-success {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

/* ÉTAT VIDE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 0;
  gap: 8px;
  color: #555;
}

.empty-state.small {
  padding: 28px 0;
}

.empty-icon {
  font-size: 32px;
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
  max-width: 300px;
}

/* RESPONSIVE */
@media (max-width: 900px) {
  .settings-layout {
    grid-template-columns: 1fr;
  }

  .loading-state {
    grid-template-columns: 1fr;
  }

  .settings-nav {
    flex-direction: row;
    overflow-x: auto;
  }

  .nav-tab {
    white-space: nowrap;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .settings {
    padding: 20px;
  }

  .theme-grid {
    grid-template-columns: 1fr;
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
