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
        <!-- 多表格区域选择器 -->
        <el-select
          v-if="tableRegions.length > 0"
          v-model="currentRegionIndex"
          placeholder="选择表格区域"
          @change="handleRegionChange"
          style="margin-left: 10px; width: 180px;"
        >
          <el-option
            :value="-1"
            label="全部数据"
          />
          <el-option
            v-for="region in tableRegions"
            :key="region.region_index"
            :label="region.table_name || `表格 ${region.region_index + 1}`"
            :value="region.region_index"
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

    <!-- 图片和图表展示区域 -->
    <div v-if="images.length > 0 || charts.length > 0" class="media-section">
      <el-collapse v-model="activeMedia">
        <el-collapse-item v-if="images.length > 0" title="内嵌图片" name="images">
          <div class="media-grid">
            <div
              v-for="img in images"
              :key="img.id"
              class="media-item"
              @click="showImagePreview(img)"
            >
              <el-image
                :src="getImageUrl(img.id)"
                fit="contain"
                class="thumbnail"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="media-info">位置: {{ getColumnLetter(img.anchor_col) }}{{ img.anchor_row + 1 }}</div>
            </div>
          </div>
        </el-collapse-item>
        <el-collapse-item v-if="charts.length > 0" title="内嵌图表" name="charts">
          <div class="charts-list">
            <el-tag
              v-for="chart in charts"
              :key="chart.id"
              type="info"
              class="chart-tag"
            >
              <el-icon><DataLine /></el-icon>
              {{ chart.chart_title || getChartTypeName(chart.chart_type) }}
              ({{ getColumnLetter(chart.anchor_col) }}{{ chart.anchor_row + 1 }})
            </el-tag>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 数据表格 -->
    <div class="table-wrapper" ref="tableWrapperRef" v-loading="loading">
      <div class="table-container" :style="{ maxHeight: tableHeight + 'px' }">
        <table class="excel-table">
          <thead>
            <tr>
              <th class="row-index-header">#</th>
              <th
                v-for="(header, index) in displayHeaders"
                :key="index"
                class="column-header"
              >
                <div class="header-content">
                  <span class="header-title">{{ header }}</span>
                  <span class="header-index">{{ getColumnLetter(index) }}</span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, rowIdx) in displayData" :key="rowIdx" :class="rowIdx % 2 === 0 ? 'even-row' : 'odd-row'">
              <td class="row-index-cell">{{ getActualRowNumber(rowIdx) }}</td>
              <template v-for="(cell, colIdx) in row" :key="colIdx">
                <td
                  v-if="!isCellHidden(rowIdx, colIdx)"
                  :colspan="getCellColspan(rowIdx, colIdx)"
                  :rowspan="getCellRowspan(rowIdx, colIdx)"
                  :class="{ 'merged-cell': isMergedCell(rowIdx, colIdx) }"
                >
                  {{ cell }}
                </td>
              </template>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 底部状态栏 -->
    <div class="statusbar">
      <div class="status-left">
        <el-tag type="info" effect="plain">
          {{ totalRows }} 行 × {{ displayHeaders.length }} 列
        </el-tag>
        <el-tag v-if="currentSheet" type="success" effect="plain" style="margin-left: 10px;">
          {{ currentSheet.sheet_name }}
        </el-tag>
        <el-tag v-if="mergedCells.length > 0" type="warning" effect="plain" style="margin-left: 10px;">
          {{ mergedCells.length }} 个合并单元格
        </el-tag>
        <el-tag v-if="tableRegions.length > 0" type="primary" effect="plain" style="margin-left: 10px;">
          {{ tableRegions.length }} 个表格区域
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

    <!-- 图片预览对话框 -->
    <el-dialog v-model="imagePreviewVisible" title="图片预览" width="80%">
      <div class="image-preview-container">
        <img :src="previewImageUrl" class="preview-image" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from 'vue'
import { ArrowLeft, Download, Picture, DataLine } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getFileDetail, getSheetData, downloadFile, getImageUrl } from '../api/excel'

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

