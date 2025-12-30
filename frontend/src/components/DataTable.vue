<template>
  <el-card v-if="file" class="data-table-card">
    <template #header>
      <div class="card-header">
        <span class="filename">{{ file.filename }}</span>
        <div class="header-controls">
          <el-select v-model="currentSheetId" placeholder="选择 Sheet" @change="handleSheetChange" style="width: 150px;">
            <el-option
              v-for="sheet in sheets"
              :key="sheet.id"
              :label="sheet.sheet_name"
              :value="sheet.id"
            />
          </el-select>
          <el-switch
            v-model="enablePagination"
            active-text="分页"
            inactive-text="全部"
            @change="handlePaginationChange"
            style="margin-left: 15px;"
          />
          <el-select
            v-if="enablePagination"
            v-model="pageSize"
            @change="handlePageSizeChange"
            style="width: 100px; margin-left: 10px;"
          >
            <el-option :value="20" label="20条/页" />
            <el-option :value="50" label="50条/页" />
            <el-option :value="100" label="100条/页" />
            <el-option :value="200" label="200条/页" />
          </el-select>
        </div>
      </div>
    </template>

    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        style="width: 100%"
        border
        :max-height="tableMaxHeight"
        :height="tableMaxHeight"
      >
        <el-table-column type="index" label="#" width="60" fixed="left" />
        <el-table-column
          v-for="(header, index) in headers"
          :key="index"
          :prop="String(index)"
          :label="header"
          min-width="150"
          show-overflow-tooltip
        />
      </el-table>
    </div>

    <div class="table-footer">
      <span class="data-info">
        共 {{ totalRows }} 行 × {{ headers.length }} 列
        <template v-if="enablePagination">
          ，当前第 {{ currentPage }} 页
        </template>
      </span>
      <el-pagination
        v-if="enablePagination && totalRows > pageSize"
        class="pagination"
        background
        layout="prev, pager, next, jumper"
        :total="totalRows"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </el-card>

  <el-empty v-else description="请选择一个文件查看内容" />
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFileDetail, getSheetData } from '../api/excel'

const props = defineProps({
  file: {
    type: Object,
    default: null
  }
})

const loading = ref(false)
const sheets = ref([])
const currentSheetId = ref(null)
const headers = ref([])
const tableData = ref([])
const totalRows = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const enablePagination = ref(true)
const tableMaxHeight = ref(600)

// 动态计算表格高度
const updateTableHeight = () => {
  const windowHeight = window.innerHeight
  // 减去头部、卡片头部、底部分页等高度
  tableMaxHeight.value = Math.max(400, windowHeight - 280)
}

onMounted(() => {
  updateTableHeight()
  window.addEventListener('resize', updateTableHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight)
})

watch(() => props.file, async (newFile) => {
  if (newFile) {
    await loadFileDetail()
  } else {
    sheets.value = []
    currentSheetId.value = null
    headers.value = []
    tableData.value = []
    totalRows.value = 0
    currentPage.value = 1
  }
}, { immediate: true })

const loadFileDetail = async () => {
  try {
    const response = await getFileDetail(props.file.id)
    sheets.value = response.data.sheets
    if (sheets.value.length > 0) {
      currentSheetId.value = sheets.value[0].id
      await loadSheetData()
    }
  } catch (error) {
    ElMessage.error('获取文件详情失败')
  }
}

const loadSheetData = async () => {
  if (!currentSheetId.value) return

  loading.value = true
  try {
    const actualPageSize = enablePagination.value ? pageSize.value : 10000
    const response = await getSheetData(
      props.file.id,
      currentSheetId.value,
      currentPage.value,
      actualPageSize
    )
    headers.value = response.data.headers
    tableData.value = response.data.data.map((row, rowIndex) => {
      const rowObj = { _rowIndex: rowIndex }
      row.forEach((cell, colIndex) => {
        rowObj[String(colIndex)] = cell
      })
      return rowObj
    })
    totalRows.value = response.data.total_rows - 1 // 减去表头行
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleSheetChange = () => {
  currentPage.value = 1
  loadSheetData()
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadSheetData()
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  loadSheetData()
}

const handlePaginationChange = () => {
  currentPage.value = 1
  loadSheetData()
}
</script>

<style scoped>
.data-table-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filename {
  font-weight: 500;
  font-size: 15px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-controls {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 5px;
}

.table-container {
  flex: 1;
  overflow: hidden;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
  flex-wrap: wrap;
  gap: 10px;
}

.data-info {
  color: #909399;
  font-size: 13px;
}

.pagination {
  justify-content: flex-end;
}
</style>
