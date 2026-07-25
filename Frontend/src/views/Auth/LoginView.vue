<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import api from '../../api'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')
const isDarkMode = ref(true)

onMounted(() => {
  if (localStorage.getItem('token')) {
    if (authStore.user?.role === 'admin') {
      router.push('/admin')
    } else {
      router.push('/')
    }
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

const handleLogin = async () => {
  if (!email.value || !password.value) {
    errorMsg.value = 'Veuillez remplir tous les champs.'
    return
  }

  try {
    isLoading.value = true
    errorMsg.value = ''
    const { data } = await api.post('/api/auth/login', {
      email: email.value,
      password: password.value
    })
      if (data.requires_2fa) {

    localStorage.setItem('pending_2fa_email', data.mail)
    router.push('/2fa-login')  // nouvelle route
    } else {
      localStorage.setItem('token', data.access_token)
      authStore.setAuth(data.access_token, data.user)
      if (data.user?.role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/')
      }
    }
  } catch (err) {
    console.error('Erreur login complète:', err)
    console.error('Response data:', err.response?.data)
    errorMsg.value = err.response?.data?.detail || err.response?.data?.message || 'Identifiants invalides.'
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
        <i class="ti ti-lock brand-icon"></i>
        <span class="brand-name">FileSafe</span>
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
          <button class="tab active">Connexion</button>
          <button class="tab" @click="router.push('/register')">Inscription</button>
        </div>

        <div class="form-container">
          <h2>Heureux de vous revoir 👋</h2>
          
          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="form-group">
              <label>Adresse email</label>
              <div class="input-wrapper">
                <i class="ti ti-mail input-icon"></i>
                <input type="email" v-model="email" placeholder="votre@email.com" required>
              </div>
            </div>

            <div class="form-group">
              <div class="label-row">
                <label>Mot de passe</label>
                <a href="#" class="forgot-link">Mot de passe oublié ?</a>
              </div>
              <div class="input-wrapper">
                <i class="ti ti-lock input-icon"></i>
                <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="••••••••" required>
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <i :class="showPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
                </button>
              </div>
            </div>

            <button type="submit" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Chargement...' : 'Se connecter' }}
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
  background-color: var(--bg-card); /* Background right by default on mobile */
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
  gap: 12px;
}

.brand-icon {
  font-size: 32px;
  color: var(--primary);
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
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
  /* On desktop it blends with background, on mobile we can add shadow if needed */
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-group label {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
}

.forgot-link {
  color: var(--primary);
  font-size: 13px;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
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
