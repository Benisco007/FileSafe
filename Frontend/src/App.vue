<template>
  <div id="app" :data-theme="isDark ? 'dark' : 'light'">
    <!-- Écran d'authentification -->
    <login-view
      v-if="!isAuthenticated"
      :is-dark="isDark"
      @toggle-theme="toggleTheme"
      @login-success="handleLoginSuccess"
      @notification="showNotification"
    />

    <!-- Application principale (à développer) -->
    <div v-else>
      <!-- Contenu de l'application -->
      <div class="app-layout">
        <!-- Sidebar, etc. -->
        <div class="main-content">
          <h1>Bienvenue dans CoffreDoc</h1>
        </div>
      </div>
    </div>

    <!-- Notification toast -->
    <div v-if="notification" class="notification" :class="notification.type">
      <i :class="notification.icon"></i>
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import LoginView from '@/views/Auth/Login.vue';
import '@/styles/theme.css';

export default {
  name: 'App',
  
  components: {
    LoginView
  },

  data() {
    return {
      isDark: true,
      isAuthenticated: false,
      notification: null
    }
  },

  methods: {
    toggleTheme() {
      this.isDark = !this.isDark;
      // Sauvegarder la préférence
      localStorage.setItem('theme', this.isDark ? 'dark' : 'light');
    },

    handleLoginSuccess(data) {
      console.log('Connexion réussie:', data);
      this.isAuthenticated = true;
      // Sauvegarder les données utilisateur
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }
    },

    showNotification(data) {
      this.notification = {
        ...data,
        icon: data.type === 'success' ? 'ti ti-check-circle' : 'ti ti-info-circle'
      };
      
      // Masquer après 5 secondes
      setTimeout(() => {
        this.notification = null;
      }, 5000);
    }
  },

  mounted() {
    // Restaurer la préférence de thème
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      this.isDark = savedTheme === 'dark';
    }
    
    // Vérifier si l'utilisateur est déjà connecté
    const user = localStorage.getItem('user');
    if (user) {
      this.isAuthenticated = true;
    }
  }
}
</script>

<style>
/* Styles globaux */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background 0.3s, color 0.3s;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-ghost:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 16px 24px;
  border-radius: 12px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.notification.success {
  border-color: var(--success);
}

.notification.success i {
  color: var(--success);
}

.notification.error {
  border-color: var(--danger);
}

.notification.error i {
  color: var(--danger);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>