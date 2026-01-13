<template>
  <div class="task-dashboard">
    <div class="dashboard-header">
      <h2>我的任务</h2>
      <div class="header-actions">
        <button class="btn-icon" @click="refreshTasks" :disabled="isRefreshing">
          <span :class="{ 'spin': isRefreshing }">🔄</span>
        </button>
        <button class="btn-clear" @click="clearCompleted">
          清理已完成
        </button>
      </div>
    </div>

    <!-- 筛选标签 -->
    <div class="task-filters">
      <button
        v-for="filter in filters"
        :key="filter.key"
        class="filter-btn"
        :class="{ active: currentFilter === filter.key }"
        @click="currentFilter = filter.key"
      >
        {{ filter.label }}
        <span class="badge">{{ getTaskCount(filter.key) }}</span>
      </button>
    </div>

    <!-- 任务列表 -->
    <div class="task-list">
      <div v-if="filteredTasks.length === 0" class="empty-state">
        <div class="empty-icon">📝</div>
        <p>{{ emptyMessage }}</p>
      </div>

      <transition-group name="task-list" tag="div">
        <div
          v-for="task in filteredTasks"
          :key="task.id"
          class="task-card"
          :class="`status-${task.status}`"
        >
          <!-- 任务头部 -->
          <div class="task-header">
            <div class="task-info">
              <h3 class="task-title">{{ getTaskTitle(task) }}</h3>
              <p class="task-time">{{ formatTime(task.createdAt) }}</p>
            </div>
            <div class="task-status">
              <span class="status-badge" :class="`status-${task.status}`">
                {{ getStatusLabel(task.status) }}
              </span>
            </div>
          </div>

          <!-- 进度条 -->
          <div v-if="task.status === 'running'" class="task-progress">
            <div class="progress-info">
              <span class="progress-message">{{ getProgressMessage(task.id) }}</span>
              <span class="progress-percent">{{ getProgressPercent(task.id) }}%</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${getProgressPercent(task.id)}%` }"
              ></div>
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="task.status === 'failed'" class="task-error">
            <div class="error-message">
              <span class="error-icon">⚠️</span>
              <div class="error-content">
                <p class="error-text">{{ getErrorMessage(task.id) }}</p>
                <p v-if="getErrorSuggestion(task.id)" class="error-suggestion">
                  💡 {{ getErrorSuggestion(task.id) }}
                </p>
              </div>
            </div>
          </div>

          <!-- 任务操作 -->
          <div class="task-actions">
            <button
              v-if="task.status === 'completed'"
              class="btn-action btn-view"
              @click="viewResult(task)"
            >
              查看结果
            </button>
            
            <button
              v-if="task.status === 'failed' && canRetry(task.id)"
              class="btn-action btn-retry"
              @click="retryTask(task.id)"
            >
              重试
            </button>
            
            <button
              v-if="task.status === 'running'"
              class="btn-action btn-cancel"
              @click="cancelTask(task.id)"
            >
              取消
            </button>
            
            <button
              v-if="['completed', 'failed', 'cancelled'].includes(task.status)"
              class="btn-action btn-delete"
              @click="deleteTask(task.id)"
            >
              删除
            </button>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

export default {
  name: 'TaskDashboard',
  data() {
    return {
      currentFilter: 'all',
      isRefreshing: false,
      filters: [
        { key: 'all', label: '全部' },
        { key: 'running', label: '进行中' },
        { key: 'completed', label: '已完成' },
        { key: 'failed', label: '失败' },
      ],
    };
  },
  computed: {
    ...mapGetters('tasks', [
      'tasksByStatus',
      'runningTasks',
      'completedTasks',
      'failedTasks',
      'taskProgress',
      'taskError',
    ]),
    
    allTasks() {
      return this.$store.state.tasks.tasks || [];
    },
    
    filteredTasks() {
      if (this.currentFilter === 'all') {
        return this.allTasks;
      }
      return this.tasksByStatus(this.currentFilter);
    },
    
    emptyMessage() {
      const messages = {
        all: '暂无任务',
        running: '暂无进行中的任务',
        completed: '暂无已完成的任务',
        failed: '暂无失败的任务',
      };
      return messages[this.currentFilter] || '暂无任务';
    },
  },
  mounted() {
    this.$store.dispatch('tasks/restoreTasks');
  },
  methods: {
    ...mapActions('tasks', [
      'retryTask',
      'cancelTask',
      'deleteTask',
      'clearCompletedTasks',
    ]),
    
    getTaskCount(filterKey) {
      if (filterKey === 'all') {
        return this.allTasks.length;
      }
      return this.tasksByStatus(filterKey).length;
    },
    
    getTaskTitle(task) {
      const titles = {
        story_generation: '故事视频生成',
        image_generation: '图片生成',
        video_synthesis: '视频合成',
      };
      return titles[task.type] || '任务';
    },
    
    getStatusLabel(status) {
      const labels = {
        pending: '待处理',
        running: '生成中',
        paused: '已暂停',
        completed: '已完成',
        failed: '失败',
        cancelled: '已取消',
      };
      return labels[status] || status;
    },
    
    getProgressMessage(taskId) {
      const progress = this.taskProgress(taskId);
      return progress.message || '处理中...';
    },
    
    getProgressPercent(taskId) {
      const progress = this.taskProgress(taskId);
      return progress.progress || 0;
    },
    
    getErrorMessage(taskId) {
      const error = this.taskError(taskId);
      return error?.message || error?.friendlyMessage || '任务失败';
    },
    
    getErrorSuggestion(taskId) {
      const error = this.taskError(taskId);
      return error?.suggestion;
    },
    
    canRetry(taskId) {
      const error = this.taskError(taskId);
      return error?.canRetry !== false;
    },
    
    formatTime(timestamp) {
      return dayjs(timestamp).fromNow();
    },
    
    async refreshTasks() {
      this.isRefreshing = true;
      try {
        await new Promise((resolve) => setTimeout(resolve, 500));
      } finally {
        this.isRefreshing = false;
      }
    },
    
    async clearCompleted() {
      const confirmed = await this.$confirm(
        '确定要清理所有已完成的任务吗？',
        '确认清理'
      );
      
      if (confirmed) {
        this.clearCompletedTasks();
        this.$message.success('已清理完成的任务');
      }
    },
    
    viewResult(task) {
      this.$router.push({
        name: 'TaskResult',
        params: { id: task.id },
      });
    },
  },
};
</script>

<style scoped>
.task-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #f3f4f6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.btn-icon:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-icon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spin {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.btn-clear {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-clear:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.task-filters {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.filter-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-btn:hover {
  color: #1f2937;
}

.filter-btn.active {
  color: #3b82f6;
  font-weight: 600;
}

.filter-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #3b82f6;
}

.badge {
  padding: 0.125rem 0.5rem;
  border-radius: 1rem;
  background: #e5e7eb;
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 600;
}

.filter-btn.active .badge {
  background: #dbeafe;
  color: #3b82f6;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.task-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  transition: all 0.3s;
}

.task-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.task-card.status-running {
  border-left: 4px solid #3b82f6;
}

.task-card.status-completed {
  border-left: 4px solid #10b981;
}

.task-card.status-failed {
  border-left: 4px solid #ef4444;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.task-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.task-time {
  font-size: 0.875rem;
  color: #9ca3af;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.status-running {
  background: #dbeafe;
  color: #3b82f6;
}

.status-badge.status-completed {
  background: #d1fae5;
  color: #10b981;
}

.status-badge.status-failed {
  background: #fee2e2;
  color: #ef4444;
}

.status-badge.status-pending {
  background: #f3f4f6;
  color: #6b7280;
}

.task-progress {
  margin-bottom: 1rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.progress-message {
  color: #6b7280;
}

.progress-percent {
  color: #3b82f6;
  font-weight: 600;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 1rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.3s ease;
  border-radius: 1rem;
}

.task-error {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border-radius: 0.5rem;
}

.error-message {
  display: flex;
  gap: 0.75rem;
}

.error-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.error-text {
  color: #dc2626;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.error-suggestion {
  color: #6b7280;
  font-size: 0.875rem;
}

.task-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-action {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-view {
  background: #3b82f6;
  color: white;
}

.btn-view:hover {
  background: #2563eb;
}

.btn-retry {
  background: #f59e0b;
  color: white;
}

.btn-retry:hover {
  background: #d97706;
}

.btn-cancel {
  background: #6b7280;
  color: white;
}

.btn-cancel:hover {
  background: #4b5563;
}

.btn-delete {
  background: #f3f4f6;
  color: #6b7280;
}

.btn-delete:hover {
  background: #fee2e2;
  color: #dc2626;
}

.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.3s ease;
}

.task-list-enter {
  opacity: 0;
  transform: translateY(-10px);
}

.task-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
