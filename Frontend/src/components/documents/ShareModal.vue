<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../api'

const props = defineProps({
  document: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'share-created'])

const documents = ref([])
const selectedDocId = ref(null)

onMounted(async () => {
  if (!props.document) {
    try {
      const { data } = await api.get('/api/documents/')
      documents.value = data
      if (data.length > 0) {
        selectedDocId.value = data[0].id_doc
      }
    } catch (err) {
      console.error(err)
    }
  }
})

const currentDocument = computed(() => {
  if (props.document) return props.document
  return documents.value.find(d => d.id_doc === selectedDocId.value) || {}
})

const destinataire = ref('')
const duree = ref('24h')
const joursPersonnalises = ref(1)
const limitesTelechargements = ref('illimite')

const isGenerating = ref(false)
const generatedLink = ref(null)
const downloadLink = ref('')
const shareDetails = ref(null)
const copySuccess = ref(false)
const errorMsg = ref('')

const handleGenerateLink = async () => {
  errorMsg.value = ''
  
  // Calculer durée en heures
  let dureeHeures = 24
  if (duree.value === '1h') dureeHeures = 1
  if (duree.value === '7j') dureeHeures = 168
  if (duree.value === 'perso') dureeHeures = joursPersonnalises.value * 24
  
  // Limites téléchargements
  let maxTelechargements = limitesTelechargements.value === 'illimite' ? null : parseInt(limitesTelechargements.value)

  const docId = currentDocument.value.id_doc
  if (!docId) {
    errorMsg.value = 'Aucun document sélectionné.'
    return
  }

  try {
    isGenerating.value = true
    let url = `/api/shares/${docId}/partager?duree_heures=${dureeHeures}`
    if (maxTelechargements) url += `&max_telechargements=${maxTelechargements}`
    if (destinataire.value) url += `&email_destinataire=${encodeURIComponent(destinataire.value.trim())}`

    const { data } = await api.post(url, {})

    if (data.lien) {
      generatedLink.value = data.lien  // http://localhost:5173/share/{token}
      downloadLink.value = data.lien   // C'est ce lien qu'on copie pour l'accès
    } else {
      errorMsg.value = `Erreur: champ "lien" absent. Reçu: ${JSON.stringify(data)}`
      return
    }

    shareDetails.value = data
    emit('share-created', data)
  } catch (err) {
    console.error('[ShareModal] Erreur:', err)
    errorMsg.value = err.response?.data?.detail || err.response?.data?.message || 'Erreur lors de la génération du lien.'
  } finally {
    isGenerating.value = false
  }
}

