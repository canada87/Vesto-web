import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { apiLogin, apiGetMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('vesto_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login(username: string, password: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const data = await apiLogin(username, password)
      token.value = data.access_token
      localStorage.setItem('vesto_token', data.access_token)
      await fetchMe()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Errore di accesso'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchMe(): Promise<void> {
    try {
      user.value = await apiGetMe()
    } catch {
      logout()
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('vesto_token')
  }

  function isAdmin(): boolean {
    return user.value?.role === 'admin'
  }

  return { token, user, loading, error, login, logout, fetchMe, isAdmin }
})
