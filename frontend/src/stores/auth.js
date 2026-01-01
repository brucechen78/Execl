import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, logout, getCurrentUser } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const sessionToken = ref(localStorage.getItem('session_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value && !!sessionToken.value)

  // 设置认证信息
  const setAuth = (token, userData) => {
    sessionToken.value = token
    user.value = userData
    localStorage.setItem('session_token', token)
  }

  // 清除认证信息
  const clearAuth = () => {
    sessionToken.value = null
    user.value = null
    localStorage.removeItem('session_token')
  }

  // 登录
  const loginAction = async (username, password) => {
    loading.value = true
    try {
      const response = await login(username, password)
      setAuth(response.data.access_token, response.data.user)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || '登录失败'
      }
    } finally {
      loading.value = false
    }
  }

  // 注册
  const registerAction = async (username, email, password) => {
    loading.value = true
    try {
      await register(username, email, password)
      // 注册后自动登录
      const response = await login(username, password)
      setAuth(response.data.access_token, response.data.user)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || '注册失败'
      }
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logoutAction = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      clearAuth()
    }
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!sessionToken.value) {
      return false
    }

    loading.value = true
    try {
      const response = await getCurrentUser()
      user.value = response.data
      return true
    } catch (error) {
      clearAuth()
      return false
    } finally {
      loading.value = false
    }
  }

  // 初始化：检查本地存储的 token
  const initialize = async () => {
    if (sessionToken.value) {
      const success = await fetchCurrentUser()
      if (!success) {
        clearAuth()
      }
    }
  }

  return {
    user,
    sessionToken,
    loading,
    isAuthenticated,
    setAuth,
    clearAuth,
    loginAction,
    registerAction,
    logoutAction,
    fetchCurrentUser,
    initialize
  }
})
