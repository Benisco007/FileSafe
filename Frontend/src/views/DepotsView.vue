<script setup>
import { ref, onMounted } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()

// ─── État de chargement ───────────────────────────────────────────
const isLoading = ref(true)

// ─── Navigation du dépôt ──────────────────────────────────────────
const selectedVault = ref(null)
const activeTab = ref('Documents')
const tabs = ['Documents', 'Membres', 'Activité']

// ─── Liste des dépôts ─────────────────────────────────────────────
const depots = ref([])

// ─── Données d'un dépôt ouvert ────────────────────────────────────
const vaultDocs = ref([])
const vaultMembers = ref([])
const vaultActivities = ref([])

// ─── Helpers ──────────────────────────────────────────────────────
const openVault = (depot) => {
  selectedVault.value = depot
  activeTab.value = 'Documents'
  // TODO: fetch /api/vaults/${depot.id}/documents, members, activity
}

const backToList = () => {
  selectedVault.value = null
}

const statusBadgeClass = (statut) => {
  if (statut === 'Valide') return 'badge-valide'
  if (statut === 'Expire bientôt') return 'badge-warning'
  return 'badge-expire'
}

const fileIconClass = (type) => {
  if (type === 'pdf') return 'ti-file-type-pdf'
  if (type === 'image') return 'ti-photo'
  if (type === 'word') return 'ti-file-type-doc'
  if (type === 'excel') return 'ti-file-spreadsheet'
  return 'ti-file-text'
}

// ─── Chargement des données ───────────────────────────────────────
const fetchDepots = async () => {
  // TODO: remplacer par → const res = await fetch('/api/vaults')
  // depots.value = await res.json()
}

