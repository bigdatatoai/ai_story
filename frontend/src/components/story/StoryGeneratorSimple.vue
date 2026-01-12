<template>
  <div class="story-generator-simple">
    <h1>📚 AI故事生成器</h1>
    
    <div class="generator-form">
      <div class="form-group">
        <label>故事主题</label>
        <input 
          v-model="topic" 
          type="text" 
          placeholder="例如：勇敢的小兔子"
          class="form-input"
        >
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>年龄段</label>
          <select v-model="ageGroup" class="form-select">
            <option value="preschool">学龄前</option>
            <option value="elementary">小学生</option>
            <option value="teenager">青少年</option>
          </select>
        </div>

        <div class="form-group">
          <label>题材</label>
          <select v-model="genre" class="form-select">
            <option value="fairy_tale">童话</option>
            <option value="adventure">冒险</option>
            <option value="sci_fi">科幻</option>
          </select>
        </div>
      </div>

      <button 
        @click="generateStory" 
        :disabled="!topic || isGenerating"
        class="btn-generate"
      >
        {{ isGenerating ? '生成中...' : '生成故事' }}
      </button>
    </div>

    <div v-if="isGenerating" class="loading-state">
      <div class="spinner"></div>
      <p>AI正在创作故事，请稍候...</p>
    </div>

    <div v-if="generatedStory" class="story-result">
      <h2>{{ generatedStory.title }}</h2>
      <div class="story-content">{{ generatedStory.content }}</div>
      <div class="story-actions">
        <button @click="copyStory">📋 复制</button>
        <button @click="downloadStory">💾 下载</button>
      </div>
    </div>

    <div v-if="errorMessage" class="toast toast-error" @click="errorMessage = ''">
      ❌ {{ errorMessage }}
    </div>

    <div v-if="successMessage" class="toast toast-success" @click="successMessage = ''">
      ✅ {{ successMessage }}
    </div>
  </div>
</template>

<script>
import storyAPI from '@/api/story'

export default {
  name: 'StoryGeneratorSimple',
  
  data() {
    return {
      topic: '',
      ageGroup: 'elementary',
      genre: 'fairy_tale',
      isGenerating: false,
      generatedStory: null,
      errorMessage: '',
      successMessage: ''
    }
  },
  
  methods: {
    async generateStory() {
      this.isGenerating = true
      this.errorMessage = ''
      
      try {
        const response = await storyAPI.generateStory({
          topic: this.topic,
          age_group: this.ageGroup,
          genre: this.genre,
          word_count: 800
        })
        
        if (response.success) {
          this.generatedStory = response.data
          this.successMessage = '故事生成成功！'
          setTimeout(() => { this.successMessage = '' }, 3000)
        } else {
          throw new Error(response.error || '生成失败')
        }
      } catch (error) {
        console.error('生成故事失败:', error)
        this.errorMessage = error.response?.data?.error || error.message || '生成失败，请检查网络连接或稍后重试'
        setTimeout(() => { this.errorMessage = '' }, 5000)
      } finally {
        this.isGenerating = false
      }
    },
    
    copyStory() {
      if (this.generatedStory) {
        navigator.clipboard.writeText(this.generatedStory.content)
          .then(() => {
            this.successMessage = '已复制到剪贴板'
            setTimeout(() => { this.successMessage = '' }, 2000)
          })
          .catch(() => {
            this.errorMessage = '复制失败'
            setTimeout(() => { this.errorMessage = '' }, 2000)
          })
      }
    },
    
    downloadStory() {
      if (this.generatedStory) {
        const blob = new Blob([this.generatedStory.content], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${this.generatedStory.title || this.topic}.txt`
        a.click()
        URL.revokeObjectURL(url)
        this.successMessage = '下载成功'
        setTimeout(() => { this.successMessage = '' }, 2000)
      }
    }
  }
}
</script>

<style scoped>
.story-generator-simple {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  font-size: 28px;
  margin-bottom: 30px;
}

.generator-form {
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.btn-generate {
  width: 100%;
  padding: 14px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.btn-generate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.story-result {
  background: white;
  padding: 30px;
  border-radius: 12px;
}

.story-result h2 {
  margin-bottom: 20px;
}

.story-content {
  line-height: 1.8;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.story-actions {
  display: flex;
  gap: 12px;
}

.story-actions button {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.story-actions button:hover {
  background: #5568d3;
  transform: translateY(-1px);
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 30px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-state p {
  color: #666;
  font-size: 16px;
}

.toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  padding: 16px 24px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.toast-success {
  background: #4CAF50;
}

.toast-error {
  background: #f44336;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
