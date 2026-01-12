<template>
  <div class="story-generator">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">AI故事生成器</h1>
        <p class="page-subtitle">输入主题，让AI为你创作精彩故事</p>
      </div>
    </div>

    <!-- 生成表单 -->
    <div class="generator-form">
      <div class="form-card">
        <!-- 主题输入 -->
        <div class="form-section">
          <label class="form-label">
            <span class="label-text">故事主题</span>
            <span class="label-required">*</span>
          </label>
          <div class="input-wrapper">
            <input
              v-model="formData.topic"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.topic }"
              placeholder="例如：森林里的小兔子、太空探险、友谊的力量..."
              maxlength="100"
              @input="validateTopic"
            />
            <div class="input-counter">{{ formData.topic.length }}/100</div>
          </div>
          <div v-if="errors.topic" class="error-message">{{ errors.topic }}</div>
          <div class="input-hint">
            <svg class="hint-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <span>请输入2-100字的故事主题，简洁明了最佳</span>
          </div>
        </div>

        <!-- 快捷模板 -->
        <div class="form-section">
          <label class="form-label">快捷模板</label>
          <div class="template-grid">
            <button
              v-for="template in quickTemplates"
              :key="template.topic"
              class="template-btn"
              @click="applyTemplate(template)"
            >
              <span class="template-icon">{{ template.icon }}</span>
              <span class="template-text">{{ template.topic }}</span>
            </button>
          </div>
        </div>

        <!-- 配置选项 -->
        <div class="form-section">
          <label class="form-label">故事配置</label>
          
          <div class="config-grid">
            <!-- 年龄段 -->
            <div class="config-item">
              <label class="config-label">目标年龄段</label>
              <select v-model="formData.age_group" class="config-select">
                <option value="preschool">学龄前 (3-6岁)</option>
                <option value="elementary">小学生 (7-12岁)</option>
                <option value="teenager">青少年 (13-18岁)</option>
                <option value="adult">成人 (18岁以上)</option>
              </select>
            </div>

            <!-- 题材 -->
            <div class="config-item">
              <label class="config-label">故事题材</label>
              <select v-model="formData.genre" class="config-select">
                <option value="fairy_tale">童话故事</option>
                <option value="adventure">冒险故事</option>
                <option value="sci_fi">科幻故事</option>
                <option value="fable">寓言故事</option>
                <option value="friendship">友谊故事</option>
                <option value="mystery">悬疑推理</option>
              </select>
            </div>

            <!-- 风格 -->
            <div class="config-item">
              <label class="config-label">故事风格</label>
              <select v-model="formData.style" class="config-select">
                <option value="warm_healing">温馨治愈</option>
                <option value="humorous">幽默诙谐</option>
                <option value="inspirational">励志向上</option>
                <option value="poetic">诗意唯美</option>
                <option value="suspenseful">紧张悬疑</option>
              </select>
            </div>

            <!-- 字数 -->
            <div class="config-item">
              <label class="config-label">故事长度</label>
              <div class="slider-wrapper">
                <input
                  v-model.number="formData.word_count"
                  type="range"
                  min="200"
                  max="3000"
                  step="100"
                  class="word-count-slider"
                />
                <div class="slider-value">{{ formData.word_count }} 字</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button
            class="btn btn-primary btn-generate"
            :disabled="isGenerating || !canGenerate"
            @click="generateStory"
          >
            <span v-if="isGenerating" class="loading-spinner"></span>
            <svg v-else class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
            <span>{{ isGenerating ? '生成中...' : '开始生成' }}</span>
          </button>

          <button
            v-if="hasHistory"
            class="btn btn-secondary"
            @click="showHistory = true"
          >
            <svg class="btn-icon" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
            </svg>
            <span>历史记录</span>
          </button>
        </div>
      </div>

      <!-- 生成进度 -->
      <div v-if="isGenerating" class="progress-card">
        <div class="progress-header">
          <h3 class="progress-title">正在生成故事...</h3>
          <div class="progress-percentage">{{ generationProgress }}%</div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: generationProgress + '%' }"></div>
        </div>
        <div class="progress-message">{{ generationMessage }}</div>
      </div>

      <!-- 生成结果 -->
      <div v-if="generatedStory" class="result-card">
        <div class="result-header">
          <h2 class="result-title">{{ generatedStory.title }}</h2>
          <div class="result-actions">
            <button class="action-btn" @click="copyStory" title="复制">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
              </svg>
            </button>
            <button class="action-btn" @click="downloadStory" title="下载">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </button>
            <button class="action-btn" @click="shareStory" title="分享">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z" />
              </svg>
            </button>
            <button class="action-btn" @click="regenerateStory" title="重新生成">
              <svg viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
              </svg>
            </button>
          </div>
        </div>

        <!-- 质量评分 -->
        <div v-if="generatedStory.quality_score" class="quality-score">
          <div class="score-label">质量评分</div>
          <div class="score-value" :class="getScoreClass(generatedStory.quality_score)">
            {{ generatedStory.quality_score.toFixed(1) }}
          </div>
          <div class="score-bar">
            <div class="score-fill" :style="{ width: generatedStory.quality_score + '%' }"></div>
          </div>
        </div>

        <!-- 故事内容 -->
        <div class="story-content" :class="{ 'night-mode': nightMode }">
          <div class="content-text" v-html="formattedContent"></div>
        </div>

        <!-- 内容控制 -->
        <div class="content-controls">
          <button class="control-btn" @click="toggleNightMode">
            <svg v-if="!nightMode" viewBox="0 0 20 20" fill="currentColor">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
            <svg v-else viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd" />
            </svg>
            <span>{{ nightMode ? '日间模式' : '夜间模式' }}</span>
          </button>

          <div class="font-size-control">
            <button class="control-btn" @click="decreaseFontSize">A-</button>
            <span class="font-size-label">{{ fontSize }}px</span>
            <button class="control-btn" @click="increaseFontSize">A+</button>
          </div>
        </div>

        <!-- 续写和编辑 -->
        <div class="story-actions">
          <button class="action-btn-large" @click="continueStory">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd" />
            </svg>
            <span>续写故事</span>
          </button>

          <button class="action-btn-large" @click="editStory">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
            <span>编辑修改</span>
          </button>

          <button class="action-btn-large" @click="exportStory">
            <svg viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0015.414 6L12 2.586A2 2 0 0010.586 2H6zm5 6a1 1 0 10-2 0v3.586l-1.293-1.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V8z" clip-rule="evenodd" />
            </svg>
            <span>导出文件</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="error-toast" @click="errorMessage = ''">
      <svg class="error-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-toast" @click="successMessage = ''">
      <svg class="success-icon" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
      </svg>
      <span>{{ successMessage }}</span>
    </div>
  </div>
