<template>
  <div class="video-production-dashboard">
    <div class="dashboard-header">
      <h1>🎬 AI视频生产控制台</h1>
      <div class="header-actions">
        <button @click="showCreateDialog = true" class="btn btn-primary">
          + 新建项目
        </button>
      </div>
    </div>

    <!-- 生产类型选择 -->
    <div class="production-types">
      <button
        v-for="type in productionTypes"
        :key="type.value"
        @click="activeType = type.value"
        :class="{ active: activeType === type.value }"
        class="type-btn"
      >
        <span class="type-icon">{{ type.icon }}</span>
        <span class="type-name">{{ type.name }}</span>
      </button>
    </div>

    <!-- 项目列表 -->
    <div class="projects-section">
      <div class="section-header">
        <h2>生产项目</h2>
        <div class="filters">
          <select v-model="filterStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="pending">等待中</option>
            <option value="processing">生产中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </div>
      </div>

      <div class="projects-grid">
        <div
          v-for="project in filteredProjects"
          :key="project.id"
          class="project-card"
          @click="viewProject(project)"
        >
          <div class="card-header">
            <h3>{{ project.title }}</h3>
            <span class="status-badge" :class="project.status">
              {{ getStatusText(project.status) }}
            </span>
          </div>

          <div class="card-body">
            <div class="project-info">
              <span class="info-item">
                <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
                {{ project.episode_count }}集
              </span>
              <span class="info-item">
                <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                </svg>
                {{ project.total_duration }}秒
              </span>
            </div>

            <!-- 进度条 -->
            <div v-if="project.status === 'processing'" class="progress-section">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: project.progress + '%' }"></div>
              </div>
              <span class="progress-text">{{ project.progress }}%</span>
            </div>

            <!-- 缩略图 -->
            <div v-if="project.thumbnail_url" class="thumbnail">
              <img :src="project.thumbnail_url" alt="缩略图">
            </div>
          </div>

          <div class="card-footer">
            <span class="created-time">{{ formatDate(project.created_at) }}</span>
            <div class="card-actions">
              <button @click.stop="editProject(project)" class="action-btn" title="编辑">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>
              </button>
              <button @click.stop="downloadProject(project)" class="action-btn" title="下载">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2z"/>
                </svg>
              </button>
              <button @click.stop="deleteProject(project)" class="action-btn delete" title="删除">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建项目对话框 -->
    <div v-if="showCreateDialog" class="dialog-overlay" @click.self="showCreateDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h2>创建新项目</h2>
          <button @click="showCreateDialog = false" class="btn-close">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label>项目类型</label>
            <select v-model="newProject.type" class="form-select">
              <option value="short_drama">AI短剧</option>
              <option value="anime">AI动漫</option>
              <option value="comic_drama">AI漫剧</option>
            </select>
          </div>

          <div class="form-group">
            <label>项目主题</label>
            <input v-model="newProject.theme" type="text" class="form-input" placeholder="例如：都市爱情故事">
          </div>

          <div class="form-group">
            <label>集数</label>
            <input v-model.number="newProject.episode_count" type="number" min="1" max="100" class="form-input">
          </div>

          <div class="form-group">
            <label>每集时长（秒）</label>
            <input v-model.number="newProject.duration_per_episode" type="number" min="30" max="300" class="form-input">
          </div>

          <div class="form-group">
            <label>视觉风格</label>
            <select v-model="newProject.visual_style" class="form-select">
              <option value="realistic">写实</option>
              <option value="anime">动漫</option>
              <option value="cartoon">卡通</option>
              <option value="comic">漫画</option>
            </select>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="showCreateDialog = false" class="btn btn-secondary">取消</button>
          <button @click="createProject" class="btn btn-primary" :disabled="!canCreate">
            开始生产
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import videoAPI from '@/api/video'

