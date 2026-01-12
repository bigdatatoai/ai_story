<template>
  <div class="character-consistency-manager">
    <h2>👥 角色一致性管理</h2>

    <div class="characters-library">
      <div class="library-header">
        <h3>角色库</h3>
        <button @click="showAddDialog = true" class="btn btn-primary">+ 添加角色</button>
      </div>

      <div class="characters-grid">
        <div v-for="character in characters" :key="character.id" class="character-card">
          <div class="character-preview">
            <img v-if="character.reference_image" :src="character.reference_image" alt="角色参考图">
            <div v-else class="placeholder">无参考图</div>
          </div>

          <div class="character-info">
            <h4>{{ character.name }}</h4>
            <p class="character-desc">{{ character.description }}</p>
            
            <div class="character-tags">
              <span class="tag">{{ character.age }}岁</span>
              <span class="tag">{{ character.gender }}</span>
            </div>

            <div class="reference-images">
              <h5>参考图库</h5>
              <div class="images-grid">
                <img v-for="(img, index) in character.reference_images" :key="index" :src="img" alt="参考">
              </div>
            </div>

            <div class="character-actions">
              <button @click="generateMoreReferences(character)" class="btn-sm">生成更多参考</button>
              <button @click="editCharacter(character)" class="btn-sm">编辑</button>
              <button @click="deleteCharacter(character)" class="btn-sm danger">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加角色对话框 -->
    <div v-if="showAddDialog" class="dialog-overlay" @click.self="showAddDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h2>添加新角色</h2>
          <button @click="showAddDialog = false" class="btn-close">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label>角色名称</label>
            <input v-model="newCharacter.name" type="text" class="form-input">
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>年龄</label>
              <input v-model.number="newCharacter.age" type="number" class="form-input">
            </div>
            <div class="form-group">
              <label>性别</label>
              <select v-model="newCharacter.gender" class="form-select">
                <option value="male">男</option>
                <option value="female">女</option>
                <option value="other">其他</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>外貌描述</label>
            <textarea v-model="newCharacter.appearance" rows="4" class="form-textarea" placeholder="详细描述角色的外貌特征..."></textarea>
          </div>

          <div class="form-group">
            <label>性格特征</label>
            <textarea v-model="newCharacter.personality" rows="3" class="form-textarea"></textarea>
          </div>

          <div class="form-group">
            <label>视觉风格</label>
            <select v-model="newCharacter.style" class="form-select">
              <option value="realistic">写实</option>
              <option value="anime">动漫</option>
              <option value="cartoon">卡通</option>
            </select>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="showAddDialog = false" class="btn btn-secondary">取消</button>
          <button @click="addCharacter" class="btn btn-primary">生成角色</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import videoAPI from '@/api/video'

export default {
  name: 'CharacterConsistencyManager',
  
  setup() {
    const characters = ref([])
    const showAddDialog = ref(false)
    
    const newCharacter = ref({
      name: '',
      age: 20,
      gender: 'female',
      appearance: '',
      personality: '',
      style: 'anime'
    })
    
    const addCharacter = async () => {
      try {
        const response = await videoAPI.generateAnimeCharacter({
          character_description: newCharacter.value,
          anime_style: newCharacter.value.style,
          poses: ['standing', 'side_view', 'back_view'],
          expressions: ['neutral', 'happy', 'angry', 'surprised']
        })
        
        if (response.success) {
          characters.value.push({
            id: Date.now(),
            ...newCharacter.value,
            reference_image: response.data.reference_sheet,
            reference_images: Object.values(response.data.poses || {})
          })
          
          showAddDialog.value = false
          newCharacter.value = {
            name: '',
            age: 20,
            gender: 'female',
            appearance: '',
            personality: '',
            style: 'anime'
          }
        }
      } catch (error) {
        console.error('生成角色失败:', error)
        alert('生成失败，请重试')
      }
    }
    
    const generateMoreReferences = async (character) => {
      try {
        const response = await videoAPI.generateAnimeCharacter({
          character_description: character,
          anime_style: character.style,
          poses: ['action', 'sitting', 'walking']
        })
        
        if (response.success && response.data.poses) {
          character.reference_images.push(...Object.values(response.data.poses))
        }
      } catch (error) {
        console.error('生成参考图失败:', error)
      }
    }
    
    const editCharacter = (character) => {
      console.log('编辑角色:', character)
    }
    
    const deleteCharacter = (character) => {
      if (confirm(`确定要删除角色"${character.name}"吗？`)) {
        characters.value = characters.value.filter(c => c.id !== character.id)
      }
    }
    
    return {
      characters,
      showAddDialog,
      newCharacter,
      addCharacter,
      generateMoreReferences,
      editCharacter,
      deleteCharacter
    }
  }
}
</script>

<style scoped>
.character-consistency-manager {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

h2 {
  font-size: 28px;
  margin-bottom: 24px;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.character-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
}

.character-preview {
  height: 300px;
  background: #f0f0f0;
}

.character-preview img {
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

.character-info {
  padding: 20px;
}

.character-info h4 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.character-desc {
  color: #666;
  margin-bottom: 12px;
  font-size: 14px;
}

.character-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.reference-images h5 {
  font-size: 14px;
  margin: 16px 0 12px 0;
}

.images-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.images-grid img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
}

.character-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
}

.btn-sm.danger {
  color: #f44336;
  border-color: #f44336;
}

.dialog-overlay {
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

.dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
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

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding: 24px;
  border-top: 1px solid #e0e0e0;
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
</style>
