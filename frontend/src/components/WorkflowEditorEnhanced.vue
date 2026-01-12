<template>
  <div class="workflow-editor-enhanced" @keydown="handleKeyDown">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button @click="saveWorkflow" class="btn btn-primary">
          <svg class="icon" viewBox="0 0 24 24"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
          保存
        </button>
        <button @click="executeWorkflow" class="btn btn-success" :disabled="isExecuting">
          <svg class="icon" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          {{ isExecuting ? '执行中...' : '执行' }}
        </button>
        
        <!-- 撤销/重做 -->
        <div class="btn-group">
          <button @click="undo" :disabled="!canUndo" class="btn btn-secondary" title="撤销 (Ctrl+Z)">
            <svg class="icon" viewBox="0 0 24 24"><path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/></svg>
          </button>
          <button @click="redo" :disabled="!canRedo" class="btn btn-secondary" title="重做 (Ctrl+Y)">
            <svg class="icon" viewBox="0 0 24 24"><path d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/></svg>
          </button>
        </div>
        
        <!-- 自动布局 -->
        <button @click="autoLayout" class="btn btn-secondary" title="自动布局 (Ctrl+L)">
          <svg class="icon" viewBox="0 0 24 24"><path d="M3 3v8h8V3H3zm6 6H5V5h4v4zm-6 4v8h8v-8H3zm6 6H5v-4h4v4zm4-16v8h8V3h-8zm6 6h-4V5h4v4zm-6 4v8h8v-8h-8zm6 6h-4v-4h4v4z"/></svg>
          自动布局
        </button>
        
        <!-- 节点模板 -->
        <button @click="showTemplates = true" class="btn btn-secondary">
          <svg class="icon" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
          模板
        </button>
      </div>
      
      <div class="toolbar-right">
        <span class="zoom-info">{{ Math.round(zoom * 100) }}%</span>
        <button @click="zoomIn" class="btn-icon" title="放大 (Ctrl++)">+</button>
        <button @click="zoomOut" class="btn-icon" title="缩小 (Ctrl+-)">-</button>
        <button @click="fitView" class="btn-icon" title="适应画布 (Ctrl+0)">
          <svg class="icon" viewBox="0 0 24 24"><path d="M15 3l2.3 2.3-2.89 2.87 1.42 1.42L18.7 6.7 21 9V3zM3 9l2.3-2.3 2.87 2.89 1.42-1.42L6.7 5.3 9 3H3zm6 12l-2.3-2.3 2.89-2.87-1.42-1.42L5.3 17.3 3 15v6zm12-6l-2.3 2.3-2.87-2.89-1.42 1.42 2.89 2.87L15 21h6z"/></svg>
        </button>
      </div>
    </div>

    <!-- 主编辑区 -->
    <div class="editor-main">
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
          
          <!-- 节点分类 -->
          <div v-for="category in enhancedNodeCategories" :key="category.name" class="node-category">
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

      <!-- 画布 -->
      <div 
        ref="canvas"
        class="canvas-area"
        @drop="onCanvasDrop"
        @dragover.prevent
        @mousedown="onCanvasMouseDown"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
        @wheel="onCanvasWheel"
        tabindex="0"
      >
        <svg class="canvas-svg" :style="canvasStyle">
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
          
          <!-- 选择框 -->
          <rect
            v-if="selectionBox"
            :x="selectionBox.x"
            :y="selectionBox.y"
            :width="selectionBox.width"
            :height="selectionBox.height"
            class="selection-box"
          />
        </svg>

        <!-- 节点 -->
        <div
          v-for="node in nodes"
          :key="node.id"
          :data-node-id="node.id"
          class="workflow-node"
          :class="{ 
            selected: selectedNodes.includes(node.id),
            executing: executingNode === node.id 
          }"
          :style="getNodeStyle(node)"
          @mousedown.stop="onNodeMouseDown($event, node.id)"
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
    </div>

    <!-- 模板对话框 -->
    <div v-if="showTemplates" class="modal-overlay" @click="showTemplates = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>节点组合模板</h3>
          <button @click="showTemplates = false" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="template-grid">
            <div
              v-for="template in nodeTemplates"
              :key="template.id"
              class="template-card"
              @click="applyNodeTemplate(template)"
            >
              <div class="template-preview">
                <img v-if="template.preview" :src="template.preview" alt="预览" />
                <div v-else class="template-placeholder">{{ template.icon }}</div>
              </div>
              <div class="template-info">
                <h4>{{ template.name }}</h4>
                <p>{{ template.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快捷键提示 -->
    <div v-if="showShortcuts" class="shortcuts-panel">
      <h4>快捷键</h4>
      <ul>
        <li><kbd>Ctrl</kbd> + <kbd>Z</kbd> - 撤销</li>
        <li><kbd>Ctrl</kbd> + <kbd>Y</kbd> - 重做</li>
        <li><kbd>Ctrl</kbd> + <kbd>S</kbd> - 保存</li>
        <li><kbd>Ctrl</kbd> + <kbd>L</kbd> - 自动布局</li>
        <li><kbd>Ctrl</kbd> + <kbd>+</kbd> - 放大</li>
        <li><kbd>Ctrl</kbd> + <kbd>-</kbd> - 缩小</li>
        <li><kbd>Ctrl</kbd> + <kbd>0</kbd> - 适应画布</li>
        <li><kbd>Delete</kbd> - 删除选中</li>
        <li><kbd>Ctrl</kbd> + <kbd>A</kbd> - 全选</li>
        <li><kbd>Ctrl</kbd> + <kbd>D</kbd> - 复制</li>
        <li><kbd>?</kbd> - 显示/隐藏快捷键</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WorkflowEditorEnhanced',
  props: {
    projectId: String,
    initialWorkflow: Object
  },
  data() {
    return {
      nodes: [],
      edges: [],
      selectedNodes: [],
      selectedEdge: null,
      executingNode: null,
      nodeResults: {},
      
      // 历史记录
      history: [],
      historyIndex: -1,
      maxHistorySize: 50,
      
      // 画布状态
      zoom: 1,
      panX: 0,
      panY: 0,
      isPanning: false,
      isDraggingNode: false,
      dragStartPos: null,
      
      // 选择框
      isSelecting: false,
      selectionBox: null,
      selectionStart: null,
      
      // UI 状态
      libraryCollapsed: false,
      searchQuery: '',
      expandedCategories: ['input', 'ai', 'processing', 'filter', 'transition', 'text', 'effect'],
      isExecuting: false,
      showTemplates: false,
      showShortcuts: false,
      
      // 连接状态
      connectingFrom: null,
      tempEdge: null,
      
      // 节点模板
      nodeTemplates: [
        {
          id: 'basic_video',
          name: '基础视频生成',
          description: '文字 → AI图片 → AI视频',
          icon: '🎬',
          nodes: [
            { type: 'text_input', position: { x: 100, y: 100 } },
            { type: 'ai_image', position: { x: 400, y: 100 } },
            { type: 'ai_video', position: { x: 700, y: 100 } }
          ],
          edges: [
            { source: 0, target: 1, sourcePort: 'text', targetPort: 'prompt' },
            { source: 1, target: 2, sourcePort: 'image', targetPort: 'image' }
          ]
        },
        {
          id: 'video_with_music',
          name: '视频配乐',
          description: '视频 + 音乐 → 成品',
          icon: '🎵',
          nodes: [
            { type: 'video_input', position: { x: 100, y: 100 } },
            { type: 'music_input', position: { x: 100, y: 250 } },
            { type: 'add_music', position: { x: 400, y: 150 } }
          ],
          edges: [
            { source: 0, target: 2, sourcePort: 'video', targetPort: 'video' },
            { source: 1, target: 2, sourcePort: 'audio', targetPort: 'music' }
          ]
        },
        {
          id: 'color_grading',
          name: '色彩调整',
          description: '视频 → 调色 → 输出',
          icon: '🎨',
          nodes: [
            { type: 'video_input', position: { x: 100, y: 100 } },
            { type: 'color_grading', position: { x: 400, y: 100 } }
          ],
          edges: [
            { source: 0, target: 1, sourcePort: 'video', targetPort: 'video' }
          ]
        }
      ],
      
      // 增强的节点分类
      enhancedNodeCategories: []
    }
  },
  computed: {
    canUndo() {
      return this.historyIndex > 0
    },
    canRedo() {
      return this.historyIndex < this.history.length - 1
    },
    canvasStyle() {
      return {
        transform: `translate(${this.panX}px, ${this.panY}px) scale(${this.zoom})`
      }
    }
  },
  mounted() {
    this.initializeNodeCategories()
    
    if (this.initialWorkflow) {
      this.nodes = this.initialWorkflow.nodes || []
      this.edges = this.initialWorkflow.edges || []
      this.saveToHistory()
    }
    
    // 监听键盘事件
    window.addEventListener('keydown', this.handleGlobalKeyDown)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleGlobalKeyDown)
  },
  methods: {
    // ==================== 历史记录 ====================
    saveToHistory() {
      const state = {
        nodes: JSON.parse(JSON.stringify(this.nodes)),
        edges: JSON.parse(JSON.stringify(this.edges))
      }
      
      // 删除当前位置之后的历史
      this.history = this.history.slice(0, this.historyIndex + 1)
      
      // 添加新状态
      this.history.push(state)
      
      // 限制历史大小
      if (this.history.length > this.maxHistorySize) {
        this.history.shift()
      } else {
        this.historyIndex++
      }
    },
    
    undo() {
      if (this.canUndo) {
        this.historyIndex--
        const state = this.history[this.historyIndex]
        this.nodes = JSON.parse(JSON.stringify(state.nodes))
        this.edges = JSON.parse(JSON.stringify(state.edges))
      }
    },
    
    redo() {
      if (this.canRedo) {
        this.historyIndex++
        const state = this.history[this.historyIndex]
        this.nodes = JSON.parse(JSON.stringify(state.nodes))
        this.edges = JSON.parse(JSON.stringify(state.edges))
      }
    },
    
    // ==================== 自动布局 ====================
    autoLayout() {
      // 使用 Dagre 算法进行自动布局
      const nodeSpacing = 150
      const levelSpacing = 300
      
      // 构建依赖图
      const inDegree = {}
      const adjacency = {}
      
      this.nodes.forEach(node => {
        inDegree[node.id] = 0
        adjacency[node.id] = []
      })
      
      this.edges.forEach(edge => {
        adjacency[edge.source].push(edge.target)
        inDegree[edge.target]++
      })
      
      // 拓扑排序分层
      const levels = []
      const queue = Object.keys(inDegree).filter(id => inDegree[id] === 0)
      const visited = new Set()
      
      while (queue.length > 0) {
        const levelNodes = [...queue]
        levels.push(levelNodes)
        queue.length = 0
        
        levelNodes.forEach(nodeId => {
          visited.add(nodeId)
          adjacency[nodeId].forEach(targetId => {
            inDegree[targetId]--
            if (inDegree[targetId] === 0 && !visited.has(targetId)) {
              queue.push(targetId)
            }
          })
        })
      }
      
      // 应用布局
      levels.forEach((level, levelIndex) => {
        level.forEach((nodeId, nodeIndex) => {
          const node = this.nodes.find(n => n.id === nodeId)
          if (node) {
            node.position = {
              x: levelIndex * levelSpacing + 100,
              y: nodeIndex * nodeSpacing + 100
            }
          }
        })
      })
      
      this.saveToHistory()
      this.$message.success('自动布局完成')
    },
    
    // ==================== 快捷键 ====================
    handleGlobalKeyDown(event) {
      // 只在编辑器获得焦点时处理
      if (!this.$el.contains(document.activeElement)) return
      
      this.handleKeyDown(event)
    },
    
    handleKeyDown(event) {
      const ctrl = event.ctrlKey || event.metaKey
      
      // Ctrl+Z - 撤销
      if (ctrl && event.key === 'z' && !event.shiftKey) {
        event.preventDefault()
        this.undo()
      }
      // Ctrl+Y 或 Ctrl+Shift+Z - 重做
      else if (ctrl && (event.key === 'y' || (event.key === 'z' && event.shiftKey))) {
        event.preventDefault()
        this.redo()
      }
      // Ctrl+S - 保存
      else if (ctrl && event.key === 's') {
        event.preventDefault()
        this.saveWorkflow()
      }
      // Ctrl+L - 自动布局
      else if (ctrl && event.key === 'l') {
        event.preventDefault()
        this.autoLayout()
      }
      // Ctrl++ - 放大
      else if (ctrl && (event.key === '+' || event.key === '=')) {
        event.preventDefault()
        this.zoomIn()
      }
      // Ctrl+- - 缩小
      else if (ctrl && event.key === '-') {
        event.preventDefault()
        this.zoomOut()
      }
      // Ctrl+0 - 适应画布
      else if (ctrl && event.key === '0') {
        event.preventDefault()
        this.fitView()
      }
      // Delete - 删除选中
      else if (event.key === 'Delete' || event.key === 'Backspace') {
        event.preventDefault()
        this.deleteSelected()
      }
      // Ctrl+A - 全选
      else if (ctrl && event.key === 'a') {
        event.preventDefault()
        this.selectAll()
      }
      // Ctrl+D - 复制
      else if (ctrl && event.key === 'd') {
        event.preventDefault()
        this.duplicateSelected()
      }
      // ? - 显示快捷键
      else if (event.key === '?') {
        this.showShortcuts = !this.showShortcuts
      }
    },
    
    deleteSelected() {
      this.selectedNodes.forEach(nodeId => {
        this.deleteNode(nodeId)
      })
      this.selectedNodes = []
    },
    
    selectAll() {
      this.selectedNodes = this.nodes.map(n => n.id)
    },
    
    duplicateSelected() {
      const newNodes = []
      const nodeIdMap = {}
      
      this.selectedNodes.forEach(nodeId => {
        const node = this.nodes.find(n => n.id === nodeId)
        if (node) {
          const newId = `node-${Date.now()}-${Math.random()}`
          nodeIdMap[nodeId] = newId
          
          newNodes.push({
            ...JSON.parse(JSON.stringify(node)),
            id: newId,
            position: {
              x: node.position.x + 50,
              y: node.position.y + 50
            }
          })
        }
      })
      
      this.nodes.push(...newNodes)
      this.selectedNodes = newNodes.map(n => n.id)
      this.saveToHistory()
    },
    
    // ==================== 节点模板 ====================
    applyNodeTemplate(template) {
      const startX = 200
      const startY = 200
      
      const nodeIdMap = {}
      const newNodes = []
      
      // 创建节点
      template.nodes.forEach((nodeTemplate, index) => {
        const nodeId = `node-${Date.now()}-${index}`
        nodeIdMap[index] = nodeId
        
        const nodeType = this.enhancedNodeCategories
          .flatMap(c => c.nodes)
          .find(n => n.type === nodeTemplate.type)
        
        if (nodeType) {
          newNodes.push({
            id: nodeId,
            type: nodeTemplate.type,
            position: {
              x: startX + nodeTemplate.position.x,
              y: startY + nodeTemplate.position.y
            },
            data: {
              label: nodeType.name,
              config: {}
            }
          })
        }
      })
      
      // 创建连接
      const newEdges = []
      template.edges.forEach((edgeTemplate, index) => {
        const sourceId = nodeIdMap[edgeTemplate.source]
        const targetId = nodeIdMap[edgeTemplate.target]
        
        if (sourceId && targetId) {
          newEdges.push({
            id: `edge-${Date.now()}-${index}`,
            source: sourceId,
            target: targetId,
            sourceHandle: edgeTemplate.sourcePort,
            targetHandle: edgeTemplate.targetPort
          })
        }
      })
      
      this.nodes.push(...newNodes)
      this.edges.push(...newEdges)
      this.saveToHistory()
      this.showTemplates = false
      
      this.$message.success(`已应用模板: ${template.name}`)
    },
    
    // ==================== 其他方法 ====================
    initializeNodeCategories() {
      this.enhancedNodeCategories = [
        // ... 基础节点分类
        {
          name: 'filter',
          label: '视频滤镜',
          nodes: [
            { type: 'color_grading', name: '色彩调整', description: '调整亮度、对比度、饱和度', icon: '🎨', color: '#f59e0b' },
            { type: 'vintage_filter', name: '复古滤镜', description: '怀旧、黑白、老电影', icon: '📼', color: '#a855f7' },
            { type: 'blur_filter', name: '模糊效果', description: '高斯模糊、运动模糊', icon: '🌫️', color: '#06b6d4' },
            { type: 'sharpen_filter', name: '锐化', description: '增强画面清晰度', icon: '✨', color: '#10b981' }
          ]
        },
        {
          name: 'transition',
          label: '转场效果',
          nodes: [
            { type: 'fade_transition', name: '淡入淡出', description: '平滑过渡', icon: '🌓', color: '#8b5cf6' },
            { type: 'wipe_transition', name: '擦除转场', description: '左右上下擦除', icon: '↔️', color: '#ec4899' },
            { type: 'slide_transition', name: '滑动转场', description: '滑动切换', icon: '➡️', color: '#f43f5e' }
          ]
        },
        {
          name: 'text',
          label: '文字动画',
          nodes: [
            { type: 'text_fadein', name: '淡入文字', description: '文字淡入效果', icon: '📝', color: '#3b82f6' },
            { type: 'text_typewriter', name: '打字机', description: '逐字显示', icon: '⌨️', color: '#6366f1' },
            { type: 'text_scroll', name: '滚动文字', description: '字幕滚动', icon: '📜', color: '#8b5cf6' }
          ]
        },
        {
          name: 'effect',
          label: '特效',
          nodes: [
            { type: 'glitch_effect', name: '故障艺术', description: 'Glitch效果', icon: '⚡', color: '#ef4444' },
            { type: 'chroma_key', name: '绿幕抠图', description: '色度键合成', icon: '🎬', color: '#10b981' },
            { type: 'zoom_effect', name: '缩放特效', description: '放大缩小', icon: '🔍', color: '#f59e0b' }
          ]
        }
      ]
    },
    
    // 其他现有方法保持不变...
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
      this.saveToHistory()
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
      this.saveToHistory()
    },
    
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
      // 执行逻辑...
    },
    
    // 画布操作方法...
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
    
    getNodeStyle(node) {
      return {
        left: `${node.position.x}px`,
        top: `${node.position.y}px`
      }
    },
    
    getNodeColor(nodeType) {
      const node = this.enhancedNodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.color || '#6b7280'
    },
    
    getNodeInputPorts(nodeType) {
      const node = this.enhancedNodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.inputPorts || []
    },
    
    getNodeOutputPorts(nodeType) {
      const node = this.enhancedNodeCategories
        .flatMap(c => c.nodes)
        .find(n => n.type === nodeType)
      return node?.outputPorts || []
    },
    
    toggleCategory(categoryName) {
      const index = this.expandedCategories.indexOf(categoryName)
      if (index > -1) {
        this.expandedCategories.splice(index, 1)
      } else {
        this.expandedCategories.push(categoryName)
      }
    },
    
    onNodeMouseDown(event, nodeId) {
      if (!this.selectedNodes.includes(nodeId)) {
        if (!event.ctrlKey) {
          this.selectedNodes = [nodeId]
        } else {
          this.selectedNodes.push(nodeId)
        }
      }
      
      this.isDraggingNode = true
      this.dragStartPos = {
        x: event.clientX,
        y: event.clientY,
        nodes: this.selectedNodes.map(id => {
          const node = this.nodes.find(n => n.id === id)
          return {
            id,
            startX: node.position.x,
            startY: node.position.y
          }
        })
      }
    },
    
    onCanvasMouseDown(event) {
      if (event.target === this.$refs.canvas || event.target.classList.contains('canvas-svg')) {
        this.isPanning = true
        this.lastMouseX = event.clientX
        this.lastMouseY = event.clientY
        this.selectedNodes = []
      }
    },
    
    onCanvasMouseMove(event) {
      if (this.isDraggingNode && this.dragStartPos) {
        const dx = (event.clientX - this.dragStartPos.x) / this.zoom
        const dy = (event.clientY - this.dragStartPos.y) / this.zoom
        
        this.dragStartPos.nodes.forEach(({ id, startX, startY }) => {
          const node = this.nodes.find(n => n.id === id)
          if (node) {
            node.position.x = startX + dx
            node.position.y = startY + dy
          }
        })
      } else if (this.isPanning) {
        const dx = event.clientX - this.lastMouseX
        const dy = event.clientY - this.lastMouseY
        
        this.panX += dx
        this.panY += dy
        
        this.lastMouseX = event.clientX
        this.lastMouseY = event.clientY
      }
    },
    
    onCanvasMouseUp() {
      if (this.isDraggingNode) {
        this.saveToHistory()
      }
      
      this.isDraggingNode = false
      this.isPanning = false
      this.dragStartPos = null
    },
    
    onCanvasWheel(event) {
      event.preventDefault()
      const delta = event.deltaY > 0 ? 0.9 : 1.1
      this.zoom = Math.max(0.1, Math.min(3, this.zoom * delta))
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
    
    selectEdge(edgeId) {
      this.selectedEdge = edgeId
      this.selectedNodes = []
    },
    
    startConnection(nodeId, portName, portType) {
      this.connectingFrom = { nodeId, portName, portType }
    }
  }
}
</script>

<style scoped>
/* 样式与之前类似，添加新的样式 */
.shortcuts-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(0,0,0,0.9);
  color: #fff;
  padding: 20px;
  border-radius: 8px;
  max-width: 300px;
  z-index: 1000;
}

.shortcuts-panel h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
}

.shortcuts-panel ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.shortcuts-panel li {
  margin: 8px 0;
  font-size: 13px;
}

kbd {
  display: inline-block;
  padding: 2px 6px;
  background: #374151;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.selection-box {
  fill: rgba(59, 130, 246, 0.1);
  stroke: #3b82f6;
  stroke-width: 2;
  stroke-dasharray: 5;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 12px;
  max-width: 800px;
  max-height: 80vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-body {
  padding: 20px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.template-card {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.template-preview {
  width: 100%;
  height: 120px;
  background: #f3f4f6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin-bottom: 12px;
}

.template-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
}

.template-info p {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}
</style>
