<script setup>
import { ref, computed, onMounted } from 'vue'

// ─── ÉTAT DE CHARGEMENT ───────────────────────────────────────────
const isLoading = ref(true)

// ─── FILTRES ET RECHERCHE ─────────────────────────────────────────
const searchQuery = ref('')
const selectedCategory = ref('Tous')

// Catégories enrichies avec des icônes Tabler pour un rendu visuel pro
const categories = [
  { label: 'Tous', icon: 'ti-layout-grid' },
  { label: 'Identité', icon: 'ti-id' },
  { label: 'Diplômes', icon: 'ti-certificate' },
  { label: 'Santé', icon: 'ti-heart-rate-monitor' },
  { label: 'Contrats', icon: 'ti-file-contract' },
  { label: 'Divers', icon: 'ti-folder' }
]

// ─── DONNÉES INITIALES VIDES (ENTITÉ FICHIERS) ────────────────────
// Fidèle à ta logique : tableau vide au départ, rempli par l'API
const documents = ref([])

// ─── BADGES DE STATUT (CHARTE GRAPHIQUE) ──────────────────────────
const badgeClass = (statut) => {
  if (statut === 'Valide') return 'badge-valide'
  if (statut === 'Expire bientôt') return 'badge-warning'
  return 'badge-expire'
}

