<template>
  <el-upload
    class="upload-area"
    drag
    action="#"
    :auto-upload="false"
    :show-file-list="false"
    :on-change="handleFileChange"
    accept=".xls,.xlsx"
  >
    <el-icon class="el-icon--upload" :size="60"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将 Excel 文件拖到此处，或 <em>点击上传</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        支持 .xls 和 .xlsx 格式，文件大小不超过 50MB
      </div>
    </template>
  </el-upload>

  <el-dialog v-model="dialogVisible" title="上传文件" width="400px" :close-on-click-modal="false">
    <div class="upload-info">
      <p><strong>文件名：</strong>{{ selectedFile?.name }}</p>
      <p><strong>大小：</strong>{{ formatSize(selectedFile?.size) }}</p>
    </div>
    <el-progress v-if="uploading" :percentage="uploadProgress" :status="uploadStatus" />
    <template #footer>
      <el-button @click="dialogVisible = false" :disabled="uploading">取消</el-button>
      <el-button type="primary" @click="handleUpload" :loading="uploading">
        {{ uploading ? '上传中...' : '确认上传' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadFile } from '../api/excel'

const emit = defineEmits(['uploaded'])

const dialogVisible = ref(false)
const selectedFile = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')

const formatSize = (size) => {
  if (!size) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

const handleFileChange = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['xls', 'xlsx'].includes(ext)) {
    ElMessage.error('只支持 .xls 和 .xlsx 格式的文件')
    return
  }
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return
  }
  selectedFile.value = file.raw
  uploadProgress.value = 0
  uploadStatus.value = ''
  dialogVisible.value = true
}

const handleUpload = async () => {
  if (!selectedFile.value) return

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = ''

  try {
    await uploadFile(selectedFile.value, (progress) => {
      uploadProgress.value = progress
    })
    uploadStatus.value = 'success'
    ElMessage.success('上传成功')
    dialogVisible.value = false
    emit('uploaded')
  } catch (error) {
    uploadStatus.value = 'exception'
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.upload-area {
  width: 100%;
  margin-bottom: 20px;
}
.upload-info {
  margin-bottom: 15px;
}
.upload-info p {
  margin: 8px 0;
  color: #606266;
}
</style>
