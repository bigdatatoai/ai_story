<template>
  <div class="anime-generation-studio">
    <h1>🎨 AI动漫生成工作室</h1>

    <!-- 动漫风格选择 -->
    <div class="style-selector">
      <h2>选择动漫风格</h2>
      <div class="styles-grid">
        <div
          v-for="style in animeStyles"
          :key="style.value"
          @click="selectedStyle = style.value"
          :class="{ selected: selectedStyle === style.value }"
          class="style-card"
        >
          <div class="style-icon">{{ style.icon }}</div>
          <div class="style-name">{{ style.name }}</div>
          <div class="style-desc">{{ style.description }}</div>
        </div>
      </div>
    </div>

    <!-- 角色生成 -->
    <div class="character-section">
      <h2>角色生成</h2>
      
      <div class="character-form">
        <input v-model="characterForm.name" placeholder="角色名称" class="form-input">
        <input v-model="characterForm.age" type="number" placeholder="年龄" class="form-input">
        <textarea v-model="characterForm.appearance" placeholder="外貌描述..." rows="3" class="form-textarea"></textarea>
        <button @click="generateCharacter" class="btn btn-primary">生成角色</button>
      </div>

      <div v-if="generatedCharacters.length > 0" class="characters-display">
        <div v-for="char in generatedCharacters" :key="char.id" class="character-result">
          <h3>{{ char.name }}</h3>
          <div class="character-images">
            <img v-if="char.reference_sheet" :src="char.reference_sheet" alt="设定图">
            <div class="poses-grid">
              <img v-for="(url, pose) in char.poses" :key="pose" :src="url" :alt="pose">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 场景生成 -->
    <div class="scene-section">
      <h2>场景生成</h2>
      
      <div class="scene-form">
        <textarea v-model="sceneDescription" placeholder="场景描述..." rows="4" class="form-textarea"></textarea>
        <select v-model="cameraAngle" class="form-select">
          <option value="wide_shot">远景</option>
          <option value="medium_shot">中景</option>
          <option value="close_up">特写</option>
        </select>
        <button @click="generateScene" class="btn btn-primary">生成场景</button>
      </div>

      <div v-if="generatedScenes.length > 0" class="scenes-grid">
        <img v-for="(scene, index) in generatedScenes" :key="index" :src="scene" alt="场景">
      </div>
    </div>

    <!-- 漫画分格 -->
    <div class="comic-section">
      <h2>漫画分格生成</h2>
      
      <div class="comic-form">
        <select v-model="panelLayout" class="form-select">
          <option value="4_panel">4格漫画</option>
          <option value="manga_page">漫画页</option>
          <option value="webtoon">条漫</option>
        </select>
        <button @click="generateComicPanels" class="btn btn-primary">生成分格</button>
      </div>

      <div v-if="comicPanels.length > 0" class="panels-display">
        <div v-for="(panel, index) in comicPanels" :key="index" class="panel-item">
          <img :src="panel.image_url" alt="分格">
          <p>{{ panel.dialogue }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import videoAPI from '@/api/video'

export default {
  name: 'AnimeGenerationStudio',
  
  setup() {
    const animeStyles = [
      { value: 'shounen', name: '少年动漫', icon: '⚡', description: '热血、动作' },
      { value: 'shoujo', name: '少女动漫', icon: '💖', description: '浪漫、柔和' },
      { value: 'seinen', name: '青年动漫', icon: '🎯', description: '成熟、写实' },
      { value: 'chibi', name: 'Q版', icon: '🎀', description: '可爱、简化' },
      { value: 'ghibli', name: '吉卜力', icon: '🌿', description: '手绘、温暖' }
    ]
    
    const selectedStyle = ref('shounen')
    
    const characterForm = ref({
      name: '',
      age: 16,
      appearance: ''
    })
    
    const generatedCharacters = ref([])
    const sceneDescription = ref('')
    const cameraAngle = ref('medium_shot')
    const generatedScenes = ref([])
    const panelLayout = ref('4_panel')
    const comicPanels = ref([])
    
    const generateCharacter = async () => {
      try {
        const response = await videoAPI.generateAnimeCharacter({
          character_description: characterForm.value,
          anime_style: selectedStyle.value,
          poses: ['standing', 'running', 'fighting'],
          expressions: ['happy', 'angry', 'surprised']
        })
        
        if (response.success) {
          generatedCharacters.value.push(response.data)
        }
      } catch (error) {
        console.error('生成角色失败:', error)
      }
    }
    
    const generateScene = async () => {
      try {
        const response = await videoAPI.generateAnimeScene({
          scene_description: sceneDescription.value,
          characters: [],
          anime_style: selectedStyle.value,
          camera_angle: cameraAngle.value
        })
        
        if (response.success) {
          generatedScenes.value.push(response.data)
        }
      } catch (error) {
        console.error('生成场景失败:', error)
      }
    }
    
    const generateComicPanels = async () => {
      try {
        const response = await videoAPI.generateComicPanels({
          script: { scenes: [] },
          panel_layout: panelLayout.value
        })
        
        if (response.success) {
          comicPanels.value = response.data
        }
      } catch (error) {
        console.error('生成分格失败:', error)
      }
    }
    
    return {
      animeStyles,
      selectedStyle,
      characterForm,
      generatedCharacters,
      sceneDescription,
      cameraAngle,
      generatedScenes,
      panelLayout,
      comicPanels,
      generateCharacter,
      generateScene,
      generateComicPanels
    }
  }
}
</script>

<style scoped>
.anime-generation-studio {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

h1 {
  font-size: 32px;
  margin-bottom: 32px;
}

h2 {
  font-size: 24px;
  margin-bottom: 20px;
}

.style-selector {
  margin-bottom: 40px;
}

.styles-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.style-card {
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.style-card:hover {
  border-color: #667eea;
  transform: translateY(-2px);
}

.style-card.selected {
  border-color: #667eea;
  background: #f0f4ff;
}

.style-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.style-name {
  font-weight: 600;
  margin-bottom: 8px;
}

.style-desc {
  font-size: 12px;
  color: #666;
}

.character-section,
.scene-section,
.comic-section {
  margin-bottom: 40px;
  padding: 24px;
  background: white;
  border-radius: 12px;
}

.character-form,
.scene-form,
.comic-form {
  display: grid;
  gap: 12px;
  max-width: 600px;
  margin-bottom: 24px;
}

.form-input,
.form-textarea,
.form-select {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
}

.characters-display {
  display: grid;
  gap: 24px;
}

.character-result {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
}

.character-images {
  display: grid;
  gap: 16px;
}

.poses-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.poses-grid img {
  width: 100%;
  border-radius: 8px;
}

.scenes-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.scenes-grid img {
  width: 100%;
  border-radius: 8px;
}

.panels-display {
  display: grid;
  gap: 16px;
}

.panel-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.panel-item img {
  width: 100%;
}

.panel-item p {
  padding: 12px;
  background: #f8f9fa;
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
</style>