// 新增状态
const mergedCells = ref([])
const images = ref([])
const charts = ref([])
const tableRegions = ref([])
const currentRegionIndex = ref(-1)  // -1 表示显示全部
const activeMedia = ref([])
const imagePreviewVisible = ref(false)
const previewImageUrl = ref('')

const currentSheet = computed(() => {
  return sheets.value.find(s => s.id === currentSheetId.value)
})

// 根据当前选择的表格区域计算显示的数据
const displayData = computed(() => {
  if (currentRegionIndex.value === -1 || tableRegions.value.length === 0) {
    return tableData.value
  }
  const region = tableRegions.value.find(r => r.region_index === currentRegionIndex.value)
  if (!region) return tableData.value

  // 过滤出当前区域的数据
  const startRow = region.start_row
  const endRow = region.end_row
  return tableData.value.filter((_, idx) => {
    const actualRow = (currentPage.value - 1) * pageSize.value + idx
    return actualRow >= startRow && actualRow <= endRow
  })
})

const displayHeaders = computed(() => {
  return headers.value
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

// 获取实际行号
const getActualRowNumber = (rowIdx) => {
  if (currentRegionIndex.value === -1 || tableRegions.value.length === 0) {
    return (currentPage.value - 1) * pageSize.value + rowIdx + 1
  }
  const region = tableRegions.value.find(r => r.region_index === currentRegionIndex.value)
  if (!region) return rowIdx + 1
  return region.start_row + rowIdx + 1
}

// 检查单元格是否是合并单元格的起始位置
const isMergedCell = (rowIdx, colIdx) => {
  const actualRow = (currentPage.value - 1) * pageSize.value + rowIdx
  return mergedCells.value.some(mc =>
    mc.start_row === actualRow && mc.start_col === colIdx
  )
}

// 检查单元格是否应该被隐藏（被合并到其他单元格）
const isCellHidden = (rowIdx, colIdx) => {
  const actualRow = (currentPage.value - 1) * pageSize.value + rowIdx
  return mergedCells.value.some(mc =>
    actualRow >= mc.start_row && actualRow <= mc.end_row &&
    colIdx >= mc.start_col && colIdx <= mc.end_col &&
    !(actualRow === mc.start_row && colIdx === mc.start_col)
  )
}

// 获取单元格的colspan
const getCellColspan = (rowIdx, colIdx) => {
  const actualRow = (currentPage.value - 1) * pageSize.value + rowIdx
  const merged = mergedCells.value.find(mc =>
    mc.start_row === actualRow && mc.start_col === colIdx
  )
  return merged ? merged.end_col - merged.start_col + 1 : 1
}

// 获取单元格的rowspan
const getCellRowspan = (rowIdx, colIdx) => {
  const actualRow = (currentPage.value - 1) * pageSize.value + rowIdx
  const merged = mergedCells.value.find(mc =>
    mc.start_row === actualRow && mc.start_col === colIdx
  )
  return merged ? merged.end_row - merged.start_row + 1 : 1
}

// 图表类型名称映射
const getChartTypeName = (type) => {
  const typeMap = {
    'bar': '柱状图',
    'bar3d': '3D柱状图',
    'line': '折线图',
    'line3d': '3D折线图',
    'pie': '饼图',
    'pie3d': '3D饼图',
    'area': '面积图',
    'scatter': '散点图',
    'radar': '雷达图',
    'doughnut': '环形图',
    'bubble': '气泡图',
    'unknown': '图表'
  }
  return typeMap[type] || '图表'
}

// 显示图片预览
const showImagePreview = (img) => {
  previewImageUrl.value = getImageUrl(img.id)
  imagePreviewVisible.value = true
}

// 动态计算表格高度
const updateTableHeight = () => {
  if (tableWrapperRef.value) {
    tableHeight.value = tableWrapperRef.value.clientHeight
  } else {
    tableHeight.value = window.innerHeight - 200
  }
}

onMounted(() => {
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
    tableData.value = response.data.data
    totalRows.value = response.data.total_rows - 1

    // 加载新增的数据
    mergedCells.value = response.data.merged_cells || []
    images.value = response.data.images || []
    charts.value = response.data.charts || []
    tableRegions.value = response.data.table_regions || []

    // 如果有多个表格区域，默认显示全部
    if (tableRegions.value.length > 0) {
      currentRegionIndex.value = -1
    }
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
  currentRegionIndex.value = -1
  loadSheetData()
}

const handleRegionChange = () => {
  // 表格区域切换不需要重新加载数据，只需要过滤显示
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
/* 导入全局样式 */
@import '../styles/theme.css';

.data-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  background: var(--bg-primary);
}

/* 工具栏 */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 25px;
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-primary);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
}

.filename {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 媒体展示区域 */
.media-section {
  padding: 20px 25px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-primary);
  flex-shrink: 0;
}

.media-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.media-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.media-item:hover {
  transform: scale(1.05);
}

.thumbnail {
  width: 120px;
  height: 90px;
  border: 2px solid var(--border-primary);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
}

.thumbnail:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
  border-color: var(--primary-color);
}

