<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()
const mail = ref('')
const isLoading = ref(false)
const errorMsg = ref('')

const handleSubmit = async () => {
  if (!mail.value) {
    errorMsg.value = 'Veuillez saisir votre email.'
    return
  }
  try {
    isLoading.value = true
    errorMsg.value = ''
    await api.post('/api/auth/forgot-password', { mail: mail.value })
    localStorage.setItem('reset_mail', mail.value)
    router.push('/reset-password')
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Une erreur est survenue.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-layout">
    <div class="auth-right">
      <div class="auth-card">
        <div class="back-link" @click="router.push('/login')">
          <i class="ti ti-arrow-left"></i> Retour à la connexion
        </div>

        <div class="form-container">
          <h2>Mot de passe oublié</h2>
          <p class="subtitle">Saisissez votre email, nous vous enverrons un code de vérification.</p>

          <form @submit.prevent="handleSubmit" class="auth-form">
            <div class="form-group">
              <label>Adresse email</label>
              <div class="input-wrapper">
                <i class="ti ti-mail input-icon"></i>
                <input type="email" v-model="mail" placeholder="votre@email.com" required>
              </div>
            </div>

            <button type="submit" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Envoi en cours...' : 'Envoyer le code' }}
            </button>

            <p v-if="errorMsg" class="error-msg">
              <i class="ti ti-alert-circle"></i> {{ errorMsg }}
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: flex;
  min-height: 100vh;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-card);
}

.auth-right {
  width: 100%;
  max-width: 480px;
  padding: 20px;
}

.auth-card {
  background-color: var(--bg-card);
  border-radius: 18px;
  padding: 8px;
}

.back-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 32px;
  transition: color 0.2s;
}

.back-link:hover {
  color: var(--primary);
}

.form-container h2 {
  font-size: 28px;
  color: var(--text-primary);
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 24px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-secondary);
  font-size: 20px;
}

.input-wrapper input {
  width: 100%;
  height: 48px;
  background-color: var(--bg-primary);
  border: 0.5px solid var(--input-border);
  border-radius: 8px;
  color: var(--text-primary);
  padding-left: 42px;
  padding-right: 16px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.input-wrapper input:focus {
  border: 1.5px solid var(--primary);
}

.btn-primary {
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
  gap: 6px;
}
</style>