<template>
  <el-card class="file-list-card">
    <template #header>
      <div class="card-header">
        <span>文件列表</span>
        <el-button type="primary" size="small" @click="loadFiles">
          <el-icon><refresh /></el-icon> 刷新
        </el-button>
      </div>
    </template>

    <el-table
      v-loading="loading"
      :data="files"
      style="width: 100%"
      @row-click="handleRowClick"
      highlight-current-row
    >
      <el-table-column prop="filename" label="文件名" min-width="200" />
      <el-table-column prop="file_size" label="大小" width="120">
        <template #default="{ row }">
          {{ formatSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="sheet_count" label="Sheet数" width="100" align="center" />
      <el-table-column prop="created_at" label="上传时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <el-button type="primary" size="small" link @click.stop="handleDownload(row)">
            <el-icon><download /></el-icon>
          </el-button>
          <el-button type="danger" size="small" link @click.stop="handleDelete(row)">
            <el-icon><delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > pageSize"
      class="pagination"
      background
      layout="prev, pager, next"
      :total="total"
      :page-size="pageSize"
      :current-page="currentPage"
      @current-change="handlePageChange"
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Refresh, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getFiles, downloadFile, deleteFile } from '../api/excel'

const emit = defineEmits(['select'])

const loading = ref(false)
const files = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

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

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadFiles = async () => {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const response = await getFiles(skip, pageSize.value)
    files.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadFiles()
}

const handleRowClick = (row) => {
  emit('select', row)
}

const handleDownload = async (row) => {
  try {
    await downloadFile(row.id, row.filename)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除文件 "${row.filename}" 吗？`,
      '确认删除',
      { type: 'warning' }
    )
    await deleteFile(row.id)
    ElMessage.success('删除成功')
    loadFiles()
    emit('select', null)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

defineExpose({ loadFiles })

onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.file-list-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination {
  margin-top: 15px;
  justify-content: center;
}
:deep(.el-table__row) {
  cursor: pointer;
}
</style>
