import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const lastIp = ref(localStorage.getItem('last_ip') || null)
  const lastLogin = ref(localStorage.getItem('last_login') || null)

  const isAuthenticated = computed(() => !!token.value)

  const setAuth = (newToken, newUser) => {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  const login = async (credentials) => {
    const { data } = await api.post('/api/auth/login', credentials)
    token.value = data.access_token
    user.value = data.user
    lastIp.value = data.ip_address || null
    lastLogin.value = data.derniere_connexion || null
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    localStorage.setItem('last_ip', data.ip_address || '')
    localStorage.setItem('last_login', data.derniere_connexion || '')
  }

  const logout = () => {
    token.value = null
    user.value = null
    lastIp.value = null
    lastLogin.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('last_ip')
    localStorage.removeItem('last_login')
  }

  return {
    token,
    user,
    lastIp,
    lastLogin,
    isAuthenticated,
    setAuth,
    login,
    logout
  }
})