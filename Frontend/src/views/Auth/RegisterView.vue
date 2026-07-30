<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()

const nom = ref('')
const prenom = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const isLoading = ref(false)
const errorMsg = ref('')
const isDarkMode = ref(true)

onMounted(() => {
  if (localStorage.getItem('token')) {
    router.push('/')
  }
  isDarkMode.value = localStorage.getItem('theme') !== 'light'
})

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.remove('light-mode')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.add('light-mode')
    localStorage.setItem('theme', 'light')
  }
}

const validatePassword = (pwd) => {
  const minLength = pwd.length >= 8
  const hasUpperCase = /[A-Z]/.test(pwd)
  const hasNumber = /[0-9]/.test(pwd)
  return minLength && hasUpperCase && hasNumber
}

const handleRegister = async () => {
  errorMsg.value = ''

  if (!nom.value || !prenom.value || !email.value || !password.value || !confirmPassword.value) {
    errorMsg.value = 'Veuillez remplir tous les champs.'
    return
  }

  if (password.value !== confirmPassword.value) {
    errorMsg.value = 'Les mots de passe ne correspondent pas.'
    return
  }

  if (!validatePassword(password.value)) {
    errorMsg.value = 'Le mot de passe doit contenir 8 caractères, 1 majuscule et 1 chiffre.'
    return
  }

  try {
    isLoading.value = true
    const { data } = await api.post('/api/auth/register', {
      nom: nom.value,
      prenom: prenom.value,
      mail: email.value,
      pswd: password.value
    })

    localStorage.setItem('pending_email', email.value)
    router.push('/2fa')
  } catch (err) {
    console.error(err)
    errorMsg.value = err.response?.data?.message || 'Erreur lors de l\'inscription.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="auth-layout">
    <!-- Colonne Gauche -->
    <div class="auth-left">
      <div class="brand">
        <img src="/logo.png" alt="FileSafe Logo" class="brand-logo-img" />
      </div>
      
      <div class="hero-content">
        <h1>Vos documents officiels, protégés et toujours accessibles.</h1>
        
        <div class="features-list">
          <div class="feature-item">
            <div class="feature-icon"><i class="ti ti-scan"></i></div>
            <div class="feature-text">Analyse IA pour extraire et vérifier les données</div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><i class="ti ti-bell-ringing"></i></div>
            <div class="feature-text">Alertes intelligentes avant expiration</div>
          </div>
          <div class="feature-item">
            <div class="feature-icon"><i class="ti ti-share"></i></div>
            <div class="feature-text">Partage sécurisé avec contrôle d'accès</div>
          </div>
        </div>
      </div>
      
      <div class="footer">
        © 2026 FileSafe
      </div>
    </div>

    <!-- Colonne Droite -->
    <div class="auth-right">
      <div class="top-controls">
        <button class="theme-toggle" @click="toggleTheme" title="Changer de thème">
          <i :class="isDarkMode ? 'ti ti-sun' : 'ti ti-moon'"></i>
        </button>
      </div>

      <div class="auth-card">
        <div class="tabs">
          <button class="tab" @click="router.push('/login')">Connexion</button>
          <button class="tab active">Inscription</button>
        </div>

        <div class="form-container">
          <h2>Créer un compte</h2>
          
          <form @submit.prevent="handleRegister" class="auth-form">
            
            <div class="row">
              <div class="form-group flex-1">
                <label>Nom</label>
                <div class="input-wrapper no-icon">
                  <input type="text" v-model="nom" placeholder="Nom" required>
                </div>
              </div>
              <div class="form-group flex-1">
                <label>Prénom</label>
                <div class="input-wrapper no-icon">
                  <input type="text" v-model="prenom" placeholder="Prénom" required>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>Adresse email</label>
              <div class="input-wrapper">
                <i class="ti ti-mail input-icon"></i>
                <input type="email" v-model="email" placeholder="votre@email.com" required>
              </div>
            </div>

            <div class="form-group">
              <label>Mot de passe</label>
              <div class="input-wrapper">
                <i class="ti ti-lock input-icon"></i>
                <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="••••••••" required>
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <i :class="showPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
                </button>
              </div>
            </div>

            <div class="form-group">
              <label>Confirmer le mot de passe</label>
              <div class="input-wrapper">
                <i class="ti ti-lock input-icon"></i>
                <input :type="showConfirmPassword ? 'text' : 'password'" v-model="confirmPassword" placeholder="••••••••" required>
                <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
                  <i :class="showConfirmPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
                </button>
              </div>
            </div>

            <button type="submit" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Chargement...' : 'Créer mon compte' }}
            </button>
            
            <p v-if="errorMsg" class="error-msg"><i class="ti ti-alert-circle"></i> {{ errorMsg }}</p>
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
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-card);
}

/* --- Left Column --- */
.auth-left {
  display: none;
  width: 42%;
  background-color: var(--bg-primary);
  padding: 40px;
  flex-direction: column;
  justify-content: space-between;
}

@media (min-width: 1024px) {
  .auth-left {
    display: flex;
  }
}

.brand {
  display: flex;
  align-items: center;
}

.brand-logo-img {
  height: 50px;
  object-fit: contain;
}

.hero-content {
  max-width: 400px;
}

.hero-content h1 {
  font-size: 36px;
  line-height: 1.2;
  color: var(--text-primary);
  margin-bottom: 40px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.feature-icon {
  width: 48px;
  height: 48px;
  background-color: rgba(244, 180, 0, 0.1);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-icon i {
  font-size: 24px;
  color: var(--primary);
}

.feature-text {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
}

.footer {
  color: var(--text-secondary);
  font-size: 14px;
}

/* --- Right Column --- */
.auth-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-card);
  position: relative;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.top-controls {
  position: absolute;
  top: 24px;
  right: 24px;
}

.theme-toggle {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s;
}

.theme-toggle:hover {
  color: var(--text-primary);
}

.auth-card {
  width: 100%;
  max-width: 480px;
  background-color: var(--bg-card);
  border-radius: 18px;
}

/* Tabs */
.tabs {
  display: flex;
  background-color: var(--bg-primary);
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 32px;
}

.tab {
  flex: 1;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 15px;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab.active {
  background-color: var(--primary);
  color: var(--bg-primary);
}

.tab:not(.active):hover {
  color: var(--text-primary);
}

/* Form */
.form-container h2 {
  font-size: 28px;
  color: var(--text-primary);
  margin-bottom: 24px;
  font-weight: 600;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.row {
  display: flex;
  gap: 16px;
}

.flex-1 {
  flex: 1;
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
  font-family: 'Inter', sans-serif;
  outline: none;
  transition: border-color 0.2s;
}

.input-wrapper.no-icon input {
  padding-left: 16px;
}

.input-wrapper input:focus {
  border: 1.5px solid var(--primary);
}

.toggle-password {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
}

.toggle-password:hover {
  color: var(--text-primary);
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
  margin-top: 8px;
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
  margin-top: 4px;
}
</style>
