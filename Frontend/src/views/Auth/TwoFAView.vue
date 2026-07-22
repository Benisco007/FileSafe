<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()

const email = ref('')
const maskedEmail = computed(() => {
  if (!email.value) return ''
  const [name, domain] = email.value.split('@')
  if (!name || !domain) return email.value
  const first = name.charAt(0)
  const last = name.charAt(name.length - 1)
  return `${first}${'•'.repeat(Math.max(1, name.length - 2))}${name.length > 1 ? last : ''}@${domain}`
})

const code = ref(['', '', '', '', '', ''])
const inputRefs = ref([])

const isLoading = ref(false)
const errorMsg = ref('')

onMounted(() => {
  if (localStorage.getItem('token')) {
    router.push('/')
    return
  }
  email.value = localStorage.getItem('pending_email') || ''
  if (!email.value) {
    router.push('/login')
  }
})

const handleInput = (index, event) => {
  const val = event.target.value
  if (val && !/^[0-9]$/.test(val)) {
    code.value[index] = ''
    return
  }
  
  if (val && index < 5) {
    nextTick(() => {
      inputRefs.value[index + 1]?.focus()
    })
  }
}

const handleKeydown = (index, event) => {
  if (event.key === 'Backspace' && !code.value[index] && index > 0) {
    nextTick(() => {
      inputRefs.value[index - 1]?.focus()
    })
  } else if (event.key === 'ArrowLeft' && index > 0) {
    inputRefs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowRight' && index < 5) {
    inputRefs.value[index + 1]?.focus()
  }
}

const handlePaste = (event) => {
  event.preventDefault()
  const pastedData = event.clipboardData.getData('text').slice(0, 6)
  if (/^\d+$/.test(pastedData)) {
    for (let i = 0; i < pastedData.length; i++) {
      if (i < 6) code.value[i] = pastedData[i]
    }
    const focusIndex = Math.min(5, pastedData.length)
    inputRefs.value[focusIndex]?.focus()
  }
}

const verify2FA = async () => {
  const fullCode = code.value.join('')
  if (fullCode.length < 6) {
    errorMsg.value = 'Veuillez saisir le code à 6 chiffres.'
    return
  }

  try {
    isLoading.value = true
    errorMsg.value = ''
    await api.post('/api/auth/verify-2fa', {
      mail: email.value,
      code: fullCode
    })
    
    // Clean up
    localStorage.removeItem('pending_email')
    // Redirect to login
    router.push({ path: '/login', query: { verified: 'true' }})
  } catch (err) {
    console.error(err)
    errorMsg.value = err.response?.data?.message || 'Code invalide.'
  } finally {
    isLoading.value = false
  }
}

const resendCode = () => {
  // Optionnel: logiques d'API pour renvoyer le code
  alert('Nouveau code envoyé (simulation)')
}
</script>

<template>
  <div class="twofa-layout">
    <div class="twofa-card">
      <div class="brand">
        <i class="ti ti-lock brand-icon"></i>
        <span class="brand-name">FileSafe</span>
      </div>

      <div class="icon-container">
        <i class="ti ti-shield-check"></i>
      </div>

      <h1>Vérification en deux étapes</h1>
      <p class="subtitle">Un code à 6 chiffres a été envoyé à <strong>{{ maskedEmail }}</strong></p>

      <form @submit.prevent="verify2FA" class="twofa-form">
        <div class="code-inputs" @paste="handlePaste">
          <input 
            v-for="(digit, index) in code" 
            :key="index"
            type="text"
            inputmode="numeric"
            maxlength="1"
            v-model="code[index]"
            :ref="el => inputRefs[index] = el"
            @input="handleInput(index, $event)"
            @keydown="handleKeydown(index, $event)"
          />
        </div>

        <div class="resend-container">
          <a href="#" class="resend-link" @click.prevent="resendCode">Renvoyer le code</a>
        </div>

        <p v-if="errorMsg" class="error-msg"><i class="ti ti-alert-circle"></i> {{ errorMsg }}</p>

        <button type="submit" class="btn-primary" :disabled="isLoading">
          {{ isLoading ? 'Chargement...' : 'Valider et accéder' }}
        </button>
      </form>

      <div class="security-note">
        <i class="ti ti-info-circle"></i>
        <span>Ce code expire dans 10 minutes. Ne le partagez jamais.</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.twofa-layout {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-primary);
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.twofa-card {
  width: 100%;
  max-width: 480px;
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 24px;
  color: var(--primary);
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.icon-container {
  width: 80px;
  height: 80px;
  background-color: rgba(244, 180, 0, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.icon-container i {
  font-size: 40px;
  color: var(--primary);
}

h1 {
  font-size: 24px;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 12px;
}

.subtitle {
  color: #aaa;
  font-size: 15px;
  margin-bottom: 32px;
  line-height: 1.5;
}

.subtitle strong {
  color: var(--text-primary);
  font-weight: 500;
}

.twofa-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.code-inputs {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.code-inputs input {
  width: 100%;
  max-width: 52px;
  height: 52px;
  background-color: var(--bg-primary);
  border: 1px solid var(--input-border);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  outline: none;
  transition: border-color 0.2s;
}

.code-inputs input:focus {
  border: 1.5px solid var(--primary);
}

.resend-container {
  text-align: center;
}

.resend-link {
  color: var(--primary);
  font-size: 14px;
  text-decoration: none;
  font-weight: 500;
}

.resend-link:hover {
  text-decoration: underline;
}

.btn-primary {
  width: 100%;
  height: 48px;
  background-color: var(--primary);
  color: var(--bg-primary);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #D89E00;
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-msg {
  color: var(--danger);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin: -8px 0 0 0;
}

.security-note {
  margin-top: 32px;
  width: 100%;
  background-color: rgba(244, 180, 0, 0.05);
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--primary);
  font-size: 13px;
  text-align: left;
}

.security-note i {
  font-size: 18px;
}
</style>
