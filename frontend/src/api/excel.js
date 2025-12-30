import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

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
