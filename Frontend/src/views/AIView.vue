<script setup>
import { ref, onMounted, nextTick } from 'vue'
import api from '../api'

const documents = ref([])
const selectedDoc = ref(null)
const question = ref('')
const messages = ref([])
const isLoading = ref(false)
const isLoadingDocs = ref(true)
const chatContainer = ref(null)

const fetchDocuments = async () => {
  try {
    isLoadingDocs.value = true
    const { data } = await api.get('/api/documents/')
    documents.value = data.filter(d => d.autorisation_ia)
  } catch (err) {
    console.error(err)
  } finally {
    isLoadingDocs.value = false
  }
}

onMounted(() => fetchDocuments())

const selectDoc = (doc) => {
  selectedDoc.value = doc
  messages.value = []
  messages.value.push({
    role: 'assistant',
    text: `Bonjour ! J'ai accès au document **${doc.nom_doc}**. Posez-moi vos questions dessus.`
  })
}

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  const q = question.value.trim()
  if (!q || !selectedDoc.value || isLoading.value) return

  messages.value.push({ role: 'user', text: q })
  question.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    const formData = new FormData()
    formData.append('question', q)

    const { data } = await api.post(
      `/api/documents/${selectedDoc.value.id_doc}/chat-ia`,
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    messages.value.push({ role: 'assistant', text: data.reponse })
  } catch (err) {
    messages.value.push({
      role: 'assistant',
      text: err.response?.data?.detail || "Une erreur s'est produite. Réessayez.",
      error: true
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const resetChat = () => {
  selectedDoc.value = null
  messages.value = []
}

const formatText = (text) => {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}
</script>

<template>
  <div class="ai-view">

    <!-- HEADER -->
    <div class="page-header">
      <div class="header-left">
        <div class="ai-badge"><i class="ti ti-sparkles"></i></div>
        <div>
          <h1>Assistant IA</h1>
          <p class="subtitle">Posez des questions sur vos documents</p>
        </div>
      </div>
      <button class="btn-outline" @click="resetChat" v-if="selectedDoc">
        <i class="ti ti-refresh"></i> Changer de document
      </button>
    </div>

    <!-- SÉLECTION DU DOCUMENT -->
    <div v-if="!selectedDoc" class="doc-selection">
      <div class="selection-header">
        <i class="ti ti-files"></i>
        <h2>Choisissez un document à analyser</h2>
        <p>Seuls les documents avec l'autorisation IA activée sont disponibles.</p>
      </div>

      <div v-if="isLoadingDocs" class="skeleton-grid">
        <div class="skeleton-card" v-for="i in 4" :key="i"></div>
      </div>

      <div v-else-if="documents.length === 0" class="empty-state">
        <i class="ti ti-robot-off"></i>
        <h3>Aucun document disponible</h3>
        <p>Uploadez un document en activant l'option "Autoriser l'IA" pour pouvoir l'analyser ici.</p>
      </div>

      <div v-else class="docs-grid">
        <div
          class="doc-card"
          v-for="doc in documents"
          :key="doc.id_doc"
          @click="selectDoc(doc)"
        >
          <div class="doc-icon">
            <i class="ti ti-file-text"></i>
          </div>
          <div class="doc-info">
            <span class="doc-name">{{ doc.nom_doc }}</span>
            <span class="doc-meta">{{ doc.categorie }}</span>
          </div>
          <div class="ia-tag"><i class="ti ti-sparkles"></i> IA activée</div>
        </div>
      </div>
    </div>

    <!-- INTERFACE CHAT -->
    <div v-else class="chat-container">
      <!-- Info document sélectionné -->
      <div class="selected-doc-bar">
        <div class="doc-icon-sm"><i class="ti ti-file-text"></i></div>
        <span>{{ selectedDoc.nom_doc }}</span>
        <span class="doc-cat">{{ selectedDoc.categorie }}</span>
      </div>

      <!-- Messages -->
      <div class="messages-area" ref="chatContainer">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message', msg.role, { error: msg.error }]"
        >
          <div class="msg-avatar" v-if="msg.role === 'assistant'">
            <i class="ti ti-sparkles"></i>
          </div>
          <div class="msg-bubble" v-html="formatText(msg.text)"></div>
          <div class="msg-avatar user-avatar" v-if="msg.role === 'user'">
            {{ $store?.user?.prenom?.[0] || 'U' }}
          </div>
        </div>

        <!-- Indicateur de chargement -->
        <div class="message assistant" v-if="isLoading">
          <div class="msg-avatar"><i class="ti ti-sparkles"></i></div>
          <div class="msg-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <!-- Zone de saisie -->
      <div class="input-area">
        <textarea
          v-model="question"
          @keydown="handleKeydown"
          placeholder="Posez une question sur ce document... (Entrée pour envoyer)"
          rows="1"
          :disabled="isLoading"
        ></textarea>
        <button class="btn-send" @click="sendMessage" :disabled="!question.trim() || isLoading">
          <i class="ti ti-send"></i>
        </button>
      </div>
      <p class="hint">Appuyez sur Entrée pour envoyer · Shift+Entrée pour un saut de ligne</p>
    </div>

  </div>
</template>

<style scoped>
.ai-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: calc(100vh - 48px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ai-badge {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(244,180,0,0.2), rgba(244,180,0,0.05));
  border: 1px solid rgba(244,180,0,0.3);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--primary);
}

.page-header h1 { font-size: 24px; font-weight: 600; color: var(--text-primary); margin: 0; }
.subtitle { color: var(--text-secondary); font-size: 14px; margin: 0; }

.btn-outline {
  background: transparent;
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}
.btn-outline:hover { border-color: var(--primary); color: var(--primary); }

/* SÉLECTION DOCUMENT */
.doc-selection { display: flex; flex-direction: column; gap: 24px; }

.selection-header {
  text-align: center;
  padding: 32px;
  background-color: var(--bg-card);
  border-radius: 16px;
}
.selection-header i { font-size: 40px; color: var(--primary); display: block; margin-bottom: 12px; }
.selection-header h2 { margin: 0 0 8px; font-size: 20px; }
.selection-header p { color: var(--text-secondary); margin: 0; }

.docs-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }

.doc-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
}
.doc-card:hover { border-color: var(--primary); transform: translateY(-2px); }

