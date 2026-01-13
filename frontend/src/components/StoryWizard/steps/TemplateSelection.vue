<template>
  <div class="template-selection">
    <h3 class="step-title">选择故事模板</h3>
    <p class="step-description">选择一个适合的模板开始创作</p>

    <!-- 筛选器 -->
    <div class="filters">
      <div class="filter-group">
        <label>类型</label>
        <select v-model="filters.type" @change="filterTemplates">
          <option value="">全部</option>
          <option value="children">儿童故事</option>
          <option value="science">科普故事</option>
          <option value="education">教育故事</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>时长</label>
        <select v-model="filters.duration" @change="filterTemplates">
          <option value="">全部</option>
          <option value="30">30秒</option>
          <option value="60">60秒</option>
          <option value="120">2分钟</option>
        </select>
      </div>
    </div>

    <!-- 模板卡片 -->
    <div class="template-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
        :class="{ selected: selectedTemplate?.id === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-preview">
          <img :src="template.thumbnail" :alt="template.name" />
          <div v-if="template.featured" class="featured-badge">推荐</div>
        </div>
        
        <div class="template-info">
          <h4 class="template-name">{{ template.name }}</h4>
          <p class="template-desc">{{ template.description }}</p>
          
          <div class="template-meta">
            <span class="meta-item">
              <span class="icon">🎬</span>
              {{ template.duration }}秒
            </span>
            <span class="meta-item">
              <span class="icon">📊</span>
              {{ template.scenes }}个场景
            </span>
          </div>
        </div>
        
        <div v-if="selectedTemplate?.id === template.id" class="selected-indicator">
          ✓
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredTemplates.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <p>没有找到符合条件的模板</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="errors.template" class="error-message">
      {{ errors.template }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'TemplateSelection',
  props: {
    data: {
      type: Object,
      required: true
    },
    errors: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      templates: [],
      filteredTemplates: [],
      selectedTemplate: null,
      filters: {
        type: '',
        duration: ''
      },
      loading: false
    };
  },
  mounted() {
    this.loadTemplates();
    if (this.data.template) {
      this.selectedTemplate = this.data.template;
    }
  },
  methods: {
    async loadTemplates() {
      this.loading = true;
      try {
        const response = await this.$store.dispatch('content/fetchTemplates');
        this.templates = response || [];
        this.filteredTemplates = this.templates;
      } catch (error) {
        this.$message.error('加载模板失败');
      } finally {
        this.loading = false;
      }
    },
    
    selectTemplate(template) {
      this.selectedTemplate = template;
      this.$emit('update', { template });
    },
    
    filterTemplates() {
      this.filteredTemplates = this.templates.filter(template => {
        if (this.filters.type && template.type !== this.filters.type) {
          return false;
        }
        if (this.filters.duration && template.duration !== parseInt(this.filters.duration)) {
          return false;
        }
        return true;
      });
    }
  }
};
</script>

<style scoped>
.template-selection {
  padding: 2rem 0;
}

.step-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.step-description {
  color: #6b7280;
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.template-card.selected {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.template-preview {
  position: relative;
  width: 100%;
  height: 160px;
  background: #f3f4f6;
}

.template-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.featured-badge {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #f59e0b;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 1rem;
}

.template-info {
  padding: 1rem;
}

.template-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.template-desc {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.template-meta {
  display: flex;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.meta-item .icon {
  font-size: 1rem;
}

.selected-indicator {
  position: absolute;
  top: 0.5rem;
  left: 0.5rem;
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #9ca3af;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-message {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
  border-radius: 0.5rem;
}
</style>
