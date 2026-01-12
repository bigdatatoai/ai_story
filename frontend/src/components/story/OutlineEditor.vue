<template>
  <div class="outline-editor">
    <div class="editor-header">
      <h2>故事大纲编辑器</h2>
      <div class="header-actions">
        <button @click="generateOutline" class="btn btn-primary" :disabled="isGenerating">
          <span v-if="isGenerating" class="loading-spinner"></span>
          <span>{{ isGenerating ? '生成中...' : '生成大纲' }}</span>
        </button>
        <button @click="generateStoryFromOutline" class="btn btn-success" :disabled="!hasOutline || isGeneratingStory">
          <span>基于大纲生成故事</span>
        </button>
        <button @click="saveOutline" class="btn btn-secondary">保存大纲</button>
      </div>
    </div>

    <!-- 大纲表单 -->
    <div class="outline-form" v-if="outline">
      <!-- 主题 -->
      <div class="form-section">
        <label class="section-label">主题</label>
        <textarea v-model="outline.theme" class="form-textarea" rows="2" placeholder="故事的核心主题..."></textarea>
      </div>

      <!-- 背景设定 -->
      <div class="form-section">
        <label class="section-label">背景设定</label>
        <textarea v-model="outline.setting" class="form-textarea" rows="3" placeholder="故事发生的时间、地点、世界观..."></textarea>
      </div>

      <!-- 角色 -->
      <div class="form-section">
        <div class="section-header">
          <label class="section-label">角色</label>
          <button @click="addCharacter" class="btn-add">+ 添加角色</button>
        </div>
        
        <div class="characters-list">
          <div v-for="(char, index) in outline.characters" :key="index" class="character-card">
            <div class="card-header">
              <input v-model="char.名称" class="char-name-input" placeholder="角色名称">
              <button @click="removeCharacter(index)" class="btn-remove">×</button>
            </div>
            <div class="char-fields">
              <div class="field-group">
                <label>类型</label>
                <select v-model="char.类型" class="char-select">
                  <option value="主角">主角</option>
                  <option value="配角">配角</option>
                  <option value="反派">反派</option>
                  <option value="导师">导师</option>
                </select>
              </div>
              <div class="field-group">
                <label>性格</label>
                <input v-model="char.性格" class="char-input" placeholder="性格特征">
              </div>
              <div class="field-group">
                <label>目标</label>
                <input v-model="char.目标" class="char-input" placeholder="角色的目标或动机">
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 情节结构 -->
      <div class="form-section">
        <label class="section-label">情节结构</label>
        
        <div class="plot-points">
          <div class="plot-point">
            <div class="point-header">
              <h4>开端 (25%)</h4>
              <span class="point-hint">介绍主角、建立背景、引出冲突</span>
            </div>
            <textarea v-model="outline.plot_points.opening" class="plot-textarea" rows="4"></textarea>
          </div>

          <div class="plot-point">
            <div class="point-header">
              <h4>发展 (50%)</h4>
              <span class="point-hint">冲突升级、主角努力、遇到挫折</span>
            </div>
            <textarea v-model="outline.plot_points.development" class="plot-textarea" rows="6"></textarea>
          </div>

          <div class="plot-point">
            <div class="point-header">
              <h4>高潮 (15%)</h4>
              <span class="point-hint">最激烈的冲突、关键决策</span>
            </div>
            <textarea v-model="outline.plot_points.climax" class="plot-textarea" rows="4"></textarea>
          </div>

          <div class="plot-point">
            <div class="point-header">
              <h4>结局 (10%)</h4>
              <span class="point-hint">问题解决、主题升华</span>
            </div>
            <textarea v-model="outline.plot_points.resolution" class="plot-textarea" rows="3"></textarea>
          </div>
        </div>
      </div>

      <!-- 情感基调和价值观 -->
      <div class="form-row">
        <div class="form-section half">
          <label class="section-label">情感基调</label>
          <input v-model="outline.tone" class="form-input" placeholder="整体情感氛围">
        </div>
        <div class="form-section half">
          <label class="section-label">核心价值观</label>
          <input v-model="outline.core_values" class="form-input" placeholder="要传递的价值观">
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <p>还没有大纲，点击"生成大纲"开始创作</p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'OutlineEditor',
  
  props: {
    storyId: String,
    initialOutline: Object
  },
  
  setup(props, { emit }) {
    const outline = ref(props.initialOutline || null)
    const isGenerating = ref(false)
    const isGeneratingStory = ref(false)
    
    const hasOutline = computed(() => outline.value !== null)
    
    const generateOutline = async () => {
      isGenerating.value = true
      
      try {
        const response = await storyAPI.generateOutline({
          topic: '勇敢的小兔子', // 从父组件传入
          age_group: 'elementary',
          genre: 'fairy_tale',
          style: 'warm_healing',
          word_count: 800,
          character_count: 3
        })
        
        if (response.success) {
          outline.value = response.data
          emit('outline-generated', outline.value)
        }
      } catch (error) {
        console.error('生成大纲失败:', error)
      } finally {
        isGenerating.value = false
      }
    }
    
    const generateStoryFromOutline = async () => {
      if (!outline.value) return
      
      isGeneratingStory.value = true
      
      try {
        const response = await storyAPI.generateFromOutline({
          outline: outline.value,
          expand_level: 'detailed'
        })
        
        if (response.success) {
          emit('story-generated', response.data)
        }
      } catch (error) {
        console.error('生成故事失败:', error)
      } finally {
        isGeneratingStory.value = false
      }
    }
    
    const saveOutline = async () => {
      try {
        await storyAPI.saveOutline(props.storyId, outline.value)
        emit('outline-saved')
      } catch (error) {
        console.error('保存大纲失败:', error)
      }
    }
    
    const addCharacter = () => {
      if (!outline.value.characters) {
        outline.value.characters = []
      }
      
      outline.value.characters.push({
        名称: '',
        类型: '主角',
        性格: '',
        目标: ''
      })
    }
    
    const removeCharacter = (index) => {
      outline.value.characters.splice(index, 1)
    }
    
    return {
      outline,
      isGenerating,
      isGeneratingStory,
      hasOutline,
      generateOutline,
      generateStoryFromOutline,
      saveOutline,
      addCharacter,
      removeCharacter
    }
  }
}
</script>

<style scoped>
.outline-editor {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.form-section {
  margin-bottom: 30px;
}

.section-label {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.form-textarea,
.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}

.form-textarea {
  resize: vertical;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.btn-add {
  padding: 8px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.characters-list {
  display: grid;
  gap: 15px;
}

.character-card {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.char-name-input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  font-weight: 600;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.btn-remove {
  width: 32px;
  height: 32px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
}

.char-fields {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.field-group label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.char-input,
.char-select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.plot-points {
  display: grid;
  gap: 20px;
}

.plot-point {
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
}

.point-header {
  margin-bottom: 10px;
}

.point-header h4 {
  margin: 0 0 5px 0;
  color: #333;
}

.point-hint {
  font-size: 12px;
  color: #999;
}

.plot-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid #ffffff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
