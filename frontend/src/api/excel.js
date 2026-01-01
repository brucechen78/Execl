import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  withCredentials: true  // 允许携带 cookie
})

// 请求拦截器：添加认证 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('session_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理认证错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // 401 未认证
      if (error.response.status === 401) {
        localStorage.removeItem('session_token')
        ElMessage.error('登录已过期，请重新登录')
        // 刷新页面让用户重新登录
        setTimeout(() => {
          window.location.reload()
        }, 1000)
      }
      // 403 无权限
      else if (error.response.status === 403) {
        ElMessage.error('无权限访问')
      }
    }
    return Promise.reject(error)
  }
)

// 上传Excel文件
export const uploadFile = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded / e.total) * 100))
      }
    }
  })
}

// 获取文件列表
export const getFiles = (skip = 0, limit = 20) => {
  return api.get('/files', { params: { skip, limit } })
}

// 获取文件详情
export const getFileDetail = (fileId) => {
  return api.get(`/files/${fileId}`)
}

// 获取Sheet数据
export const getSheetData = (fileId, sheetId, page = 1, pageSize = 50) => {
  return api.get(`/files/${fileId}/sheets/${sheetId}/data`, {
    params: { page, page_size: pageSize }
  })
}

// 获取图片URL
export const getImageUrl = (imageId) => {
  return `/api/images/${imageId}`
}

// 下载文件
export const downloadFile = (fileId, filename) => {
  return api.get(`/files/${fileId}/download`, {
    responseType: 'blob'
  }).then(response => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  })
}

// 删除文件
export const deleteFile = (fileId) => {
  return api.delete(`/files/${fileId}`)
}

export default api
