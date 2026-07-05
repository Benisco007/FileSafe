<script setup>
import { ref, computed, onMounted } from 'vue'

// ─── État de chargement ───────────────────────────────────────────
const isLoading = ref(true)

// ─── Données utilisateur ─────────────────────────────────────────
const userName = ref('')

const today = new Date().toLocaleDateString('fr-FR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric'
})

// ─── Métriques ───────────────────────────────────────────────────
const stats = ref({
  totalDocuments: null,
  espaceUtilise: null,
  espaceTotal: null,
  documentsExpires: null,
  depotsActifs: null
})

// ─── Score documentaire ──────────────────────────────────────────
const score = ref(null)

const scoreColor = computed(() => {
  if (!score.value) return '#888'
  if (score.value >= 75) return '#22C55E'
  if (score.value >= 50) return '#F4B400'
  return '#EF4444'
})

const scoreDashArray = computed(() => {
  if (!score.value) return '0 264'
  return `${score.value * 2.64} 264`
})

// ─── Documents récents ───────────────────────────────────────────
const documents = ref([])

// ─── Alertes actives ─────────────────────────────────────────────
const alertes = ref([])

// ─── Badge statut ────────────────────────────────────────────────
const badgeClass = (statut) => {
  if (statut === 'Valide') return 'badge-valide'
  if (statut === 'Expire bientôt') return 'badge-warning'
  return 'badge-expire'
}

// ─── Chargement des données depuis l'API ─────────────────────────
// Ces fonctions appelleront ton backend FastAPI plus tard.
// Pour l'instant elles sont vides — on les remplira lors de
// l'intégration backend.

const fetchStats = async () => {
  // TODO: remplacer par → const res = await fetch('/api/dashboard/stats')
  // stats.value = await res.json()
}

const fetchDocuments = async () => {
  // TODO: remplacer par → const res = await fetch('/api/documents/recent')
  // documents.value = await res.json()
}

const fetchAlertes = async () => {
  // TODO: remplacer par → const res = await fetch('/api/alertes')
  // alertes.value = await res.json()
}

const fetchUserName = async () => {
  // TODO: remplacer par les données du store Pinia (session utilisateur)
  // userName.value = authStore.user.prenom
}

