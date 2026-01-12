<template>
  <div class="multimodal-generator">
    <h2>多模态生成</h2>
    
    <div class="generator-tabs">
      <button
        @click="activeTab = 'illustration'"
        :class="{ active: activeTab === 'illustration' }"
        class="tab-btn"
      >
        🎨 插画生成
      </button>
      <button
        @click="activeTab = 'audio'"
        :class="{ active: activeTab === 'audio' }"
        class="tab-btn"
      >
        🎵 有声故事
      </button>
    </div>

    <!-- 插画生成 -->
    <div v-if="activeTab === 'illustration'" class="tab-content">
      <div class="config-section">
        <label>插画风格</label>
        <select v-model="illustrationStyle" class="style-select">
          <option value="cartoon">卡通风格</option>
          <option value="watercolor">水彩画</option>
          <option value="realistic">写实风格</option>
          <option value="anime">动漫风格</option>
        </select>

        <label>插画数量</label>
        <input v-model.number="illustrationCount" type="number" min="1" max="10" class="count-input">

        <button @click="generateIllustrations" :disabled="isGenerating" class="btn btn-primary">
          {{ isGenerating ? '生成中...' : '生成插画' }}
        </button>
      </div>

      <div v-if="illustrations.length > 0" class="illustrations-grid">
        <div v-for="(ill, index) in illustrations" :key="index" class="illustration-card">
          <img :src="ill.image_url" :alt="ill.scene" class="illustration-image">
          <p class="illustration-scene">{{ ill.scene }}</p>
        </div>
      </div>
    </div>

    <!-- 有声故事 -->
    <div v-if="activeTab === 'audio'" class="tab-content">
      <div class="config-section">
        <label>音色配置</label>
        <div class="voice-config">
          <div class="voice-item">
            <span>旁白</span>
            <select v-model="voiceConfig.narrator" class="voice-select">
              <option value="zh-CN-XiaoxiaoNeural">小晓（女声）</option>
              <option value="zh-CN-YunxiNeural">云希（男声）</option>
            </select>
          </div>
        </div>

        <label>
          <input v-model="addBackgroundMusic" type="checkbox">
          添加背景音乐
        </label>

        <button @click="generateAudio" :disabled="isGeneratingAudio" class="btn btn-primary">
          {{ isGeneratingAudio ? '生成中...' : '生成有声故事' }}
        </button>
      </div>

      <div v-if="audioUrl" class="audio-player">
        <audio :src="audioUrl" controls class="audio-element"></audio>
        <button @click="downloadAudio" class="btn btn-secondary">下载音频</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'MultimodalGenerator',
  
  props: {
    storyId: String,
    storyContent: String
  },
  
  setup(props) {
    const activeTab = ref('illustration')
    const illustrationStyle = ref('cartoon')
    const illustrationCount = ref(4)
    const illustrations = ref([])
    const isGenerating = ref(false)
    
    const voiceConfig = ref({
      narrator: 'zh-CN-XiaoxiaoNeural'
    })
    const addBackgroundMusic = ref(true)
    const audioUrl = ref(null)
    const isGeneratingAudio = ref(false)
    
    const generateIllustrations = async () => {
      isGenerating.value = true
      
      try {
        const response = await storyAPI.generateIllustrations({
          story_id: props.storyId,
          style: illustrationStyle.value,
          num_illustrations: illustrationCount.value
        })
        
        if (response.success) {
          illustrations.value = response.data
        }
      } catch (error) {
        console.error('生成插画失败:', error)
      } finally {
        isGenerating.value = false
      }
    }
    
    const generateAudio = async () => {
      isGeneratingAudio.value = true
      
      try {
        const response = await storyAPI.generateAudioStory({
          story_id: props.storyId,
          voice_config: voiceConfig.value,
          add_background_music: addBackgroundMusic.value
        })
        
        if (response.success) {
          audioUrl.value = response.data.audio_url
        }
      } catch (error) {
        console.error('生成音频失败:', error)
      } finally {
        isGeneratingAudio.value = false
      }
    }
    
    const downloadAudio = () => {
      if (audioUrl.value) {
        const link = document.createElement('a')
        link.href = audioUrl.value
        link.download = 'story_audio.mp3'
        link.click()
      }
    }
    
    return {
      activeTab,
      illustrationStyle,
      illustrationCount,
      illustrations,
      isGenerating,
      voiceConfig,
      addBackgroundMusic,
      audioUrl,
      isGeneratingAudio,
      generateIllustrations,
      generateAudio,
      downloadAudio
    }
  }
}
</script>

<style scoped>
.multimodal-generator {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.generator-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.tab-btn {
  padding: 12px 24px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s;
}

.tab-btn.active {
  border-color: #667eea;
  background: #667eea;
  color: white;
}

.tab-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
}

.config-section {
  margin-bottom: 24px;
}

.config-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.style-select,
.count-input,
.voice-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  margin-bottom: 16px;
}

.illustrations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.illustration-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.illustration-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.illustration-scene {
  padding: 12px;
  font-size: 14px;
  color: #666;
}

.audio-player {
  text-align: center;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 8px;
}

.audio-element {
  width: 100%;
  margin-bottom: 16px;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
