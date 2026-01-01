<template>
  <div class="auth-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration bg-decoration-1"></div>
    <div class="bg-decoration bg-decoration-2"></div>
    <div class="bg-decoration bg-decoration-3"></div>

    <!-- 主卡片容器 -->
    <div class="auth-wrapper">
      <!-- 左侧装饰 -->
      <div class="auth-decoration">
        <div class="decoration-shape shape-1"></div>
        <div class="decoration-shape shape-2"></div>
        <div class="logo-area">
          <h1 class="logo-text">
            <span class="logo-gradient">Excel</span>
            <span class="logo-highlight">管家</span>
          </h1>
          <p class="logo-subtitle">你的智能 Excel 管理助手</p>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <el-card class="auth-card shadow-gradient">
        <template #header>
          <div class="card-header">
            <h2 class="welcome-text">欢迎回来！</h2>
            <p class="welcome-subtitle">登录你的账户，继续你的工作</p>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          hide-required-asterisk
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <div class="input-group">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="form.username"
                placeholder="用户名"
                clearable
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="password">
            <div class="input-group">
              <el-icon class="input-icon"><Lock /></el-icon>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="密码"
                show-password
                class="custom-input"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>

          <div class="form-actions">
            <el-button
              type="primary"
              class="login-btn v-btn-primary"
              :loading="authStore.loading"
              @click="handleLogin"
            >
              <span v-if="!authStore.loading">立即登录</span>
              <span v-else>登录中...</span>
            </el-button>
          </div>

          <div class="form-footer">
            <div class="footer-links">
              <span>还没有账号？</span>
              <el-button class="register-link" @click="$emit('switch-to-register')">
                立即注册
              </el-button>
            </div>
          </div>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['switch-to-register', 'login-success'])

const authStore = useAuthStore()
const formRef = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    const result = await authStore.loginAction(form.username, form.password)

    if (result.success) {
      ElMessage.success('登录成功')
      emit('login-success')
    } else {
      ElMessage.error(result.error)
    }
  })
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.auth-wrapper {
  display: flex;
  width: 900px;
  height: 500px;
  border-radius: 30px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.95);
}

.auth-decoration {
  flex: 1;
  background: linear-gradient(135deg, var(--primary-gradient) 0%, var(--accent-gradient) 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  padding: 40px;
  color: white;
}

.decoration-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.shape-1 {
  width: 150px;
  height: 150px;
  top: 50px;
  right: -50px;
  animation: float 15s ease-in-out infinite;
}

.shape-2 {
  width: 100px;
  height: 100px;
  bottom: 80px;
  left: -30px;
  animation: float 20s ease-in-out infinite reverse;
}

.logo-area {
  text-align: center;
  z-index: 10;
}

.logo-text {
  font-size: 3rem;
  font-weight: 800;
  margin: 0;
  line-height: 1.2;
}

.logo-gradient {
  background: var(--text-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-highlight {
  color: white;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
}

.logo-subtitle {
  font-size: 1.1rem;
  margin-top: 10px;
  opacity: 0.9;
  font-weight: 300;
}

.auth-card {
  flex: 1;
  margin: 40px;
  border: none;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.welcome-text {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-subtitle {
  font-size: 1rem;
  color: var(--text-secondary);
  margin: 10px 0 0 0;
  font-weight: 400;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 18px;
  z-index: 10;
}

.custom-input {
  padding-left: 45px !important;
}

.form-actions {
  margin: 30px 0 20px 0;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 25px;
  transition: all 0.3s ease;
}

.login-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(103, 126, 234, 0.3);
}

.form-footer {
  text-align: center;
  margin-top: 20px;
}

.footer-links {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.register-link {
  color: var(--primary-color);
  font-weight: 600;
  padding: 0;
  margin-left: 5px;
  transition: all 0.2s ease;
}

.register-link:hover {
  color: var(--primary-dark);
  transform: scale(1.05);
}

/* 导入全局样式 */
@import '../styles/theme.css';

/* 动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}
</style>
