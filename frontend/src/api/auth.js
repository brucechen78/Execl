import api from './excel'

// 用户注册
export const register = (username, email, password) => {
  return api.post('/auth/register', { username, email, password })
}

// 用户登录
export const login = (username, password) => {
  return api.post('/auth/login', { username, password })
}

// 用户登出
export const logout = () => {
  return api.post('/auth/logout')
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return api.get('/auth/me')
}
