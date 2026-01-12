<template>
  <div class="simple-workflow-editor">
    <div class="editor-container">
      <!-- 左侧节点库 -->
      <div class="node-library">
        <h3 class="library-title">节点库 ({{ availableNodes.length }})</h3>
        <div class="node-list">
          <!-- 输入节点 -->
          <div class="category-section">
            <div class="category-title">📥 输入节点</div>
            <div
              v-for="node in getNodesByCategory('input')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- AI生成节点 -->
          <div class="category-section">
            <div class="category-title">🤖 AI生成</div>
            <div
              v-for="node in getNodesByCategory('ai')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- 视频处理节点 -->
          <div class="category-section">
            <div class="category-title">🎬 视频处理</div>
            <div
              v-for="node in getNodesByCategory('video')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- 滤镜效果 -->
          <div class="category-section">
            <div class="category-title">🎨 滤镜效果</div>
            <div
              v-for="node in getNodesByCategory('filter')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- 转场效果 -->
          <div class="category-section">
            <div class="category-title">🔄 转场效果</div>
            <div
              v-for="node in getNodesByCategory('transition')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- 文字动画 -->
          <div class="category-section">
            <div class="category-title">📝 文字动画</div>
            <div
              v-for="node in getNodesByCategory('text')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>

          <!-- 特效 -->
          <div class="category-section">
            <div class="category-title">✨ 特效</div>
            <div
              v-for="node in getNodesByCategory('effect')"
              :key="node.type"
              class="node-item"
              @click="addNode(node)"
            >
              <div class="node-icon" :style="{ backgroundColor: node.color }">
                {{ node.icon }}
              </div>
              <div class="node-info">
                <div class="node-name">{{ node.name }}</div>
                <div class="node-desc">{{ node.description }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧画布 -->
      <div class="canvas-area">
        <div class="canvas-header">
          <h3>工作流画布</h3>
          <div class="canvas-actions">
            <button @click="clearCanvas" class="btn btn-sm btn-ghost">清空</button>
            <button @click="saveWorkflow" class="btn btn-sm btn-primary">保存</button>
          </div>
        </div>
        
        <div class="canvas-content">
          <div v-if="workflowNodes.length === 0" class="empty-state">
            <p>从左侧拖拽或点击节点开始构建工作流</p>
          </div>
          
          <div v-else class="workflow-nodes">
            <div
              v-for="(node, index) in workflowNodes"
              :key="index"
              class="workflow-node-card"
            >
              <div class="node-card-header" :style="{ backgroundColor: node.color }">
                <span>{{ node.name }}</span>
                <button @click="removeNode(index)" class="btn-remove">×</button>
              </div>
              <div class="node-card-body">
                <p class="text-sm">{{ node.description }}</p>
                <div v-if="node.type === 'text_input'" class="mt-2">
                  <textarea
                    v-model="node.config.text"
                    class="textarea textarea-bordered w-full"
                    placeholder="输入文本内容..."
                    rows="3"
                  ></textarea>
                </div>
                <div v-if="node.type === 'image_input' || node.type === 'video_input'" class="mt-2">
                  <input
                    type="file"
                    class="file-input file-input-bordered w-full"
                    @change="handleFileUpload($event, node)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SimpleWorkflowEditor',
  props: {
    projectId: String,
    initialWorkflow: Object
  },
  data() {
    return {
      availableNodes: [
        // 基础输入节点
        {
          type: 'image_input',
          name: '图片输入',
          description: '上传图片或视频文件',
          icon: '📷',
          color: '#3b82f6',
          category: 'input',
          config: {}
        },
        {
          type: 'video_input',
          name: '视频输入',
          description: '上传视频',
          icon: '🎬',
          color: '#8b5cf6',
          category: 'input',
          config: {}
        },
        {
          type: 'text_input',
          name: '文字输入',
          description: '输入文字内容',
          icon: '📝',
          color: '#10b981',
          category: 'input',
          config: { text: '' }
        },
        // AI生成节点
        {
          type: 'ai_image',
          name: 'AI 绘图',
          description: '使用AI生成图片',
          icon: '🎨',
          color: '#f59e0b',
          category: 'ai',
          config: {}
        },
        {
          type: 'ai_video',
          name: 'AI 视频',
          description: '使用AI生成视频',
          icon: '🎥',
          color: '#ef4444',
          category: 'ai',
          config: {}
        },
        {
          type: 'llm_process',
          name: 'LLM 处理',
          description: '使用大语言模型处理文本',
          icon: '🤖',
          color: '#6366f1',
          category: 'ai',
          config: {}
        },
        // 视频处理节点
        {
          type: 'video_merge',
          name: '视频合并',
          description: '合并多个视频片段',
          icon: '🔗',
          color: '#8b5cf6',
          category: 'video',
          config: {}
        },
        {
          type: 'add_subtitles',
          name: '添加字幕',
          description: '为视频添加字幕',
          icon: '💬',
          color: '#06b6d4',
          category: 'video',
          config: {}
        },
        {
          type: 'add_music',
          name: '添加音乐',
          description: '为视频添加背景音乐',
          icon: '🎵',
          color: '#ec4899',
          category: 'video',
          config: {}
        },
        // 视频滤镜节点
        {
          type: 'color_grading',
          name: '色彩调整',
          description: '调整视频色彩和对比度',
          icon: '🎨',
          color: '#f97316',
          category: 'filter',
          config: { brightness: 1.0, contrast: 1.0, saturation: 1.0 }
        },
        {
          type: 'vintage_filter',
          name: '复古滤镜',
          description: '应用复古效果',
          icon: '📷',
          color: '#a855f7',
          category: 'filter',
          config: { intensity: 0.5 }
        },
        {
          type: 'blur_filter',
          name: '模糊效果',
          description: '添加模糊效果',
          icon: '🌫️',
          color: '#64748b',
          category: 'filter',
          config: { radius: 5 }
        },
        {
          type: 'sharpen_filter',
          name: '锐化效果',
          description: '增强画面清晰度',
          icon: '✨',
          color: '#0ea5e9',
          category: 'filter',
          config: { amount: 1.0 }
        },
        // 转场效果节点
        {
          type: 'fade_transition',
          name: '淡入淡出',
          description: '平滑的淡入淡出转场',
          icon: '🌅',
          color: '#f59e0b',
          category: 'transition',
          config: { duration: 1.0 }
        },
        {
          type: 'wipe_transition',
          name: '擦除转场',
          description: '擦除式转场效果',
          icon: '🔄',
          color: '#14b8a6',
          category: 'transition',
          config: { direction: 'left', duration: 0.5 }
        },
        {
          type: 'slide_transition',
          name: '滑动转场',
          description: '滑动式转场效果',
          icon: '➡️',
          color: '#8b5cf6',
          category: 'transition',
          config: { direction: 'right', duration: 0.5 }
        },
        // 文字动画节点
        {
          type: 'fade_in_text',
          name: '文字淡入',
          description: '文字淡入动画',
          icon: '📝',
          color: '#10b981',
          category: 'text',
          config: { duration: 1.0, delay: 0 }
        },
        {
          type: 'typewriter_text',
          name: '打字机效果',
          description: '打字机式文字动画',
          icon: '⌨️',
          color: '#6366f1',
          category: 'text',
          config: { speed: 0.05 }
        },
        {
          type: 'scrolling_text',
          name: '滚动文字',
          description: '滚动字幕效果',
          icon: '📜',
          color: '#ec4899',
          category: 'text',
          config: { speed: 50, direction: 'up' }
        },
        // 特效节点
        {
          type: 'glitch_effect',
          name: '故障艺术',
          description: '数字故障效果',
          icon: '⚡',
          color: '#ef4444',
          category: 'effect',
          config: { intensity: 0.5 }
        },
        {
          type: 'chroma_key',
          name: '绿幕抠图',
          description: '色度键抠图',
          icon: '🎬',
          color: '#22c55e',
          category: 'effect',
          config: { color: '#00ff00', threshold: 0.3 }
        },
        {
          type: 'particle_effect',
          name: '粒子效果',
          description: '粒子特效',
          icon: '✨',
          color: '#f59e0b',
          category: 'effect',
          config: { count: 100, type: 'snow' }
        },
        {
          type: 'zoom_effect',
          name: '缩放效果',
          description: '画面缩放动画',
          icon: '🔍',
          color: '#06b6d4',
          category: 'effect',
          config: { scale: 1.2, duration: 2.0 }
        }
      ],
      workflowNodes: []
    }
  },
  mounted() {
    if (this.initialWorkflow && this.initialWorkflow.nodes) {
      this.workflowNodes = this.initialWorkflow.nodes
    }
  },
  computed: {
    nodeCategories() {
      const categories = {}
      this.availableNodes.forEach(node => {
        if (!categories[node.category]) {
          categories[node.category] = []
        }
        categories[node.category].push(node)
      })
      return categories
    }
  },
  methods: {
    getNodesByCategory(category) {
      return this.availableNodes.filter(node => node.category === category)
    },
    
    addNode(nodeTemplate) {
      const newNode = {
        ...nodeTemplate,
        id: `node_${Date.now()}`,
        config: { ...nodeTemplate.config }
      }
      this.workflowNodes.push(newNode)
      this.emitChange()
    },
    
    removeNode(index) {
      this.workflowNodes.splice(index, 1)
      this.emitChange()
    },
    
    clearCanvas() {
      if (confirm('确定要清空画布吗？')) {
        this.workflowNodes = []
        this.emitChange()
      }
    },
    
    saveWorkflow() {
      this.$emit('save', {
        nodes: this.workflowNodes,
        edges: []
      })
    },
    
    handleFileUpload(event, node) {
      const file = event.target.files[0]
      if (file) {
        node.config.file = file.name
        this.emitChange()
      }
    },
    
    emitChange() {
      this.$emit('workflow-change', {
        nodes: this.workflowNodes,
        edges: []
      })
    }
  }
}
</script>

<style scoped>
.simple-workflow-editor {
  width: 100%;
  height: 600px;
  background: #f3f4f6;
  border-radius: 8px;
  overflow: hidden;
}

.editor-container {
  display: flex;
  height: 100%;
}

.node-library {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
}

.library-title {
  padding: 16px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #e5e7eb;
}

.node-list {
  padding: 12px;
}

.node-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.node-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
  transform: translateX(4px);
}

.node-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.node-info {
  flex: 1;
  min-width: 0;
}

.node-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 2px;
}

.node-desc {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.canvas-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.canvas-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.canvas-actions {
  display: flex;
  gap: 8px;
}

.canvas-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
  font-size: 14px;
}

.workflow-nodes {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.workflow-node-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.node-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  color: white;
  font-weight: 600;
}

.btn-remove {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  transition: background 0.2s;
}

.btn-remove:hover {
  background: rgba(255, 255, 255, 0.3);
}

.node-card-body {
  padding: 16px;
}

.category-section {
  margin-bottom: 16px;
}

.category-title {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  padding: 8px 12px;
  background: #f3f4f6;
  border-radius: 4px;
  margin-bottom: 8px;
  position: sticky;
  top: 0;
  z-index: 10;
}
</style>
