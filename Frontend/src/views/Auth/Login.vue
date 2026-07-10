<template>
  <div class="auth-layout">
    <div class="auth-left">
      <div>
        <div class="auth-brand">
          <div class="auth-brand-icon"><i class="ti ti-lock"></i></div>
          <div class="auth-brand-name">CoffreDoc</div>
        </div>
        <h1 class="auth-tagline">Vos documents officiels, en sécurité, toujours accessibles.</h1>
        <div class="auth-features">
          <div class="auth-feature">
            <i class="ti ti-brain"></i>
            <span>Analyse IA intelligente de vos documents</span>
          </div>
          <div class="auth-feature">
            <i class="ti ti-clock-hour-4"></i>
            <span>Alertes avant expiration automatiques</span>
          </div>
          <div class="auth-feature">
            <i class="ti ti-shield-lock"></i>
            <span>Partage sécurisé avec traçabilité complète</span>
          </div>
        </div>
      </div>
      <div class="auth-left-footer">
        © 2026 CoffreDoc — Conçu pour les particuliers béninois et africains.
      </div>
    </div>

    <div class="auth-right">
      <div class="auth-header">
        <button class="notification-btn" @click="$router.push('/notifications')">
          <i class="ti ti-bell"></i>
          <span class="notification-badge">3</span>
        </button>
        <button class="theme-toggle" @click="toggleTheme" :title="isDark ? 'Mode clair' : 'Mode sombre'">
          <i :class="isDark ? 'ti ti-sun' : 'ti ti-moon'"></i>
        </button>
      </div>

      <div class="auth-form-container">
        <!-- Écran 2FA -->
        <two-factor-auth
          v-if="show2FA"
          :email="loginForm.email"
          :on-verify="verify2FACode"
          @resend="handleResend2FA"
          @success="showSuccessMessage"
        />

        <!-- Écran de connexion -->
        <div v-else>
          <div class="auth-tabs">
            <button 
              class="auth-tab" 
              :class="{ active: activeTab === 'login' }" 
              @click="activeTab = 'login'">
              Connexion
            </button>
            <button 
              class="auth-tab" 
              :class="{ active: activeTab === 'register' }" 
              @click="activeTab = 'register'">
              Inscription
            </button>
          </div>

          <form v-if="activeTab === 'login'" @submit.prevent="submitLogin">
            <h2 class="auth-form-title">Heureux de vous revoir </h2>
            
            <div v-if="loginError" class="auth-error">
              <i class="ti ti-alert-circle"></i>
              {{ loginError }}
            </div>

            <div class="input-group">
              <i class="ti ti-mail input-icon"></i>
              <input 
                type="email" 
                class="input-field" 
                placeholder="Adresse email" 
                v-model="loginForm.email"
                required
              />
            </div>

            <div class="input-group">
              <i class="ti ti-lock input-icon"></i>
              <input 
                :type="showPassword ? 'text' : 'password'" 
                class="input-field" 
                placeholder="Mot de passe" 
                v-model="loginForm.password"
                required
              />
              <button type="button" class="input-toggle" @click="showPassword = !showPassword">
                <i :class="showPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
              </button>
            </div>

            <a class="auth-link" @click.prevent="handleForgotPassword">
              Mot de passe oublié ?
            </a>

            <button type="submit" class="btn btn-primary auth-submit" :disabled="isLoading">
              <span v-if="!isLoading">Se connecter</span>
              <span v-else>Connexion en cours...</span>
            </button>
          </form>

          <form v-else @submit.prevent="submitRegister">
            <h2 class="auth-form-title">Créer votre compte</h2>
            
            <div v-if="registerError" class="auth-error">
              <i class="ti ti-alert-circle"></i>
              {{ registerError }}
            </div>

            <div class="auth-input-row">
              <div class="input-group">
                <i class="ti ti-user input-icon"></i>
                <input 
                  type="text" 
                  class="input-field" 
                  placeholder="Nom" 
                  v-model="registerForm.lastName"
                  required
                />
              </div>
              <div class="input-group">
                <i class="ti ti-user input-icon"></i>
                <input 
                  type="text" 
                  class="input-field" 
                  placeholder="Prénom" 
                  v-model="registerForm.firstName"
                  required
                />
              </div>
            </div>

            <div class="input-group">
              <i class="ti ti-mail input-icon"></i>
              <input 
                type="email" 
                class="input-field" 
                placeholder="Adresse email" 
                v-model="registerForm.email"
                required
              />
            </div>

            <div class="input-group">
              <i class="ti ti-lock input-icon"></i>
              <input 
                :type="showRegisterPassword ? 'text' : 'password'" 
                class="input-field" 
                placeholder="Mot de passe" 
                v-model="registerForm.password"
                required
              />
              <button type="button" class="input-toggle" @click="showRegisterPassword = !showRegisterPassword">
                <i :class="showRegisterPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
              </button>
            </div>

            <div class="input-group">
              <i class="ti ti-lock input-icon"></i>
              <input 
                :type="showRegisterConfirmPassword ? 'text' : 'password'" 
                class="input-field" 
                placeholder="Confirmer le mot de passe" 
                v-model="registerForm.confirmPassword"
                required
              />
              <button type="button" class="input-toggle" @click="showRegisterConfirmPassword = !showRegisterConfirmPassword">
                <i :class="showRegisterConfirmPassword ? 'ti ti-eye-off' : 'ti ti-eye'"></i>
              </button>
            </div>

            <button type="submit" class="btn btn-primary auth-submit" style="margin-top:8px" :disabled="isLoading">
              <span v-if="!isLoading">Créer mon compte</span>
              <span v-else>Inscription en cours...</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import TwoFactorAuth from './TwoFactorAuth.vue';
