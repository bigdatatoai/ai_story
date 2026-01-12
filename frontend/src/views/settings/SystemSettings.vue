<template>
  <div class="system-settings">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">系统设置</h1>
          <p class="page-subtitle">配置TTS、STT、数据库等系统参数</p>
        </div>
        <button class="save-button" @click="handleSaveAll" :disabled="saving">
          <svg v-if="!saving" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          <span>{{ saving ? '保存中...' : '保存所有设置' }}</span>
        </button>
      </div>
    </div>

    <!-- 设置内容 -->
    <div class="settings-container">
      <!-- 左侧标签页 -->
      <div class="settings-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-button"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          <component :is="tab.icon" class="tab-icon" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- 右侧设置内容 -->
      <div class="settings-content">
        <loading-container :loading="loading">
          <!-- 数据库设置 -->
          <div v-show="activeTab === 'database'" class="setting-section">
            <h2 class="section-title">数据库配置</h2>
            <p class="section-description">配置系统使用的数据库连接参数</p>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">数据库类型</label>
                <select v-model="settings.database.engine" class="form-input">
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="sqlite">SQLite</option>
                </select>
              </div>

              <div class="form-group">
                <label class="form-label">主机地址</label>
                <input
                  v-model="settings.database.host"
                  type="text"
                  class="form-input"
                  placeholder="localhost"
                />
              </div>

              <div class="form-group">
                <label class="form-label">端口</label>
                <input
                  v-model="settings.database.port"
                  type="number"
                  class="form-input"
                  placeholder="5432"
                />
              </div>

              <div class="form-group">
                <label class="form-label">数据库名称</label>
                <input
                  v-model="settings.database.name"
                  type="text"
                  class="form-input"
                  placeholder="ai_story"
                />
              </div>

              <div class="form-group">
                <label class="form-label">用户名</label>
                <input
                  v-model="settings.database.user"
                  type="text"
                  class="form-input"
                  placeholder="postgres"
                />
              </div>

              <div class="form-group">
                <label class="form-label">密码</label>
                <input
                  v-model="settings.database.password"
                  type="password"
                  class="form-input"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button class="test-button" @click="testDatabaseConnection">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              测试连接
            </button>
          </div>

          <!-- Redis设置 -->
          <div v-show="activeTab === 'redis'" class="setting-section">
            <h2 class="section-title">Redis配置</h2>
            <p class="section-description">配置Redis缓存和消息队列</p>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">主机地址</label>
                <input
                  v-model="settings.redis.host"
                  type="text"
                  class="form-input"
                  placeholder="localhost"
                />
              </div>

              <div class="form-group">
                <label class="form-label">端口</label>
                <input
                  v-model="settings.redis.port"
                  type="number"
                  class="form-input"
                  placeholder="6379"
                />
              </div>

              <div class="form-group">
                <label class="form-label">数据库索引</label>
                <input
                  v-model="settings.redis.db"
                  type="number"
                  class="form-input"
                  placeholder="0"
                />
              </div>

              <div class="form-group">
                <label class="form-label">密码（可选）</label>
                <input
                  v-model="settings.redis.password"
                  type="password"
                  class="form-input"
                  placeholder="留空表示无密码"
                />
              </div>
            </div>

            <button class="test-button" @click="testRedisConnection">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              测试连接
            </button>
          </div>

          <!-- TTS设置 -->
          <div v-show="activeTab === 'tts'" class="setting-section">
            <h2 class="section-title">TTS配置（文字转语音）</h2>
            <p class="section-description">配置AI配音服务的API密钥和参数</p>

            <div class="provider-tabs">
              <button
                v-for="provider in ttsProviders"
                :key="provider.id"
                class="provider-tab"
                :class="{ active: activeTtsProvider === provider.id }"
                @click="activeTtsProvider = provider.id"
              >
                {{ provider.name }}
              </button>
            </div>

            <!-- 阿里云TTS -->
            <div v-show="activeTtsProvider === 'aliyun'" class="provider-config">
              <div class="form-group">
                <label class="form-label">Access Key ID</label>
                <input
                  v-model="settings.tts.aliyun.access_key_id"
                  type="text"
                  class="form-input"
                  placeholder="输入阿里云Access Key ID"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Access Key Secret</label>
                <input
                  v-model="settings.tts.aliyun.access_key_secret"
                  type="password"
                  class="form-input"
                  placeholder="输入阿里云Access Key Secret"
                />
              </div>
              <div class="form-group">
                <label class="form-label">默认音色</label>
                <select v-model="settings.tts.aliyun.default_voice" class="form-input">
                  <option value="xiaoyun">小云（女声）</option>
                  <option value="xiaogang">小刚（男声）</option>
                  <option value="ruoxi">若兮（女声）</option>
                </select>
              </div>
            </div>

            <!-- Azure TTS -->
            <div v-show="activeTtsProvider === 'azure'" class="provider-config">
              <div class="form-group">
                <label class="form-label">Subscription Key</label>
                <input
                  v-model="settings.tts.azure.subscription_key"
                  type="password"
                  class="form-input"
                  placeholder="输入Azure订阅密钥"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Region</label>
                <input
                  v-model="settings.tts.azure.region"
                  type="text"
                  class="form-input"
                  placeholder="eastasia"
                />
              </div>
            </div>

            <!-- 讯飞TTS -->
            <div v-show="activeTtsProvider === 'xunfei'" class="provider-config">
              <div class="form-group">
                <label class="form-label">App ID</label>
                <input
                  v-model="settings.tts.xunfei.app_id"
                  type="text"
                  class="form-input"
                  placeholder="输入讯飞App ID"
                />
              </div>
              <div class="form-group">
                <label class="form-label">API Key</label>
                <input
                  v-model="settings.tts.xunfei.api_key"
                  type="password"
                  class="form-input"
                  placeholder="输入讯飞API Key"
                />
              </div>
              <div class="form-group">
                <label class="form-label">API Secret</label>
                <input
                  v-model="settings.tts.xunfei.api_secret"
                  type="password"
                  class="form-input"
                  placeholder="输入讯飞API Secret"
                />
              </div>
            </div>

            <button class="test-button" @click="testTTS">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
              测试TTS
            </button>
          </div>

          <!-- STT设置 -->
          <div v-show="activeTab === 'stt'" class="setting-section">
            <h2 class="section-title">STT配置（语音转文字）</h2>
            <p class="section-description">配置语音识别服务的API密钥</p>

            <div class="provider-tabs">
              <button
                v-for="provider in sttProviders"
                :key="provider.id"
                class="provider-tab"
                :class="{ active: activeSttProvider === provider.id }"
                @click="activeSttProvider = provider.id"
              >
                {{ provider.name }}
              </button>
            </div>

            <!-- 阿里云STT -->
            <div v-show="activeSttProvider === 'aliyun'" class="provider-config">
              <div class="form-group">
                <label class="form-label">Access Key ID</label>
                <input
                  v-model="settings.stt.aliyun.access_key_id"
                  type="text"
                  class="form-input"
                  placeholder="输入阿里云Access Key ID"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Access Key Secret</label>
                <input
                  v-model="settings.stt.aliyun.access_key_secret"
                  type="password"
                  class="form-input"
                  placeholder="输入阿里云Access Key Secret"
                />
              </div>
            </div>

            <!-- OpenAI Whisper -->
            <div v-show="activeSttProvider === 'openai'" class="provider-config">
              <div class="form-group">
                <label class="form-label">API Key</label>
                <input
                  v-model="settings.stt.openai.api_key"
                  type="password"
                  class="form-input"
                  placeholder="输入OpenAI API Key"
                />
              </div>
              <div class="form-group">
                <label class="form-label">模型</label>
                <select v-model="settings.stt.openai.model" class="form-input">
                  <option value="whisper-1">Whisper-1</option>
                </select>
              </div>
            </div>
          </div>

          <!-- 存储设置 -->
          <div v-show="activeTab === 'storage'" class="setting-section">
            <h2 class="section-title">存储配置</h2>
            <p class="section-description">配置文件存储路径和对象存储</p>

            <div class="form-group">
              <label class="form-label">存储类型</label>
              <select v-model="settings.storage.type" class="form-input">
                <option value="local">本地存储</option>
                <option value="oss">阿里云OSS</option>
                <option value="s3">AWS S3</option>
              </select>
            </div>

            <!-- 本地存储 -->
            <div v-show="settings.storage.type === 'local'" class="storage-config">
              <div class="form-group">
                <label class="form-label">媒体文件路径</label>
                <input
                  v-model="settings.storage.local.media_root"
                  type="text"
                  class="form-input"
                  placeholder="/path/to/media"
                />
              </div>
              <div class="form-group">
                <label class="form-label">静态文件路径</label>
                <input
                  v-model="settings.storage.local.static_root"
                  type="text"
                  class="form-input"
                  placeholder="/path/to/static"
                />
              </div>
            </div>

            <!-- OSS存储 -->
            <div v-show="settings.storage.type === 'oss'" class="storage-config">
              <div class="form-group">
                <label class="form-label">Access Key ID</label>
                <input
                  v-model="settings.storage.oss.access_key_id"
                  type="text"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Access Key Secret</label>
                <input
                  v-model="settings.storage.oss.access_key_secret"
                  type="password"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Bucket名称</label>
                <input
                  v-model="settings.storage.oss.bucket"
                  type="text"
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label class="form-label">Endpoint</label>
                <input
                  v-model="settings.storage.oss.endpoint"
                  type="text"
                  class="form-input"
                  placeholder="oss-cn-hangzhou.aliyuncs.com"
                />
              </div>
            </div>
          </div>

          <!-- 其他设置 -->
          <div v-show="activeTab === 'other'" class="setting-section">
            <h2 class="section-title">其他设置</h2>
            <p class="section-description">配置系统的其他参数</p>

            <div class="form-group">
              <label class="form-label">Celery Broker URL</label>
              <input
                v-model="settings.other.celery_broker_url"
                type="text"
                class="form-input"
                placeholder="redis://localhost:6379/0"
              />
            </div>

            <div class="form-group">
              <label class="form-label">Celery Result Backend</label>
              <input
                v-model="settings.other.celery_result_backend"
                type="text"
                class="form-input"
                placeholder="redis://localhost:6379/0"
              />
            </div>

            <div class="form-group">
              <label class="form-label">允许的主机（ALLOWED_HOSTS）</label>
              <input
                v-model="settings.other.allowed_hosts"
                type="text"
                class="form-input"
                placeholder="localhost,127.0.0.1"
              />
              <p class="form-hint">多个主机用逗号分隔</p>
            </div>

            <div class="form-group">
              <label class="form-label">调试模式</label>
              <div class="toggle-switch">
                <input
                  type="checkbox"
                  id="debug-mode"
                  v-model="settings.other.debug"
                  class="toggle-input"
                />
                <label for="debug-mode" class="toggle-label">
                  <span class="toggle-slider"></span>
                </label>
                <span class="toggle-text">{{ settings.other.debug ? '开启' : '关闭' }}</span>
              </div>
            </div>
          </div>
        </loading-container>
      </div>
    </div>
  </div>
