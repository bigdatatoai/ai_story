<template>
  <div class="workflow-editor-page">
    <div class="container mx-auto px-4 py-6">
      <!-- 错误提示 -->
      <div v-if="error" class="alert alert-error shadow-lg mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <!-- 页面头部 - 现代化设计 -->
      <div class="page-header">
        <div class="header-content">
          <div class="header-left">
            <button @click="goBack" class="back-button">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
            </button>
            <div>
              <h1 class="page-title">工作流编辑器</h1>
              <p v-if="project" class="page-subtitle">{{ project.name }}</p>
            </div>
          </div>
          
          <div class="header-actions">
            <button @click="saveWorkflow" class="action-button save-button" :disabled="saving">
              <svg v-if="!saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
              </svg>
              <span>{{ saving ? '保存中...' : '保存工作流' }}</span>
            </button>
            <button @click="executeWorkflow" class="action-button execute-button" :disabled="executing">
              <svg v-if="!executing" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
                <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>{{ executing ? '执行中...' : '执行工作流' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 工作流编辑器 -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <div v-if="loading" class="flex justify-center items-center py-20">
            <span class="loading loading-spinner loading-lg"></span>
            <span class="ml-3">加载中...</span>
          </div>
          
          <div v-else-if="!project" class="alert alert-error">
            <span>项目加载失败</span>
          </div>
          
          <SimpleWorkflowEditor
            v-else
            :project-id="project.id"
            :initial-workflow="workflowData"
            @workflow-change="handleWorkflowChange"
            @save="handleSaveWorkflow"
          />
        </div>
      </div>

      <!-- 执行进度 -->
      <div v-if="executionProgress" class="card bg-base-100 shadow-xl mt-4">
        <div class="card-body">
          <h3 class="card-title text-lg">执行进度</h3>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <span>状态: {{ executionProgress.status }}</span>
              <span>{{ executionProgress.progress }}%</span>
            </div>
            <progress class="progress progress-primary w-full" :value="executionProgress.progress" max="100"></progress>
            <div v-if="executionProgress.current_node" class="text-sm text-base-content/70">
              当前节点: {{ executionProgress.current_node }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SimpleWorkflowEditor from '@/components/SimpleWorkflowEditor.vue'
import projectsAPI from '@/api/projects'

export default {
  name: 'ProjectWorkflow',
  components: {
    SimpleWorkflowEditor
  },
  data() {
    return {
      project: null,
      workflowData: { nodes: [], edges: [] },
      loading: true,
      saving: false,
      executing: false,
      error: null,
      executionProgress: {
        status: 'idle',
        progress: 0,
        current_node: null
      }
    }
  },
  async mounted() {
    await this.loadProject()
  },
  methods: {
    async loadProject() {
      try {
        this.loading = true
        const projectId = this.$route.params.id
        
        if (!projectId) {
          throw new Error('项目ID不存在')
        }
        
        const response = await projectsAPI.getProject(projectId)
        
        // 处理不同的响应格式
        if (response.success && response.data) {
          this.project = response.data
        } else if (response.data) {
          this.project = response.data
        } else if (response.id) {
          this.project = response
        } else {
          throw new Error('项目数据格式错误')
        }
        
        // 加载工作流数据
        this.workflowData = this.project.workflow || { nodes: [], edges: [] }
        
      } catch (error) {
        console.error('加载项目失败:', error)
        this.error = '项目加载失败: ' + (error.response?.data?.message || error.message || '未知错误')
        // 延迟跳转，让用户看到错误信息
        setTimeout(() => {
          this.$router.push('/projects')
        }, 2000)
      } finally {
        this.loading = false
      }
    },
    
    handleWorkflowChange(workflow) {
      this.workflowData = workflow
    },
    
    handleSaveWorkflow(workflow) {
      this.workflowData = workflow
      this.saveWorkflow()
    },
    
    async saveWorkflow() {
      try {
        this.saving = true
        // TODO: 调用保存工作流 API
        console.log('保存工作流:', this.workflowData)
        alert('工作流保存成功！')
      } catch (error) {
        console.error('保存工作流失败:', error)
        alert('保存失败: ' + (error.message || '未知错误'))
      } finally {
        this.saving = false
      }
    },
    
    async executeWorkflow() {
      try {
        this.executing = true
        this.executionProgress = {
          status: 'running',
          progress: 0,
          current_node: null
        }
        
        // TODO: 调用执行工作流 API
        console.log('执行工作流:', this.workflowData)
        
        // 模拟进度更新
        const interval = setInterval(() => {
          if (this.executionProgress.progress < 100) {
            this.executionProgress.progress += 10
          } else {
            clearInterval(interval)
            this.executionProgress.status = 'completed'
            this.executing = false
          }
        }, 500)
        
      } catch (error) {
        console.error('执行工作流失败:', error)
        alert('执行失败: ' + (error.message || '未知错误'))
        this.executing = false
      }
    },
    
    goBack() {
      const projectId = this.$route.params.id
      if (projectId) {
        this.$router.push(`/projects/${projectId}`)
      } else {
        this.$router.push('/projects')
      }
    }
  }
}
</script>

<style scoped>
.workflow-editor-page {
  min-height: 100vh;
  background: #f7fafc;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 30px 40px;
  margin-bottom: 24px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
}

.back-button {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(-3px);
}

.back-button svg {
  width: 20px;
  height: 20px;
  color: white;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-button svg {
  width: 18px;
  height: 18px;
}

.save-button {
  background: white;
  color: #667eea;
}

.save-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.execute-button {
  background: #10b981;
  color: white;
}

.execute-button:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .page-header {
    padding: 20px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