import ThemeToggle from '@/components/Common/ThemeToggle.vue';

export default {
  name: 'LoginView',
  
  components: {
    TwoFactorAuth,
    ThemeToggle
  },

  props: {
    isDark: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      activeTab: 'login',
      showPassword: false,
      showRegisterPassword: false,
      showRegisterConfirmPassword: false,
      show2FA: false,
      isLoading: false,
      loginError: null,
      registerError: null,
      
      loginForm: {
        email: '',
        password: ''
      },
      
      registerForm: {
        firstName: '',
        lastName: '',
        email: '',
        password: '',
        confirmPassword: ''
      }
    }
  },

  methods: {
    toggleTheme() {
      const body = document.body;
      if (body.classList.contains('light')) {
        body.classList.remove('light');
        body.classList.add('dark');
      } else {
        body.classList.remove('dark');
        body.classList.add('light');
      }
      this.$emit('toggle-theme');
    },

    async submitLogin() {
      if (!this.loginForm.email || !this.loginForm.password) {
        this.loginError = 'Veuillez remplir tous les champs.';
        return;
      }

      this.isLoading = true;
      this.loginError = null;

      try {
        // Simuler une requête de connexion
        const response = await this.mockLogin(this.loginForm);
        
        if (response.requires2FA) {
          // L'utilisateur a besoin de 2FA
          this.show2FA = true;
          // Ne pas émettre 'login-success' ici, sinon App.vue cache le formulaire !
        } else {
          // Connexion réussie sans 2FA
          this.$emit('login-success', { user: response.user });
        }
      } catch (error) {
        this.loginError = error.message || 'Erreur de connexion. Veuillez réessayer.';
      } finally {
        this.isLoading = false;
      }
    },

    async mockLogin(credentials) {
      // Simuler une API
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          // Simuler une vérification
          if (credentials.email === 'beni.hountondji@email.bj' && credentials.password === 'password') {
            resolve({
              requires2FA: true,
              user: {
                id: '1',
                name: 'Béni Hountondji',
                email: credentials.email
              }
            });
          } else {
            reject(new Error('Email ou mot de passe incorrect.'));
          }
        }, 1500);
      });
    },

    async verify2FACode(code) {
      // Simuler la vérification du code 2FA
      return new Promise((resolve) => {
        setTimeout(() => {
          const isValid = code && code.length === 6; // Accepte n'importe quel code à 6 chiffres
          if (isValid) {
            this.$emit('login-success', { 
              user: {
                id: '1',
                name: 'Béni Hountondji',
                email: this.loginForm.email
              }
            });
          }
          resolve(isValid);
        }, 1000);
      });
    },

    handleResend2FA() {
      console.log('Renvoyer le code 2FA');
      // Logique pour renvoyer le code
    },

    showSuccessMessage(message) {
      this.$emit('notification', {
        type: 'success',
        message
      });
    },

    handleForgotPassword() {
      this.$emit('forgot-password');
    },

    async submitRegister() {
      if (!this.validateRegisterForm()) return;

      this.isLoading = true;
      this.registerError = null;

      try {
        // Simuler une inscription
        await this.mockRegister(this.registerForm);
        this.$emit('register-success', { 
          user: {
            name: `${this.registerForm.firstName} ${this.registerForm.lastName}`,
            email: this.registerForm.email
          }
        });
      } catch (error) {
        this.registerError = error.message || 'Erreur d\'inscription. Veuillez réessayer.';
      } finally {
        this.isLoading = false;
      }
    },

    validateRegisterForm() {
      if (!this.registerForm.firstName || !this.registerForm.lastName || 
          !this.registerForm.email || !this.registerForm.password || 
          !this.registerForm.confirmPassword) {
        this.registerError = 'Veuillez remplir tous les champs.';
        return false;
      }

      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.registerError = 'Les mots de passe ne correspondent pas.';
        return false;
      }

      if (this.registerForm.password.length < 8) {
        this.registerError = 'Le mot de passe doit contenir au moins 8 caractères.';
        return false;
      }

      this.registerError = null;
      return true;
    },

    async mockRegister(formData) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            success: true,
            user: {
              id: '1',
              name: `${formData.firstName} ${formData.lastName}`,
              email: formData.email
            }
          });
        }, 1500);
      });
    }
  }
}
</script>

