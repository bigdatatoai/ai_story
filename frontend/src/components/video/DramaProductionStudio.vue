<template>
  <div class="drama-production-studio">
    <div class="studio-header">
      <h1>🎬 AI短剧制作工作室</h1>
    </div>

    <!-- 制作步骤 -->
    <div class="production-steps">
      <div
        v-for="(step, index) in steps"
        :key="index"
        :class="{ active: currentStep === index, completed: currentStep > index }"
        class="step-item"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-name">{{ step.name }}</div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="step-content">
      <!-- 步骤1: 剧本生成 -->
      <div v-if="currentStep === 0" class="step-panel">
        <h2>📝 剧本生成</h2>
        
        <div class="form-section">
          <div class="form-group">
            <label>剧本主题</label>
            <input v-model="scriptForm.theme" type="text" class="form-input" placeholder="例如：都市爱情故事">
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>集数</label>
              <input v-model.number="scriptForm.episode_count" type="number" min="1" class="form-input">
            </div>
            <div class="form-group">
              <label>每集时长（秒）</label>
              <input v-model.number="scriptForm.duration" type="number" min="30" class="form-input">
            </div>
          </div>

          <button @click="generateScript" class="btn btn-primary" :disabled="isGenerating">
            {{ isGenerating ? '生成中...' : '生成剧本' }}
          </button>
        </div>

        <div v-if="generatedScript" class="script-preview">
          <h3>{{ generatedScript.title }}</h3>
          <p class="synopsis">{{ generatedScript.synopsis }}</p>
          
          <div class="episodes">
            <div v-for="episode in generatedScript.episodes" :key="episode.episode_number" class="episode-card">
              <h4>第{{ episode.episode_number }}集</h4>
              <div class="scenes-count">{{ episode.scenes.length }}个场景</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤2: 角色设定 -->
      <div v-if="currentStep === 1" class="step-panel">
        <h2>👥 角色设定</h2>
        
        <div class="characters-grid">
          <div v-for="character in characters" :key="character.id" class="character-card">
            <div v-if="character.reference_image" class="character-image">
              <img :src="character.reference_image" alt="角色参考图">
            </div>
            <div class="character-info">
              <h3>{{ character.name }}</h3>
              <p>{{ character.personality }}</p>
              <button @click="generateCharacterRef(character)" class="btn-sm">
                生成参考图
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3: 分镜生成 -->
      <div v-if="currentStep === 2" class="step-panel">
        <h2>🎞️ 分镜脚本</h2>
        
        <div class="storyboard-list">
          <div v-for="(shot, index) in storyboard" :key="index" class="shot-card">
            <div class="shot-number">镜头 {{ index + 1 }}</div>
            <div class="shot-preview">
              <img v-if="shot.image_url" :src="shot.image_url" alt="分镜">
              <div v-else class="placeholder">待生成</div>
            </div>
            <div class="shot-info">
              <p>{{ shot.description }}</p>
              <button @click="generateShotImage(shot)" class="btn-sm">
                生成画面
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤4: 视频生成 -->
      <div v-if="currentStep === 3" class="step-panel">
        <h2>🎥 视频生成</h2>
        
        <div class="production-progress">
          <div class="progress-info">
            <span>总进度: {{ productionProgress }}%</span>
            <span>{{ completedShots }}/{{ totalShots }} 镜头已完成</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: productionProgress + '%' }"></div>
          </div>
        </div>

        <button @click="startProduction" class="btn btn-primary btn-large" :disabled="isProducing">
          {{ isProducing ? '生产中...' : '开始生产' }}
        </button>
      </div>

      <!-- 步骤5: 成片预览 -->
      <div v-if="currentStep === 4" class="step-panel">
        <h2>✅ 成片预览</h2>
        
        <div v-if="finalVideo" class="video-preview">
          <video :src="finalVideo.video_url" controls class="preview-video"></video>
          
          <div class="video-actions">
            <button @click="downloadVideo" class="btn btn-primary">下载视频</button>
            <button @click="shareVideo" class="btn btn-secondary">分享</button>
            <button @click="exportVideo" class="btn btn-secondary">导出其他格式</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 导航按钮 -->
    <div class="navigation-buttons">
      <button @click="prevStep" :disabled="currentStep === 0" class="btn btn-secondary">
        上一步
      </button>
      <button @click="nextStep" :disabled="!canProceed" class="btn btn-primary">
        {{ currentStep === 4 ? '完成' : '下一步' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import videoAPI from '@/api/video'

export default {
  name: 'DramaProductionStudio',
  
  setup() {
    const currentStep = ref(0)
    const isGenerating = ref(false)
    const isProducing = ref(false)
    
    const steps = [
      { name: '剧本生成' },
      { name: '角色设定' },
      { name: '分镜脚本' },
      { name: '视频生成' },
      { name: '成片预览' }
    ]
    
    const scriptForm = ref({
      theme: '',
      episode_count: 3,
      duration: 60
    })
    
    const generatedScript = ref(null)
    const characters = ref([])
    const storyboard = ref([])
    const productionProgress = ref(0)
    const completedShots = ref(0)
    const totalShots = ref(0)
    const finalVideo = ref(null)
    
    const canProceed = computed(() => {
      if (currentStep.value === 0) return generatedScript.value !== null
      if (currentStep.value === 1) return characters.value.length > 0
      if (currentStep.value === 2) return storyboard.value.length > 0
      if (currentStep.value === 3) return finalVideo.value !== null
      return true
    })
    
    const generateScript = async () => {
      isGenerating.value = true
      
      try {
        // 调用剧本生成API
        const response = await videoAPI.generateDramaScript({
          theme: scriptForm.value.theme,
          episode_count: scriptForm.value.episode_count,
          duration_per_episode: scriptForm.value.duration
        })
        
        if (response.success) {
          generatedScript.value = response.data
          characters.value = response.data.characters || []
        }
      } catch (error) {
        console.error('生成剧本失败:', error)
      } finally {
        isGenerating.value = false
      }
    }
    
    const generateCharacterRef = async (character) => {
      try {
        const response = await videoAPI.generateAnimeCharacter({
          character_description: character,
          anime_style: 'realistic'
        })
        
        if (response.success) {
          character.reference_image = response.data.reference_sheet
        }
      } catch (error) {
        console.error('生成角色参考图失败:', error)
      }
    }
    
    const generateShotImage = async (shot) => {
      try {
        const response = await videoAPI.generateAnimeScene({
          scene_description: shot.description,
          characters: shot.characters || [],
          anime_style: 'realistic'
        })
        
        if (response.success) {
          shot.image_url = response.data
        }
      } catch (error) {
        console.error('生成镜头画面失败:', error)
      }
    }
    
    const startProduction = async () => {
      isProducing.value = true
      
      try {
        const response = await videoAPI.produceDramaVideo({
          script: generatedScript.value,
          visual_style: 'realistic',
          auto_dubbing: true,
          auto_subtitle: true
        })
        
        if (response.success) {
          finalVideo.value = response.data
          currentStep.value = 4
        }
      } catch (error) {
        console.error('视频生产失败:', error)
      } finally {
        isProducing.value = false
      }
    }
    
    const prevStep = () => {
      if (currentStep.value > 0) {
        currentStep.value--
      }
    }
    
    const nextStep = () => {
      if (currentStep.value < 4 && canProceed.value) {
        currentStep.value++
      }
    }
    
    const downloadVideo = () => {
      if (finalVideo.value?.video_url) {
        window.open(finalVideo.value.video_url, '_blank')
      }
    }
    
    const shareVideo = () => {
      console.log('分享视频')
    }
    
    const exportVideo = () => {
      console.log('导出视频')
    }
    
    return {
      currentStep,
      steps,
      scriptForm,
      isGenerating,
      isProducing,
      generatedScript,
      characters,
      storyboard,
      productionProgress,
      completedShots,
      totalShots,
      finalVideo,
      canProceed,
      generateScript,
      generateCharacterRef,
      generateShotImage,
      startProduction,
      prevStep,
      nextStep,
      downloadVideo,
      shareVideo,
      exportVideo
    }
  }
}
</script>

<style scoped>
.drama-production-studio {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.studio-header h1 {
  font-size: 32px;
  margin-bottom: 32px;
}

.production-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  position: relative;
}

.production-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background: #e0e0e0;
  z-index: 0;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s;
}

.step-item.active .step-number {
  background: #667eea;
  color: white;
}

.step-item.completed .step-number {
  background: #4CAF50;
  color: white;
}

.step-name {
  font-size: 14px;
  color: #666;
}

.step-content {
  background: white;
  border-radius: 12px;
  padding: 32px;
  min-height: 500px;
  margin-bottom: 24px;
}

.form-section {
  max-width: 600px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.script-preview {
  margin-top: 32px;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 12px;
}

.episodes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.episode-card {
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.character-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.character-image {
  height: 200px;
  background: #f0f0f0;
}

.character-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.character-info {
  padding: 16px;
}

.storyboard-list {
  display: grid;
  gap: 16px;
}

.shot-card {
  display: grid;
  grid-template-columns: auto 200px 1fr;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.shot-preview {
  width: 200px;
  height: 120px;
  background: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
}

.shot-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}

.production-progress {
  margin-bottom: 32px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
}

.progress-bar {
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.video-preview {
  max-width: 800px;
  margin: 0 auto;
}

.preview-video {
  width: 100%;
  border-radius: 12px;
  margin-bottom: 24px;
}

.video-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.navigation-buttons {
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.btn-large {
  padding: 16px 48px;
  font-size: 16px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
