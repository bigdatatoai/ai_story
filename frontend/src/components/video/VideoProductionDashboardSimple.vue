<template>
  <div class="video-dashboard-simple">
    <h1>🎬 AI视频生产控制台</h1>
    
    <div class="dashboard-stats">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">总项目数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.processing }}</div>
        <div class="stat-label">生产中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.completed }}</div>
        <div class="stat-label">已完成</div>
      </div>
    </div>

    <div class="create-section">
      <h2>创建新项目</h2>
      <div class="project-types">
        <div class="type-card" @click="createProject('short_drama')">
          <div class="type-icon">🎬</div>
          <div class="type-name">AI短剧</div>
          <div class="type-desc">自动生成短视频剧</div>
        </div>
        <div class="type-card" @click="createProject('anime')">
          <div class="type-icon">🎨</div>
          <div class="type-name">AI动漫</div>
          <div class="type-desc">生成动漫风格视频</div>
        </div>
        <div class="type-card" @click="createProject('comic_drama')">
          <div class="type-icon">📱</div>
          <div class="type-name">AI漫剧</div>
          <div class="type-desc">漫画+视频混合</div>
        </div>
      </div>
    </div>

    <div v-if="isLoading && projects.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div class="projects-list">
      <h2>我的项目</h2>
      <div v-if="!isLoading && projects.length === 0" class="empty-state">
        <p>还没有项目，点击上方卡片创建第一个项目</p>
      </div>
      <div v-else class="projects-grid">
        <div v-for="project in projects" :key="project.id" class="project-card">
          <h3>{{ project.title }}</h3>
          <p>{{ project.type }}</p>
          <span class="project-status" :class="project.status">
            {{ project.status === 'processing' ? '生产中' : project.status === 'completed' ? '已完成' : '等待中' }}
          </span>
        </div>
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
import videoAPI from '@/api/video'

export default {
  name: 'VideoProductionDashboardSimple',
  
  data() {
    return {
      projects: [],
      stats: {
        total: 0,
        processing: 0,
        completed: 0
      },
      isLoading: false,
      errorMessage: '',
      successMessage: ''
    }
  },
  
  mounted() {
    this.loadProjects()
  },
  
  methods: {
    async loadProjects() {
      this.isLoading = true
      try {
        const response = await videoAPI.getProjects()
        if (response.success) {
          this.projects = response.data.results || response.data || []
          this.updateStats()
        }
      } catch (error) {
        console.error('加载项目失败:', error)
        this.errorMessage = '加载项目列表失败，请刷新重试'
        setTimeout(() => { this.errorMessage = '' }, 3000)
      } finally {
        this.isLoading = false
      }
    },
    
    async createProject(type) {
      const typeNames = {
        'short_drama': 'AI短剧',
        'anime': 'AI动漫',
        'comic_drama': 'AI漫剧'
      }
      
      const theme = prompt(`请输入${typeNames[type]}的主题：`, '都市爱情故事')
      if (!theme) return
      
      this.isLoading = true
      
      try {
        const response = await videoAPI.createDramaProject({
          type: type,
          theme: theme,
          episode_count: 3,
          duration_per_episode: 60,
          visual_style: type === 'anime' ? 'anime' : 'realistic'
        })
        
        if (response.success) {
          this.projects.unshift(response.data)
          this.updateStats()
          this.successMessage = `${typeNames[type]}项目创建成功！`
          setTimeout(() => { this.successMessage = '' }, 3000)
        }
      } catch (error) {
        console.error('创建项目失败:', error)
        this.errorMessage = error.response?.data?.error || '创建项目失败，请重试'
        setTimeout(() => { this.errorMessage = '' }, 5000)
      } finally {
        this.isLoading = false
      }
    },
    
    updateStats() {
      this.stats.total = this.projects.length
      this.stats.processing = this.projects.filter(p => p.status === 'processing').length
      this.stats.completed = this.projects.filter(p => p.status === 'completed').length
    }
  }
}
</script>

<style scoped>
.video-dashboard-simple {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  font-size: 28px;
  margin-bottom: 30px;
}

h2 {
  font-size: 20px;
  margin-bottom: 20px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.create-section {
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 40px;
}

.project-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.type-card {
  padding: 30px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.type-card:hover {
  border-color: #667eea;
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.type-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.type-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.type-desc {
  font-size: 14px;
  color: #666;
}

.projects-list {
  background: white;
  padding: 30px;
  border-radius: 12px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.project-card {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.project-card h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.project-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.project-status {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.project-status.processing {
  background: #e3f2fd;
  color: #1976d2;
}

.project-status.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.project-status.pending {
  background: #fff3e0;
  color: #f57c00;
}

.loading-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  margin-bottom: 40px;
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
