<template>
  <div class="collaborative-editor">
    <div class="editor-header">
      <h2>协作编辑</h2>
      <div class="online-users">
        <div v-for="user in onlineUsers" :key="user.id" class="user-badge" :title="user.username">
          <div class="user-avatar" :style="{ background: user.color }">
            {{ user.username[0] }}
          </div>
        </div>
      </div>
    </div>

    <div class="role-selector">
      <label>我的角色：</label>
      <select v-model="myRole" @change="updateRole" class="role-select">
        <option value="parent">家长（编辑框架）</option>
        <option value="child">孩子（填充对话）</option>
        <option value="viewer">观看者</option>
      </select>
    </div>

    <div class="editor-container">
      <textarea
        ref="editorRef"
        v-model="content"
        @input="handleInput"
        @keyup="handleCursorMove"
        @click="handleCursorMove"
        :disabled="!canEdit"
        class="collaborative-textarea"
        :class="{ 'read-only': !canEdit }"
        placeholder="开始协作创作故事..."
      ></textarea>

      <div class="remote-cursors">
        <div
          v-for="cursor in remoteCursors"
          :key="cursor.userId"
          class="remote-cursor"
          :style="getCursorStyle(cursor)"
        >
          <div class="cursor-flag" :style="{ background: cursor.color }">
            {{ cursor.username }}
          </div>
        </div>
      </div>
    </div>

    <div class="editor-status">
      <span v-if="isConnected" class="status-connected">● 已连接</span>
      <span v-else class="status-disconnected">● 未连接</span>
      <span class="last-edit">最后编辑: {{ lastEditUser }}</span>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'CollaborativeEditor',
  
  props: {
    storyId: {
      type: String,
      required: true
    },
    initialContent: {
      type: String,
      default: ''
    }
  },
  
  setup(props) {
    const ws = ref(null)
    const content = ref(props.initialContent)
    const onlineUsers = ref([])
    const remoteCursors = ref([])
    const myRole = ref('parent')
    const isConnected = ref(false)
    const lastEditUser = ref('无')
    const editorRef = ref(null)
    
    const canEdit = computed(() => myRole.value !== 'viewer')
    
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/ws/story/${props.storyId}/`
      ws.value = new WebSocket(wsUrl)
      
      ws.value.onopen = () => {
        isConnected.value = true
        console.log('WebSocket连接成功')
      }
      
      ws.value.onmessage = (event) => {
        const data = JSON.parse(event.data)
        handleWebSocketMessage(data)
      }
      
      ws.value.onerror = (error) => {
        console.error('WebSocket错误:', error)
        isConnected.value = false
      }
      
      ws.value.onclose = () => {
        isConnected.value = false
        console.log('WebSocket连接关闭')
        // 尝试重连
        setTimeout(connectWebSocket, 3000)
      }
    }
    
    const handleWebSocketMessage = (data) => {
      switch (data.type) {
        case 'user_joined':
          addOnlineUser(data)
          break
        case 'user_left':
          removeOnlineUser(data.user_id)
          break
        case 'edit':
          handleRemoteEdit(data)
          break
        case 'cursor_move':
          updateRemoteCursor(data)
          break
        default:
          console.log('未处理的消息类型:', data.type)
      }
    }
    
    const addOnlineUser = (userData) => {
      if (!onlineUsers.value.find(u => u.id === userData.user_id)) {
        onlineUsers.value.push({
          id: userData.user_id,
          username: userData.username,
          color: generateUserColor(userData.user_id)
        })
      }
    }
    
    const removeOnlineUser = (userId) => {
      onlineUsers.value = onlineUsers.value.filter(u => u.id !== userId)
      remoteCursors.value = remoteCursors.value.filter(c => c.userId !== userId)
    }
    
    const handleInput = () => {
      if (!canEdit.value) return
      
      sendEdit()
    }
    
    const sendEdit = () => {
      if (!ws.value || ws.value.readyState !== WebSocket.OPEN) return
      
      ws.value.send(JSON.stringify({
        action: 'edit',
        content: content.value,
        position: editorRef.value?.selectionStart || 0,
        edit_type: 'replace'
      }))
    }
    
    const handleCursorMove = () => {
      if (!canEdit.value || !editorRef.value) return
      
      const position = editorRef.value.selectionStart
      
      if (ws.value && ws.value.readyState === WebSocket.OPEN) {
        ws.value.send(JSON.stringify({
          action: 'cursor_move',
          position: position
        }))
      }
    }
    
    const handleRemoteEdit = (data) => {
      content.value = data.content
      lastEditUser.value = data.username
    }
    
    const updateRemoteCursor = (data) => {
      const existingCursor = remoteCursors.value.find(c => c.userId === data.user_id)
      
      if (existingCursor) {
        existingCursor.position = data.position
      } else {
        remoteCursors.value.push({
          userId: data.user_id,
          username: data.username,
          position: data.position,
          color: generateUserColor(data.user_id)
        })
      }
    }
    
    const getCursorStyle = (cursor) => {
      // 简化版：固定位置
      return {
        left: '0px',
        top: `${cursor.position * 0.1}px`
      }
    }
    
    const generateUserColor = (userId) => {
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
      const hash = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[hash % colors.length]
    }
    
    const updateRole = () => {
      // 通知服务器角色变更
      console.log('角色变更为:', myRole.value)
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
      content,
      onlineUsers,
      remoteCursors,
      myRole,
      isConnected,
      lastEditUser,
      editorRef,
      canEdit,
      handleInput,
      handleCursorMove,
      getCursorStyle,
      updateRole
    }
  }
}
</script>

<style scoped>
.collaborative-editor {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.online-users {
  display: flex;
  gap: 8px;
}

.user-badge {
  position: relative;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.role-selector {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.role-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.editor-container {
  position: relative;
  margin-bottom: 16px;
}

.collaborative-textarea {
  width: 100%;
  min-height: 500px;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  line-height: 1.8;
  font-family: inherit;
  resize: vertical;
}

.collaborative-textarea.read-only {
  background: #f5f5f5;
  cursor: not-allowed;
}

.remote-cursors {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.remote-cursor {
  position: absolute;
  width: 2px;
  height: 20px;
  animation: blink 1s infinite;
}

.cursor-flag {
  position: absolute;
  top: -20px;
  left: 0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  color: white;
  white-space: nowrap;
}

@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.editor-status {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

.status-connected {
  color: #4CAF50;
}

.status-disconnected {
  color: #f44336;
}
</style>