</template>

<script>
import storyAPI from '@/api/story'

export default {
  name: 'StoryGenerator',
  
  data() {
    return {
      // 表单数据
      formData: {
        topic: '',
        age_group: 'elementary',
        genre: 'fairy_tale',
        style: 'warm_healing',
        word_count: 800,
      },
      style: 'warm_healing',
      word_count: 800,
    })

    // 快捷模板
    const quickTemplates = ref([
      { icon: '🐰', topic: '森林里的小兔子', genre: 'fairy_tale', style: 'warm_healing' },
      { icon: '🚀', topic: '太空探险之旅', genre: 'sci_fi', style: 'suspenseful' },
      { icon: '🏰', topic: '勇敢的小公主', genre: 'adventure', style: 'inspirational' },
      { icon: '🌟', topic: '友谊的力量', genre: 'friendship', style: 'warm_healing' },
      { icon: '🔍', topic: '神秘的失踪案', genre: 'mystery', style: 'suspenseful' },
      { icon: '🦁', topic: '骄傲的狮子', genre: 'fable', style: 'humorous' },
    ])

    // 状态
    const isGenerating = ref(false)
    const generationProgress = ref(0)
    const generationMessage = ref('')
    const generatedStory = ref(null)
    const errors = ref({})
    const errorMessage = ref('')
    const successMessage = ref('')
    const nightMode = ref(false)
    const fontSize = ref(16)
    const hasHistory = ref(false)
    const showHistory = ref(false)

    // 验证
    const validateTopic = () => {
      if (!formData.value.topic) {
        errors.value.topic = '请输入故事主题'
      } else if (formData.value.topic.length < 2) {
        errors.value.topic = '主题至少需要2个字'
      } else if (formData.value.topic.length > 100) {
        errors.value.topic = '主题不能超过100个字'
      } else {
        errors.value.topic = ''
      }
    }

    const canGenerate = computed(() => {
      return formData.value.topic.length >= 2 && !errors.value.topic
    })

    // 格式化内容
    const formattedContent = computed(() => {
      if (!generatedStory.value) return ''
      
      let content = generatedStory.value.content
      
      // 分段
      content = content.replace(/\n\n/g, '</p><p>')
      content = `<p>${content}</p>`
      
      // 对话加粗
      content = content.replace(/"([^"]+)"/g, '<strong>"$1"</strong>')
      
      return content
    })

    // 应用模板
    const applyTemplate = (template) => {
      formData.value.topic = template.topic
      formData.value.genre = template.genre
      formData.value.style = template.style
      validateTopic()
    }

    // 生成故事
    const generateStory = async () => {
      if (!canGenerate.value) return

      isGenerating.value = true
      generationProgress.value = 0
      generationMessage.value = '正在准备生成...'
      errorMessage.value = ''

      try {
        // 模拟进度
        const progressInterval = setInterval(() => {
          if (generationProgress.value < 90) {
            generationProgress.value += 10
            
            if (generationProgress.value < 30) {
              generationMessage.value = '正在分析主题...'
            } else if (generationProgress.value < 60) {
              generationMessage.value = '正在构思情节...'
            } else {
              generationMessage.value = '正在生成故事...'
            }
          }
        }, 500)

        const response = await storyAPI.generateStory(formData.value)

        clearInterval(progressInterval)
        generationProgress.value = 100
        generationMessage.value = '生成完成！'

        if (response.success) {
          generatedStory.value = response.data
          successMessage.value = '故事生成成功！'
          setTimeout(() => {
            successMessage.value = ''
          }, 3000)
        } else {
          throw new Error(response.error || '生成失败')
        }
      } catch (error) {
        console.error('生成失败:', error)
        errorMessage.value = error.response?.data?.error || error.message || '生成失败，请重试'
      } finally {
        isGenerating.value = false
      }
    }

    // 复制故事
    const copyStory = async () => {
      try {
        await navigator.clipboard.writeText(generatedStory.value.content)
        successMessage.value = '已复制到剪贴板'
        setTimeout(() => {
          successMessage.value = ''
        }, 2000)
      } catch (error) {
        errorMessage.value = '复制失败'
      }
    }

    // 下载故事
    const downloadStory = () => {
      const content = generatedStory.value.content
      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${generatedStory.value.title}.txt`
      link.click()
      URL.revokeObjectURL(url)
      
      successMessage.value = '下载成功'
      setTimeout(() => {
        successMessage.value = ''
      }, 2000)
    }

    // 分享故事
    const shareStory = async () => {
      if (navigator.share) {
        try {
          await navigator.share({
            title: generatedStory.value.title,
            text: generatedStory.value.content.substring(0, 200) + '...',
          })
        } catch (error) {
          console.log('分享取消')
        }
      } else {
        copyStory()
      }
    }

    // 重新生成
    const regenerateStory = () => {
      generatedStory.value = null
      generateStory()
    }

    // 续写故事
    const continueStory = () => {
      // TODO: 实现续写功能
      console.log('续写故事')
    }

    // 编辑故事
    const editStory = () => {
      // TODO: 实现编辑功能
      console.log('编辑故事')
    }

    // 导出故事
    const exportStory = () => {
      // TODO: 实现导出功能
      console.log('导出故事')
    }

    // 夜间模式
    const toggleNightMode = () => {
      nightMode.value = !nightMode.value
    }

    // 字体大小
    const increaseFontSize = () => {
      if (fontSize.value < 24) fontSize.value += 2
    }

    const decreaseFontSize = () => {
      if (fontSize.value > 12) fontSize.value -= 2
    }

    // 质量评分样式
    const getScoreClass = (score) => {
      if (score >= 80) return 'score-excellent'
      if (score >= 60) return 'score-good'
      return 'score-fair'
    }

    // 监听字体大小变化
    watch(fontSize, (newSize) => {
      document.documentElement.style.setProperty('--story-font-size', `${newSize}px`)
    })

    return {
      formData,
      quickTemplates,
      isGenerating,
      generationProgress,
      generationMessage,
      generatedStory,
      errors,
      errorMessage,
      successMessage,
      nightMode,
      fontSize,
      hasHistory,
      showHistory,
      canGenerate,
      formattedContent,
      validateTopic,
      applyTemplate,
      generateStory,
      copyStory,
      downloadStory,
      shareStory,
      regenerateStory,
      continueStory,
      editStory,
      exportStory,
      toggleNightMode,
      increaseFontSize,
      decreaseFontSize,
      getScoreClass,
    }
  },
}
</script>

<style scoped>
/* 组件样式省略，实际项目中需要完整实现 */
.story-generator {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 更多样式... */
</style>
