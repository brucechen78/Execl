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
/* 导入认证页面共享样式 */
@import '../styles/auth.css';
</style>
