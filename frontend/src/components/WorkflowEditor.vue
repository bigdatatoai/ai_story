<template>
  <div class="workflow-editor">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button @click="saveWorkflow" class="btn btn-primary">
          <svg class="icon" viewBox="0 0 24 24"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
          保存
        </button>
        <button @click="executeWorkflow" class="btn btn-success" :disabled="isExecuting">
          <svg class="icon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          {{ isExecuting ? '执行中...' : '执行工作流' }}
        </button>
        <button @click="clearWorkflow" class="btn btn-secondary">
          <svg class="icon" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
          清空
        </button>
      </div>
      <div class="toolbar-right">
        <span class="zoom-info">{{ Math.round(zoom * 100) }}%</span>
        <button @click="zoomIn" class="btn-icon">+</button>
        <button @click="zoomOut" class="btn-icon">-</button>
        <button @click="fitView" class="btn-icon">
          <svg class="icon" viewBox="0 0 24 24"><path d="M15 3l2.3 2.3-2.89 2.87 1.42 1.42L18.7 6.7 21 9V3zM3 9l2.3-2.3 2.87 2.89 1.42-1.42L6.7 5.3 9 3H3zm6 12l-2.3-2.3 2.89-2.87-1.42-1.42L5.3 17.3 3 15v6zm12-6l-2.3 2.3-2.87-2.89-1.42 1.42 2.89 2.87L15 21h6z"/></svg>
        </button>
      </div>
    </div>

    <!-- 主编辑区域 -->
    <div class="editor-container">
      <!-- 左侧节点库 -->
      <div class="node-library" :class="{ collapsed: libraryCollapsed }">
        <div class="library-header">
          <h3>节点库</h3>
          <button @click="libraryCollapsed = !libraryCollapsed" class="btn-collapse">
            {{ libraryCollapsed ? '>' : '<' }}
          </button>
        </div>
        
        <div v-if="!libraryCollapsed" class="library-content">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索节点..." 
            class="search-input"
          />
          
          <div v-for="category in filteredNodeCategories" :key="category.name" class="node-category">
            <div class="category-header" @click="toggleCategory(category.name)">
              <span>{{ category.label }}</span>
              <span class="toggle-icon">{{ expandedCategories.includes(category.name) ? '▼' : '▶' }}</span>
            </div>
            
            <div v-if="expandedCategories.includes(category.name)" class="category-nodes">
              <div
                v-for="node in category.nodes"
                :key="node.type"
                class="node-item"
                draggable="true"
                @dragstart="onNodeDragStart($event, node)"
              >
                <div class="node-icon" :style="{ background: node.color }">
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
      </div>

      <!-- 画布区域 -->
      <div 
        ref="canvas"
        class="canvas-area"
        @drop="onCanvasDrop"
        @dragover.prevent
        @mousedown="onCanvasMouseDown"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
        @wheel="onCanvasWheel"
      >
        <svg class="canvas-svg" :style="canvasStyle">
          <!-- 网格背景 -->
          <defs>
            <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
              <rect width="20" height="20" fill="none" stroke="#e5e7eb" stroke-width="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          <!-- 连接线 -->
          <g class="edges">
            <path
              v-for="edge in edges"
              :key="edge.id"
              :d="getEdgePath(edge)"
              class="edge"
              :class="{ selected: selectedEdge === edge.id }"
              @click="selectEdge(edge.id)"
            />
          </g>
          
          <!-- 临时连接线 -->
          <path
            v-if="tempEdge"
            :d="tempEdge.path"
            class="edge temp-edge"
          />
        </svg>

        <!-- 节点 -->
        <div
          v-for="node in nodes"
          :key="node.id"
          class="workflow-node"
          :class="{ selected: selectedNode === node.id, executing: executingNode === node.id }"
          :style="getNodeStyle(node)"
          @mousedown.stop="selectNode(node.id)"
        >
          <div class="node-header" :style="{ background: getNodeColor(node.type) }">
            <span class="node-title">{{ node.data.label }}</span>
            <button @click.stop="deleteNode(node.id)" class="btn-delete">×</button>
          </div>
          
          <div class="node-body">
            <!-- 输入端口 -->
            <div class="node-ports input-ports">
              <div
                v-for="port in getNodeInputPorts(node.type)"
                :key="port.name"
                class="port input-port"
                :data-port="port.name"
                @mousedown.stop="startConnection(node.id, port.name, 'input')"
              >
                <div class="port-dot"></div>
                <span class="port-label">{{ port.label }}</span>
              </div>
            </div>
            
            <!-- 节点内容 -->
            <div class="node-content">
              <component
                :is="getNodeComponent(node.type)"
                v-model="node.data.config"
                :node="node"
              />
            </div>
            
            <!-- 输出端口 -->
            <div class="node-ports output-ports">
              <div
                v-for="port in getNodeOutputPorts(node.type)"
                :key="port.name"
                class="port output-port"
                :data-port="port.name"
                @mousedown.stop="startConnection(node.id, port.name, 'output')"
              >
                <span class="port-label">{{ port.label }}</span>
                <div class="port-dot"></div>
              </div>
            </div>
          </div>
          
          <!-- 执行状态 -->
          <div v-if="nodeResults[node.id]" class="node-status">
            <span v-if="nodeResults[node.id].status === 'completed'" class="status-success">✓</span>
            <span v-else-if="nodeResults[node.id].status === 'failed'" class="status-error">✗</span>
            <span v-else class="status-running">⟳</span>
          </div>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <div v-if="selectedNode" class="properties-panel">
        <div class="panel-header">
          <h3>节点属性</h3>
          <button @click="selectedNode = null" class="btn-close">×</button>
        </div>
        <div class="panel-content">
          <div class="property-group">
            <label>节点ID</label>
            <input type="text" :value="selectedNode" disabled />
          </div>
          <div class="property-group">
            <label>节点类型</label>
            <input type="text" :value="getSelectedNodeType()" disabled />
          </div>
          <!-- 动态配置表单 -->
          <component
            :is="getNodeConfigComponent(getSelectedNodeType())"
            v-model="getSelectedNodeConfig()"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WorkflowEditor',
  props: {
    projectId: {
      type: String,
      required: true
    },
    initialWorkflow: {
      type: Object,
      default: () => ({ nodes: [], edges: [] })
    }
  },
  data() {
    return {
      nodes: [],
      edges: [],
      selectedNode: null,
      selectedEdge: null,
      executingNode: null,
      nodeResults: {},
      
      // 画布状态
      zoom: 1,
      panX: 0,
      panY: 0,
      isPanning: false,
      lastMouseX: 0,
      lastMouseY: 0,
      
      // 连接状态
      connectingFrom: null,
      tempEdge: null,
      
      // UI 状态
      libraryCollapsed: false,
      searchQuery: '',
      expandedCategories: ['input', 'ai', 'processing'],
      isExecuting: false,
      
      // 节点定义
      nodeCategories: [
        {
          name: 'input',
          label: '输入',
          nodes: [
            {
              type: 'image_input',
              name: '图片输入',
              description: '上传本地或链接文件',
              icon: '🖼️',
              color: '#3b82f6',
              inputPorts: [],
              outputPorts: [{ name: 'image', label: '图片', type: 'image' }]
            },
            {
              type: 'video_input',
              name: '视频输入',
              description: '上传视频',
              icon: '🎬',
              color: '#8b5cf6',
              inputPorts: [],
              outputPorts: [{ name: 'video', label: '视频', type: 'video' }]
            },
            {
              type: 'text_input',
              name: '文字输入',
              description: '输入文字内容',
              icon: '📝',
              color: '#10b981',
              inputPorts: [],
              outputPorts: [{ name: 'text', label: '文本', type: 'text' }]
            }
          ]
        },
        {
          name: 'ai',
          label: 'AI生成',
          nodes: [
            {
              type: 'ai_image',
              name: 'AI 绘图',
              description: '使用 AI 生成图像',
              icon: '🎨',
              color: '#f59e0b',
              inputPorts: [{ name: 'prompt', label: '提示词', type: 'text' }],
              outputPorts: [{ name: 'image', label: '图片', type: 'image' }]
            },
            {
              type: 'ai_video',
              name: 'AI 视频',
              description: '使用 AI 生成视频',
              icon: '🎥',
              color: '#ef4444',
              inputPorts: [
                { name: 'image', label: '图片', type: 'image' },
                { name: 'prompt', label: '提示词', type: 'text' }
              ],
              outputPorts: [{ name: 'video', label: '视频', type: 'video' }]
            }
          ]
        },
        {
          name: 'processing',
          label: '处理',
          nodes: [
            {
              type: 'add_music',
              name: '添加音乐',
              description: '添加背景音乐',
              icon: '🎵',
              color: '#06b6d4',
              inputPorts: [
                { name: 'video', label: '视频', type: 'video' },
                { name: 'music', label: '音乐', type: 'audio' }
              ],
              outputPorts: [{ name: 'video', label: '视频', type: 'video' }]
            },
            {
              type: 'add_subtitles',
              name: '添加字幕',
              description: '自动生成字幕',
              icon: '💬',
              color: '#ec4899',
              inputPorts: [
                { name: 'video', label: '视频', type: 'video' },
                { name: 'audio', label: '音频', type: 'audio' }
              ],
              outputPorts: [{ name: 'video', label: '视频', type: 'video' }]
            }
          ]
        }
      ]
    }
  },
  computed: {
    canvasStyle() {
      return {
        transform: `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`
      }
    },
    filteredNodeCategories() {
      if (!this.searchQuery) return this.nodeCategories
      
      const query = this.searchQuery.toLowerCase()
      return this.nodeCategories.map(category => ({
        ...category,
        nodes: category.nodes.filter(node => 
          node.name.toLowerCase().includes(query) ||
          node.description.toLowerCase().includes(query)
        )
      })).filter(category => category.nodes.length > 0)
    }
  },
  mounted() {
    if (this.initialWorkflow) {
      this.nodes = this.initialWorkflow.nodes || []
      this.edges = this.initialWorkflow.edges || []
    }
  },
  methods: {
    // 节点拖拽
    onNodeDragStart(event, nodeType) {
      event.dataTransfer.setData('nodeType', JSON.stringify(nodeType))
    },
    
    onCanvasDrop(event) {
      event.preventDefault()
      const nodeType = JSON.parse(event.dataTransfer.getData('nodeType'))
      
      const rect = this.$refs.canvas.getBoundingClientRect()
      const x = (event.clientX - rect.left - this.panX) / this.zoom
      const y = (event.clientY - rect.top - this.panY) / this.zoom
      
      this.addNode(nodeType, x, y)
    },
    
    addNode(nodeType, x, y) {
      const nodeId = `node-${Date.now()}`
      
      this.nodes.push({
        id: nodeId,
        type: nodeType.type,
        position: { x, y },
        data: {
          label: nodeType.name,
          config: {}
        }
      })
    },
    
    deleteNode(nodeId) {
      this.nodes = this.nodes.filter(n => n.id !== nodeId)
      this.edges = this.edges.filter(e => e.source !== nodeId && e.target !== nodeId)
      if (this.selectedNode === nodeId) {
        this.selectedNode = null
      }
    },
    
    selectNode(nodeId) {
      this.selectedNode = nodeId
      this.selectedEdge = null
    },
    
    selectEdge(edgeId) {
      this.selectedEdge = edgeId
      this.selectedNode = null
    },
    
    // 连接管理
    startConnection(nodeId, portName, portType) {
      this.connectingFrom = { nodeId, portName, portType }
    },
    
    onCanvasMouseMove(event) {
      if (this.connectingFrom) {
        const rect = this.$refs.canvas.getBoundingClientRect()
        const x = (event.clientX - rect.left - this.panX) / this.zoom
        const y = (event.clientY - rect.top - this.panY) / this.zoom
        
        const sourceNode = this.nodes.find(n => n.id === this.connectingFrom.nodeId)
        if (sourceNode) {
          const startX = sourceNode.position.x + 150
          const startY = sourceNode.position.y + 50
          
          this.tempEdge = {
            path: `M ${startX} ${startY} L ${x} ${y}`
          }
        }
      } else if (this.isPanning) {
        const dx = event.clientX - this.lastMouseX
        const dy = event.clientY - this.lastMouseY
        
        this.panX += dx
        this.panY += dy
        
        this.lastMouseX = event.clientX
        this.lastMouseY = event.clientY
      }
    },
    
    onCanvasMouseUp(event) {
      if (this.connectingFrom) {
        // 检查是否连接到端口
        const target = event.target.closest('.port')
        if (target) {
          const targetNodeEl = target.closest('.workflow-node')
          const targetNodeId = targetNodeEl?.dataset?.nodeId
          const targetPort = target.dataset.port
          
          if (targetNodeId && targetPort) {
            this.createEdge(
              this.connectingFrom.nodeId,
              targetNodeId,
              this.connectingFrom.portName,
              targetPort
            )
          }
        }
        
        this.connectingFrom = null
        this.tempEdge = null
      }
      
      this.isPanning = false
    },
    
    createEdge(sourceId, targetId, sourcePort, targetPort) {
      const edgeId = `edge-${Date.now()}`
      
      this.edges.push({
        id: edgeId,
        source: sourceId,
        target: targetId,
        sourceHandle: sourcePort,
        targetHandle: targetPort
      })
    },
    
    getEdgePath(edge) {
      const sourceNode = this.nodes.find(n => n.id === edge.source)
      const targetNode = this.nodes.find(n => n.id === edge.target)
      
      if (!sourceNode || !targetNode) return ''
      
      const startX = sourceNode.position.x + 300
      const startY = sourceNode.position.y + 50
      const endX = targetNode.position.x
      const endY = targetNode.position.y + 50
      
      const midX = (startX + endX) / 2
      
      return `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`
    },
    
    // 画布操作
    onCanvasMouseDown(event) {
      if (event.target === this.$refs.canvas || event.target.classList.contains('canvas-svg')) {
        this.isPanning = true
        this.lastMouseX = event.clientX
        this.lastMouseY = event.clientY
        this.selectedNode = null
        this.selectedEdge = null
      }
    },
    
    onCanvasWheel(event) {
      event.preventDefault()
      const delta = event.deltaY > 0 ? 0.9 : 1.1
      this.zoom = Math.max(0.1, Math.min(3, this.zoom * delta))
    },
    
    zoomIn() {
      this.zoom = Math.min(3, this.zoom * 1.2)
    },
    
    zoomOut() {
      this.zoom = Math.max(0.1, this.zoom / 1.2)
    },
    
    fitView() {
      this.zoom = 1
      this.panX = 0
      this.panY = 0
    },
    
    // 工作流操作
    async saveWorkflow() {
      const workflowData = {
        nodes: this.nodes,
        edges: this.edges
      }
      
      try {
        await this.$store.dispatch('project/saveWorkflow', {
          projectId: this.projectId,
          workflowData
        })
        
        this.$message.success('工作流已保存')
      } catch (error) {
        this.$message.error('保存失败: ' + error.message)
      }
    },
    
    async executeWorkflow() {
      this.isExecuting = true
      this.nodeResults = {}
      
      try {
        const response = await this.$store.dispatch('project/executeWorkflow', {
          projectId: this.projectId
        })
        
        // 监听执行进度
        this.subscribeToProgress(response.channel)
        
      } catch (error) {
        this.$message.error('执行失败: ' + error.message)
        this.isExecuting = false
      }
    },
    
    subscribeToProgress(channel) {
      // 使用 WebSocket 或 SSE 监听进度
      const ws = new WebSocket(`ws://localhost:8000/ws/${channel}/`)
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        
        if (data.type === 'node_update') {
          this.executingNode = data.node_id
          this.nodeResults[data.node_id] = {
            status: data.status,
            result: data.result
          }
        } else if (data.type === 'workflow_complete') {
          this.isExecuting = false
          this.executingNode = null
          this.$message.success('工作流执行完成')
          ws.close()
        }
      }
    },
    
    clearWorkflow() {
      if (confirm('确定要清空工作流吗？')) {
        this.nodes = []
        this.edges = []
        this.selectedNode = null
        this.selectedEdge = null
      }
    },
    
    // 辅助方法
    getNodeStyle(node) {
      return {
        left: `${node.position.x}px`,
        top: `${node.position.y}px`
      }
    },
    
    getNodeColor(nodeType) {
      const node = this.nodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.color || '#6b7280'
    },
    
    getNodeInputPorts(nodeType) {
      const node = this.nodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.inputPorts || []
    },
    
    getNodeOutputPorts(nodeType) {
      const node = this.nodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.outputPorts || []
    },
    
    getNodeComponent(nodeType) {
      // 返回节点内容组件
      return 'div'  // 简化版本
    },
    
    getNodeConfigComponent(nodeType) {
      // 返回配置表单组件
      return 'div'  // 简化版本
    },
    
    getSelectedNodeType() {
      const node = this.nodes.find(n => n.id === this.selectedNode)
      return node?.type || ''
    },
    
    getSelectedNodeConfig() {
      const node = this.nodes.find(n => n.id === this.selectedNode)
      return node?.data?.config || {}
    },
    
    toggleCategory(categoryName) {
      const index = this.expandedCategories.indexOf(categoryName)
      if (index > -1) {
        this.expandedCategories.splice(index, 1)
      } else {
        this.expandedCategories.push(categoryName)
      }
    }
  }
}
</script>