// ─── Déclenchement au montage ─────────────────────────────────────
onMounted(async () => {
  try {
    await fetchDepots()
  } catch (error) {
    console.error('Erreur chargement dépôts :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="depots">
    <!-- EN-TÊTE -->
    <div class="header">
      <div class="header-left">
        <h1>Dépôts partagés</h1>
        <p class="subtitle">Espaces collaboratifs pour vos documents</p>
      </div>
      <div class="header-right">
        <button class="btn-create">
          <i class="ti ti-plus"></i> Créer un dépôt
        </button>
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
      <div class="skeleton-grid">
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div>
        <div class="skeleton skeleton-card"></div>
      </div>
    </div>

    <!-- LISTE DES DÉPÔTS -->
    <div v-else-if="!selectedVault" class="depots-grid">
      <!-- État vide -->
      <div v-if="depots.length === 0" class="empty-state">
        <i class="ti ti-folder-off empty-icon"></i>
        <p>Aucun dépôt partagé</p>
        <span>Créez un dépôt pour partager des documents en famille, entre amis ou collègues.</span>
      </div>

      <!-- Cartes dépôts -->
      <div
        v-for="depot in depots"
        :key="depot.id"
        class="card depot-card"
        @click="openVault(depot)"
      >
        <div class="depot-icon">
          <i :class="'ti ' + depot.icon"></i>
        </div>
        <h3 class="depot-name">{{ depot.nom }}</h3>
        <p class="depot-type">{{ depot.type }}</p>

        <div class="depot-members-row">
          <div class="avatar-stack">
            <div
              v-for="(initial, idx) in depot.membres.slice(0, 4)"
              :key="idx"
              class="member-avatar"
            >
              {{ initial }}
            </div>
          </div>
          <span class="depot-meta">{{ depot.membres.length }} membres</span>
        </div>

        <p class="depot-meta" style="margin-bottom: 16px">
          {{ depot.documents }} documents • Créé le {{ depot.dateCreation }}
        </p>

        <button class="btn-access">Accéder</button>
      </div>
    </div>

    <!-- VUE INTÉRIEURE D'UN DÉPÔT -->
    <div v-else class="vault-detail">
      <button class="btn-back" @click="backToList">
        <i class="ti ti-arrow-left"></i> Retour aux dépôts
      </button>

      <div class="detail-header card">
        <div class="detail-icon">
          <i :class="'ti ' + selectedVault.icon"></i>
        </div>
        <div class="detail-info">
          <h2>{{ selectedVault.nom }}</h2>
          <p>
            {{ selectedVault.description }}
            • {{ selectedVault.membres.length }} membres
            • {{ selectedVault.documents }} documents
          </p>
        </div>
      </div>

      <div class="detail-tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="tab-btn"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          {{ tab }}
        </button>
      </div>

      <!-- Onglet Documents -->
      <div v-if="activeTab === 'Documents'" class="card documents-card">
        <div class="table-header">
          <div class="cell cell-doc">Document</div>
          <div class="cell hide-mobile">Catégorie</div>
          <div class="cell hide-mobile">Ajouté par</div>
          <div class="cell hide-mobile">Expiration</div>
          <div class="cell">Statut</div>
          <div class="cell">Actions</div>
        </div>

        <div
          v-for="doc in vaultDocs"
          :key="doc.id"
          class="table-row"
        >
          <div class="cell cell-doc">
            <i :class="'ti ' + fileIconClass(doc.type)" class="doc-type-icon"></i>
            <span class="doc-name">{{ doc.nom }}</span>
          </div>
          <div class="cell hide-mobile">{{ doc.categorie }}</div>
          <div class="cell hide-mobile">{{ doc.ajoutePar }}</div>
          <div class="cell hide-mobile">{{ doc.expiration }}</div>
          <div class="cell">
            <span :class="['badge', statusBadgeClass(doc.statut)]">
              {{ doc.statut }}
            </span>
          </div>
          <div class="cell actions">
            <button class="btn-action"><i class="ti ti-eye"></i></button>
            <button class="btn-action"><i class="ti ti-share"></i></button>
            <button class="btn-action"><i class="ti ti-trash"></i></button>
          </div>
        </div>

        <div v-if="vaultDocs.length === 0" class="empty-state small">
          <i class="ti ti-file-off empty-icon"></i>
          <p>Aucun document dans ce dépôt</p>
        </div>
      </div>

      <!-- Onglet Membres -->
      <div v-if="activeTab === 'Membres'" class="card members-card">
        <div
          v-for="member in vaultMembers"
          :key="member.id"
          class="member-row"
        >
          <div class="member-avatar large">{{ member.initiales }}</div>
          <div class="member-info">
            <p class="member-name">{{ member.nom }}</p>
            <p class="member-role">{{ member.role }}</p>
          </div>
          <button class="btn-action"><i class="ti ti-dots-vertical"></i></button>
        </div>

        <div v-if="vaultMembers.length === 0" class="empty-state small">
          <i class="ti ti-users empty-icon"></i>
          <p>Aucun membre dans ce dépôt</p>
        </div>
      </div>

      <!-- Onglet Activité -->
      <div v-if="activeTab === 'Activité'" class="card activity-card">
        <div
          v-for="(act, idx) in vaultActivities"
          :key="idx"
          class="activity-row"
        >
          <div class="activity-icon">
            <i class="ti ti-history"></i>
          </div>
          <div class="activity-info">
            <p class="activity-text">{{ act.texte }}</p>
          </div>
          <span class="activity-time">{{ act.heure }}</span>
        </div>

        <div v-if="vaultActivities.length === 0" class="empty-state small">
          <i class="ti ti-activity empty-icon"></i>
          <p>Aucune activité récente</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.depots {
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

.btn-create {
  background: #F4B400;
  color: #121212;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-create:hover {
  background: #D89E00;
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
  height: 60px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.skeleton-card {
  height: 260px;
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

/* GRILLE DES DÉPÔTS */
.depots-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.depot-card {
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.depot-card:hover {
  transform: translateY(-2px);
  border-color: rgba(244, 180, 0, 0.4);
}

.depot-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-bottom: 16px;
}

.depot-name {
  font-size: 17px;
  font-weight: 500;
  margin-bottom: 4px;
}

.depot-type {
  font-size: 13px;
  color: #888;
  margin-bottom: 16px;
}

.depot-members-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.avatar-stack {
  display: flex;
  align-items: center;
}

.member-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #F4B400;
  color: #121212;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 500;
  border: 2px solid #1E1E1E;
  margin-left: -8px;
}

.member-avatar:first-child {
  margin-left: 0;
}

.member-avatar.large {
  width: 40px;
  height: 40px;
  font-size: 14px;
  margin-left: 0;
  border: none;
}

.depot-meta {
  font-size: 12px;
  color: #888;
}

.btn-access {
  width: 100%;
  background: #F4B400;
  color: #121212;
  border: none;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.btn-access:hover {
  background: #D89E00;
}

/* VUE INTÉRIEURE */
.btn-back {
  background: transparent;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
}

.btn-back:hover {
  color: white;
  border-color: #F4B400;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 20px;
}

.detail-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 34px;
}

.detail-info h2 {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 4px;
}

.detail-info p {
  font-size: 13px;
  color: #888;
}

.detail-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 0.5px solid #2a2a2a;
  padding-bottom: 12px;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #888;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.tab-btn:hover {
  color: white;
}

.tab-btn.active {
  background: #F4B400;
  color: #121212;
}

/* TABLEAU DOCUMENTS */
.table-header,
.table-row {
  display: grid;
  grid-template-columns: 2.5fr 1.2fr 1.2fr 1fr 1fr 1.2fr;
  align-items: center;
  padding: 12px;
  gap: 12px;
}

.table-header {
  font-size: 12px;
  color: #888;
  border-bottom: 0.5px solid #2a2a2a;
  margin-bottom: 4px;
}

.table-row {
  border-radius: 10px;
  transition: background 0.15s ease;
}

.table-row:hover {
  background: rgba(244, 180, 0, 0.06);
}

.cell {
  font-size: 13px;
  color: #ccc;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-doc {
  display: flex;
  align-items: center;
  gap: 10px;
}

.doc-type-icon {
  font-size: 20px;
  color: #F4B400;
}

.doc-name {
  font-weight: 500;
  color: white;
}

.actions {
  display: flex;
  gap: 4px;
}

.btn-action {
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 16px;
  padding: 6px;
  border-radius: 6px;
}

.btn-action:hover {
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
}

/* MEMBRES */
.member-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 0.5px solid #2a2a2a;
}

.member-row:last-child {
  border-bottom: none;
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.member-role {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

/* ACTIVITÉ */
.activity-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 6px;
}

.activity-row:nth-child(odd) {
  background: rgba(255, 255, 255, 0.03);
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(244, 180, 0, 0.1);
  color: #F4B400;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-info {
  flex: 1;
}

.activity-text {
  font-size: 13px;
  color: #ccc;
}

.activity-time {
  font-size: 12px;
  color: #888;
}

/* BADGES */
.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 20px;
}

.badge-valide {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.badge-warning {
  background: rgba(244, 180, 0, 0.15);
  color: #F4B400;
}

.badge-expire {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

/* ÉTAT VIDE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0;
  gap: 8px;
  color: #555;
  grid-column: 1 / -1;
}

.empty-state.small {
  padding: 32px 0;
}

.empty-icon {
  font-size: 36px;
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
@media (max-width: 1200px) {
  .depots-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .depots {
    padding: 20px;
  }

  .depots-grid {
    grid-template-columns: 1fr;
  }

  .skeleton-grid {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-header,
  .table-row {
    grid-template-columns: 2fr 1fr 1fr;
  }

  .hide-mobile {
    display: none;
  }
}
</style>
