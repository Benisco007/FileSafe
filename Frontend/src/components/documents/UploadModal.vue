<script setup>
import { ref } from 'vue'
import api from '../../api'

const props = defineProps({
  isOpen: Boolean
})

const emit = defineEmits(['close', 'uploaded'])

const nom_doc = ref('')
const categorie = ref('Divers')
const date_exp = ref('')
const consentement_ia = ref(false)
const file = ref(null)
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const errorMsg = ref('')

const categories = ['Identité', 'Diplômes', 'Santé', 'Contrats', 'Divers']

const handleDragOver = (e) => {
  e.preventDefault()
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  isDragging.value = false
}

const handleDrop = (e) => {
  e.preventDefault()
  isDragging.value = false
  const droppedFiles = e.dataTransfer.files
  if (droppedFiles.length > 0) {
    validateAndSetFile(droppedFiles[0])
  }
}

const handleFileSelect = (e) => {
  const selectedFile = e.target.files[0]
  if (selectedFile) {
    validateAndSetFile(selectedFile)
  }
}

const validateAndSetFile = (selectedFile) => {
  errorMsg.value = ''
  const allowedTypes = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ]
  const maxSize = 10 * 1024 * 1024 // 10 Mo

  if (!allowedTypes.includes(selectedFile.type)) {
    errorMsg.value = 'Type de fichier non autorisé. (PDF, Image, Word, Excel)'
    return
  }

  if (selectedFile.size > maxSize) {
    errorMsg.value = 'Le fichier dépasse la taille maximale de 10 Mo.'
    return
  }

  file.value = selectedFile
  if (!nom_doc.value) {
    nom_doc.value = selectedFile.name.split('.').slice(0, -1).join('.')
  }
}

const removeFile = () => {
  file.value = null
  uploadProgress.value = 0
}

const submitUpload = async () => {
  if (!file.value || !nom_doc.value) {
    errorMsg.value = 'Veuillez remplir tous les champs obligatoires.'
    return
  }

  isUploading.value = true
  errorMsg.value = ''
  uploadProgress.value = 0

  const formData = new FormData()
  formData.append('file', file.value)
  formData.append('nom_doc', nom_doc.value)
  formData.append('categorie', categorie.value)
  if (date_exp.value) {
    formData.append('date_exp', date_exp.value)
  }
  formData.append('autorisation_ia', consentement_ia.value)

  try {
    await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        uploadProgress.value = percentCompleted
      }
    })

    // Reset form
    nom_doc.value = ''
    categorie.value = 'Divers'
    date_exp.value = ''
    consentement_ia.value = false
    file.value = null
    
    emit('uploaded')
    emit('close')
  } catch (err) {
    console.error(err)
    errorMsg.value = err.response?.data?.detail || 'Une erreur est survenue lors du téléversement.'
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Téléverser un document</h2>
        <button class="close-btn" @click="emit('close')">
          <i class="ti ti-x"></i>
        </button>
      </div>

      <div class="modal-body">
        <!-- Zone Drag & Drop -->
        <div 
          class="drop-zone" 
          :class="{ 'dragging': isDragging, 'has-file': file }"
          @dragover="handleDragOver"
          @dragleave="handleDragLeave"
          @drop="handleDrop"
          @click="!file && $refs.fileInput.click()"
        >
          <input 
            type="file" 
            ref="fileInput" 
            class="hidden-input" 
            @change="handleFileSelect"
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx"
          >
          
          <template v-if="!file">
            <i class="ti ti-cloud-upload upload-icon"></i>
            <p>Glissez et déposez votre fichier ici ou cliquez pour parcourir</p>
            <span class="file-hint">PDF, Images, Word, Excel (Max 10 Mo)</span>
          </template>
          
          <template v-else>
            <i class="ti ti-file-check file-icon"></i>
            <p class="file-name">{{ file.name }}</p>
            <span class="file-size">{{ (file.size / (1024 * 1024)).toFixed(2) }} Mo</span>
            <button class="remove-btn" @click.stop="removeFile">
              <i class="ti ti-trash"></i> Retirer
            </button>
          </template>
        </div>

        <div v-if="errorMsg" class="error-message">
          <i class="ti ti-alert-circle"></i> {{ errorMsg }}
        </div>

        <!-- Formulaire -->
        <div class="form-group">
          <label>Nom du document *</label>
          <input type="text" v-model="nom_doc" placeholder="Ex: CNI Recto" required>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Catégorie *</label>
            <select v-model="categorie">
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Date d'expiration (optionnel)</label>
            <input type="date" v-model="date_exp">
          </div>
        </div>

        <!-- Consentement IA -->
        <div class="ia-consent">
          <h3>Analyse par l'IA</h3>
          <p class="ia-desc">Autorisez l'IA à analyser ce document pour en extraire des données utiles.</p>
          
          <div class="consent-options">
            <label class="consent-card" :class="{ 'selected': consentement_ia === true }">
              <input type="radio" v-model="consentement_ia" :value="true" class="hidden-radio">
              <i class="ti ti-robot"></i>
              <span>Autoriser</span>
            </label>
            
            <label class="consent-card" :class="{ 'selected': consentement_ia === false }">
              <input type="radio" v-model="consentement_ia" :value="false" class="hidden-radio">
              <i class="ti ti-robot-off"></i>
              <span>Refuser</span>
            </label>
          </div>
        </div>

        <!-- Barre de progression -->
        <div v-if="isUploading" class="progress-container">
          <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
          <span class="progress-text">{{ uploadProgress }}%</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="emit('close')" :disabled="isUploading">Annuler</button>
        <button class="btn-primary" @click="submitUpload" :disabled="!file || !nom_doc || isUploading">
          <i class="ti ti-upload" v-if="!isUploading"></i>
          <i class="ti ti-loader animate-spin" v-else></i>
          {{ isUploading ? 'Téléversement...' : 'Téléverser' }}
        </button>
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
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--bg-card);
  width: 100%;
  max-width: 600px;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: var(--danger);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Drag & Drop Zone */
