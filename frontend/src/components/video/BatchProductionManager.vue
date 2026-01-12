<template>
  <div class="batch-production-manager">
    <div class="manager-header">
      <h2>📦 批量生产管理</h2>
      <button @click="showBatchDialog = true" class="btn btn-primary">
        + 新建批量任务
      </button>
    </div>

    <!-- 批量任务列表 -->
    <div class="batch-tasks">
      <div v-for="task in batchTasks" :key="task.id" class="task-card">
        <div class="task-header">
          <h3>{{ task.name }}</h3>
          <span class="task-status" :class="task.status">
            {{ getStatusText(task.status) }}
          </span>
        </div>

        <div class="task-info">
          <div class="info-row">
            <span class="label">总数量：</span>
            <span class="value">{{ task.total_count }}个</span>
          </div>
          <div class="info-row">
            <span class="label">已完成：</span>
            <span class="value">{{ task.completed_count }}/{{ task.total_count }}</span>
          </div>
          <div class="info-row">
            <span class="label">失败：</span>
            <span class="value error">{{ task.failed_count }}</span>
          </div>
        </div>

        <!-- 进度条 -->
        <div class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: getProgress(task) + '%' }"></div>
          </div>
          <span class="progress-text">{{ getProgress(task) }}%</span>
        </div>

        <!-- 子任务列表 -->
        <div v-if="task.expanded" class="subtasks">
          <div v-for="subtask in task.items" :key="subtask.id" class="subtask-item">
            <span class="subtask-name">{{ subtask.title }}</span>
            <span class="subtask-status" :class="subtask.status">
              {{ getStatusText(subtask.status) }}
            </span>
          </div>
        </div>

        <div class="task-actions">
          <button @click="toggleExpand(task)" class="btn-action">
            {{ task.expanded ? '收起' : '展开' }}
          </button>
          <button v-if="task.status === 'processing'" @click="pauseTask(task)" class="btn-action">
            暂停
          </button>
          <button v-if="task.status === 'paused'" @click="resumeTask(task)" class="btn-action">
            继续
          </button>
          <button @click="deleteTask(task)" class="btn-action danger">
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 批量创建对话框 -->
    <div v-if="showBatchDialog" class="dialog-overlay" @click.self="showBatchDialog = false">
      <div class="dialog">
        <div class="dialog-header">
          <h2>创建批量生产任务</h2>
          <button @click="showBatchDialog = false" class="btn-close">×</button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label>任务名称</label>
            <input v-model="batchForm.name" type="text" class="form-input" placeholder="例如：爱情短剧系列">
          </div>

          <div class="form-group">
            <label>生产类型</label>
            <select v-model="batchForm.type" class="form-select">
              <option value="short_drama">AI短剧</option>
              <option value="anime">AI动漫</option>
              <option value="comic_drama">AI漫剧</option>
            </select>
          </div>

          <div class="form-group">
            <label>主题列表（每行一个）</label>
            <textarea v-model="batchForm.themes" rows="6" class="form-textarea" placeholder="都市爱情故事&#10;校园青春故事&#10;职场励志故事"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>每个项目集数</label>
              <input v-model.number="batchForm.episode_count" type="number" min="1" class="form-input">
            </div>
            <div class="form-group">
              <label>每集时长（秒）</label>
              <input v-model.number="batchForm.duration" type="number" min="30" class="form-input">
            </div>
          </div>

          <div class="form-group">
            <label>视觉风格</label>
            <select v-model="batchForm.style" class="form-select">
              <option value="realistic">写实</option>
              <option value="anime">动漫</option>
              <option value="cartoon">卡通</option>
            </select>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="showBatchDialog = false" class="btn btn-secondary">取消</button>
          <button @click="createBatchTask" class="btn btn-primary" :disabled="!canCreateBatch">
            开始批量生产
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import videoAPI from '@/api/video'

export default {
  name: 'BatchProductionManager',
  
  setup() {
    const batchTasks = ref([])
    const showBatchDialog = ref(false)
    
    const batchForm = ref({
      name: '',
      type: 'short_drama',
      themes: '',
      episode_count: 3,
      duration: 60,
      style: 'realistic'
    })
    
    const canCreateBatch = computed(() => {
      return batchForm.value.name && batchForm.value.themes.trim().length > 0
    })
    
    const getProgress = (task) => {
      if (task.total_count === 0) return 0
      return Math.round((task.completed_count / task.total_count) * 100)
    }
    
    const getStatusText = (status) => {
      const map = {
        'pending': '等待中',
        'processing': '生产中',
        'paused': '已暂停',
        'completed': '已完成',
        'failed': '失败'
      }
      return map[status] || status
    }
    
    const toggleExpand = (task) => {
      task.expanded = !task.expanded
    }
    
    const createBatchTask = async () => {
      const themes = batchForm.value.themes.split('\n').filter(t => t.trim())
      
      try {
        const response = await videoAPI.batchProduce({
          name: batchForm.value.name,
          type: batchForm.value.type,
          themes: themes,
          episode_count: batchForm.value.episode_count,
          duration_per_episode: batchForm.value.duration,
          visual_style: batchForm.value.style
        })
        
        if (response.success) {
          batchTasks.value.unshift(response.data)
          showBatchDialog.value = false
          batchForm.value = {
            name: '',
            type: 'short_drama',
            themes: '',
            episode_count: 3,
            duration: 60,
            style: 'realistic'
          }
        }
      } catch (error) {
        console.error('创建批量任务失败:', error)
        alert('创建失败，请重试')
      }
    }
    
    const pauseTask = (task) => {
      task.status = 'paused'
    }
    
    const resumeTask = (task) => {
      task.status = 'processing'
    }
    
    const deleteTask = (task) => {
      if (confirm('确定要删除这个批量任务吗？')) {
        batchTasks.value = batchTasks.value.filter(t => t.id !== task.id)
      }
    }
    
    return {
      batchTasks,
      showBatchDialog,
      batchForm,
      canCreateBatch,
      getProgress,
      getStatusText,
      toggleExpand,
      createBatchTask,
      pauseTask,
      resumeTask,
      deleteTask
    }
  }
}
</script>

<style scoped>
.batch-production-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.batch-tasks {
  display: grid;
  gap: 20px;
}

.task-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.task-header h3 {
  margin: 0;
  font-size: 18px;
}

.task-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.task-status.processing {
  background: #e3f2fd;
  color: #1976d2;
}

.task-status.completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.task-status.paused {
  background: #fff3e0;
  color: #f57c00;
}

.task-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: #999;
}

.value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.value.error {
  color: #f44336;
}

.progress-section {
  margin-bottom: 16px;
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

.subtasks {
  margin: 16px 0;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.subtask-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}

.subtask-item:last-child {
  border-bottom: none;
}

.subtask-status {
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 11px;
}

.task-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-action {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-action.danger {
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

.form-textarea {
  resize: vertical;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
