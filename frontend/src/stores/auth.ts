import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types'
import { apiLogin, apiVerify2FA, apiGetMe } from '@/api/auth'

const STORAGE_TOKEN = 'vesto_token'
const STORAGE_TRUSTED = 'vesto_trusted_device'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(STORAGE_TOKEN))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function login(username: string, password: string): Promise<{ done: true } | { done: false; partialToken: string }> {
    loading.value = true
    error.value = null
    try {
      const trustedDevice = localStorage.getItem(STORAGE_TRUSTED)
      const data = await apiLogin(username, password, trustedDevice)

      if (data.requires_2fa && data.partial_token) {
        return { done: false, partialToken: data.partial_token }
      }

      _setToken(data.access_token!)
      await fetchMe()
      return { done: true }
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Errore di accesso'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function verify2FA(partialToken: string, otpCode: string, rememberDevice: boolean): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const data = await apiVerify2FA(partialToken, otpCode, rememberDevice)
      if (data.trusted_device_token) {
        localStorage.setItem(STORAGE_TRUSTED, data.trusted_device_token)
      }
      _setToken(data.access_token)
      await fetchMe()
    } catch (e: any) {
      error.value = e.response?.data?.detail || 'Codice OTP non valido'
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

  function _setToken(t: string) {
    token.value = t
    localStorage.setItem(STORAGE_TOKEN, t)
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem(STORAGE_TOKEN)
    // trusted device token è mantenuto intenzionalmente per il prossimo login
  }

  function isAdmin(): boolean {
    return user.value?.role === 'admin'
  }

  return { token, user, loading, error, login, verify2FA, logout, fetchMe, isAdmin }
})