// ─── FILTRAGE RÉACTIF (COMPUTED) ──────────────────────────────────
const filteredDocuments = computed(() => {
  if (!documents.value) return []
  return documents.value.filter(doc => {
    const matchesSearch = doc.nom_fich?.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'Tous' || doc.categorie === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

// ─── FONCTIONS ASYNCHRONES EN ATTENTE DU BACKEND FASTAPI ──────────
const fetchDocuments = async () => {
  // TODO: remplacer par → const res = await fetch('/api/documents')
  // documents.value = await res.json()
}

const handleDeleteDocument = async (id) => {
  // TODO: remplacer par → await fetch(`/api/documents/${id}`, { method: 'DELETE' })
}

const handleToggleIA = async (doc) => {
  // TODO: remplacer par l'appel API lié à l'analyse Gemini
}

// ─── DÉCLENCHEMENT AU CHARGEMENT DE LA PAGE ──────────────────────
onMounted(async () => {
  try {
    await Promise.all([
      fetchDocuments()
    ])
  } catch (error) {
    console.error('Erreur chargement documents :', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="documents-page">
    
    <div class="header">
      <div class="header-left">
        <h1>Mes documents</h1>
        <p class="subtitle">Gérez et organisez tous vos documents officiels en un clin d'œil</p>
      </div>
      <div class="header-right">
        <button class="btn-upload">
          <i class="ti ti-upload upload-icon"></i> Téléverser un document
        </button>
      </div>
    </div>

    <div class="filter-zone">
      <div class="search-container">
        <i class="ti ti-search search-icon"></i>
        <input 
          v-model="searchQuery"
          type="text" 
          placeholder="Rechercher par nom de document, catégorie, date d'ajout..." 
          class="input-search"
        />
      </div>

      <div class="categories-tabs">
        <button 
          v-for="cat in categories" 
          :key="cat.label"
          @click="selectedCategory = cat.label"
          :class="['tab-pill', selectedCategory === cat.label ? 'active' : '']"
        >
          <i :class="['ti', cat.icon, 'tab-icon']"></i>
          <span>{{ cat.label }}</span>
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="skeleton skeleton-table"></div>
    </div>

    <div v-else class="card table-card">
      
      <div v-if="filteredDocuments.length === 0" class="empty-state">
        <div class="empty-icon-wrapper">
          <i class="ti ti-folder-off empty-icon"></i>
        </div>
        <p>Aucun document pour l'instant</p>
        <span>Les fichiers de votre coffre-fort numérique apparaîtront dans cet espace dès que vous les aurez synchronisés avec le serveur.</span>
      </div>

      <div v-else class="table-wrapper">
        <table class="custom-table">
          <thead>
            <tr>
              <th>Document</th>
              <th>Catégorie</th>
              <th>Ajouté le</th>
              <th>Expiration</th>
              <th>Statut</th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in filteredDocuments" :key="doc.id">
              <td class="col-filename">
                <div class="file-info">
                  <span class="file-icon-box">
                    <i v-if="doc.type_fich === 'PDF'" class="ti ti-file-text"></i>
                    <i v-else-if="doc.type_fich === 'IMAGE'" class="ti ti-photo"></i>
                    <i v-else class="ti ti-file"></i>
                  </span>
                  <div class="file-name-meta">
                    <span class="file-name">{{ doc.nom_fich }}</span>
                    <span class="file-size">{{ doc.taille_fich }}</span>
                  </div>
                </div>
              </td>
              <td class="col-text">{{ doc.categorie }}</td>
              <td class="col-text">{{ doc.date_ajout }}</td>
              <td class="col-text">{{ doc.date_exp }}</td>
              <td>
                <span :class="['badge', badgeClass(doc.status)]">
                  {{ doc.status }}
                </span>
              </td>
              <td class="col-actions">
                <div class="actions-group">
                  <button @click="handleToggleIA(doc)" class="btn-action" title="Analyse IA (Gemini)">
                    <i class="ti ti-brain"></i>
                  </button>
                  <button class="btn-action" title="Consulter le fichier">
                    <i class="ti ti-eye"></i>
                  </button>
                  <button @click="handleDeleteDocument(doc.id)" class="btn-action btn-delete" title="Supprimer">
                    <i class="ti ti-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

  </div>
</template>

<style scoped>
/* ==========================================================================
   VARIABLES DE TAILLES — Modifie facilement les polices ici
   ========================================================================== */
.documents-page {
  --font-title:       26px;  /* Titre "Mes documents"             */
  --font-subtitle:    15px;  /* Sous-titre en-tête                */
  --font-search:      15px;  /* Texte de la barre de recherche    */
  --font-tabs:        14px;  /* Onglets de catégories             */
  --font-th:          13px;  /* En-têtes du tableau (UPPERCASE)   */
  --font-td:          15px;  /* Contenu du tableau (Nom, date...) */
  --font-meta:        13px;  /* Taille du fichier (ex: 1.2 Mo)    */
  --font-badge:       12px;  /* Badges de statut                  */
  
  --icon-search:      20px;  /* Icône loupe                       */
  --icon-tab:         18px;  /* Icônes dans les onglets           */
  --icon-file:        24px;  /* Icônes PDF / Word                 */
  --icon-actions:     20px;  /* Icônes Œil, Cerveau, Poubelle     */
  --icon-empty:       48px;  /* Grosse icône d'état vide          */
}
/* ========================================================================== */

.documents-page {
  padding: 28px 36px;
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
  margin-bottom: 32px;
}
.header h1 { 
  font-size: var(--font-title); 
  font-weight: 600; 
  letter-spacing: -0.02em; 
}
.subtitle { 
  font-size: var(--font-subtitle); 
  color: #888; 
  margin-top: 6px; 
}

.btn-upload {
  background: #F4B400;
  color: #121212;
  border: none;
  border-radius: 10px;
  padding: 12px 22px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s, transform 0.1s;
}
.btn-upload:hover { background: #D89E00; }
.btn-upload:active { transform: scale(0.98); }
.upload-icon { font-size: 20px; }

/* RECHERCHE ET FILTRES */
.filter-zone {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 28px;
}
.search-container { position: relative; width: 100%; }
.search-icon { 
  position: absolute; 
  left: 18px; 
  top: 50%; 
  transform: translateY(-50%); 
  color: #666; 
  font-size: var(--icon-search); 
}
.input-search {
  width: 100%;
  background: #1E1E1E;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 14px 16px 14px 50px;
  color: white;
  font-size: var(--font-search);
  outline: none;
  transition: border-color 0.2s;
}
.input-search:focus { border-color: #F4B400; }
.input-search::placeholder { color: #555; }

/* ONGLETS AVEC ICÔNES */
.categories-tabs { display: flex; flex-wrap: wrap; gap: 10px; }
.tab-pill {
  background: #1E1E1E;
  color: #aaa;
  border: 1px solid #2a2a2a;
  padding: 8px 18px;
  border-radius: 24px;
  font-size: var(--font-tabs);
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.tab-pill:hover { background: #262626; color: white; border-color: #444; }
.tab-pill.active { 
  background: #F4B400; 
  color: #121212; 
  border-color: #F4B400; 
  font-weight: 600; 
}
.tab-icon { font-size: var(--icon-tab); }

/* SKELETON */
.skeleton-table {
  height: 350px;
  background: linear-gradient(90deg, #1E1E1E 25%, #2a2a2a 50%, #1E1E1E 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 18px;
}
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* TABLEAU ET CARTES */
.card { 
  background: #1E1E1E; 
  border-radius: 18px; 
  padding: 24px; 
  border: 1px solid #2a2a2a; 
}
.table-wrapper { overflow-x: auto; }
.custom-table { 
  width: 100%; 
  border-collapse: collapse; 
  text-align: left; 
}
.custom-table th { 
  color: #888; 
  font-weight: 600; 
  padding: 16px 18px; 
  border-bottom: 1px solid #2a2a2a; 
  font-size: var(--font-th); 
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.custom-table td { 
  padding: 18px; 
  border-bottom: 1px solid rgba(42, 42, 42, 0.5); 
  font-size: var(--font-td);
}
.custom-table tbody tr:hover { background: rgba(255, 255, 255, 0.02); }

.file-info { display: flex; align-items: center; gap: 14px; }
.file-icon-box { 
  width: 44px; 
  height: 44px; 
  background: rgba(244, 180, 0, 0.1); 
  color: #F4B400; 
  border-radius: 10px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: var(--icon-file);
  flex-shrink: 0;
}
.file-name-meta { display: flex; flex-direction: column; gap: 3px; }
.file-name { color: white; font-weight: 500; }
.file-size { font-size: var(--font-meta); color: #777; }
.col-text { color: #bbb; }

/* BADGES */
.badge { 
  font-size: var(--font-badge); 
  font-weight: 600; 
  padding: 5px 12px; 
  border-radius: 20px; 
}
.badge-valide { background: rgba(34, 197, 94, 0.15); color: #22C55E; }
.badge-warning { background: rgba(244, 180, 0, 0.15); color: #F4B400; }
.badge-expire { background: rgba(239, 68, 68, 0.15); color: #EF4444; }

/* ACTIONS (ICÔNES BIEN VISIBLES) */
.actions-group { display: flex; gap: 14px; justify-content: center; }
.btn-action { 
  background: #252525; 
  border: 1px solid #333; 
  color: #aaa; 
  cursor: pointer; 
  font-size: var(--icon-actions); 
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.btn-action:hover { background: #333; color: white; border-color: #555; }
.btn-action.btn-delete:hover { background: rgba(239, 68, 68, 0.15); color: #EF4444; border-color: rgba(239, 68, 68, 0.3); }

/* ÉTAT VIDE BIEN MIS EN VALEUR */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64px 20px;
  gap: 12px;
  color: #555;
  text-align: center;
}
.empty-icon-wrapper {
  width: 80px;
  height: 80px;
  background: rgba(244, 180, 0, 0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}
.empty-icon { font-size: var(--icon-empty); color: #F4B400; }
.empty-state p { font-size: 18px; font-weight: 600; color: #ccc; }
.empty-state span { font-size: 14px; color: #777; max-width: 450px; line-height: 1.6; }
</style>