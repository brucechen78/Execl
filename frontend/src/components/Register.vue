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
            <span class="logo-gradient">加入</span>
            <span class="logo-highlight">我们</span>
          </h1>
          <p class="logo-subtitle">开启你的 Excel 管理之旅</p>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <el-card class="auth-card shadow-gradient">
        <template #header>
          <div class="card-header">
            <h2 class="welcome-text">创建新账号</h2>
            <p class="welcome-subtitle">填写信息，开始你的高效之旅</p>
          </div>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          hide-required-asterisk
          @submit.prevent="handleRegister"
        >
          <el-form-item prop="username">
            <div class="input-group">
              <el-icon class="input-icon"><User /></el-icon>
              <el-input
                v-model="form.username"
                placeholder="设置用户名"
                clearable
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="email">
            <div class="input-group">
              <el-icon class="input-icon"><Message /></el-icon>
              <el-input
                v-model="form.email"
                type="email"
                placeholder="输入邮箱地址"
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
                placeholder="设置密码（至少6位）"
                show-password
                class="custom-input"
              />
            </div>
          </el-form-item>

          <el-form-item prop="confirmPassword">
            <div class="input-group">
              <el-icon class="input-icon"><Check /></el-icon>
              <el-input
                v-model="form.confirmPassword"
                type="password"
                placeholder="再次输入密码"
                show-password
                class="custom-input"
                @keyup.enter="handleRegister"
              />
            </div>
          </el-form-item>

          <div class="form-actions">
            <el-button
              type="primary"
              class="register-btn v-btn-accent"
              :loading="authStore.loading"
              @click="handleRegister"
            >
              <span v-if="!authStore.loading">立即注册</span>
              <span v-else>注册中...</span>
            </el-button>
          </div>

          <div class="form-footer">
            <div class="footer-links">
              <span>已有账号？</span>
              <el-button class="login-link" @click="$emit('switch-to-login')">
                立即登录
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
import { User, Lock, Message, Check } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['switch-to-login', 'register-success'])

const authStore = useAuthStore()
const formRef = ref(null)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    const result = await authStore.registerAction(
      form.username,
      form.email,
      form.password
    )

    if (result.success) {
      ElMessage.success('注册成功')
      emit('register-success')
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
