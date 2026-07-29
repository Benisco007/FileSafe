<script setup>
import { ref, onMounted } from 'vue'
import NotificationBell from './NotificationBell.vue'

defineProps({
  sidebarOpen: { type: Boolean, default: false }
})

const emit = defineEmits(['toggle-sidebar'])

const isDarkMode = ref(true)

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'light') {
    isDarkMode.value = false
    document.documentElement.classList.add('light-mode')
  } else {
    isDarkMode.value = true
    document.documentElement.classList.remove('light-mode')
  }
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
</script>

<template>
  <header class="topbar">
    <button class="burger-btn" @click="emit('toggle-sidebar')" aria-label="Menu">
      <i :class="sidebarOpen ? 'ti ti-x' : 'ti ti-menu-2'"></i>
    </button>
    <div class="spacer"></div>
    <div class="actions">
      <button class="theme-toggle" @click="toggleTheme" title="Changer le thème">
        <i :class="isDarkMode ? 'ti ti-sun' : 'ti ti-moon'"></i>
      </button>
      <NotificationBell />
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: var(--bg-primary);
  border-bottom: 0.5px solid var(--border-color);
  flex-shrink: 0;
}

.burger-btn {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  transition: background-color 0.2s;
  margin-right: 8px;
}

.burger-btn:hover {
  background-color: var(--bg-card);
}

.spacer {
  flex: 1;
}

.actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.theme-toggle {
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.theme-toggle:hover {
  background-color: var(--border-color);
}

.theme-toggle i {
  font-size: 24px;
}

/* Mobile: show burger button, shorter topbar */
@media (max-width: 767px) {
  .topbar {
    height: 56px;
    padding: 0 16px;
  }

  .burger-btn {
    display: flex;
  }

  .theme-toggle {
    width: 44px;
    height: 44px;
  }
}
</style>
