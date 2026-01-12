<template>
  <div class="modern-project-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">我的项目</h1>
          <p class="page-subtitle">管理您的AI视频创作项目</p>
        </div>
        <button class="create-button" @click="handleCreate">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>创建项目</span>
        </button>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-section">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="filters.search"
          type="text"
          placeholder="搜索项目名称..."
          class="search-input"
          @keyup.enter="handleFilter"
        />
      </div>
      
      <select
        v-model="filters.status"
        class="status-filter"
        @change="handleFilter"
      >
        <option value="">全部状态</option>
        <option value="draft">草稿</option>
        <option value="processing">处理中</option>
        <option value="completed">已完成</option>
        <option value="failed">失败</option>
        <option value="paused">已暂停</option>
      </select>
    </div>

    <!-- 项目卡片网格 -->
    <loading-container :loading="loading">
      <div v-if="projects.length === 0" class="empty-state">
        <div class="empty-illustration">
          <div class="illustration-circle circle-1"></div>
          <div class="illustration-circle circle-2"></div>
          <div class="illustration-circle circle-3"></div>
          <div class="empty-icon-wrapper">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
        </div>
        <h3 class="empty-title">开始您的创作之旅</h3>
        <p class="empty-description">创建您的第一个AI视频项目<br/>从文本到视频，一键生成</p>
        <button class="btn-create-first" @click="handleCreate">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          <span>创建第一个项目</span>
        </button>
      </div>

      <div v-else class="projects-grid">
        <div
          v-for="project in projects"
          :key="project.id"
          class="project-card"
          @click="handleView(project.id)"
        >
          <!-- 卡片头部 -->
          <div class="card-header">
            <div class="card-title-section">
              <h3 class="card-title">{{ project.name }}</h3>
              <status-badge :status="project.status" type="project" />
            </div>
            <div class="card-actions" @click.stop>
              <button class="action-btn" @click="handleView(project.id)" title="查看详情">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
              <button class="action-btn delete-btn" @click="handleDelete(project)" title="删除">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 卡片内容 -->
          <div class="card-body">
            <p class="card-description">{{ project.description || '暂无描述' }}</p>
            
            <div class="card-meta">
              <div class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                <span>{{ formatDate(project.created_at) }}</span>
              </div>
              <div class="meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
                <span>{{ formatDate(project.updated_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 卡片底部渐变装饰 -->
          <div class="card-gradient"></div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="projects.length > 0" class="pagination">
        <button
          class="pagination-btn"
          :disabled="pagination.page === 1"
          @click="handlePageChange(pagination.page - 1)"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
          上一页
        </button>
        
        <div class="pagination-info">
          第 <span class="current-page">{{ pagination.page }}</span> 页 / 共 {{ totalPages }} 页
        </div>
        
        <button
          class="pagination-btn"
          :disabled="pagination.page >= totalPages"
          @click="handlePageChange(pagination.page + 1)"
        >
          下一页
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </loading-container>

    <!-- 删除确认模态框 -->
    <dialog ref="deleteModal" class="modal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">确认删除</h3>
        <p class="py-4">
          确定要删除项目 <span class="font-semibold">"{{ deletingProject?.name }}"</span> 吗?
        </p>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="closeDeleteModal">取消</button>
          <button class="btn btn-error" @click="confirmDelete">删除</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="closeDeleteModal">close</button>
      </form>
    </dialog>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import StatusBadge from '@/components/common/StatusBadge.vue'
import LoadingContainer from '@/components/common/LoadingContainer.vue'
import { formatDate } from '@/utils/helpers'

export default {
  name: 'ProjectList',
  components: {
    StatusBadge,
    LoadingContainer
  },
  data() {
    return {
      loading: false,
      projects: [],
      filters: {
        search: '',
        status: ''
      },
      pagination: {
        page: 1,
        pageSize: 12
      },
      totalPages: 1,
      deletingProject: null
    }
  },
  created() {
    this.fetchProjects()
  },
  methods: {
    ...mapActions('projects', ['getProjects', 'deleteProject']),
    formatDate,

    async fetchProjects() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          pageSize: this.pagination.pageSize,
          ...this.filters
        }
        const response = await this.getProjects(params)
        this.projects = response.results || []
        this.totalPages = Math.ceil((response.count || 0) / this.pagination.pageSize)
      } catch (error) {
        console.error('获取项目列表失败:', error)
      } finally {
        this.loading = false
      }
    },

    handleFilter() {
      this.pagination.page = 1
      this.fetchProjects()
    },

    handlePageChange(page) {
      this.pagination.page = page
      this.fetchProjects()
    },

    handleCreate() {
      this.$router.push('/projects/create')
    },

    handleView(projectId) {
      this.$router.push(`/projects/${projectId}`)
    },

    handleDelete(project) {
      this.deletingProject = project
      this.$refs.deleteModal.showModal()
    },

    closeDeleteModal() {
      this.$refs.deleteModal.close()
      this.deletingProject = null
    },

    async confirmDelete() {
      if (!this.deletingProject) return

      try {
        await this.deleteProject(this.deletingProject.id)
        this.closeDeleteModal()
        this.fetchProjects()
      } catch (error) {
        console.error('删除项目失败:', error)
        alert('删除失败: ' + (error.message || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
.modern-project-list {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
  border-radius: 50%;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  z-index: 1;
}

.header-left {
  color: white;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.create-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.create-button svg {
  width: 20px;
  height: 20px;
}

/* 筛选区域 */
.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 30px;
}

.search-box {
  flex: 1;
  position: relative;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #a0aec0;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  transition: all 0.3s ease;
  outline: none;
}

.search-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.status-filter {
  padding: 14px 20px;
  font-size: 15px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  outline: none;
}

.status-filter:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #718096;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 30px;
}

.btn-create-first {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.btn-create-first:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-create-first svg {
  width: 20px;
  height: 20px;
}

/* 项目卡片网格 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.project-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
}

.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(102, 126, 234, 0.15);
  border-color: #667eea;
}

.project-card:hover .card-gradient {
  opacity: 1;
}

.card-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-title-section {
  flex: 1;
  min-width: 0;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-left: 12px;
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.action-btn:hover {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.delete-btn:hover {
  background: #fc8181;
  border-color: #fc8181;
}

.card-body {
  margin-bottom: 16px;
}

.card-description {
  font-size: 14px;
  color: #718096;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #a0aec0;
}

.meta-item svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 40px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  border-color: #667eea;
  color: #667eea;
  background: #f7fafc;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 16px;
  height: 16px;
}

.pagination-info {
  font-size: 14px;
  color: #718096;
}

.current-page {
  font-weight: 700;
  color: #667eea;
  font-size: 16px;
}

/* 空状态美化 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  padding: 60px 20px;
}

.empty-illustration {
  position: relative;
  width: 200px;
  height: 200px;
  margin-bottom: 40px;
}

.illustration-circle {
  position: absolute;
  border-radius: 50%;
  animation: float 3s ease-in-out infinite;
}

.circle-1 {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  opacity: 0.2;
  top: 0;
  left: 0;
  animation-delay: 0s;
}

.circle-2 {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  opacity: 0.2;
  bottom: 20px;
  right: 0;
  animation-delay: 0.5s;
}

.circle-3 {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  opacity: 0.2;
  top: 50px;
  right: 30px;
  animation-delay: 1s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.empty-icon-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.05); }
}

.empty-icon {
  width: 60px;
  height: 60px;
  color: white;
}

.empty-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 12px;
}

.empty-description {
  font-size: 16px;
  color: #718096;
  text-align: center;
  line-height: 1.8;
  margin-bottom: 32px;
}

.btn-create-first {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
}

.btn-create-first:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
}

.btn-create-first svg {
  width: 22px;
  height: 22px;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-header {
    padding: 30px 20px;
  }

  .header-content {
    flex-direction: column;
    gap: 20px;
    align-items: flex-start;
  }

  .page-title {
    font-size: 28px;
  }

  .filter-section {
    flex-direction: column;
  }

  .search-box {
    max-width: 100%;
  }

  .projects-grid {
    grid-template-columns: 1fr;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>
