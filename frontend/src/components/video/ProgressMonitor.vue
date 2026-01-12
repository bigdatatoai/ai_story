<template>
  <div class="progress-monitor">
    <div class="monitor-header">
      <h3>🔄 实时进度监控</h3>
      <span :class="['connection-status', connectionStatus]">
        {{ connectionStatus === 'connected' ? '● 已连接' : '○ 未连接' }}
      </span>
    </div>

    <div class="tasks-list">
      <div v-for="task in activeTasks" :key="task.id" class="task-item">
        <div class="task-info">
          <h4>{{ task.title }}</h4>
          <span class="task-type">{{ getTaskType(task.type) }}</span>
        </div>

        <div class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
          </div>
          <div class="progress-details">
            <span>{{ task.progress }}%</span>
            <span class="current-step">{{ task.current_step }}</span>
          </div>
        </div>

        <div v-if="task.eta" class="eta">
          预计剩余时间: {{ formatTime(task.eta) }}
        </div>
      </div>
    </div>

    <div v-if="activeTasks.length === 0" class="empty-state">
      <p>暂无进行中的任务</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ProgressMonitor',
  
  setup() {
    const ws = ref(null)
    const connectionStatus = ref('disconnected')
    const activeTasks = ref([])
    
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/ws/progress/`
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onopen = () => {
        connectionStatus.value = 'connected'
        console.log('进度监控WebSocket已连接')
      }
      
      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleProgressUpdate(data)
      }
      
      ws.value.onerror = (error) => {
        console.error('WebSocket错误:', error)
        connectionStatus.value = 'error'
      }
      
      ws.value.onclose = () => {
        connectionStatus.value = 'disconnected'
        console.log('WebSocket连接关闭')
        // 3秒后重连
        setTimeout(connectWebSocket, 3000)
      }
    }
    
    const handleProgressUpdate = (data) => {
      const { task_id, progress, current_step, eta, status } = data
      
      const existingTask = activeTasks.value.find(t => t.id === task_id)
      
      if (status === 'completed' || status === 'failed') {
        // 移除已完成或失败的任务
        activeTasks.value = activeTasks.value.filter(t => t.id !== task_id)
      } else if (existingTask) {
        // 更新现有任务
        existingTask.progress = progress
        existingTask.current_step = current_step
        existingTask.eta = eta
      } else {
        // 添加新任务
        activeTasks.value.push({
          id: task_id,
          title: data.title || '未命名任务',
          type: data.type || 'unknown',
          progress: progress,
          current_step: current_step,
          eta: eta
        })
      }
    }
    
    const getTaskType = (type) => {
      const types = {
        'text_to_video': '文本转视频',
        'image_to_video': '图片转视频',
        'drama_production': '短剧生产',
        'anime_generation': '动漫生成'
      }
      return types[type] || type
    }
    
    const formatTime = (seconds) => {
      if (!seconds) return '--'
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}分${secs}秒`
    }
    
    onMounted(() => {
      connectWebSocket()
    })
    
    onUnmounted(() => {
      if (ws.value) {
        ws.value.close()
      }
    })
    
    return {
      connectionStatus,
      activeTasks,
      getTaskType,
      formatTime
    }
  }
}
</script>

<style scoped>
.progress-monitor {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.monitor-header h3 {
  margin: 0;
  font-size: 18px;
}

.connection-status {
  font-size: 14px;
  font-weight: 500;
}

.connection-status.connected {
  color: #4CAF50;
}

.connection-status.disconnected {
  color: #999;
}

.tasks-list {
  display: grid;
  gap: 16px;
}

.task-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.task-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.task-info h4 {
  margin: 0;
  font-size: 16px;
}

.task-type {
  padding: 4px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
}

.progress-section {
  margin-bottom: 8px;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.current-step {
  font-style: italic;
}

.eta {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