<style scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.toolbar-left, .toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: #fff;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-success {
  background: #10b981;
  color: #fff;
}

.btn-success:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6b7280;
  color: #fff;
}

.icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.node-library {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.node-library.collapsed {
  width: 40px;
}

.library-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.library-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 16px;
}

.node-category {
  margin-bottom: 16px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
}

.category-nodes {
  margin-top: 8px;
}

.node-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 8px;
  cursor: move;
  transition: all 0.2s;
}

.node-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.node-info {
  flex: 1;
}

.node-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.node-desc {
  font-size: 12px;
  color: #6b7280;
}

.canvas-area {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #fafafa;
}

.canvas-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.edge {
  fill: none;
  stroke: #94a3b8;
  stroke-width: 2;
  pointer-events: stroke;
  cursor: pointer;
}

.edge.selected {
  stroke: #3b82f6;
  stroke-width: 3;
}

.temp-edge {
  stroke: #3b82f6;
  stroke-dasharray: 5;
}

.workflow-node {
  position: absolute;
  width: 300px;
  background: #fff;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: move;
  transition: all 0.2s;
}

.workflow-node.selected {
  border-color: #3b82f6;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
}

.workflow-node.executing {
  border-color: #10b981;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3); }
  50% { box-shadow: 0 4px 24px rgba(16, 185, 129, 0.6); }
}

.node-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 6px 6px 0 0;
  color: #fff;
  font-weight: 600;
}

.btn-delete {
  background: rgba(255,255,255,0.2);
  border: none;
  color: #fff;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 18px;
}

.node-body {
  padding: 16px;
}

.port {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  cursor: pointer;
}

.port-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #3b82f6;
}

.port-label {
  font-size: 12px;
  color: #6b7280;
}

.output-port {
  justify-content: flex-end;
}

.properties-panel {
  width: 320px;
  background: #fff;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.property-group {
  margin-bottom: 16px;
}

.property-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #374151;
}

.property-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
}
</style>