.image-error {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background: var(--bg-primary);
  color: var(--text-muted);
  border-radius: var(--radius-md);
}

.media-info {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
  margin-top: 6px;
  font-weight: 500;
}

.charts-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-tag {
  cursor: default;
  border-radius: var(--radius-md);
  font-weight: 500;
  padding: 6px 12px;
  transition: all var(--transition-normal);
}

.chart-tag:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  overflow: hidden;
  padding: 0;
  min-height: 0;
  background: var(--bg-secondary);
  position: relative;
}

.table-container {
  overflow: auto;
  width: 100%;
  height: 100%;
}

.excel-table {
  border-collapse: separate;
  border-spacing: 0;
  font-size: 14px;
  width: max-content;
  min-width: 100%;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', Arial, sans-serif;
}

.excel-table th,
.excel-table td {
  border: 1px solid var(--border-primary);
  padding: 10px 14px;
  text-align: left;
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.excel-table th {
  background: var(--primary-gradient) !important;
  color: white !important;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
  box-shadow: var(--shadow-md);
  text-transform: none;
  letter-spacing: 0.5px;
}

.row-index-header,
.row-index-cell {
  background: var(--accent-gradient) !important;
  color: white !important;
  font-size: 13px;
  font-weight: 600;
  text-align: center;
  width: 60px;
  min-width: 60px;
  position: sticky;
  left: 0;
  z-index: 5;
  box-shadow: var(--shadow-md);
}

.row-index-header {
  z-index: 15;
}

.column-header {
  min-width: 120px;
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  line-height: 1.3;
  padding: 4px 0;
}

.header-title {
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.header-index {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: normal;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  margin-top: 2px;
}

.even-row td {
  background-color: var(--bg-secondary);
}

.odd-row td {
  background-color: var(--bg-primary);
}

.excel-table tr:hover td {
  background-color: rgba(102, 126, 234, 0.1) !important;
  transform: scale(1.01);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15) inset;
}

.merged-cell {
  background: linear-gradient(135deg, rgba(240, 147, 251, 0.1) 0%, rgba(245, 87, 108, 0.1) 100%) !important;
  font-weight: 600;
  color: var(--accent-color);
  position: relative;
}

.merged-cell::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 50%, transparent 100%);
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.excel-table tr:hover .merged-cell::before {
  opacity: 1;
}

/* 状态栏 */
.statusbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 25px;
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  border-top: 1px solid var(--border-primary);
  flex-shrink: 0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.status-left,
.status-right {
  display: flex;
  align-items: center;
}

.all-data-hint {
  color: var(--success-color);
  font-size: 14px;
  font-weight: 500;
  animation: pulse 2s ease-in-out infinite;
}

/* 图片预览 */
.image-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  max-height: 70vh;
  overflow: auto;
  padding: 20px;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-xl);
  transition: all var(--transition-normal);
}

.preview-image:hover {
  transform: scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}
</style>
