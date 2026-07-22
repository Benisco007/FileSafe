<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const router = useRouter()
const authStore = useAuthStore()
const codes = ref(['', '', '', '', '', ''])
const mail = ref('')
const error = ref('')
const isLoading = ref(false)

onMounted(() => {
  mail.value = localStorage.getItem('pending_2fa_email') || ''
  if (!mail.value) router.push('/login')
})

const fullCode = computed(() => codes.value.join(''))

const nextInput = (index) => {
  if (codes.value[index] && index < 5) {
    document.getElementById(`code-${index + 1}`)?.focus()
  }
}

const verify = async () => {
  if (fullCode.value.length !== 6) {
    error.value = 'Entrez les 6 chiffres du code.'
    return
  }
  try {
    isLoading.value = true
    const { data } = await api.post('/api/auth/verify-login-2fa', {
      mail: mail.value,
      code: fullCode.value
    })
    localStorage.removeItem('pending_2fa_email')
    localStorage.setItem('token', data.access_token)
    authStore.setAuth(data.access_token, data.user)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Code invalide.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="twofa-page">
    <div class="twofa-card">
      <div class="logo">
        <div class="logo-icon"><i class="ti ti-lock"></i></div>
        <span>FileSafe</span>
      </div>
      <div class="shield-icon"><i class="ti ti-shield-check"></i></div>
      <h1>Vérification en deux étapes</h1>
      <p>Un code à 6 chiffres a été envoyé à</p>
      <span class="mail-badge">{{ mail }}</span>

      <div class="code-inputs">
        <input
          v-for="(_, i) in codes"
          :key="i"
          :id="`code-${i}`"
          type="text"
          maxlength="1"
          inputmode="numeric"
          v-model="codes[i]"
          @input="nextInput(i)"
          class="code-input"
        />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="btn-primary" @click="verify" :disabled="isLoading">
        {{ isLoading ? 'Vérification...' : 'Valider et accéder' }}
      </button>

      <div class="security-note">
        <i class="ti ti-info-circle"></i>
        <span>Ce code expire dans 10 minutes. Ne le partagez jamais.</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.twofa-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
}
.twofa-card {
  background: var(--bg-card);
  border-radius: 18px;
  padding: 40px;
  width: 100%;
  max-width: 460px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  border: 0.5px solid var(--border-color);
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.logo-icon {
  width: 34px; height: 34px;
  background: var(--primary);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #121212; font-size: 18px;
}
.logo span { font-size: 18px; font-weight: 500; color: var(--text-primary); }
.shield-icon { font-size: 52px; color: var(--primary); }
h1 { font-size: 20px; font-weight: 500; color: var(--text-primary); text-align: center; }
p { font-size: 13px; color: var(--text-secondary); text-align: center; }
.mail-badge {
  background: rgba(244,180,0,0.1);
  border: 0.5px solid rgba(244,180,0,0.3);
  color: var(--primary);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 13px;
}
.code-inputs { display: flex; gap: 8px; margin: 8px 0; }
.code-input {
  width: 48px; height: 56px;
  text-align: center;
  font-size: 22px; font-weight: 500;
  background: var(--input-bg);
  border: 0.5px solid var(--input-border);
  border-radius: 10px;
  color: var(--text-primary);
  outline: none;
}
.code-input:focus { border-color: var(--primary); }
.error { color: var(--danger); font-size: 13px; }
.btn-primary {
  width: 100%;
  background: var(--primary); color: #121212;
  border: none; border-radius: 8px;
  padding: 12px; font-size: 15px; font-weight: 500;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.security-note {
  display: flex; align-items: flex-start; gap: 8px;
  background: rgba(244,180,0,0.07);
  border: 0.5px solid rgba(244,180,0,0.2);
  border-radius: 10px; padding: 12px;
  font-size: 12px; color: var(--text-secondary);
  width: 100%;
}
.security-note i { color: var(--primary); flex-shrink: 0; font-size: 16px; }
</style>