<template>
  <div class="pipeline-flow">
    <div class="pipeline-header">
      <h3 class="pipeline-title">工作流进度</h3>
      <div class="pipeline-status">
        <span class="status-badge" :class="overallStatusClass">
          {{ overallStatusText }}
        </span>
      </div>
    </div>

    <div class="stages-container">
      <div
        v-for="(stage, index) in stages"
        :key="stage.stage_type"
        class="stage-item"
        :class="getStageClass(stage)"
      >
        <!-- 连接线 -->
        <div v-if="index > 0" class="connector" :class="getConnectorClass(stages[index - 1])"></div>

        <!-- 阶段卡片 -->
        <div class="stage-card">
          <!-- 图标 -->
          <div class="stage-icon">
            <svg v-if="stage.status === 'completed'" class="icon icon-success" viewBox="0 0 24 24">
              <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
            <svg v-else-if="stage.status === 'failed'" class="icon icon-error" viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
            <div v-else-if="stage.status === 'processing'" class="spinner-small"></div>
            <svg v-else class="icon icon-pending" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
          </div>

          <!-- 内容 -->
          <div class="stage-content">
            <div class="stage-name">{{ getStageDisplayName(stage.stage_type) }}</div>
            <div class="stage-status-text">{{ getStageStatusText(stage) }}</div>
            
            <!-- 进度条 -->
            <div v-if="stage.status === 'processing' && stage.progress !== undefined" class="progress-bar">
              <div class="progress-fill" :style="{ width: stage.progress + '%' }"></div>
            </div>

            <!-- 时间信息 -->
            <div v-if="stage.started_at" class="stage-time">
              <span v-if="stage.completed_at">
                耗时: {{ formatDuration(stage.started_at, stage.completed_at) }}
              </span>
              <span v-else-if="stage.status === 'processing'">
                已运行: {{ formatDuration(stage.started_at, new Date()) }}
              </span>
            </div>

            <!-- 错误信息 -->
            <div v-if="stage.error_message" class="error-message">
              {{ stage.error_message }}
            </div>

            <!-- 操作按钮 -->
            <div v-if="stage.status === 'failed'" class="stage-actions">
              <button @click="$emit('retry-stage', stage.stage_type)" class="btn-retry">
                重试
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineFlow',
  props: {
    stages: {
      type: Array,
      required: true,
      default: () => []
    },
    projectStatus: {
      type: String,
      default: 'draft'
    }
  },
  computed: {
    overallStatusClass() {
      const status = this.projectStatus
      return {
        'status-draft': status === 'draft',
        'status-processing': status === 'processing',
        'status-completed': status === 'completed',
        'status-failed': status === 'failed',
        'status-paused': status === 'paused'
      }
    },
    overallStatusText() {
      const statusMap = {
        'draft': '草稿',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败',
        'paused': '已暂停'
      }
      return statusMap[this.projectStatus] || this.projectStatus
    }
  },
  methods: {
    getStageClass(stage) {
      return {
        'stage-pending': stage.status === 'pending',
        'stage-processing': stage.status === 'processing',
        'stage-completed': stage.status === 'completed',
        'stage-failed': stage.status === 'failed'
      }
    },
    getConnectorClass(prevStage) {
      return {
        'connector-completed': prevStage.status === 'completed',
        'connector-failed': prevStage.status === 'failed'
      }
    },
    getStageDisplayName(stageType) {
      const nameMap = {
        'rewrite': '文案改写',
        'storyboard': '分镜生成',
        'image_generation': '文生图',
        'camera_movement': '运镜生成',
        'video_generation': '图生视频'
      }
      return nameMap[stageType] || stageType
    },
    getStageStatusText(stage) {
      const statusMap = {
        'pending': '等待中',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '失败'
      }
      let text = statusMap[stage.status] || stage.status
      
      if (stage.status === 'processing' && stage.message) {
        text = stage.message
      }
      
      return text
    },
    formatDuration(startTime, endTime) {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diff = Math.floor((end - start) / 1000) // 秒
      
      if (diff < 60) {
        return `${diff}秒`
      } else if (diff < 3600) {
        const mins = Math.floor(diff / 60)
        const secs = diff % 60
        return `${mins}分${secs}秒`
      } else {
        const hours = Math.floor(diff / 3600)
        const mins = Math.floor((diff % 3600) / 60)
        return `${hours}小时${mins}分`
      }
    }
  }
}
</script>

<style scoped>
.pipeline-flow {
  background: #fff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.pipeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.pipeline-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
}

.status-draft {
  background: #e5e7eb;
  color: #6b7280;
}

.status-processing {
  background: #dbeafe;
  color: #1e40af;
}

.status-completed {
  background: #d1fae5;
  color: #065f46;
}

.status-failed {
  background: #fee2e2;
  color: #991b1b;
}

.status-paused {
  background: #fef3c7;
  color: #92400e;
}

.stages-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stage-item {
  position: relative;
}

.connector {
  position: absolute;
  left: 20px;
  top: -16px;
  width: 2px;
  height: 16px;
  background: #e5e7eb;
}

.connector-completed {
  background: #10b981;
}

.connector-failed {
  background: #ef4444;
}

.stage-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  transition: all 0.3s;
}

.stage-pending .stage-card {
  border-color: #e5e7eb;
  background: #f9fafb;
}

.stage-processing .stage-card {
  border-color: #3b82f6;
  background: #eff6ff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.stage-completed .stage-card {
  border-color: #10b981;
  background: #f0fdf4;
}

.stage-failed .stage-card {
  border-color: #ef4444;
  background: #fef2f2;
}

.stage-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.stage-pending .stage-icon {
  background: #e5e7eb;
  color: #6b7280;
}

.stage-processing .stage-icon {
  background: #dbeafe;
  color: #1e40af;
}

.stage-completed .stage-icon {
  background: #d1fae5;
  color: #065f46;
}

.stage-failed .stage-icon {
  background: #fee2e2;
  color: #991b1b;
}

.icon {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

.spinner-small {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(59, 130, 246, 0.3);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.stage-content {
  flex: 1;
  min-width: 0;
}

.stage-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.stage-status-text {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.progress-bar {
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 3px;
  transition: width 0.3s;
}

.stage-time {
  font-size: 12px;
  color: #9ca3af;
}

.error-message {
  margin-top: 8px;
  padding: 8px 12px;
  background: #fee2e2;
  border-left: 3px solid #ef4444;
  border-radius: 4px;
  font-size: 13px;
  color: #991b1b;
}

.stage-actions {
  margin-top: 12px;
}

.btn-retry {
  padding: 6px 16px;
  background: #3b82f6;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-retry:hover {
  background: #2563eb;
}
</style>
