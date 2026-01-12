<template>
  <div class="modern-project-create">
    <!-- 渐变头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">创建新项目</h1>
          <p class="page-subtitle">开启您的AI视频创作之旅</p>
        </div>
        <button class="back-button" @click="handleCancel">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          <span>返回列表</span>
        </button>
      </div>
    </div>

    <!-- 表单区域 -->
    <div class="form-container">
      <form @submit.prevent="handleSubmit" class="create-form">
        <!-- 项目名称 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          
          <div class="input-group">
            <label class="input-label">
              项目名称 <span class="required">*</span>
            </label>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"/>
                </svg>
              </div>
              <input
                v-model="form.name"
                type="text"
                placeholder="请输入项目名称，例如：科技未来短视频"
                class="modern-input"
                :class="{ 'input-error': errors.name }"
                required
              />
            </div>
            <span v-if="errors.name" class="error-text">{{ errors.name }}</span>
          </div>

          <div class="input-group">
            <label class="input-label">
              项目描述 <span class="optional">(可选)</span>
            </label>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </div>
              <textarea
                v-model="form.description"
                placeholder="简要描述您的项目内容和目标..."
                class="modern-textarea"
                rows="3"
              ></textarea>
            </div>
          </div>
        </div>

        <!-- 内容输入 -->
        <div class="form-section">
          <h3 class="section-title">创作内容</h3>
          
          <div class="input-group">
            <label class="input-label">
              原始主题/文案 <span class="required">*</span>
            </label>
            <div class="char-count">{{ form.original_topic.length }} 字符</div>
            <div class="input-wrapper">
              <textarea
                v-model="form.original_topic"
                placeholder="请输入您的创作主题或文案内容...

示例：
讲述一个关于人工智能觉醒的故事，主角是一个在未来世界中工作的程序员，他发现自己创造的AI开始拥有了自我意识..."
                class="modern-textarea large"
                :class="{ 'input-error': errors.original_topic }"
                rows="8"
                required
              ></textarea>
            </div>
            <span v-if="errors.original_topic" class="error-text">{{ errors.original_topic }}</span>
          </div>
        </div>

        <!-- 高级设置 -->
        <div class="form-section">
          <h3 class="section-title">高级设置</h3>
          
          <div class="input-group">
            <label class="input-label">
              提示词集 <span class="optional">(可选)</span>
            </label>
            <div class="input-wrapper">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
              </div>
              <select
                v-model="form.prompt_template_set"
                class="modern-select"
                :disabled="loadingTemplates"
              >
                <option :value="null">
                  {{ loadingTemplates ? '加载中...' : '使用默认提示词集' }}
                </option>
                <option v-for="set in templateSets" :key="set.id" :value="set.id">
                  {{ set.name }}
                  {{ set.is_default ? ' (默认)' : '' }}
                  {{ set.templates_count ? ` - ${set.templates_count}个模板` : '' }}
                </option>
              </select>
            </div>
            <div v-if="selectedTemplateSetInfo" class="input-hint">
              {{ selectedTemplateSetInfo }}
            </div>
          </div>
        </div>

        <!-- 提示卡片 -->
        <div class="info-card">
          <div class="info-icon">💡</div>
          <div class="info-content">
            <h4>创建后会发生什么？</h4>
            <ul>
              <li>系统将自动初始化5个工作流阶段</li>
              <li>项目状态为"草稿"，可以随时编辑</li>
              <li>您可以在项目详情页配置AI模型并开始生成</li>
            </ul>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button
            type="button"
            class="cancel-button"
            @click="handleCancel"
            :disabled="submitting"
          >
            取消
          </button>
          <button
            type="submit"
            class="submit-button"
            :disabled="submitting"
          >
            <span v-if="!submitting">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              创建项目
            </span>
            <span v-else class="loading-spinner">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
              </svg>
              创建中...
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';
import { promptSetAPI } from '@/api/prompts';