const copyLink = async () => {
  if (downloadLink.value) {
    try {
      await navigator.clipboard.writeText(downloadLink.value)
      copySuccess.value = true
      setTimeout(() => copySuccess.value = false, 2000)
    } catch (err) {
      console.error('Erreur lors de la copie du lien', err)
    }
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
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      
      <!-- État : Saisie du partage -->
      <div v-if="!generatedLink">
        <div class="modal-header">
          <h2>Partager un document</h2>
          <button class="btn-close" @click="$emit('close')"><i class="ti ti-x"></i></button>
        </div>
        
        <div class="modal-body">
          <p class="doc-info" v-if="props.document">Document : <strong>{{ currentDocument.nom_doc }}</strong></p>
          <div class="form-group" v-else>
            <label>Document à partager</label>
            <select v-model="selectedDocId">
              <option v-for="doc in documents" :key="doc.id_doc" :value="doc.id_doc">
                {{ doc.nom_doc }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Destinataire (optionnel)</label>
            <input type="text" v-model="destinataire" placeholder="Email ou nom du destinataire">
          </div>
          
          <div class="form-group">
            <label>Durée du lien</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="duree" value="1h"> 1 heure
              </label>
              <label class="radio-label">
                <input type="radio" v-model="duree" value="24h"> 24 heures
              </label>
              <label class="radio-label">
                <input type="radio" v-model="duree" value="7j"> 7 jours
              </label>
              <label class="radio-label custom-days">
                <input type="radio" v-model="duree" value="perso"> Personnalisé 
                <input type="number" v-model="joursPersonnalises" min="1" :disabled="duree !== 'perso'" class="small-input"> jours
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>Limite de téléchargements</label>
            <select v-model="limitesTelechargements">
              <option value="illimite">Illimité</option>
              <option value="1">1</option>
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>
          
          <p v-if="errorMsg" class="error-msg"><i class="ti ti-alert-circle"></i> {{ errorMsg }}</p>
        </div>
        
        <div class="modal-footer">
          <button class="btn-secondary" @click="$emit('close')">Annuler</button>
          <button class="btn-primary" @click="handleGenerateLink" :disabled="isGenerating">
            {{ isGenerating ? 'Génération...' : 'Générer le lien' }}
          </button>
        </div>
      </div>
      
      <!-- État : Lien généré -->
      <div v-else>
        <div class="success-header">
          <i class="ti ti-check"></i>
          <h2>Lien généré avec succès</h2>
        </div>
        
        <div class="modal-body text-center">
          <label class="link-label">Lien d'accès au document</label>
          <div class="link-box">
            <input type="text" readonly :value="downloadLink">
            <button class="btn-copy" @click="copyLink" :class="{ 'copied': copySuccess }">
              <i :class="copySuccess ? 'ti ti-check' : 'ti ti-clipboard'"></i>
            </button>
          </div>
          <p class="copy-feedback" v-if="copySuccess">Copié !</p>
          
          <div class="share-details">
            <p>Expire le : <strong>{{ formatDate(shareDetails?.date_expiration) }}</strong></p>
            <p>Téléchargements : <strong>0 / {{ shareDetails?.max_telechargements || '∞' }}</strong></p>
          </div>
        </div>
        
        <div class="modal-footer justify-center">
          <button class="btn-secondary" @click="$emit('close')">Fermer</button>
          <button class="btn-primary" @click="copyLink">Copier le lien</button>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
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

.btn-close:hover {
  color: var(--text-primary);
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.doc-info {
  color: var(--text-primary);
  background-color: var(--bg-primary);
  padding: 12px 16px;
  border-radius: 8px;
  margin: 0;
  font-size: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: var(--text-secondary);
  font-size: 14px;
}

.form-group input[type="text"], .form-group select {
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 12px;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input[type="text"]:focus, .form-group select:focus {
  border-color: var(--primary);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-primary);
  font-size: 15px;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  accent-color: var(--primary);
  width: 18px;
  height: 18px;
}

.custom-days {
  display: flex;
  align-items: center;
  gap: 8px;
}

.small-input {
  width: 60px;
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  outline: none;
}

.small-input:focus {
  border-color: var(--primary);
}

.small-input:disabled {
  opacity: 0.5;
}

.error-msg {
  color: var(--danger);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

.justify-center {
  justify-content: center;
}

.btn-secondary {
  background: none;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: var(--bg-primary);
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

.btn-primary:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Success State */
.success-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.success-header i {
  font-size: 48px;
  color: var(--success);
  background-color: rgba(34, 197, 94, 0.1);
  padding: 16px;
  border-radius: 50%;
}

.success-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--text-primary);
}

.text-center {
  text-align: center;
}

.link-box {
  display: flex;
  align-items: center;
  background-color: var(--input-bg);
  border: 1px solid var(--input-border);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}

.link-box input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  padding: 12px 16px;
  font-size: 14px;
  outline: none;
}

.btn-copy {
  background: none;
  border: none;
  color: var(--primary);
  padding: 12px 16px;
  cursor: pointer;
  font-size: 20px;
  transition: background-color 0.2s;
}

.btn-copy:hover {
  background-color: rgba(244, 180, 0, 0.1);
}

.btn-copy.copied {
  color: var(--success);
}

.copy-feedback {
  color: var(--success);
  font-size: 13px;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.share-details {
  background-color: var(--bg-primary);
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.share-details p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.share-details strong {
  color: var(--text-primary);
}
</style>
