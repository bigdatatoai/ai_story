<template>
  <div class="guided-creation">
    <div class="creation-header">
      <h2>🎨 故事接龙创作</h2>
      <p class="subtitle">让我们一起创作一个精彩的故事吧！</p>
    </div>

    <!-- 故事展示区 -->
    <div class="story-display">
      <div v-for="(part, index) in storyParts" :key="index" class="story-part">
        <div class="part-content" :class="{ 'ai-part': part.author === 'ai', 'child-part': part.author === 'child' }">
          <span class="author-badge" v-if="part.author === 'child'">👦 你写的</span>
          <span class="author-badge ai" v-else>🤖 AI续写</span>
          <p>{{ part.content }}</p>
        </div>
      </div>
    </div>

    <!-- 剧情选择模式 -->
    <div v-if="showChoices && plotChoices.length > 0" class="plot-choices">
      <h3>🌟 接下来会发生什么？</h3>
      <p class="choice-hint">选择一个你喜欢的方向</p>
      
      <div class="choices-grid">
        <button
          v-for="choice in plotChoices"
          :key="choice.id"
          @click="selectChoice(choice)"
          class="choice-btn"
        >
          <div class="choice-label">{{ choice.id }}</div>
          <div class="choice-description">{{ choice.description }}</div>
          <div class="choice-preview" v-if="choice.preview">{{ choice.preview }}</div>
        </button>
      </div>
    </div>

    <!-- 孩子输入区 -->
    <div v-else class="child-input-area">
      <div class="input-header">
        <h3>{{ currentPrompt }}</h3>
        <div class="suggestions" v-if="suggestions.length > 0">
          <span class="suggestion-label">💡 提示：</span>
          <button
            v-for="(suggestion, index) in suggestions"
            :key="index"
            @click="applySuggestion(suggestion)"
            class="suggestion-chip"
          >
            {{ suggestion }}
          </button>
        </div>
      </div>

      <textarea
        v-model="childInput"
        @input="handleInput"
        class="child-textarea"
        :placeholder="inputPlaceholder"
        rows="4"
      ></textarea>

      <div class="input-footer">
        <div class="char-count">{{ childInput.length }} 字</div>
        <div class="input-actions">
          <button @click="requestChoices" class="btn btn-secondary">
            🎲 给我一些选择
          </button>
          <button
            @click="submitInput"
            :disabled="!canSubmit"
            class="btn btn-primary"
          >
            ✨ 继续故事
          </button>
        </div>
      </div>
    </div>

    <!-- 控制按钮 -->
    <div class="creation-controls">
      <button @click="restartStory" class="btn btn-outline">🔄 重新开始</button>
      <button @click="saveStory" class="btn btn-success" v-if="storyParts.length > 2">
        💾 保存故事
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'GuidedCreation',
  
  props: {
    topic: {
      type: String,
      default: '勇敢的小兔子'
    },
    ageGroup: {
      type: String,
      default: 'elementary'
    }
  },
  
  setup(props, { emit }) {
    const storyParts = ref([])
    const childInput = ref('')
    const currentPrompt = ref('让我们开始创作吧！')
    const suggestions = ref([])
    const showChoices = ref(false)
    const plotChoices = ref([])
    const chainId = ref(null)
    const isProcessing = ref(false)
    
    const canSubmit = computed(() => 
      childInput.value.trim().length > 0 && !isProcessing.value
    )
    
    const inputPlaceholder = computed(() => 
      storyParts.value.length === 0 
        ? '写下你的想法，让故事开始...' 
        : '接下来会发生什么呢？'
    )
    
    const startStoryChain = async () => {
      try {
        const response = await storyAPI.startStoryChain({
          topic: props.topic,
          age_group: props.ageGroup
        })
        
        if (response.success) {
          chainId.value = response.data.chain_id
          
          storyParts.value.push({
            author: 'ai',
            content: response.data.first_sentence
          })
          
          currentPrompt.value = response.data.next_prompt
          suggestions.value = response.data.suggestions || []
        }
      } catch (error) {
        console.error('开始故事接龙失败:', error)
      }
    }
    
    const submitInput = async () => {
      if (!canSubmit.value) return
      
      isProcessing.value = true
      
      // 添加孩子的输入
      storyParts.value.push({
        author: 'child',
        content: childInput.value
      })
      
      const userInput = childInput.value
      childInput.value = ''
      
      try {
        const response = await storyAPI.continueStoryChain({
          chain_id: chainId.value,
          previous_content: getFullStory(),
          child_input: userInput,
          age_group: props.ageGroup
        })
        
        if (response.success) {
          // 添加AI续写
          storyParts.value.push({
            author: 'ai',
            content: response.data.ai_continuation
          })
          
          currentPrompt.value = response.data.next_prompt
          suggestions.value = response.data.suggestions || []
        }
      } catch (error) {
        console.error('续写失败:', error)
      } finally {
        isProcessing.value = false
        showChoices.value = false
      }
    }
    
    const requestChoices = async () => {
      try {
        const response = await storyAPI.getPlotChoices({
          current_story: getFullStory(),
          age_group: props.ageGroup,
          num_choices: 3
        })
        
        if (response.success) {
          plotChoices.value = response.data
          showChoices.value = true
        }
      } catch (error) {
        console.error('获取选项失败:', error)
      }
    }
    
    const selectChoice = async (choice) => {
      isProcessing.value = true
      
      try {
        const response = await storyAPI.applyPlotChoice({
          current_story: getFullStory(),
          choice_id: choice.id,
          choice_description: choice.description,
          age_group: props.ageGroup
        })
        
        if (response.success) {
          storyParts.value.push({
            author: 'ai',
            content: response.data
          })
          
          showChoices.value = false
          currentPrompt.value = '故事继续发展，你想让主角做什么呢？'
        }
      } catch (error) {
        console.error('应用选择失败:', error)
      } finally {
        isProcessing.value = false
      }
    }
    
    const applySuggestion = (suggestion) => {
      childInput.value = suggestion
    }
    
    const handleInput = () => {
      // 可以添加实时验证
    }
    
    const getFullStory = () => {
      return storyParts.value.map(part => part.content).join('\n')
    }
    
    const restartStory = () => {
      if (confirm('确定要重新开始吗？当前进度将丢失。')) {
        storyParts.value = []
        childInput.value = ''
        showChoices.value = false
        plotChoices.value = []
        startStoryChain()
      }
    }
    
    const saveStory = async () => {
      try {
        const fullStory = getFullStory()
        const response = await storyAPI.saveGuidedStory({
          title: props.topic,
          content: fullStory,
          chain_id: chainId.value
        })
        
        if (response.success) {
          alert('故事保存成功！')
          emit('story-saved', response.data)
        }
      } catch (error) {
        console.error('保存失败:', error)
      }
    }
    
    // 初始化
    startStoryChain()
    
    return {
      storyParts,
      childInput,
      currentPrompt,
      suggestions,
      showChoices,
      plotChoices,
      canSubmit,
      inputPlaceholder,
      submitInput,
      requestChoices,
      selectChoice,
      applySuggestion,
      handleInput,
      restartStory,
      saveStory
    }
  }
}
</script>