<style scoped>
/* Theme Globals */
:global(body) {
  font-family: 'Inter', sans-serif;
}
:global(body.light) {
  --bg-primary: #F5F5F5;
  --bg-secondary: #FFFFFF;
  --text-primary: #2C2C2C;
  --text-secondary: #555555;
  --border-color: #DDDDDD;
  --primary: #F4B400;
}
:global(body.dark), :global(body) {
  --bg-primary: #121212;
  --bg-secondary: #1E1E1E;
  --text-primary: #FFFFFF;
  --text-secondary: #888888;
  --border-color: #333333;
  --primary: #F4B400;
}

.auth-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
  font-family: 'Inter', sans-serif;
}

.auth-left {
  flex: 1;
  background: var(--bg-secondary);
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;
  border-right: 1px solid var(--border-color);
}

.auth-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.auth-brand-icon {
  width: 40px;
  height: 40px;
  background: var(--primary);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.auth-brand-name {
  font-size: 20px;
  font-weight: 500;
  color: var(--text-primary);
}

.auth-tagline {
  font-size: 24px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 32px;
  line-height: 1.3;
}

.auth-features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: var(--text-secondary);
}

.auth-feature i {
  font-size: 20px;
  color: var(--primary);
}

.auth-left-footer {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 48px;
}

.auth-right {
  flex: 1;
  max-width: 480px;
  padding: 48px 40px;
  display: flex;
  flex-direction: column;
  position: relative;
  background: var(--bg-primary);
}

.auth-header {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 10;
}

.notification-btn, .theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-primary);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.notification-btn:hover, .theme-toggle:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--primary);
  color: #121212;
  font-size: 10px;
  font-weight: bold;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-form-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  background: var(--bg-secondary);
  padding: 4px;
  border-radius: 8px;
  margin-bottom: 32px;
}

.auth-tab {
  flex: 1;
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
}

.auth-tab.active {
  background: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.auth-form-title {
  font-size: 24px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.input-group {
  position: relative;
  margin-bottom: 16px;
}

.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 18px;
  pointer-events: none;
}

.input-field {
  width: 100%;
  padding: 10px 40px 10px 42px;
  min-height: 48px;
  border: 0.5px solid var(--border-color);
  border-radius: 8px;
  background: #121212;
  color: #FFFFFF;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.2s;
}

.input-field::placeholder {
  font-size: 14px;
  color: #555555;
  font-weight: 400;
}

.input-field:focus {
  outline: none;
  border: 1.5px solid #F4B400;
  box-shadow: none;
  background: #121212;
}

.input-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
}

.auth-link {
  display: block;
  text-align: right;
  font-size: 14px;
  color: #F4B400;
  cursor: pointer;
  margin-bottom: 20px;
}

.auth-link:hover {
  text-decoration: underline;
}

.auth-submit {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  background: #F4B400;
  color: #121212;
  border: none;
  cursor: pointer;
  transition: opacity 0.2s;
}

.auth-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.auth-error {
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  color: var(--danger);
  font-size: 14px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.auth-input-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Responsive */
@media (max-width: 1024px) {
  .auth-left {
    display: none;
  }
  
  .auth-right {
    max-width: 100%;
    padding: 32px 24px;
  }
}

@media (max-width: 480px) {
  .auth-right {
    padding: 24px 16px;
  }
  
  .auth-input-row {
    grid-template-columns: 1fr;
  }
}
</style>