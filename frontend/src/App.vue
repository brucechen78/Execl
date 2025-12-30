<template>
  <div class="app-container">
    <header class="app-header">
      <h1>Excel 文件管理系统</h1>
    </header>

    <!-- 文件列表页 -->
    <main v-if="!selectedFile" class="app-main">
      <FileUpload @uploaded="handleUploaded" />
      <FileList ref="fileListRef" @select="handleFileSelect" />
    </main>

    <!-- 数据查看页 -->
    <DataTable
      v-else
      :file="selectedFile"
      @back="handleBack"
    />
  </div>
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

const handleBack = () => {
  selectedFile.value = null
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  background-color: #f5f7fa;
}

#app {
  height: 100%;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.app-header h1 {
  font-size: 22px;
  font-weight: 500;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
}
</style>