export default {
  name: 'ProjectCreate',
  data() {
    return {
      form: {
        name: '',
        description: '',
        original_topic: '',
        prompt_template_set: null,
      },
      errors: {
        name: '',
        original_topic: '',
      },
      templateSets: [],
      loadingTemplates: false,
      submitting: false,
    };
  },
  computed: {
    selectedTemplateSetInfo() {
      if (!this.form.prompt_template_set) {
        return '';
      }
      const selected = this.templateSets.find(
        (set) => set.id === this.form.prompt_template_set
      );
      return selected?.description || '';
    },
  },
  created() {
    this.fetchTemplateSets();
  },
  methods: {
    ...mapActions('projects', ['createProject']),

    async fetchTemplateSets() {
      this.loadingTemplates = true;
      try {
        const response = await promptSetAPI.getList({
          is_active: true,
          page_size: 100
        });
        this.templateSets = response.results || response || [];
      } catch (error) {
        console.error('获取提示词集失败:', error);
        this.templateSets = [];
      } finally {
        this.loadingTemplates = false;
      }
    },

    validateForm() {
      let isValid = true;
      this.errors = {
        name: '',
        original_topic: '',
      };

      if (!this.form.name || !this.form.name.trim()) {
        this.errors.name = '请输入项目名称';
        isValid = false;
      } else if (this.form.name.length > 255) {
        this.errors.name = '项目名称不能超过255个字符';
        isValid = false;
      }

      if (!this.form.original_topic || !this.form.original_topic.trim()) {
        this.errors.original_topic = '请输入原始主题或文案';
        isValid = false;
      } else if (this.form.original_topic.length < 10) {
        this.errors.original_topic = '内容至少需要10个字符';
        isValid = false;
      }

      return isValid;
    },

    async handleSubmit() {
      if (!this.validateForm()) {
        return;
      }

      this.submitting = true;
      try {
        const projectData = {
          name: this.form.name.trim(),
          description: this.form.description.trim(),
          original_topic: this.form.original_topic.trim(),
          prompt_template_set: this.form.prompt_template_set,
        };

        const project = await this.createProject(projectData);

        setTimeout(() => {
          this.$router.push({
            name: 'ProjectDetail',
            params: { id: project.id },
          });
        }, 500);
      } catch (error) {
        console.error('创建项目失败:', error);
        const errorMsg = error.response?.data?.message || error.message || '创建项目失败';
        alert('✗ ' + errorMsg);
      } finally {
        this.submitting = false;
      }
    },

    handleCancel() {
      const hasContent =
        this.form.name || this.form.description || this.form.original_topic;

      if (hasContent) {
        if (confirm('确定要取消吗？已填写的内容将丢失。')) {
          this.$router.push({ name: 'ProjectList' });
        }
      } else {
        this.$router.push({ name: 'ProjectList' });
      }
    },
  },
};
</script>

<style scoped>
.modern-project-create {
  max-width: 900px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-left {
  color: white;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-4px);
}

.back-button svg {
  width: 20px;
  height: 20px;
}

/* 表单容器 */
.form-container {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 表单区块 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

/* 输入组 */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.input-label {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 4px;
}

.required {
  color: #fc8181;
}

.optional {
  font-size: 12px;
  font-weight: 400;
  color: #a0aec0;
}

.char-count {
  position: absolute;
  top: 0;
  right: 0;
  font-size: 12px;
  color: #a0aec0;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-start;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 14px;
  width: 20px;
  height: 20px;
  color: #a0aec0;
  pointer-events: none;
  z-index: 1;
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

.modern-textarea {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #f7fafc;
  transition: all 0.3s ease;
  outline: none;
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
}

.modern-textarea.large {
  padding: 14px 16px;
}

.modern-textarea:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.modern-textarea.input-error {
  border-color: #fc8181;
}

.modern-select {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: #f7fafc;
  transition: all 0.3s ease;
  outline: none;
  cursor: pointer;
}

.modern-select:focus {
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.modern-select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  font-size: 13px;
  color: #fc8181;
  margin-top: 4px;
}

.input-hint {
  font-size: 13px;
  color: #718096;
  margin-top: 4px;
  line-height: 1.5;
}

/* 提示卡片 */
.info-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  border-radius: 16px;
  border: 2px solid #c7d2fe;
}

.info-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.info-content h4 {
  font-size: 16px;
  font-weight: 600;
  color: #4c51bf;
  margin-bottom: 8px;
}

.info-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-content li {
  font-size: 14px;
  color: #5a67d8;
  padding-left: 20px;
  position: relative;
}

.info-content li::before {
  content: '✓';
  position: absolute;
  left: 0;
  font-weight: bold;
}

/* 表单操作 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 20px;
  border-top: 2px solid #e2e8f0;
}

.cancel-button {
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  color: #4a5568;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-button:hover:not(:disabled) {
  border-color: #cbd5e0;
  background: #f7fafc;
}

.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  font-size: 15px;
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

.submit-button svg {
  width: 20px;
  height: 20px;
}

.loading-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner svg {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    padding: 30px 20px;
  }

  .header-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .page-title {
    font-size: 28px;
  }

  .form-container {
    padding: 24px;
  }

  .form-actions {
    flex-direction: column;
  }

  .cancel-button,
  .submit-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
