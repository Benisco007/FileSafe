import { ref, watchEffect } from 'vue'

// État réactif PARTAGÉ (une seule instance pour toute l'application).
// Défini en dehors de la fonction useTheme() pour que tous les
// composants qui l'utilisent (App.vue, Login.vue, AppSidebar.vue,
// chaque vue derrière le router...) lisent et modifient le MÊME état.
const isDark = ref(true)
let initialized = false

function applyTheme() {
  const root = document.documentElement
  root.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

function initTheme() {
  if (initialized) return
  initialized = true

  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
  } else {
    // Respecte la préférence système si aucun choix n'a encore été fait
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }

  // Applique le thème dès que isDark change, où que ce soit dans l'app
  watchEffect(applyTheme)
}

export function useTheme() {
  initTheme()
  return { isDark, toggleTheme }
}
