<template>
  <div class="story-content">
    <h3 class="step-title">编写故事内容</h3>
    <p class="step-description">填写故事的标题和内容，让AI帮你创作精彩的视频</p>

    <div class="form-group">
      <label class="form-label">
        故事标题 <span class="required">*</span>
      </label>
      <input
        v-model="formData.title"
        type="text"
        class="form-input"
        placeholder="例如：小兔子的冒险之旅"
        maxlength="50"
        @input="handleUpdate"
      />
      <div class="input-hint">
        {{ formData.title.length }}/50
      </div>
      <div v-if="errors.title" class="error-message">
        {{ errors.title }}
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">
        故事内容 <span class="required">*</span>
        <span class="label-hint">建议精简到500字以内</span>
      </label>
      <textarea
        v-model="formData.content"
        class="form-textarea"
        :class="{ 'error-border': contentTooLong }"
        placeholder="在这里编写你的故事内容..."
        rows="10"
        @input="handleUpdate"
      ></textarea>
      <div class="input-hint" :class="{ 'text-warning': contentTooLong }">
        {{ formData.content.length }}/500
        <span v-if="contentTooLong" class="warning-text">
          ⚠️ 内容过长，建议精简
        </span>
      </div>
      <div v-if="errors.content" class="error-message">
        {{ errors.content }}
      </div>
    </div>

    <!-- AI辅助功能 -->
    <div class="ai-assist">
      <h4 class="assist-title">✨ AI 辅助创作</h4>
      <div class="assist-actions">
        <button
          class="btn-assist"
          :disabled="isGenerating"
          @click="generateOutline"
        >
          <span v-if="!isGenerating">生成大纲</span>
          <span v-else>
            <span class="loading-spinner"></span>
            生成中...
          </span>
        </button>
        <button
          class="btn-assist"
          :disabled="isGenerating || !formData.content"
          @click="improveContent"
        >
          优化内容
        </button>
        <button
          class="btn-assist"
          :disabled="isGenerating || !formData.content"
          @click="expandContent"
        >
          扩展内容
        </button>
      </div>
    </div>

    <!-- 大纲编辑 -->
    <div v-if="formData.outline && formData.outline.length > 0" class="outline-section">
      <h4 class="outline-title">故事大纲</h4>
      <div class="outline-list">
        <div
          v-for="(item, index) in formData.outline"
          :key="index"
          class="outline-item"
        >
          <div class="outline-number">{{ index + 1 }}</div>
          <input
            v-model="item.text"
            type="text"
            class="outline-input"
            placeholder="场景描述"
            @input="handleUpdate"
          />
          <button class="btn-remove" @click="removeOutlineItem(index)">×</button>
        </div>
      </div>
      <button class="btn-add-outline" @click="addOutlineItem">
        + 添加场景
      </button>
    </div>
  </div>
</template>

<script>
import requestLock from '@/utils/requestLock';
import notificationService from '@/services/notificationService';

export default {
  name: 'StoryContent',
  props: {
    data: {
      type: Object,
      required: true
    },
    errors: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      formData: {
        title: '',
        content: '',
        outline: []
      },
      isGenerating: false
    };
  },
  computed: {
    contentTooLong() {
      return this.formData.content.length > 500;
    }
  },
  mounted() {
    if (this.data.story) {
      this.formData = { ...this.formData, ...this.data.story };
    }
  },
  methods: {
    handleUpdate() {
      this.$emit('update', { story: this.formData });
    },

    async generateOutline() {
      try {
        await requestLock.withLock('generate_outline', async () => {
          this.isGenerating = true;

          const response = await this.$store.dispatch('content/generateOutline', {
            title: this.formData.title,
            content: this.formData.content
          });

          this.formData.outline = response.outline || [];
          this.handleUpdate();

          notificationService.success('大纲生成成功');
        });
      } catch (error) {
        if (!error.message.includes('重复提交')) {
          notificationService.error('生成大纲失败', {
            suggestion: error.suggestion
          });
        }
      } finally {
        this.isGenerating = false;
      }
    },

    async improveContent() {
      try {
        await requestLock.withLock('improve_content', async () => {
          this.isGenerating = true;

          const response = await this.$store.dispatch('content/improveStory', {
            content: this.formData.content
          });

          this.formData.content = response.improved_content;
          this.handleUpdate();

          notificationService.success('内容优化成功');
        });
      } catch (error) {
        if (!error.message.includes('重复提交')) {
          notificationService.error('优化失败');
        }
      } finally {
        this.isGenerating = false;
      }
    },

    async expandContent() {
      try {
        await requestLock.withLock('expand_content', async () => {
          this.isGenerating = true;

          const response = await this.$store.dispatch('content/expandStory', {
            content: this.formData.content
          });

          this.formData.content = response.expanded_content;
          this.handleUpdate();

          notificationService.success('内容扩展成功');
        });
      } catch (error) {
        if (!error.message.includes('重复提交')) {
          notificationService.error('扩展失败');
        }
      } finally {
        this.isGenerating = false;
      }
    },

    addOutlineItem() {
      this.formData.outline.push({ text: '' });
      this.handleUpdate();
    },

    removeOutlineItem(index) {
      this.formData.outline.splice(index, 1);
      this.handleUpdate();
    }
  }
};
</script>

<style scoped>
.story-content {
  padding: 2rem 0;
}

.step-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.step-description {
  color: #6b7280;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.required {
  color: #ef4444;
}

.label-hint {
  font-weight: 400;
  color: #9ca3af;
  margin-left: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.3s;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-textarea.error-border {
  border-color: #f59e0b;
}

.input-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #9ca3af;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-hint.text-warning {
  color: #f59e0b;
}

.warning-text {
  font-weight: 600;
}

.error-message {
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.ai-assist {
  margin: 2rem 0;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.75rem;
  color: white;
}

.assist-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.assist-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-assist {
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-assist:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.btn-assist:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.outline-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.outline-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.outline-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.outline-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.outline-number {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.outline-input {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: white;
}

.btn-remove {
  width: 32px;
  height: 32px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-remove:hover {
  background: #fecaca;
}

.btn-add-outline {
  width: 100%;
  padding: 0.75rem;
  background: white;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  color: #6b7280;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-add-outline:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}
</style>
