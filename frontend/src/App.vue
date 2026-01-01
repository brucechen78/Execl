<template>
  <div class="app-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration bg-decoration-1"></div>
    <div class="bg-decoration bg-decoration-2"></div>

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
      <!-- 顶部导航栏 -->
      <header class="app-header">
        <div class="header-left">
          <div class="logo-section">
            <el-icon class="logo-icon"><Document /></el-icon>
            <h1 class="app-title text-gradient">Excel 管理专家</h1>
          </div>
          <nav class="nav-menu">
            <el-button
              :icon="House"
              class="nav-btn"
              @click="handleBack"
              v-if="selectedFile"
            >
              文件列表
            </el-button>
            <el-button
              :icon="Upload"
              class="nav-btn"
              @click="handleBack"
              v-if="!selectedFile"
            >
              上传文件
            </el-button>
          </nav>
        </div>

        <div class="header-right">
          <div class="user-section">
            <el-avatar :size="36" :icon="UserFilled" class="user-avatar" />
            <div class="user-details">
              <div class="user-name">{{ authStore.user?.username }}</div>
              <div class="user-role">高级用户</div>
            </div>
            <el-button
              :icon="SwitchButton"
              type="primary"
              class="logout-btn"
              @click="handleLogout"
            >
              退出
            </el-button>
          </div>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main v-if="!selectedFile" class="app-main">
        <!-- 上传区域 -->
        <div class="upload-section">
          <FileUpload @uploaded="handleUploaded" />
        </div>

        <!-- 文件列表区域 -->
        <div class="files-section">
          <FileList ref="fileListRef" @select="handleFileSelect" />
        </div>
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
import {
  Document,
  House,
  Upload,
  UserFilled,
  SwitchButton
} from '@element-plus/icons-vue'
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
/* 导入全局样式 */
@import './styles/theme.css';

/* 基础样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
}

body {
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', Arial, sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

#app {
  height: 100%;
}

.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  pointer-events: none;
  z-index: 0;
}

.bg-decoration-1 {
  top: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, var(--primary-color) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
}

.bg-decoration-2 {
  bottom: -150px;
  left: -150px;
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, var(--accent-color) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0.1;
  animation: float 25s ease-in-out infinite reverse;
}

/* 认证容器 */
.auth-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 头部导航 */
.app-header {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-md);
  padding: 0 30px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--border-primary);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  color: var(--primary-color);
}

.app-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.nav-menu {
  display: flex;
  gap: 10px;
}

.nav-btn {
  border-radius: var(--radius-md);
  font-weight: 500;
  transition: all var(--transition-normal);
}

.nav-btn:hover {
  transform: translateY(-2px);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  background: var(--primary-gradient);
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.user-role {
  font-size: 12px;
  color: var(--text-muted);
}

.logout-btn {
  border-radius: 20px;
  font-weight: 600;
  padding: 8px 20px;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.upload-section {
  margin-bottom: 30px;
}

.files-section {
  animation: slideIn 0.5s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 15px;
  }

  .header-left {
    gap: 15px;
  }

  .app-title {
    font-size: 18px;
  }

  .user-section {
    gap: 10px;
  }

  .user-details {
    display: none;
  }

  .app-main {
    padding: 15px;
  }
}
</style>
