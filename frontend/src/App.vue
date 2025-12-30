<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>Excel 文件管理系统</h1>
    </el-header>
    <el-main class="app-main">
      <el-row :gutter="20">
        <el-col :span="10">
          <FileUpload @uploaded="handleUploaded" />
          <FileList ref="fileListRef" @select="handleFileSelect" />
        </el-col>
        <el-col :span="14">
          <DataTable :file="selectedFile" />
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import FileList from './components/FileList.vue'
import DataTable from './components/DataTable.vue'

const fileListRef = ref(null)
const selectedFile = ref(null)

const handleUploaded = () => {
  fileListRef.value?.loadFiles()
}

const handleFileSelect = (file) => {
  selectedFile.value = file
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 24px;
  font-weight: 500;
}

.app-main {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}
</style>
