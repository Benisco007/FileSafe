<script setup>
import { ref, onMounted } from 'vue'

// ─── État de chargement ───────────────────────────────────────────
const isLoading = ref(true)

// ─── Partages actifs ──────────────────────────────────────────────
const shares = ref([])

// ─── Journal d'accès ──────────────────────────────────────────────
const activities = ref([])

// ─── Helpers ──────────────────────────────────────────────────────
const copyLink = async (link) => {
  try {
    await navigator.clipboard.writeText(link)
    // TODO: remplacer par un toast/toaster
    alert('Lien copié dans le presse-papiers')
  } catch (err) {
    console.error('Erreur copie :', err)
  }
}

const revokeShare = async (id) => {
  // TODO: appeler DELETE /api/shares/${id}
  const share = shares.value.find((s) => s.id === id)
  if (share) {
    share.statut = 'Révoqué'
  }
}

const activityIconClass = (type) => {
  return type === 'download' ? 'ti-download' : 'ti-eye'
}

const badgeClassForShare = (statut) => {
  if (statut === 'Actif') return 'badge-success'
  if (statut === 'Expiré') return 'badge-warning'
  return 'badge-danger'
}

const badgeClassForActivity = (action) => {
  if (action === 'Téléchargement') return 'badge-info'
  return 'badge-neutral'
}

// ─── Chargement des données ───────────────────────────────────────
const fetchShares = async () => {
  // TODO: remplacer par → const res = await fetch('/api/shares')
  // shares.value = await res.json()
}

const fetchActivities = async () => {
  // TODO: remplacer par → const res = await fetch('/api/shares/activity')
  // activities.value = await res.json()
}

// ─── Déclenchement au montage ─────────────────────────────────────
onMounted(async () => {
  try {
    await Promise.all([fetchShares(), fetchActivities()])
  } catch (error) {
    console.error('Erreur chargement partages :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="shares">
    <!-- EN-TÊTE -->
    <div class="header">
      <div class="header-left">
        <h1>Partages & Journal d'accès</h1>
        <p class="subtitle">Contrôlez vos liens et suivez l'activité</p>
      </div>
      <div class="header-right">
        <button class="btn-new">
          <i class="ti ti-plus"></i> Nouveau partage
        </button>
        <button class="btn-icon">
          <i class="ti ti-settings"></i>
        </button>
      </div>
    </div>

    <!-- SKELETON -->
    <div v-if="isLoading" class="loading-state">
      <div class="skeleton skeleton-header"></div>
      <div class="skeleton-grid">
        <div class="skeleton skeleton-column"></div>
        <div class="skeleton skeleton-column"></div>
      </div>
    </div>

    <!-- CONTENU -->
    <div v-else class="shares-layout">
      <!-- COLONNE GAUCHE : LIENS DE PARTAGE -->
      <div class="shares-column">
        <h2 class="section-title">Liens de partage actifs</h2>

        <div v-if="shares.length === 0" class="empty-state">
          <i class="ti ti-link-off empty-icon"></i>
          <p>Aucun lien actif</p>
          <span>Partagez un document pour générer un lien sécurisé.</span>
        </div>

        <div
          v-for="share in shares"
          :key="share.id"
          class="card share-card"
        >
          <div class="share-header">
            <h3 class="share-doc">{{ share.document }}</h3>
            <span :class="['badge', badgeClassForShare(share.statut)]">
              {{ share.statut }}
            </span>
          </div>

          <div class="share-link-box">
            <span class="share-url">{{ share.lien }}</span>
            <button class="btn-copy" @click="copyLink(share.lien)">
              <i class="ti ti-copy"></i>
            </button>
          </div>

          <div class="share-footer">
            <span class="share-expiry">Expire le {{ share.expiration }}</span>
            <button
              v-if="share.statut === 'Actif'"
              class="btn-revoke"
              @click="revokeShare(share.id)"
            >
              Révoquer
            </button>
          </div>
        </div>
      </div>

      <!-- COLONNE DROITE : JOURNAL D'ACCÈS -->
      <div class="card activity-column">
        <h2 class="section-title">Activité récente</h2>

        <div v-if="activities.length === 0" class="empty-state small">
          <i class="ti ti-activity empty-icon"></i>
          <p>Aucune activité récente</p>
        </div>

        <div v-else class="activity-list">
          <div
            v-for="(act, idx) in activities"
            :key="idx"
            class="activity-row"
          >
            <div class="activity-icon">
              <i :class="'ti ' + activityIconClass(act.type)"></i>
            </div>
            <div class="activity-info">
              <p class="activity-ip">{{ act.ip }}</p>
              <p class="activity-location">{{ act.pays }}</p>
            </div>
            <div class="activity-right">
              <p class="activity-time">{{ act.horodatage }}</p>
              <span :class="['badge', badgeClassForActivity(act.action)]">
                {{ act.action }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.shares {
  padding: 24px 32px;
  background-color: #121212;
  min-height: 100vh;
  color: white;
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

.btn-new {
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

.btn-new:hover {
  background: #D89E00;
}

.btn-icon {
  background: #1E1E1E;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  font-size: 16px;
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
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.skeleton-column {
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

/* LAYOUT DEUX COLONNES */
.shares-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.section-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 16px;
}

.shares-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* CARTE DE PARTAGE */
.share-card {
  transition: border-color 0.15s ease;
}

.share-card:hover {
  border-color: rgba(244, 180, 0, 0.3);
}

.share-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.share-doc {
  font-size: 15px;
  font-weight: 500;
  line-height: 1.3;
}

.share-link-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 0.5px solid #2a2a2a;
  border-radius: 10px;
  padding: 10px 12px;
  margin-bottom: 14px;
}

.share-url {
  flex: 1;
  font-size: 13px;
  color: #888;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-copy {
  background: transparent;
  border: none;
  color: #aaa;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
  border-radius: 6px;
}

.btn-copy:hover {
  color: #F4B400;
  background: rgba(244, 180, 0, 0.1);
}

.share-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.share-expiry {
  font-size: 12px;
  color: #888;
}

.btn-revoke {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
}

.btn-revoke:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* COLONNE ACTIVITÉ */
.activity-column {
  align-self: flex-start;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.activity-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 12px;
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
  flex-shrink: 0;
}

.activity-info {
  flex: 1;
  min-width: 0;
}

.activity-ip {
  font-size: 13px;
  font-weight: 500;
  color: white;
}

.activity-location {
  font-size: 12px;
  color: #888;
  margin-top: 2px;
}

.activity-right {
  text-align: right;
  flex-shrink: 0;
}

.activity-time {
  font-size: 11px;
  color: #888;
  margin-bottom: 4px;
}

/* BADGES */
.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: 20px;
  display: inline-block;
}

.badge-success {
  background: rgba(34, 197, 94, 0.15);
  color: #22C55E;
}

.badge-warning {
  background: rgba(244, 180, 0, 0.15);
  color: #F4B400;
}

.badge-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

.badge-neutral {
  background: rgba(255, 255, 255, 0.08);
  color: #aaa;
}

.badge-info {
  background: rgba(59, 130, 246, 0.15);
  color: #60A5FA;
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
@media (max-width: 1024px) {
  .shares-layout {
    grid-template-columns: 1fr;
  }

  .skeleton-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .shares {
    padding: 20px;
  }

  .activity-row {
    flex-wrap: wrap;
  }

  .activity-right {
    width: 100%;
    text-align: left;
    margin-top: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>
