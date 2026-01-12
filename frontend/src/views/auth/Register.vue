<template>
  <div class="register-container">
    <!-- 动态渐变背景 -->
    <div class="animated-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>

    <!-- 主注册卡片 -->
    <div class="register-card">
      <!-- 左侧品牌展示 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo-wrapper">
            <div class="logo-circle">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
          </div>
          <h1 class="brand-title">智绘视界</h1>
          <p class="brand-subtitle">AI智能视频创作平台</p>
          
          <div class="benefits">
            <div class="benefit-item">
              <div class="benefit-icon">✨</div>
              <div class="benefit-content">
                <h4>免费开始</h4>
                <p>注册即可体验AI创作</p>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">🚀</div>
              <div class="benefit-content">
                <h4>极速上手</h4>
                <p>3分钟完成首个作品</p>
              </div>
            </div>
            <div class="benefit-item">
              <div class="benefit-icon">💎</div>
              <div class="benefit-content">
                <h4>专业品质</h4>
                <p>商业级视频输出</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="form-section">
        <div class="form-content">
          <div class="form-header">
            <h2 class="form-title">创建账户</h2>
            <p class="form-subtitle">填写信息开始使用</p>
          </div>

          <form @submit.prevent="handleSubmit" class="register-form">
            <!-- 用户名 -->
            <div class="input-group">
              <label class="input-label">用户名</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <input
                  v-model="form.username"
                  type="text"
                  placeholder="请输入用户名"
                  class="modern-input"
                  :class="{ 'input-error': errors.username }"
                  required
                />
              </div>
              <span v-if="errors.username" class="error-text">{{ errors.username }}</span>
            </div>

            <!-- 邮箱 -->
            <div class="input-group">
              <label class="input-label">邮箱</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <input
                  v-model="form.email"
                  type="email"
                  placeholder="请输入邮箱"
                  class="modern-input"
                  :class="{ 'input-error': errors.email }"
                  required
                />
              </div>
              <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
            </div>

            <!-- 密码 -->
            <div class="input-group">
              <label class="input-label">密码</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </div>
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="至少6位密码"
                  class="modern-input"
                  :class="{ 'input-error': errors.password }"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
            </div>

            <!-- 确认密码 -->
            <div class="input-group">
              <label class="input-label">确认密码</label>
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                </div>
                <input
                  v-model="form.password_confirm"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  class="modern-input"
                  :class="{ 'input-error': errors.password_confirm }"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <svg v-if="!showConfirmPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                </button>
              </div>
              <span v-if="errors.password_confirm" class="error-text">{{ errors.password_confirm }}</span>
            </div>

            <!-- 错误提示 -->
            <div v-if="errorMessage" class="error-alert">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>{{ errorMessage }}</span>
            </div>

            <!-- 注册按钮 -->
            <button
              type="submit"
              class="submit-button"
              :disabled="loading"
            >
              <span v-if="!loading">注册</span>
              <span v-else class="loading-spinner">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
                </svg>
                注册中...
              </span>
            </button>
          </form>

          <!-- 登录链接 -->
          <div class="form-footer">
            <p>
              已有账户？
              <router-link to="/login" class="login-link">立即登录</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  data() {
    return {
      form: {
        username: '',
        email: '',
        password: '',
        password_confirm: ''
      },
      errors: {},
      errorMessage: '',
      loading: false,
      showPassword: false,
      showConfirmPassword: false
    }
  },
  methods: {
    ...mapActions('auth', ['register']),

    async handleSubmit() {
      this.errors = {}
      this.errorMessage = ''

      // 表单验证
      if (!this.form.username) {
        this.errors.username = '请输入用户名'
        return
      }
      if (!this.form.email) {
        this.errors.email = '请输入邮箱'
        return
      }
      if (!this.form.password) {
        this.errors.password = '请输入密码'
        return
      }
      if (this.form.password.length < 6) {
        this.errors.password = '密码至少6位'
        return
      }
      if (!this.form.password_confirm) {
        this.errors.password_confirm = '请确认密码'
        return
      }
      if (this.form.password !== this.form.password_confirm) {
        this.errors.password_confirm = '两次密码不一致'
        return
      }

      this.loading = true

      try {
        await this.register({
          username: this.form.username,
          email: this.form.email,
          password: this.form.password,
          password_confirm: this.form.password_confirm
        })

        // 注册成功，跳转到项目列表
        this.$router.push('/projects')
      } catch (error) {
        console.error('注册失败:', error)
        
        // 处理后端返回的详细错误
        if (error.response?.data?.errors) {
          const errors = error.response.data.errors
          
          // 将后端错误映射到表单字段
          if (errors.username) {
            this.errors.username = Array.isArray(errors.username) ? errors.username[0] : errors.username
          }
          if (errors.email) {
            this.errors.email = Array.isArray(errors.email) ? errors.email[0] : errors.email
          }
          if (errors.password) {
            this.errors.password = Array.isArray(errors.password) ? errors.password[0] : errors.password
          }
          if (errors.password_confirm) {
            this.errors.password_confirm = Array.isArray(errors.password_confirm) ? errors.password_confirm[0] : errors.password_confirm
          }
          
          // 显示通用错误消息
          this.errorMessage = error.response.data.message || '注册失败，请检查输入'
        } else {
          this.errorMessage = error.response?.data?.message || error.message || '注册失败，请重试'
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* 复用登录页面的样式 */
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.animated-background {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s infinite ease-in-out;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
  top: -10%;
  left: -10%;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
  bottom: -10%;
  right: -10%;
  animation-delay: 7s;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: linear-gradient(45deg, #43e97b 0%, #38f9d7 100%);
  top: 50%;
  left: 50%;
  animation-delay: 14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.register-card {
  position: relative;
  display: flex;
  width: 100%;
  max-width: 1000px;
  min-height: 650px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.brand-section::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
}

.logo-wrapper {
  margin-bottom: 30px;
}

.logo-circle {
  width: 100px;
  height: 100px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  animation: pulse 3s ease-in-out infinite;
}

.logo-circle svg {
  width: 50px;
  height: 50px;
  color: white;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
  }
}

.brand-title {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 10px;
  letter-spacing: -1px;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 40px;
}

.benefits {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 40px;
}

.benefit-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  transition: all 0.3s ease;
  text-align: left;
}

.benefit-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(10px);
}

.benefit-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.benefit-content h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 4px;
}

.benefit-content p {
  font-size: 14px;
  opacity: 0.9;
}

.form-section {
  flex: 1;
  padding: 50px 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
}

.form-content {
  width: 100%;
  max-width: 400px;
}

.form-header {
  margin-bottom: 30px;
}

.form-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
}

.form-subtitle {
  font-size: 15px;
  color: #718096;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  width: 20px;
  height: 20px;
  color: #a0aec0;
  pointer-events: none;
}

.modern-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #f7fafc;
  transition: all 0.3s ease;
  outline: none;
}

.modern-input:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.modern-input.input-error {
  border-color: #fc8181;
}

.password-toggle {
  position: absolute;
  right: 16px;
  width: 20px;
  height: 20px;
  color: #a0aec0;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #667eea;
}

.password-toggle svg {
  width: 100%;
  height: 100%;
}

.error-text {
  font-size: 13px;
  color: #fc8181;
  margin-top: 4px;
}

.error-alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff5f5;
  border: 1px solid #feb2b2;
  border-radius: 12px;
  color: #c53030;
  font-size: 14px;
}

.error-alert svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.submit-button {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.submit-button:active:not(:disabled) {
  transform: translateY(0);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner svg {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.form-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #718096;
}

.login-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s;
}

.login-link:hover {
  color: #764ba2;
}

@media (max-width: 768px) {
  .register-card {
    flex-direction: column;
    max-width: 500px;
  }

  .brand-section {
    padding: 40px 30px;
  }

  .brand-title {
    font-size: 32px;
  }

  .benefits {
    display: none;
  }

  .form-section {
    padding: 40px 30px;
  }
}
</style>