// ─── Déclenchement au chargement de la page ──────────────────────
onMounted(async () => {
  try {
    await Promise.all([
      fetchStats(),
      fetchDocuments(),
      fetchAlertes(),
      fetchUserName(),
    ])
  } catch (error) {
    console.error('Erreur chargement dashboard :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="home">
    <div class="header">
      <div class="header-left">
        <h1>
          Bonjour<span v-if="userName">, {{ userName }}</span> 
        </h1>
        <p class="date">{{ today }}</p>
      </div>
      <div class="header-right">
        <button class="btn-upload">
          <i class="ti ti-upload"></i> Téléverser un document
        </button>
        <button class="btn-icon">
          <i class="ti ti-settings"></i>
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="skeleton skeleton-metrics"></div>
      <div class="skeleton skeleton-content"></div>
    </div>

  
    <div v-else class="main-grid">

      <!-- COLONNE GAUCHE -->
      <div class="col-left">

        <!-- 4 CARTES MÉTRIQUES -->
        <div class="metrics">
          <div class="card metric">
            <i class="ti ti-files metric-icon"></i>
            <div>
              <p class="metric-value">
                {{ stats.totalDocuments ?? '—' }}
              </p>
              <p class="metric-label">Total documents</p>
            </div>
          </div>
          <div class="card metric">
            <i class="ti ti-database metric-icon"></i>
            <div>
              <p class="metric-value">
                {{ stats.espaceUtilise ?? '—' }} Mo / {{ stats.espaceTotal ?? '—' }} Mo
              </p>
              <p class="metric-label">Espace utilisé</p>
            </div>
          </div>
          <div class="card metric">
            <i class="ti ti-clock metric-icon" style="color:#EF4444"></i>
            <div>
              <p class="metric-value">
                {{ stats.documentsExpires ?? '—' }}
              </p>
              <p class="metric-label">Documents expirés ou proches</p>
            </div>
          </div>
          <div class="card metric">
            <i class="ti ti-users metric-icon"></i>
            <div>
              <p class="metric-value">
                {{ stats.depotsActifs ?? '—' }}
              </p>
              <p class="metric-label">Dépôts actifs</p>
            </div>
          </div>
        </div>

        <!-- DOCUMENTS RÉCENTS -->
        <div class="card docs-recents">
          <h2>Documents récents</h2>

          <!-- Liste vide -->
          <div v-if="documents.length === 0" class="empty-state">
            <i class="ti ti-file-off empty-icon"></i>
            <p>Aucun document pour l'instant.</p>
            <span>Téléversez votre premier document pour commencer.</span>
          </div>

          <!-- Liste remplie -->
          <div v-else class="doc-list">
            <div
              class="doc-item"
              v-for="doc in documents"
              :key="doc.id"
            >
              <div class="doc-info">
                <i class="ti ti-file-text doc-icon"></i>
                <div>
                  <p class="doc-nom">{{ doc.nom }}</p>
                  <p class="doc-meta">
                    {{ doc.categorie }} • Ajouté le {{ doc.date }}
                  </p>
                </div>
              </div>
              <div class="doc-actions">
                <span :class="['badge', badgeClass(doc.statut)]">
                  {{ doc.statut }}
                </span>
                <button class="btn-more">
                  <i class="ti ti-dots-vertical"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- COLONNE DROITE -->
      <div class="col-right">

        <!-- SCORE DOCUMENTAIRE -->
        <div class="card score-card">
          <div class="score-circle">
            <svg viewBox="0 0 100 100" width="140" height="140">
              <circle
                cx="50" cy="50" r="42"
                fill="none" stroke="#2a2a2a" stroke-width="10"
              />
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                :stroke="scoreColor"
                stroke-width="10"
                stroke-linecap="round"
                :stroke-dasharray="scoreDashArray"
                stroke-dashoffset="66"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div class="score-text">
              <span class="score-value" :style="{ color: scoreColor }">
                {{ score !== null ? score + '%' : '—' }}
              </span>
            </div>
          </div>
          <p class="score-label">Score documentaire</p>
        </div>

        <!-- ALERTES ACTIVES -->
        <div class="card alertes-card">
          <h2>Alertes actives</h2>

          <!-- Aucune alerte -->
          <div v-if="alertes.length === 0" class="empty-state">
            <i class="ti ti-bell-off empty-icon"></i>
            <p>Aucune alerte active.</p>
          </div>

          <!-- Liste alertes -->
          <div v-else class="alerte-list">
            <div
              class="alerte-item"
              v-for="alerte in alertes"
              :key="alerte.id"
            >
              <i class="ti ti-alert-triangle alerte-icon"></i>
              <div>
                <p class="alerte-msg">{{ alerte.message }}</p>
                <p class="alerte-date">{{ alerte.date }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<style scoped>
.home {
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
.header h1 { font-size: 22px; font-weight: 500; }
.date { font-size: 13px; color: #888; margin-top: 4px; }
.header-right { display: flex; gap: 10px; align-items: center; }

.btn-upload {
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
.btn-upload:hover { background: #D89E00; }
.btn-icon {
  background: #1E1E1E;
  color: #aaa;
  border: 0.5px solid #333;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  font-size: 16px;
}

/* SKELETON LOADING */
.loading-state { display: flex; flex-direction: column; gap: 20px; }
.skeleton {
  background: linear-gradient(90deg, #1E1E1E 25%, #2a2a2a 50%, #1E1E1E 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 18px;
}
.skeleton-metrics { height: 180px; }
.skeleton-content { height: 400px; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* GRILLE */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 20px;
}
.col-left { display: flex; flex-direction: column; gap: 20px; }
.col-right { display: flex; flex-direction: column; gap: 20px; }

/* CARTES */
.card {
  background: #1E1E1E;
  border-radius: 18px;
  padding: 20px;
  border: 0.5px solid #2a2a2a;
}

/* MÉTRIQUES */
.metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.metric { display: flex; align-items: center; gap: 14px; }
.metric-icon { font-size: 26px; color: #F4B400; }
.metric-value { font-size: 20px; font-weight: 500; }
.metric-label { font-size: 12px; color: #888; margin-top: 3px; }

/* DOCUMENTS RÉCENTS */
.docs-recents h2 { font-size: 15px; font-weight: 500; margin-bottom: 16px; }
.doc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 0.5px solid #2a2a2a;
}
.doc-item:last-child { border-bottom: none; }
.doc-info { display: flex; align-items: center; gap: 12px; }
.doc-icon { font-size: 20px; color: #F4B400; }
.doc-nom { font-size: 13px; font-weight: 500; }
.doc-meta { font-size: 11px; color: #888; margin-top: 2px; }
.doc-actions { display: flex; align-items: center; gap: 10px; }
.btn-more { background: none; border: none; color: #888; cursor: pointer; font-size: 16px; }

/* BADGES */
.badge { font-size: 11px; font-weight: 500; padding: 3px 10px; border-radius: 20px; }
.badge-valide { background: rgba(34,197,94,0.15); color: #22C55E; }
.badge-warning { background: rgba(244,180,0,0.15); color: #F4B400; }
.badge-expire { background: rgba(239,68,68,0.15); color: #EF4444; }

/* SCORE */
.score-card { display: flex; flex-direction: column; align-items: center; padding: 24px 20px; }
.score-circle { position: relative; display: flex; align-items: center; justify-content: center; }
.score-text { position: absolute; }
.score-value { font-size: 22px; font-weight: 500; }
.score-label { font-size: 13px; color: #888; margin-top: 12px; }

/* ALERTES */
.alertes-card h2 { font-size: 15px; font-weight: 500; margin-bottom: 14px; }
.alerte-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px;
  background: rgba(244,180,0,0.07);
  border-radius: 10px;
  margin-bottom: 8px;
}
.alerte-icon { font-size: 18px; color: #F4B400; flex-shrink: 0; margin-top: 1px; }
.alerte-msg { font-size: 12px; font-weight: 500; line-height: 1.5; }
.alerte-date { font-size: 11px; color: #888; margin-top: 3px; }

/* ÉTAT VIDE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0;
  gap: 8px;
  color: #555;
}
.empty-icon { font-size: 32px; margin-bottom: 4px; }
.empty-state p { font-size: 13px; font-weight: 500; color: #666; }
.empty-state span { font-size: 12px; color: #444; }
</style>