.doc-icon {
  width: 44px;
  height: 44px;
  background: rgba(244,180,0,0.1);
  color: var(--primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.doc-info { flex: 1; display: flex; flex-direction: column; }
.doc-name { font-weight: 500; color: var(--text-primary); font-size: 15px; }
.doc-meta { color: var(--text-secondary); font-size: 13px; }

.ia-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(244,180,0,0.1);
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

/* CHAT */
.chat-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  background: var(--bg-card);
  border-radius: 16px;
  overflow: hidden;
  min-height: 0;
}

.selected-doc-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  flex-shrink: 0;
}

.doc-icon-sm {
  width: 32px;
  height: 32px;
  background: rgba(244,180,0,0.1);
  color: var(--primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.selected-doc-bar span { font-weight: 500; color: var(--text-primary); }
.doc-cat { background: var(--bg-card); color: var(--text-secondary); padding: 2px 10px; border-radius: 20px; font-size: 12px; margin-left: auto; }

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.message.user { flex-direction: row-reverse; }

.msg-avatar {
  width: 36px;
  height: 36px;
  background: rgba(244,180,0,0.15);
  color: var(--primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.user-avatar {
  background: var(--primary);
  color: #121212;
  font-size: 14px;
  font-weight: 700;
}

.msg-bubble {
  max-width: 70%;
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-primary);
}

.message.assistant .msg-bubble {
  background: var(--bg-primary);
  border-radius: 4px 16px 16px 16px;
}

.message.user .msg-bubble {
  background: rgba(244,180,0,0.15);
  border-radius: 16px 4px 16px 16px;
}

.message.error .msg-bubble {
  background: rgba(239,68,68,0.1);
  color: var(--danger);
}

/* Typing animation */
.typing {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
}
.typing span {
  width: 8px;
  height: 8px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

/* INPUT */
.input-area {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

textarea {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--input-border);
  color: var(--text-primary);
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  resize: none;
  outline: none;
  font-family: inherit;
  max-height: 120px;
  overflow-y: auto;
  transition: border-color 0.2s;
}
textarea:focus { border-color: var(--primary); }
textarea:disabled { opacity: 0.5; }

.btn-send {
  width: 44px;
  height: 44px;
  background: var(--primary);
  color: #121212;
  border: none;
  border-radius: 12px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.btn-send:hover:not(:disabled) { background: var(--primary-hover); transform: scale(1.05); }
.btn-send:disabled { opacity: 0.4; cursor: not-allowed; }

.hint { text-align: center; font-size: 12px; color: var(--text-secondary); margin: 0; padding: 0 20px 12px; flex-shrink: 0; }

/* Empty / skeleton */
.empty-state {
  text-align: center;
  padding: 48px 20px;
  background: var(--bg-card);
  border-radius: 16px;
}
.empty-state i { font-size: 48px; color: var(--input-border); display: block; margin-bottom: 16px; }
.empty-state h3 { color: var(--text-primary); margin-bottom: 8px; }
.empty-state p { color: var(--text-secondary); }

.skeleton-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.skeleton-card { height: 80px; background: var(--bg-card); border-radius: 12px; animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
