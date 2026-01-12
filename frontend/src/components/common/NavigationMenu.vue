<template>
  <nav class="navigation-menu">
    <div class="nav-header">
      <h1 class="app-title">🎬 AI内容生产平台</h1>
    </div>

    <div class="nav-sections">
      <!-- AI视频生产 -->
      <div class="nav-section">
        <h3 class="section-title">AI视频生产</h3>
        <router-link to="/video" class="nav-item">
          <span class="nav-icon">📺</span>
          <span class="nav-text">生产控制台</span>
        </router-link>
        <router-link to="/video/drama-studio" class="nav-item">
          <span class="nav-icon">🎬</span>
          <span class="nav-text">AI短剧工作室</span>
        </router-link>
        <router-link to="/video/anime-studio" class="nav-item">
          <span class="nav-icon">🎨</span>
          <span class="nav-text">AI动漫工作室</span>
        </router-link>
        <router-link to="/video/batch-manager" class="nav-item">
          <span class="nav-icon">📦</span>
          <span class="nav-text">批量生产管理</span>
        </router-link>
        <router-link to="/video/characters" class="nav-item">
          <span class="nav-icon">👥</span>
          <span class="nav-text">角色一致性</span>
        </router-link>
      </div>

      <!-- AI故事生成 -->
      <div class="nav-section">
        <h3 class="section-title">AI故事生成</h3>
        <router-link to="/story/generator" class="nav-item">
          <span class="nav-icon">✍️</span>
          <span class="nav-text">故事生成器</span>
        </router-link>
        <router-link to="/story/library" class="nav-item">
          <span class="nav-icon">📚</span>
          <span class="nav-text">故事库</span>
        </router-link>
        <router-link to="/story/outline-editor" class="nav-item">
          <span class="nav-icon">📝</span>
          <span class="nav-text">大纲编辑器</span>
        </router-link>
      </div>

      <!-- 项目管理 -->
      <div class="nav-section">
        <h3 class="section-title">项目管理</h3>
        <router-link to="/projects" class="nav-item">
          <span class="nav-icon">📁</span>
          <span class="nav-text">项目列表</span>
        </router-link>
        <router-link to="/projects/create" class="nav-item">
          <span class="nav-icon">➕</span>
          <span class="nav-text">创建项目</span>
        </router-link>
      </div>

      <!-- 系统设置 -->
      <div class="nav-section">
        <h3 class="section-title">系统</h3>
        <router-link to="/models" class="nav-item">
          <span class="nav-icon">🤖</span>
          <span class="nav-text">模型管理</span>
        </router-link>
        <router-link to="/settings" class="nav-item">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">系统设置</span>
        </router-link>
      </div>
    </div>

    <!-- 用户信息 -->
    <div class="nav-footer">
      <div class="user-info">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-details">
          <div class="user-name">{{ userName }}</div>
          <button @click="logout" class="logout-btn">退出登录</button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'NavigationMenu',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const userName = computed(() => store.state.auth?.user?.username || '用户')
    const userInitial = computed(() => userName.value[0].toUpperCase())
    
    const logout = () => {
      store.dispatch('auth/logout')
      router.push('/login')
    }
    
    return {
      userName,
      userInitial,
      logout
    }
  }
}
</script>

<style scoped>
.navigation-menu {
  width: 260px;
  height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.nav-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: white;
}

.nav-sections {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.nav-section {
  margin-bottom: 24px;
}

.section-title {
  padding: 8px 20px;
  margin: 0 0 8px 0;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.5px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-left-color: white;
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.15);
  border-left-color: white;
  color: white;
  font-weight: 600;
}

.nav-icon {
  font-size: 20px;
  margin-right: 12px;
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
}

.nav-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 18px;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.logout-btn {
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 4px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 滚动条样式 */
.navigation-menu::-webkit-scrollbar {
  width: 6px;
}

.navigation-menu::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.navigation-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.navigation-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
