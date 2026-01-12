<template>
  <div class="export-dialog-overlay" @click.self="$emit('close')">
    <div class="export-dialog">
      <div class="dialog-header">
        <h2>导出故事</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <div class="dialog-body">
        <div class="export-formats">
          <div
            v-for="format in exportFormats"
            :key="format.value"
            @click="selectedFormat = format.value"
            :class="{ selected: selectedFormat === format.value }"
            class="format-card"
          >
            <div class="format-icon">{{ format.icon }}</div>
            <div class="format-name">{{ format.name }}</div>
            <div class="format-desc">{{ format.description }}</div>
          </div>
        </div>

        <div v-if="selectedFormat === 'pdf'" class="format-options">
          <h3>PDF选项</h3>
          <label>
            <input v-model="pdfOptions.layout" type="radio" value="standard">
            标准布局
          </label>
          <label>
            <input v-model="pdfOptions.layout" type="radio" value="picture_book">
            绘本布局
          </label>
          <label>
            <input v-model="pdfOptions.includeIllustrations" type="checkbox">
            包含插画
          </label>
        </div>

        <div v-if="selectedFormat === 'epub'" class="format-options">
          <h3>EPUB选项</h3>
          <label>
            <input v-model="epubOptions.includeIllustrations" type="checkbox">
            包含插画
          </label>
          <label>
            <input v-model="epubOptions.includeTOC" type="checkbox">
            包含目录
          </label>
        </div>

        <div class="export-actions">
          <button @click="exportStory" :disabled="isExporting" class="btn btn-primary">
            <span v-if="isExporting" class="loading-spinner"></span>
            {{ isExporting ? '导出中...' : '开始导出' }}
          </button>
        </div>

        <div v-if="exportResult" class="export-result">
          <div class="result-success">
            <svg class="success-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <p>导出成功！</p>
          </div>
          <a :href="exportResult.file_url" download class="btn btn-download">
            下载文件
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'ExportDialog',
  
  props: {
    storyId: {
      type: String,
      required: true
    }
  },
  
  emits: ['close'],
  
  setup(props) {
    const exportFormats = [
      {
        value: 'txt',
        name: '纯文本',
        icon: '📄',
        description: '简单的文本文件'
      },
      {
        value: 'pdf',
        name: 'PDF',
        icon: '📕',
        description: '适合打印和阅读'
      },
      {
        value: 'epub',
        name: 'EPUB',
        icon: '📚',
        description: '电子书格式'
      },
      {
        value: 'docx',
        name: 'Word',
        icon: '📝',
        description: 'Microsoft Word文档'
      },
      {
        value: 'markdown',
        name: 'Markdown',
        icon: '📋',
        description: '适合开发者'
      },
      {
        value: 'script',
        name: '动画脚本',
        icon: '🎬',
        description: '分镜脚本格式'
      }
    ]
    
    const selectedFormat = ref('pdf')
    const isExporting = ref(false)
    const exportResult = ref(null)
    
    const pdfOptions = reactive({
      layout: 'standard',
      includeIllustrations: true
    })
    
    const epubOptions = reactive({
      includeIllustrations: true,
      includeTOC: true
    })
    
    const exportStory = async () => {
      isExporting.value = true
      exportResult.value = null
      
      try {
        const options = selectedFormat.value === 'pdf' ? pdfOptions :
                       selectedFormat.value === 'epub' ? epubOptions : {}
        
        const response = await storyAPI.exportStory({
          story_id: props.storyId,
          format: selectedFormat.value,
          options: options
        })
        
        if (response.success) {
          exportResult.value = response.data
        }
      } catch (error) {
        console.error('导出失败:', error)
        alert('导出失败，请重试')
      } finally {
        isExporting.value = false
      }
    }
    
    return {
      exportFormats,
      selectedFormat,
      isExporting,
      exportResult,
      pdfOptions,
      epubOptions,
      exportStory
    }
  }
}
</script>

<style scoped>
.export-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.export-dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
}

.dialog-body {
  padding: 24px;
}

.export-formats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.format-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.format-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
}

.format-card.selected {
  border-color: #667eea;
  background: #f0f4ff;
}

.format-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.format-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.format-desc {
  font-size: 12px;
  color: #666;
}

.format-options {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.format-options h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.format-options label {
  display: block;
  margin-bottom: 8px;
  cursor: pointer;
}

.export-actions {
  text-align: center;
  margin-bottom: 24px;
}

.btn {
  padding: 12px 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.export-result {
  text-align: center;
}

.result-success {
  margin-bottom: 16px;
}

.success-icon {
  width: 64px;
  height: 64px;
  color: #4CAF50;
  margin-bottom: 12px;
}

.btn-download {
  display: inline-block;
  padding: 12px 32px;
  background: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
}
</style>
