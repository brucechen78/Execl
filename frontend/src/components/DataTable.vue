<template>
  <el-card v-if="file" class="data-table-card">
    <template #header>
      <div class="card-header">
        <span>{{ file.filename }}</span>
        <el-select v-model="currentSheetId" placeholder="选择 Sheet" @change="loadSheetData">
          <el-option
            v-for="sheet in sheets"
            :key="sheet.id"
            :label="sheet.sheet_name"
            :value="sheet.id"
          />
        </el-select>
      </div>
    </template>

    <el-table
      v-loading="loading"
      :data="tableData"
      style="width: 100%"
      border
      max-height="500"
    >
      <el-table-column
        v-for="(header, index) in headers"
        :key="index"
        :prop="String(index)"
        :label="header"
        min-width="120"
        show-overflow-tooltip
      />
    </el-table>

    <el-pagination
      v-if="totalRows > pageSize"
      class="pagination"
      background
      layout="total, prev, pager, next, jumper"
      :total="totalRows"
      :page-size="pageSize"
      :current-page="currentPage"
      @current-change="handlePageChange"
    />
  </el-card>

  <el-empty v-else description="请选择一个文件查看内容" />
</template>

<script setup>
import { ref, watch } from 'vue'
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
    const response = await getSheetData(
      props.file.id,
      currentSheetId.value,
      currentPage.value,
      pageSize.value
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

const handlePageChange = (page) => {
  currentPage.value = page
  loadSheetData()
}
</script>

<style scoped>
.data-table-card {
  height: 100%;
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
</style>
