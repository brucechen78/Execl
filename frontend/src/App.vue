<template>
  <div class="app-container">
    <!-- 未登录：显示登录/注册页面 -->
    <div v-if="!authStore.isAuthenticated" class="auth-wrapper">
      <Login
        v-if="currentView === 'login'"
        @switch-to-register="currentView = 'register'"
        @login-success="handleAuthSuccess"
      />
      <Register
        v-else
        @switch-to-login="currentView = 'login'"
        @register-success="handleAuthSuccess"
      />
    </div>

    <!-- 已登录：显示主应用 -->
    <template v-else>
      <header class="app-header">
        <h1>Excel 文件管理系统</h1>
        <div class="user-info">
          <span>{{ authStore.user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">
            退出登录
          </el-button>
        </div>
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
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from './stores/auth'
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import FileUpload from './components/FileUpload.vue'
import FileList from './components/FileList.vue'
import DataTable from './components/DataTable.vue'

const authStore = useAuthStore()
const fileListRef = ref(null)
const selectedFile = ref(null)
const currentView = ref('login')

const handleAuthSuccess = () => {
  // 登录/注册成功后刷新文件列表
  fileListRef.value?.loadFiles()
}

const handleUploaded = () => {
  fileListRef.value?.loadFiles()
}

const handleFileSelect = (file) => {
  selectedFile.value = file
}

const handleBack = () => {
  selectedFile.value = null
}

const handleLogout = async () => {
  await authStore.logoutAction()
  ElMessage.success('已退出登录')
  selectedFile.value = null
  currentView.value = 'login'
}

// 初始化：检查登录状态
onMounted(async () => {
  await authStore.initialize()
  if (authStore.isAuthenticated) {
    currentView.value = 'app'
  }
})
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

.auth-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.app-header h1 {
  font-size: 22px;
  font-weight: 500;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info span {
  font-size: 14px;
}

.app-main {
  flex: 1;
  padding: 20px;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
  overflow-y: auto;
}
</style>