<style scoped>
.guided-creation {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.creation-header {
  text-align: center;
  margin-bottom: 30px;
}

.creation-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.story-display {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  max-height: 500px;
  overflow-y: auto;
}

.story-part {
  margin-bottom: 16px;
}

.part-content {
  padding: 16px;
  border-radius: 8px;
  position: relative;
}

.part-content.ai-part {
  background: white;
  border-left: 4px solid #667eea;
}

.part-content.child-part {
  background: #e3f2fd;
  border-left: 4px solid #4CAF50;
}

.author-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 8px;
  background: #4CAF50;
  color: white;
}

.author-badge.ai {
  background: #667eea;
}

.part-content p {
  margin: 0;
  line-height: 1.8;
  color: #333;
}

.plot-choices {
  background: white;
  border: 2px solid #667eea;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.plot-choices h3 {
  margin: 0 0 8px 0;
  color: #333;
}

.choice-hint {
  color: #666;
  margin-bottom: 20px;
}

.choices-grid {
  display: grid;
  gap: 12px;
}

.choice-btn {
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.3s;
}

.choice-btn:hover {
  border-color: #667eea;
  background: #f0f4ff;
  transform: translateY(-2px);
}

.choice-label {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  text-align: center;
  line-height: 32px;
  font-weight: 600;
  margin-bottom: 8px;
}

.choice-description {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.choice-preview {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.child-input-area {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.input-header h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-top: 12px;
}

.suggestion-label {
  font-size: 14px;
  color: #666;
}

.suggestion-chip {
  padding: 6px 12px;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 16px;
  font-size: 13px;
  color: #1976d2;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  background: #90caf9;
  color: white;
}

.child-textarea {
  width: 100%;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  line-height: 1.6;
  font-family: inherit;
  resize: vertical;
  margin-bottom: 12px;
}

.child-textarea:focus {
  outline: none;
  border-color: #667eea;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  font-size: 14px;
  color: #999;
}

.input-actions {
  display: flex;
  gap: 12px;
}

.creation-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-success {
  background: #4CAF50;
  color: white;
}

.btn-outline {
  background: white;
  border: 2px solid #e0e0e0;
  color: #666;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
