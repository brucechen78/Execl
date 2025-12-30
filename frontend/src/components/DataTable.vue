<template>
  <div class="data-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button @click="handleBack" :icon="ArrowLeft">返回列表</el-button>
        <el-divider direction="vertical" />
        <span class="filename">{{ file.filename }}</span>
      </div>
      <div class="toolbar-center">
        <el-select v-model="currentSheetId" placeholder="选择 Sheet" @change="handleSheetChange">
          <el-option
            v-for="sheet in sheets"
            :key="sheet.id"
            :label="sheet.sheet_name"
            :value="sheet.id"
          />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-switch
          v-model="enablePagination"
          active-text="分页"
          inactive-text="全部"
          @change="handlePaginationChange"
        />
        <el-select
          v-if="enablePagination"
          v-model="pageSize"
          @change="handlePageSizeChange"
          style="width: 110px; margin-left: 10px;"
        >
          <el-option :value="50" label="50条/页" />
          <el-option :value="100" label="100条/页" />
          <el-option :value="200" label="200条/页" />
          <el-option :value="500" label="500条/页" />
        </el-select>
        <el-divider direction="vertical" />
        <el-button type="primary" :icon="Download" @click="handleDownload">下载</el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="table-wrapper" ref="tableWrapperRef">
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        stripe
        :height="tableHeight"
        :row-class-name="tableRowClassName"
        class="custom-table"
      >
        <el-table-column type="index" label="#" width="70" fixed="left" align="center" />
        <el-table-column
          v-for="(header, index) in headers"
          :key="index"
          :prop="String(index)"
          :label="header"
          min-width="150"
          show-overflow-tooltip
        >
          <template #header>
            <div class="column-header">
              <span class="column-title">{{ header }}</span>
              <span class="column-index">{{ getColumnLetter(index) }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 底部状态栏 -->
    <div class="statusbar">
      <div class="status-left">
        <el-tag type="info" effect="plain">
          {{ totalRows }} 行 × {{ headers.length }} 列
        </el-tag>
        <el-tag v-if="currentSheet" type="success" effect="plain" style="margin-left: 10px;">
          {{ currentSheet.sheet_name }}
        </el-tag>
      </div>
      <div class="status-right">
        <el-pagination
          v-if="enablePagination && totalRows > pageSize"
          background
          layout="total, prev, pager, next, jumper"
          :total="totalRows"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
        <span v-else-if="!enablePagination" class="all-data-hint">
          显示全部数据
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getFileDetail, getSheetData, downloadFile } from '../api/excel'

const props = defineProps({
  file: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back'])

const loading = ref(false)
const sheets = ref([])
const currentSheetId = ref(null)
const headers = ref([])
const tableData = ref([])
const totalRows = ref(0)
const currentPage = ref(1)
const pageSize = ref(100)
const enablePagination = ref(true)
const tableHeight = ref(500)
const tableWrapperRef = ref(null)

const currentSheet = computed(() => {
  return sheets.value.find(s => s.id === currentSheetId.value)
})

// 列索引转Excel列名 (A, B, C, ..., Z, AA, AB, ...)
const getColumnLetter = (index) => {
  let result = ''
  let n = index
  while (n >= 0) {
    result = String.fromCharCode((n % 26) + 65) + result
    n = Math.floor(n / 26) - 1
  }
  return result
}

// 行样式
const tableRowClassName = ({ rowIndex }) => {
  if (rowIndex % 2 === 0) {
    return 'even-row'
  }
  return 'odd-row'
}

// 动态计算表格高度
const updateTableHeight = () => {
  if (tableWrapperRef.value) {
    tableHeight.value = tableWrapperRef.value.clientHeight
  } else {
    // 回退方案：顶部header 52px + 工具栏 52px + 状态栏 42px + 边距
    tableHeight.value = window.innerHeight - 150
  }
}

onMounted(() => {
  // 延迟计算以确保 DOM 已渲染
  setTimeout(updateTableHeight, 100)
  window.addEventListener('resize', updateTableHeight)
  loadFileDetail()
})

onUnmounted(() => {
  window.removeEventListener('resize', updateTableHeight)
})

watch(() => props.file, () => {
  if (props.file) {
    loadFileDetail()
  }
})

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
    const sheetRowCount = currentSheet.value ? currentSheet.value.row_count : 10000
    const actualPageSize = enablePagination.value ? pageSize.value : sheetRowCount
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
    totalRows.value = response.data.total_rows - 1
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  emit('back')
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

const handleDownload = async () => {
  try {
    await downloadFile(props.file.id, props.file.filename)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}
</script>

<style scoped>
.data-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  background: #fff;
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
}

.filename {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  overflow: hidden;
  padding: 0;
  min-height: 0;
}

.custom-table {
  font-size: 13px;
  width: 100%;
  height: 100%;
}

.column-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.3;
}

.column-title {
  font-weight: 600;
  color: #303133;
}

.column-index {
  font-size: 11px;
  color: #909399;
  font-weight: normal;
}

/* 状态栏 */
.statusbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 20px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
}

.all-data-hint {
  color: #67c23a;
  font-size: 13px;
}

/* 表格行样式 */
:deep(.el-table) {
  --el-table-border-color: #e8e8e8;
}

:deep(.el-table th.el-table__cell) {
  background-color: #f0f2f5 !important;
  color: #303133;
  font-weight: 600;
  border-right: 1px solid #e0e0e0;
}

:deep(.el-table .even-row) {
  background-color: #ffffff;
}

:deep(.el-table .odd-row) {
  background-color: #fafbfc;
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: #ecf5ff !important;
}

:deep(.el-table td.el-table__cell) {
  border-right: 1px solid #ebeef5;
  padding: 8px 0;
}

:deep(.el-table .cell) {
  padding: 0 12px;
}

/* 行号列样式 */
:deep(.el-table__fixed-left .el-table__cell) {
  background-color: #f5f7fa !important;
}

:deep(.el-table__body .el-table__row .el-table__cell:first-child) {
  background-color: #f5f7fa;
  color: #909399;
  font-size: 12px;
}
</style>