export default {
  name: 'VideoProductionDashboard',
  
  setup() {
    const activeType = ref('all')
    const filterStatus = ref('')
    const projects = ref([])
    const showCreateDialog = ref(false)
    
    const productionTypes = [
      { value: 'all', name: '全部', icon: '📺' },
      { value: 'short_drama', name: 'AI短剧', icon: '🎬' },
      { value: 'anime', name: 'AI动漫', icon: '🎨' },
      { value: 'comic_drama', name: 'AI漫剧', icon: '📱' },
    ]
    
    const newProject = ref({
      type: 'short_drama',
      theme: '',
      episode_count: 3,
      duration_per_episode: 60,
      visual_style: 'realistic'
    })
    
    const filteredProjects = computed(() => {
      let filtered = projects.value
      
      if (activeType.value !== 'all') {
        filtered = filtered.filter(p => p.type === activeType.value)
      }
      
      if (filterStatus.value) {
        filtered = filtered.filter(p => p.status === filterStatus.value)
      }
      
      return filtered
    })
    
    const canCreate = computed(() => {
      return newProject.value.theme.length > 0
    })
    
    const loadProjects = async () => {
      try {
        const response = await videoAPI.getProjects()
        if (response.success) {
          projects.value = response.data
        }
      } catch (error) {
        console.error('加载项目失败:', error)
      }
    }
    
    const createProject = async () => {
      try {
        const response = await videoAPI.createDramaProject(newProject.value)
        
        if (response.success) {
          projects.value.unshift(response.data)
          showCreateDialog.value = false
          newProject.value = {
            type: 'short_drama',
            theme: '',
            episode_count: 3,
            duration_per_episode: 60,
            visual_style: 'realistic'
          }
        }
      } catch (error) {
        console.error('创建项目失败:', error)
        alert('创建失败，请重试')
      }
    }
    
    const viewProject = (project) => {
      window.location.href = `/video/project/${project.id}`
    }
    
    const editProject = (project) => {
      console.log('编辑项目:', project)
    }
    
    const downloadProject = (project) => {
      if (project.video_url) {
        window.open(project.video_url, '_blank')
      }
    }
    
    const deleteProject = async (project) => {
      if (confirm('确定要删除这个项目吗？')) {
        try {
          await videoAPI.deleteProject(project.id)
          projects.value = projects.value.filter(p => p.id !== project.id)
        } catch (error) {
          console.error('删除失败:', error)
        }
      }
    }
    
    const getStatusText = (status) => {
      const statusMap = {
        'pending': '等待中',
        'processing': '生产中',
        'completed': '已完成',
        'failed': '失败'
      }
      return statusMap[status] || status
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    onMounted(() => {
      loadProjects()
    })
    
    return {
      activeType,
      filterStatus,
      projects,
      showCreateDialog,
      productionTypes,
      newProject,
      filteredProjects,
      canCreate,
      createProject,
      viewProject,
      editProject,
      downloadProject,
      deleteProject,
      getStatusText,
      formatDate
    }
  }
}
</script>

<style scoped>
.video-production-dashboard {
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: 32px;
  color: #333;
  margin: 0;
}

.production-types {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
}

.type-btn {
  flex: 1;
  padding: 16px;
  border: 2px solid #e0e0e0;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.type-btn:hover {
  border-color: #667eea;
  transform: translateY(-2px);
}

.type-btn.active {
  border-color: #667eea;
  background: #f0f4ff;
}

.type-icon {
  font-size: 32px;
}

.type-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.project-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.processing {
  background: #e3f2fd;
  color: #1976d2;
}

.status-badge.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.failed {
  background: #ffebee;
  color: #c62828;
}

.project-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #666;
}

.info-item .icon {
  width: 16px;
  height: 16px;
}

.progress-section {
  margin: 12px 0;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #999;
}

.thumbnail {
  margin: 12px 0;
  border-radius: 8px;
  overflow: hidden;
}

.thumbnail img {
  width: 100%;
  height: 180px;
  object-fit: cover;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.created-time {
  font-size: 12px;
  color: #999;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn svg {
  width: 18px;
  height: 18px;
  color: #666;
}

.action-btn:hover {
  background: #667eea;
}

.action-btn:hover svg {
  color: white;
}

.action-btn.delete:hover {
  background: #f44336;
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

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
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
  color: #333;
}

.form-input,
.form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
}
</style>
