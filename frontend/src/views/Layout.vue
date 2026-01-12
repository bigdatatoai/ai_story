<template>
  <div class="drawer lg:drawer-open">
    <!-- 移动端抽屉切换 -->
    <input id="main-drawer" type="checkbox" class="drawer-toggle" />

    <!-- 主内容区 -->
    <div class="drawer-content flex flex-col">
      <!-- 顶部导航栏 - 现代化设计 -->
      <header class="modern-navbar bg-white border-b border-gray-200 px-4 lg:px-6 shadow-sm">
        <!-- 桌面端折叠/展开按钮 -->
        <div class="flex-none hidden lg:block">
          <button
            class="btn btn-square btn-ghost"
            @click="toggleSidebar"
            :title="sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5 transition-transform duration-300"
              :class="{ 'rotate-180': !sidebarCollapsed }"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12"
              />
            </svg>
          </button>
        </div>

        <!-- 移动端菜单按钮 -->
        <div class="flex-none lg:hidden">
          <label for="main-drawer" class="btn btn-square btn-ghost">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="inline-block w-5 h-5 stroke-current"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              ></path>
            </svg>
          </label>
        </div>

        <!-- 面包屑导航 -->
        <div class="flex-1">
          <div class="text-sm breadcrumbs">
            <ul>
              <li v-for="(item, index) in breadcrumbs" :key="index">
                <router-link :to="item.path">{{ item.label }}</router-link>
              </li>
            </ul>
          </div>
        </div>

        <!-- 右侧操作按钮 -->
        <div class="flex-none gap-2">
          <button class="btn btn-ghost btn-circle" @click="handleRefresh">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              class="w-5 h-5"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
              />
            </svg>
          </button>

          <!-- 用户菜单 -->
          <div class="dropdown dropdown-end">
            <label tabindex="0" class="btn btn-ghost btn-circle avatar placeholder">
              <div class="bg-neutral-focus text-neutral-content rounded-full w-10">
                <span class="text-xl">{{ userInitial }}</span>
              </div>
            </label>
            <ul
              tabindex="0"
              class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52"
            >
              <li class="menu-title">
                <span>{{ username }}</span>
              </li>
              <li>
                <a @click="handleProfile">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                    class="w-5 h-5"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
                    />
                  </svg>
                  个人资料
                </a>
              </li>
              <li>
                <a @click="handleLogout">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                    class="w-5 h-5"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"
                    />
                  </svg>
                  退出登录
                </a>
              </li>
            </ul>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="flex-1 overflow-y-auto p-6 bg-base-200">
        <router-view />
      </main>
    </div>

    <!-- 侧边栏 - 现代化设计 -->
    <div class="drawer-side z-40">
      <label for="main-drawer" class="drawer-overlay"></label>
      <aside
        class="modern-sidebar min-h-full transition-all duration-300 ease-in-out overflow-hidden"
        :class="sidebarCollapsed ? 'w-16' : 'w-64'"
      >
        <!-- Logo -->
        <div
          class="sidebar-logo sticky top-0 z-20 backdrop-blur py-6 transition-all duration-300"
          :class="sidebarCollapsed ? 'px-2' : 'px-6'"
        >
          <div class="logo-wrapper">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7L12 12L22 7L12 2Z"/>
                <path d="M2 17L12 22L22 17"/>
                <path d="M2 12L12 17L22 12"/>
              </svg>
            </div>
            <h1
              v-show="!sidebarCollapsed"
              class="logo-text transition-all duration-300 overflow-hidden whitespace-nowrap"
            >
              智绘视界
            </h1>
          </div>
        </div>

        <!-- 导航菜单 -->
        <ul class="menu p-2 w-full" :class="sidebarCollapsed ? 'menu-compact' : ''">
          <li>
            <router-link
              to="/projects"
              :class="{ 'active': activeMenu === '/projects' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '项目管理' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >项目管理</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/prompts"
              :class="{ 'active': activeMenu === '/prompts' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '提示词管理' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >提示词管理</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/prompts/variables"
              :class="{ 'active': activeMenu === '/prompts/variables' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '全局变量' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >全局变量</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/content"
              :class="{ 'active': activeMenu === '/content' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '内容管理' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0118 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 016 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >内容管理</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/models"
              :class="{ 'active': activeMenu === '/models' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '模型管理' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M8.25 3v1.5M4.5 8.25H3m18 0h-1.5M4.5 12H3m18 0h-1.5m-15 3.75H3m18 0h-1.5M8.25 19.5V21M12 3v1.5m0 15V21m3.75-18v1.5m0 15V21m-9-1.5h10.5a2.25 2.25 0 002.25-2.25V6.75a2.25 2.25 0 00-2.25-2.25H6.75A2.25 2.25 0 004.5 6.75v10.5a2.25 2.25 0 002.25 2.25zm.75-12h9v9h-9v-9z"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >模型管理</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/settings"
              :class="{ 'active': activeMenu === '/settings' }"
              class="flex items-center gap-3 tooltip tooltip-right"
              :data-tip="sidebarCollapsed ? '系统设置' : ''"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5 flex-shrink-0"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span
                v-show="!sidebarCollapsed"
                class="transition-opacity duration-300"
                :class="sidebarCollapsed ? 'opacity-0' : 'opacity-100'"
              >系统设置</span>
            </router-link>
          </li>
        </ul>
      </aside>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'Layout',
  computed: {
    ...mapGetters('auth', ['username', 'user']),
    ...mapGetters('ui', ['sidebarCollapsed']),
    activeMenu() {
      const route = this.$route;
      const { path } = route;
      return path;
    },
    breadcrumbs() {
      const route = this.$route;
      const breadcrumbs = [];

      if (route.matched && route.matched.length > 0) {
        route.matched.forEach((item) => {
          if (item.meta && item.meta.title) {
            breadcrumbs.push({
              label: item.meta.title,
              path: item.path,
            });
          }
        });
      }

      return breadcrumbs;
    },
    userInitial() {
      // 获取用户名首字母作为头像
      return this.username ? this.username.charAt(0).toUpperCase() : 'U';
    },
  },
  methods: {
    ...mapActions('auth', ['logout']),
    ...mapActions('ui', ['toggleSidebar']),
    handleRefresh() {
      this.$router.go(0);
    },
    handleProfile() {
      // TODO: 跳转到个人资料页面
      console.log('跳转到个人资料页面');
    },
    async handleLogout() {
      try {
        await this.logout();
        this.$router.push('/login');
      } catch (error) {
        console.error('登出失败:', error);
      }
    },
  },
};
</script>

<style scoped>
/* 现代化导航栏 */
.modern-navbar {
  height: 64px;
  display: flex;
  align-items: center;
  background: white;
}

/* 现代化侧边栏 */
.modern-sidebar {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

/* Logo 区域 */
.sidebar-logo {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 24px;
  height: 24px;
  color: white;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: white;
  letter-spacing: -0.5px;
}

/* 菜单项美化 */
.modern-sidebar .menu li > * {
  color: rgba(255, 255, 255, 0.8);
  border-radius: 10px;
  transition: all 0.3s ease;
}

.modern-sidebar .menu li > *:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.modern-sidebar .menu li > *.active {
  background: rgba(255, 255, 255, 0.25);
  color: white;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 侧边栏折叠动画 */
</style>
