<template>
  <div class="story-library">
    <div class="library-header">
      <h1>我的故事库</h1>
      <button @click="$router.push('/story/create')" class="btn btn-primary">
        + 创作新故事
      </button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="搜索故事标题、内容..."
          class="search-input"
        >
        <svg class="search-icon" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
      </div>

      <div class="filters">
        <select v-model="filterGenre" @change="applyFilters" class="filter-select">
          <option value="">所有题材</option>
          <option value="fairy_tale">童话故事</option>
          <option value="adventure">冒险故事</option>
          <option value="sci_fi">科幻故事</option>
          <option value="fable">寓言故事</option>
          <option value="friendship">友谊故事</option>
          <option value="mystery">悬疑推理</option>
        </select>

        <select v-model="filterAgeGroup" @change="applyFilters" class="filter-select">
          <option value="">所有年龄段</option>
          <option value="preschool">学龄前</option>
          <option value="elementary">小学生</option>
          <option value="teenager">青少年</option>
          <option value="adult">成人</option>
        </select>

        <select v-model="sortBy" @change="applyFilters" class="filter-select">
          <option value="-created_at">最新创建</option>
          <option value="-updated_at">最近更新</option>
          <option value="-quality_score">质量评分</option>
          <option value="-view_count">浏览次数</option>
        </select>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_stories }}</span>
        <span class="stat-label">总故事数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.total_words }}</span>
        <span class="stat-label">总字数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.favorites }}</span>
        <span class="stat-label">收藏数</span>
      </div>
    </div>

    <!-- 故事列表 -->
    <div class="stories-grid">
      <div
        v-for="story in stories"
        :key="story.id"
        class="story-card"
        @click="viewStory(story)"
      >
        <div class="card-header">
          <h3 class="story-title">{{ story.title }}</h3>
          <div class="story-meta">
            <span class="meta-tag">{{ getGenreLabel(story.genre) }}</span>
            <span class="meta-tag">{{ story.actual_word_count }}字</span>
          </div>
        </div>

        <div class="card-body">
          <p class="story-excerpt">{{ getExcerpt(story.content) }}</p>
        </div>

        <div class="card-footer">
          <div class="story-stats">
            <span class="stat">
              <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/>
              </svg>
              {{ story.view_count }}
            </span>
            <span class="stat">
              <svg class="stat-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
              </svg>
              {{ story.like_count }}
            </span>
            <span v-if="story.quality_score" class="quality-badge" :class="getQualityClass(story.quality_score)">
              {{ story.quality_score.toFixed(0) }}分
            </span>
          </div>

          <div class="story-actions">
            <button @click.stop="editStory(story)" class="action-btn" title="编辑">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
              </svg>
            </button>
            <button @click.stop="shareStory(story)" class="action-btn" title="分享">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
              </svg>
            </button>
            <button @click.stop="deleteStory(story)" class="action-btn delete" title="删除">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="card-date">{{ formatDate(story.created_at) }}</div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore" class="load-more">
      <button @click="loadMore" class="btn btn-secondary" :disabled="isLoading">
        {{ isLoading ? '加载中...' : '加载更多' }}
      </button>
    </div>

    <!-- 空状态 -->
    <div v-if="stories.length === 0 && !isLoading" class="empty-state">
      <svg class="empty-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
      </svg>
      <p>还没有故事，开始创作第一个故事吧！</p>
      <button @click="$router.push('/story/create')" class="btn btn-primary">
        创作故事
      </button>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'StoryLibrary',
  
  setup() {
    const stories = ref([])
    const searchQuery = ref('')
    const filterGenre = ref('')
    const filterAgeGroup = ref('')
    const sortBy = ref('-created_at')
    const isLoading = ref(false)
    const hasMore = ref(true)
    const page = ref(1)
    
    const stats = reactive({
      total_stories: 0,
      total_words: 0,
      favorites: 0
    })
    
    const loadStories = async (reset = false) => {
      if (reset) {
        page.value = 1
        stories.value = []
      }
      
      isLoading.value = true
      
      try {
        const response = await storyAPI.getStories({
          page: page.value,
          search: searchQuery.value,
          genre: filterGenre.value,
          age_group: filterAgeGroup.value,
          ordering: sortBy.value
        })
        
        if (response.success) {
          if (reset) {
            stories.value = response.data.results
          } else {
            stories.value.push(...response.data.results)
          }
          
          hasMore.value = response.data.next !== null
        }
      } catch (error) {
        console.error('加载故事失败:', error)
      } finally {
        isLoading.value = false
      }
    }
    
    const loadStats = async () => {
      try {
        const response = await storyAPI.getStatistics()
        if (response.success) {
          Object.assign(stats, response.data)
        }
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    }
    
    const handleSearch = () => {
      loadStories(true)
    }
    
    const applyFilters = () => {
      loadStories(true)
    }
    
    const loadMore = () => {
      page.value++
      loadStories()
    }
    
    const viewStory = (story) => {
      // 跳转到故事详情页
      window.location.href = `/story/${story.id}`
    }
    
    const editStory = (story) => {
      window.location.href = `/story/${story.id}/edit`
    }
    
    const shareStory = (story) => {
      // 触发分享对话框
      console.log('分享故事:', story)
    }
    
    const deleteStory = async (story) => {
      if (confirm('确定要删除这个故事吗？')) {
        try {
          await storyAPI.deleteStory(story.id)
          stories.value = stories.value.filter(s => s.id !== story.id)
          stats.total_stories--
        } catch (error) {
          console.error('删除失败:', error)
        }
      }
    }
    
    const getExcerpt = (content) => {
      return content.substring(0, 150) + '...'
    }
    
    const getGenreLabel = (genre) => {
      const labels = {
        'fairy_tale': '童话',
        'adventure': '冒险',
        'sci_fi': '科幻',
        'fable': '寓言',
        'friendship': '友谊',
        'mystery': '悬疑'
      }
      return labels[genre] || genre
    }
    
    const getQualityClass = (score) => {
      if (score >= 80) return 'excellent'
      if (score >= 60) return 'good'
      return 'fair'
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    onMounted(() => {
      loadStories()
      loadStats()
    })
    
    return {
      stories,
      searchQuery,
      filterGenre,
      filterAgeGroup,
      sortBy,
      isLoading,
      hasMore,
      stats,
      handleSearch,
      applyFilters,
      loadMore,
      viewStory,
      editStory,
      shareStory,
      deleteStory,
      getExcerpt,
      getGenreLabel,
      getQualityClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.story-library {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.library-header h1 {
  font-size: 32px;
  color: #333;
  margin: 0;
}

.search-filters {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 16px;
  margin-bottom: 24px;
}

.search-box {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #999;
}

.filters {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.filter-select {
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
}

.stats-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.story-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.story-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.story-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #333;
}

.story-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.meta-tag {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.story-excerpt {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.story-stats {
  display: flex;
  gap: 16px;
  align-items: center;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #666;
}

.stat-icon {
  width: 16px;
  height: 16px;
}

.quality-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.quality-badge.excellent {
  background: #e8f5e9;
  color: #2e7d32;
}

.quality-badge.good {
  background: #fff3e0;
  color: #f57c00;
}

.quality-badge.fair {
  background: #fce4ec;
  color: #c2185b;
}

.story-actions {
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

.card-date {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 12px;
  color: #999;
}

.load-more {
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  color: #ccc;
  margin-bottom: 16px;
}

.empty-state p {
  color: #999;
  margin-bottom: 24px;
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
</style>
