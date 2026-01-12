<template>
  <div class="content-list">
    <!-- 页面头部 - 现代化设计 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">内容管理</h1>
          <p class="page-subtitle">管理生成的文案、分镜、图片和视频</p>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-wrapper">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="form-control">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索内容..."
            class="input input-bordered input-sm w-64"
            @keyup.enter="handleFilter"
          />
        </div>
        <select
          v-model="filterType"
          class="select select-bordered select-sm w-40"
          @change="handleFilter"
        >
          <option value="">全部类型</option>
          <option value="rewrite">文案改写</option>
          <option value="storyboard">分镜</option>
          <option value="image">图片</option>
          <option value="video">视频</option>
        </select>
        <select
          v-model="filterProject"
          class="select select-bordered select-sm w-48"
          @change="handleFilter"
        >
          <option value="">全部项目</option>
          <option v-for="project in projects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </div>

      <!-- 内容网格 -->
      <loading-container :loading="loading">
        <!-- 空状态 -->
        <div v-if="contents.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125"/>
            </svg>
          </div>
          <h3 class="empty-title">暂无内容</h3>
          <p class="empty-description">创建项目并执行生成任务后，内容将显示在这里</p>
          <router-link to="/projects" class="empty-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            <span>创建项目</span>
          </router-link>
        </div>

        <!-- 内容卡片网格 -->
        <div v-else class="content-grid">
          <div v-for="content in contents" :key="content.id" class="content-card">
            <div class="card-image">
              <img v-if="content.thumbnail" :src="content.thumbnail" :alt="content.title" />
              <div v-else class="placeholder-image">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <div class="card-badge">
                <span class="badge" :class="getTypeBadgeClass(content.type)">
                  {{ getTypeLabel(content.type) }}
                </span>
              </div>
            </div>
            <div class="card-body">
              <h3 class="card-title">{{ content.title }}</h3>
              <p class="card-description">{{ content.description }}</p>
              <div class="card-meta">
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75"/>
                  </svg>
                  {{ content.project_name }}
                </span>
                <span class="meta-item">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                  {{ formatDate(content.created_at) }}
                </span>
              </div>
              <div class="card-actions">
                <button class="btn-action" @click="handleView(content)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  查看
                </button>
                <button class="btn-action" @click="handleDownload(content)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  下载
                </button>
                <button class="btn-action btn-danger" @click="handleDelete(content)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="contents.length > 0" class="pagination">
          <div class="join">
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage === 1"
              @click="handlePageChange(currentPage - 1)"
            >
              «
            </button>
            <button class="join-item btn btn-sm">第 {{ currentPage }} 页</button>
            <button
              class="join-item btn btn-sm"
              :disabled="currentPage * pageSize >= total"
              @click="handlePageChange(currentPage + 1)"
            >
              »
            </button>
          </div>
        </div>
      </loading-container>
    </div>
  </div>
</template>

<script>
import LoadingContainer from '@/components/common/LoadingContainer.vue'
import { formatDate } from '@/utils/helpers'

export default {
  name: 'ContentList',
  components: {
    LoadingContainer
  },
  data() {
    return {
      searchKeyword: '',
      filterType: '',
      filterProject: '',
      currentPage: 1,
      pageSize: 12,
      total: 0,
      loading: false,
      contents: [],
      projects: []
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    formatDate,
    
    async loadData() {
      this.loading = true
      try {
        // TODO: 调用实际的API
        // const response = await contentAPI.getContents({
        //   page: this.currentPage,
        //   pageSize: this.pageSize,
        //   search: this.searchKeyword,
        //   type: this.filterType,
        //   project: this.filterProject
        // })
        // this.contents = response.data.results
        // this.total = response.data.count
        
        // 模拟数据
        this.contents = []
        this.total = 0
      } catch (error) {
        console.error('加载内容失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    handleFilter() {
      this.currentPage = 1
      this.loadData()
    },
    
    handlePageChange(page) {
      this.currentPage = page
      this.loadData()
    },
    
    handleView(content) {
      // TODO: 查看内容详情
      console.log('查看内容:', content)
    },
    
    handleDownload(content) {
      // TODO: 下载内容
      console.log('下载内容:', content)
    },
    
    handleDelete(content) {
      if (confirm(`确定要删除"${content.title}"吗？`)) {
        // TODO: 删除内容
        console.log('删除内容:', content)
      }
    },
    
    getTypeLabel(type) {
      const labels = {
        rewrite: '文案',
        storyboard: '分镜',
        image: '图片',
        video: '视频'
      }
      return labels[type] || type
    },
    
    getTypeBadgeClass(type) {
      const classes = {
        rewrite: 'badge-primary',
        storyboard: 'badge-secondary',
        image: 'badge-accent',
        video: 'badge-success'
      }
      return classes[type] || 'badge-ghost'
    }
  }
}
</script>

<style scoped>
.content-list {
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

/* 内容区域 */
.content-wrapper {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* 筛选区域 */
.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  width: 120px;
  height: 120px;
  margin: 0 auto 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s ease-in-out infinite;
}

.empty-icon svg {
  width: 60px;
  height: 60px;
  color: white;
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 12px;
}

.empty-description {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 30px;
}

.empty-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.empty-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.empty-button svg {
  width: 20px;
  height: 20px;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
  margin-bottom: 30px;
}

.content-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.content-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-image {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f3f4f6;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
}

.placeholder-image svg {
  width: 60px;
  height: 60px;
  color: #667eea;
  opacity: 0.5;
}

.card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
}

.card-body {
  padding: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.meta-item svg {
  width: 14px;
  height: 14px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 12px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: #e5e7eb;
}

.btn-action svg {
  width: 14px;
  height: 14px;
}

.btn-danger {
  color: #ef4444;
}

.btn-danger:hover {
  background: #fee2e2;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}
</style>
