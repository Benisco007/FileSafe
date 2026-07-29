<script setup>
import { computed, ref, watch ,nextTick} from 'vue'
import mammoth from 'mammoth'
import * as XLSX from 'xlsx'

const props = defineProps({
  isOpen: Boolean,
  fileUrl: String,
  fileName: String,
  mimeType: String,
  fileBlob: Blob
})

const emit = defineEmits(['close'])

const isImage = computed(() => props.mimeType?.startsWith('image/'))
const isPdf = computed(() => props.mimeType?.includes('pdf'))
const isWord = computed(() => 
  props.mimeType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
  props.mimeType === 'application/msword'
)
const isExcel = computed(() =>
  props.mimeType === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
  props.mimeType === 'application/vnd.ms-excel'
)
const isText = computed(() => props.mimeType?.startsWith('text/'))

const htmlContent = ref('')
const isConverting = ref(false)

watch(() => props.isOpen, async (open) => {
  if (!open) {
    htmlContent.value = ''
    return
  }
  if (isWord.value || isExcel.value) {
    await convertFile()
  }
})

const convertFile = async () => {
  if (!props.fileBlob) return
  isConverting.value = true
  htmlContent.value = ''
  try {
    const arrayBuffer = await props.fileBlob.arrayBuffer()
    if (isWord.value) {
      const result = await mammoth.convertToHtml({ arrayBuffer })
      htmlContent.value = result.value
    } else if (isExcel.value) {
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      const sheetName = workbook.SheetNames[0]
      const sheet = workbook.Sheets[sheetName]
      htmlContent.value = XLSX.utils.sheet_to_html(sheet, { id: 'excel-table' })
    }
  } catch (err) {
    console.error('Erreur de conversion', err)
    htmlContent.value = '<p style="color:red">Erreur lors de la conversion du document.</p>'
  } finally {
    isConverting.value = false
  }
}

import * as pdfjsLib from 'pdfjs-dist'
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`

const pdfCanvas = ref(null)
const currentPage = ref(1)
const totalPages = ref(0)
let pdfDocument = null

const renderPage = async (pageNum) => {
  if (!pdfDocument || !pdfCanvas.value) return
  const page = await pdfDocument.getPage(pageNum)
  const viewport = page.getViewport({ scale: 1.5 })
  const canvas = pdfCanvas.value
  canvas.width = viewport.width
  canvas.height = viewport.height
  await page.render({
    canvasContext: canvas.getContext('2d'),
    viewport
  }).promise
}

const prevPage = async () => {
  if (currentPage.value > 1) {
    currentPage.value--
    await renderPage(currentPage.value)
  }
}

const nextPage = async () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    await renderPage(currentPage.value)
  }
}

const loadPdf = async () => {
  if (!props.fileBlob) return
  const arrayBuffer = await props.fileBlob.arrayBuffer()
  pdfDocument = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  totalPages.value = pdfDocument.numPages
  currentPage.value = 1
  await renderPage(1)
}

watch(() => props.isOpen, async (open) => {
  if (!open) {
    htmlContent.value = ''
    currentPage.value = 1
    totalPages.value = 0
    pdfDocument = null
    return
  }
  if (isPdf.value) {
    await nextTick()
    await loadPdf()
  }
  if (isWord.value || isExcel.value) {
    await convertFile()
  }
})
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ fileName || 'Aperçu du document' }}</h2>
        <button class="close-btn" @click="emit('close')">
          <i class="ti ti-x"></i>
        </button>
      </div>

      <div class="modal-body preview-container">
        <!-- Loading state -->
        <div v-if="isConverting" class="loading-state">
          <i class="ti ti-loader animate-spin"></i>
          <p>Conversion en cours...</p>
        </div>

        <!-- Image -->
        <img v-else-if="isImage && fileUrl" :src="fileUrl" class="preview-img" alt="Aperçu" />

        <!-- PDF -->       
        <div v-else-if="isPdf && fileBlob" class="pdf-viewer">
          <div class="pdf-controls">
            <button @click="prevPage" :disabled="currentPage <= 1" class="pdf-btn">
              <i class="ti ti-chevron-left"></i>
            </button>
            <span class="pdf-page-info">Page {{ currentPage }} / {{ totalPages }}</span>
            <button @click="nextPage" :disabled="currentPage >= totalPages" class="pdf-btn">
              <i class="ti ti-chevron-right"></i>
            </button>
          </div>
          <canvas ref="pdfCanvas" class="pdf-canvas"></canvas>
        </div>

        <!-- Text -->
        <iframe v-else-if="isText && fileUrl" :src="fileUrl" class="preview-pdf" frameborder="0"></iframe>

        <!-- Word / Excel : HTML rendu -->
        <div
          v-else-if="(isWord || isExcel) && htmlContent && !isConverting"
          class="html-preview"
          v-html="htmlContent"
        ></div>

        <!-- Unsupported -->
        <div v-else-if="!isConverting" class="unsupported-msg">
          <i class="ti ti-file-unknown"></i>
          <p>L'aperçu n'est pas disponible pour ce type de fichier.</p>
          <span>Veuillez le télécharger pour le consulter.</span>
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
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--bg-card);
  width: 90%;
  max-width: 1000px;
  height: 85vh;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  background: none;
  border: none;
  color: #aaa;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
  padding: 4px;
  flex-shrink: 0;
}

.close-btn:hover {
  color: var(--danger);
}

.modal-body.preview-container {
  flex: 1;
  padding: 0;
  display: flex;
  background-color: #1a1a1a;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.preview-pdf {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border: none;
}

.html-preview {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 32px 48px;
  background-color: #fff;
  color: #1a1a1a;
  font-family: 'Calibri', 'Georgia', serif;
  font-size: 15px;
  line-height: 1.7;
  box-sizing: border-box;
}

.html-preview :deep(h1),
.html-preview :deep(h2),
.html-preview :deep(h3) {
  margin-top: 1em;
  margin-bottom: 0.4em;
}

.html-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.html-preview :deep(td),
.html-preview :deep(th) {
  border: 1px solid #ccc;
  padding: 8px 12px;
  text-align: left;
}

.html-preview :deep(th) {
  background-color: #f3f4f6;
  font-weight: 600;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--text-secondary);
}

.loading-state i {
  font-size: 48px;
  color: var(--primary);
}

.loading-state p {
  font-size: 16px;
}

.unsupported-msg {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  text-align: center;
  padding: 40px;
}

.unsupported-msg i {
  font-size: 64px;
  color: var(--input-border);
  margin-bottom: 16px;
}

.unsupported-msg p {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.pdf-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background-color: #525659;
  padding: 20px;
  gap: 16px;
}

.pdf-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(0,0,0,0.5);
  padding: 8px 16px;
  border-radius: 20px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.pdf-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.pdf-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.2);
}

.pdf-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.pdf-page-info {
  color: white;
  font-size: 14px;
  white-space: nowrap;
}

.pdf-canvas {
  max-width: 100%;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  border-radius: 4px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