.drop-zone {
  border: 2px dashed var(--primary);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  background-color: rgba(244, 180, 0, 0.05);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.drop-zone.dragging {
  background-color: rgba(244, 180, 0, 0.15);
  transform: scale(1.02);
}

.drop-zone.has-file {
  border-style: solid;
  cursor: default;
}

.hidden-input {
  display: none;
}

.upload-icon {
  font-size: 48px;
  color: var(--primary);
  margin-bottom: 12px;
}

.drop-zone p {
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 8px;
}

.file-hint {
  color: var(--text-secondary);
  font-size: 14px;
}

.file-icon {
  font-size: 48px;
  color: var(--success);
  margin-bottom: 12px;
}

.file-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.file-size {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.remove-btn {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: rgba(239, 68, 68, 0.25);
}

.error-message {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Forms */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;
}

label {
  font-size: 14px;
  font-weight: 500;
  color: #ccc;
}

input[type="text"],
input[type="date"],
select {
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
}

input:focus, select:focus {
  border-color: var(--primary);
}

/* Consentement IA */
.ia-consent {
  background-color: rgba(255, 255, 255, 0.03);
  padding: 16px;
  border-radius: 12px;
}

.ia-consent h3 {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.ia-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.consent-options {
  display: flex;
  gap: 12px;
}

.consent-card {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.consent-card i {
  font-size: 20px;
  color: var(--text-secondary);
}

.consent-card span {
  font-size: 15px;
  font-weight: 500;
  color: var(--text-secondary);
}

.consent-card.selected {
  border-color: var(--primary);
  background-color: rgba(244, 180, 0, 0.1);
}

.consent-card.selected i,
.consent-card.selected span {
  color: var(--primary);
}

.hidden-radio {
  display: none;
}

/* Progress Bar */
.progress-container {
  height: 24px;
  background-color: var(--bg-primary);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: var(--primary);
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  mix-blend-mode: difference;
}

/* Footer */
.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.btn-cancel {
  background: none;
  border: none;
  color: #aaa;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  padding: 10px 20px;
  transition: color 0.2s;
}

.btn-cancel:hover {
  color: var(--text-primary);
}

.btn-primary {
  background-color: var(--primary);
  color: var(--bg-primary);
  border: none;
  padding: 10px 24px;
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

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