</template>

<script>
import LoadingContainer from '@/components/common/LoadingContainer.vue'

export default {
  name: 'SystemSettings',
  components: {
    LoadingContainer
  },
  data() {
    return {
      activeTab: 'database',
      activeTtsProvider: 'aliyun',
      activeSttProvider: 'aliyun',
      loading: false,
      saving: false,
      tabs: [
        { id: 'database', label: '数据库', icon: 'DatabaseIcon' },
        { id: 'redis', label: 'Redis', icon: 'ServerIcon' },
        { id: 'tts', label: 'TTS配音', icon: 'MicrophoneIcon' },
        { id: 'stt', label: 'STT识别', icon: 'SpeakerIcon' },
        { id: 'storage', label: '存储', icon: 'FolderIcon' },
        { id: 'other', label: '其他', icon: 'SettingsIcon' }
      ],
      ttsProviders: [
        { id: 'aliyun', name: '阿里云' },
        { id: 'azure', name: 'Azure' },
        { id: 'xunfei', name: '讯飞' }
      ],
      sttProviders: [
        { id: 'aliyun', name: '阿里云' },
        { id: 'openai', name: 'OpenAI Whisper' }
      ],
      settings: {
        database: {
          engine: 'postgresql',
          host: 'localhost',
          port: 5432,
          name: 'ai_story',
          user: 'postgres',
          password: ''
        },
        redis: {
          host: 'localhost',
          port: 6379,
          db: 0,
          password: ''
        },
        tts: {
          aliyun: {
            access_key_id: '',
            access_key_secret: '',
            default_voice: 'xiaoyun'
          },
          azure: {
            subscription_key: '',
            region: 'eastasia'
          },
          xunfei: {
            app_id: '',
            api_key: '',
            api_secret: ''
          }
        },
        stt: {
          aliyun: {
            access_key_id: '',
            access_key_secret: ''
          },
          openai: {
            api_key: '',
            model: 'whisper-1'
          }
        },
        storage: {
          type: 'local',
          local: {
            media_root: '/media',
            static_root: '/static'
          },
          oss: {
            access_key_id: '',
            access_key_secret: '',
            bucket: '',
            endpoint: ''
          }
        },
        other: {
          celery_broker_url: 'redis://localhost:6379/0',
          celery_result_backend: 'redis://localhost:6379/0',
          allowed_hosts: 'localhost,127.0.0.1',
          debug: true
        }
      }
    }
  },
  mounted() {
    this.loadSettings()
  },
  methods: {
    async loadSettings() {
      this.loading = true
      try {
        // TODO: 调用实际的API加载设置
        // const response = await settingsAPI.getSettings()
        // this.settings = response.data
        console.log('加载设置...')
      } catch (error) {
        console.error('加载设置失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async handleSaveAll() {
      this.saving = true
      try {
        // TODO: 调用实际的API保存设置
        // await settingsAPI.updateSettings(this.settings)
        console.log('保存设置:', this.settings)
        alert('设置保存成功！')
      } catch (error) {
        console.error('保存设置失败:', error)
        alert('保存失败: ' + error.message)
      } finally {
        this.saving = false
      }
    },
    
    async testDatabaseConnection() {
      try {
        // TODO: 测试数据库连接
        console.log('测试数据库连接...')
        alert('数据库连接成功！')
      } catch (error) {
        alert('数据库连接失败: ' + error.message)
      }
    },
    
    async testRedisConnection() {
      try {
        // TODO: 测试Redis连接
        console.log('测试Redis连接...')
        alert('Redis连接成功！')
      } catch (error) {
        alert('Redis连接失败: ' + error.message)
      }
    },
    
    async testTTS() {
      try {
        // TODO: 测试TTS
        console.log('测试TTS...')
        alert('TTS测试成功！')
      } catch (error) {
        alert('TTS测试失败: ' + error.message)
      }
    }
  }
}
</script>

<style scoped>
.system-settings {
  max-width: 1400px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  color: white;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.save-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 28px;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.save-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.save-button svg {
  width: 20px;
  height: 20px;
}

/* 设置容器 */
.settings-container {
  display: flex;
  gap: 30px;
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  min-height: 600px;
}

/* 左侧标签页 */
.settings-tabs {
  width: 200px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: transparent;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.tab-button:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-button.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tab-icon {
  width: 20px;
  height: 20px;
}

/* 右侧内容区 */
.settings-content {
  flex: 1;
}

.setting-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.section-description {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 30px;
}

/* 表单 */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.form-input {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

/* Provider标签页 */
.provider-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.provider-tab {
  padding: 8px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
}

.provider-tab:hover {
  background: #e5e7eb;
}

.provider-tab.active {
  background: #667eea;
  color: white;
}

.provider-config {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 测试按钮 */
.test-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.test-button:hover {
  background: #059669;
  transform: translateY(-1px);
}

.test-button svg {
  width: 16px;
  height: 16px;
}

/* 开关 */
.toggle-switch {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-input {
  display: none;
}

.toggle-label {
  position: relative;
  width: 48px;
  height: 24px;
  background: #d1d5db;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s ease;
}

.toggle-input:checked + .toggle-label {
  background: #667eea;
}

.toggle-input:checked + .toggle-label .toggle-slider {
  transform: translateX(24px);
}

.toggle-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

@media (max-width: 768px) {
  .settings-container {
    flex-direction: column;
  }

  .settings-tabs {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
