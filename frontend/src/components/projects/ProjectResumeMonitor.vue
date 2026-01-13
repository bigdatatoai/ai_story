<template>
  <div v-if="isMonitoring" class="project-resume-monitor">
    <div class="alert alert-info">
      <div class="flex items-center gap-3">
        <span class="loading loading-spinner loading-md"></span>
        <div class="flex-1">
          <div class="font-bold">项目恢复中</div>
          <div class="text-sm">
            正在从 {{ currentStageName }} 阶段继续执行...
          </div>
        </div>
        <button class="btn btn-sm btn-ghost" @click="stopMonitoring">
          取消监控
        </button>
      </div>
    </div>

    <!-- 任务进度详情 -->
    <div v-if="taskStatus" class="mt-2 text-sm">
      <div class="flex justify-between items-center">
        <span>任务状态: {{ getTaskStatusText(taskStatus.state) }}</span>
        <span v-if="elapsedTime" class="text-base-content/60">
          已用时: {{ formatElapsedTime(elapsedTime) }}
        </span>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="taskStatus.state === 'FAILURE' && taskStatus.error" class="alert alert-error mt-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ taskStatus.error }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import projectsAPI from '@/api/projects';

export default {
  name: 'ProjectResumeMonitor',
  props: {
    projectId: {
      type: String,
      required: true,
    },
    taskId: {
      type: String,
      default: null,
    },
    currentStage: {
      type: String,
      default: null,
    },
    autoStart: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      isMonitoring: false,
      taskStatus: null,
      pollingInterval: null,
      startTime: null,
      elapsedTime: 0,
      elapsedTimer: null,
    };
  },
  computed: {
    currentStageName() {
      const stageNames = {
        rewrite: '文案改写',
        storyboard: '分镜生成',
        image_generation: '文生图',
        camera_movement: '运镜生成',
        video_generation: '图生视频',
      };
      return stageNames[this.currentStage] || this.currentStage;
    },
  },
  watch: {
    taskId: {
      immediate: true,
      handler(newTaskId) {
        if (newTaskId && this.autoStart) {
          this.startMonitoring();
        }
      },
    },
  },
  beforeDestroy() {
    this.stopMonitoring();
  },
  methods: {
    /**
     * 开始监控任务状态
     */
    startMonitoring() {
      if (!this.taskId) {
        console.warn('[ProjectResumeMonitor] 无 task_id，无法监控');
        return;
      }

      this.isMonitoring = true;
      this.startTime = Date.now();
      this.elapsedTime = 0;

      // 启动计时器
      this.elapsedTimer = setInterval(() => {
        this.elapsedTime = Math.floor((Date.now() - this.startTime) / 1000);
      }, 1000);

      // 立即查询一次
      this.checkTaskStatus();

      // 每3秒轮询一次
      this.pollingInterval = setInterval(() => {
        this.checkTaskStatus();
      }, 3000);
    },

    /**
     * 停止监控
     */
    stopMonitoring() {
      this.isMonitoring = false;
      
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }

      if (this.elapsedTimer) {
        clearInterval(this.elapsedTimer);
        this.elapsedTimer = null;
      }
    },

    /**
     * 检查任务状态
     */
    async checkTaskStatus() {
      try {
        const response = await projectsAPI.getTaskStatus(this.projectId, this.taskId);
        this.taskStatus = response;

        // 根据任务状态决定是否继续监控
        if (response.state === 'SUCCESS') {
          this.handleTaskSuccess(response);
        } else if (response.state === 'FAILURE') {
          this.handleTaskFailure(response);
        } else if (response.state === 'RETRY') {
          this.$message?.info('任务正在重试...');
        }
        // PENDING 和 STARTED 状态继续轮询
      } catch (error) {
        console.error('[ProjectResumeMonitor] 查询任务状态失败:', error);
        
        // 如果是网络错误，继续重试
        if (!error.response) {
          return;
        }

        // 其他错误停止监控
        this.stopMonitoring();
        this.$message?.error('查询任务状态失败');
      }
    },

    /**
     * 处理任务成功
     */
    handleTaskSuccess(response) {
      this.stopMonitoring();
      this.$message?.success(`${this.currentStageName} 阶段执行完成！`);
      this.$emit('success', {
        taskId: this.taskId,
        stage: this.currentStage,
        result: response.result,
      });
    },

    /**
     * 处理任务失败
     */
    handleTaskFailure(response) {
      this.stopMonitoring();
      const errorMsg = response.error || '任务执行失败';
      this.$message?.error(`${this.currentStageName} 阶段执行失败: ${errorMsg}`);
      this.$emit('failure', {
        taskId: this.taskId,
        stage: this.currentStage,
        error: errorMsg,
      });
    },

    /**
     * 获取任务状态文本
     */
    getTaskStatusText(state) {
      const statusMap = {
        PENDING: '等待执行',
        STARTED: '正在执行',
        SUCCESS: '执行成功',
        FAILURE: '执行失败',
        RETRY: '正在重试',
      };
      return statusMap[state] || state;
    },

    /**
     * 格式化已用时间
     */
    formatElapsedTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return mins > 0 ? `${mins}分${secs}秒` : `${secs}秒`;
    },
  },
};
</script>

<style scoped>
.project-resume-monitor {
  margin-bottom: 1rem;
}
</style>
