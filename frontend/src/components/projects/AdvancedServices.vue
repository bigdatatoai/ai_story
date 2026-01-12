<template>
  <div class="advanced-services">
    <h2 class="text-xl font-bold mb-4">高级功能</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- AI配音 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">🎙️ AI配音</h3>
          <p class="text-sm text-base-content/70 mb-3">将文本转换为自然语音</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">输入文本</span>
            </label>
            <textarea
              v-model="ttsForm.text"
              class="textarea textarea-bordered"
              placeholder="请输入要转换的文本..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">选择声音</span>
            </label>
            <select v-model="ttsForm.voice" class="select select-bordered">
              <option value="xiaoyun">小云（女声）</option>
              <option value="xiaogang">小刚（男声）</option>
              <option value="ruoxi">若曦（温柔女声）</option>
            </select>
          </div>
          
          <button
            @click="generateVoiceover"
            class="btn btn-primary btn-sm mt-2"
            :disabled="ttsLoading || !ttsForm.text"
          >
            <span v-if="ttsLoading" class="loading loading-spinner loading-xs"></span>
            {{ ttsLoading ? '生成中...' : '生成配音' }}
          </button>
          
          <div v-if="ttsResult" class="alert alert-success mt-2">
            <span>✓ 配音已生成：{{ ttsResult }}</span>
          </div>
        </div>
      </div>

      <!-- 字幕生成 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">💬 字幕生成</h3>
          <p class="text-sm text-base-content/70 mb-3">自动识别视频语音并生成字幕</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">视频路径</span>
            </label>
            <input
              v-model="sttForm.videoPath"
              type="text"
              class="input input-bordered"
              placeholder="/path/to/video.mp4"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">语言</span>
            </label>
            <select v-model="sttForm.language" class="select select-bordered">
              <option value="zh">中文</option>
              <option value="en">英文</option>
            </select>
          </div>
          
          <button
            @click="generateSubtitles"
            class="btn btn-primary btn-sm mt-2"
            :disabled="sttLoading || !sttForm.videoPath"
          >
            <span v-if="sttLoading" class="loading loading-spinner loading-xs"></span>
            {{ sttLoading ? '生成中...' : '生成字幕' }}
          </button>
          
          <div v-if="sttResult" class="alert alert-success mt-2">
            <span>✓ 字幕已生成</span>
          </div>
        </div>
      </div>

      <!-- 背景音乐 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">🎵 背景音乐</h3>
          <p class="text-sm text-base-content/70 mb-3">为视频添加背景音乐</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">视频路径</span>
            </label>
            <input
              v-model="musicForm.videoPath"
              type="text"
              class="input input-bordered"
              placeholder="/path/to/video.mp4"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">音乐路径</span>
            </label>
            <input
              v-model="musicForm.musicPath"
              type="text"
              class="input input-bordered"
              placeholder="/path/to/music.mp3"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">音量 ({{ musicForm.volume }})</span>
            </label>
            <input
              v-model.number="musicForm.volume"
              type="range"
              min="0"
              max="1"
              step="0.1"
              class="range range-primary range-sm"
            />
          </div>
          
          <button
            @click="addBackgroundMusic"
            class="btn btn-primary btn-sm mt-2"
            :disabled="musicLoading || !musicForm.videoPath || !musicForm.musicPath"
          >
            <span v-if="musicLoading" class="loading loading-spinner loading-xs"></span>
            {{ musicLoading ? '处理中...' : '添加音乐' }}
          </button>
          
          <div v-if="musicResult" class="alert alert-success mt-2">
            <span>✓ 音乐已添加：{{ musicResult }}</span>
          </div>
        </div>
      </div>

      <!-- 视频去重 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">🔄 视频去重</h3>
          <p class="text-sm text-base-content/70 mb-3">应用去重技术避免平台检测</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">视频路径</span>
            </label>
            <input
              v-model="dedupForm.videoPath"
              type="text"
              class="input input-bordered"
              placeholder="/path/to/video.mp4"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">去重方法</span>
            </label>
            <select v-model="dedupForm.method" class="select select-bordered">
              <option value="mirror">镜像翻转</option>
              <option value="speed">变速</option>
              <option value="crop">裁剪</option>
              <option value="filter">滤镜</option>
            </select>
          </div>
          
          <button
            @click="deduplicateVideo"
            class="btn btn-primary btn-sm mt-2"
            :disabled="dedupLoading || !dedupForm.videoPath"
          >
            <span v-if="dedupLoading" class="loading loading-spinner loading-xs"></span>
            {{ dedupLoading ? '处理中...' : '去重处理' }}
          </button>
          
          <div v-if="dedupResult" class="alert alert-success mt-2">
            <span>✓ 去重完成：{{ dedupResult }}</span>
          </div>
        </div>
      </div>

      <!-- 平台发布 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">📤 平台发布</h3>
          <p class="text-sm text-base-content/70 mb-3">一键发布到多个平台</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">视频路径</span>
            </label>
            <input
              v-model="publishForm.videoPath"
              type="text"
              class="input input-bordered"
              placeholder="/path/to/video.mp4"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">选择平台</span>
            </label>
            <select v-model="publishForm.platform" class="select select-bordered">
              <option value="douyin">抖音</option>
              <option value="kuaishou">快手</option>
              <option value="bilibili">B站</option>
            </select>
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">标题</span>
            </label>
            <input
              v-model="publishForm.title"
              type="text"
              class="input input-bordered"
              placeholder="视频标题"
            />
          </div>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">描述</span>
            </label>
            <textarea
              v-model="publishForm.description"
              class="textarea textarea-bordered"
              placeholder="视频描述"
              rows="2"
            ></textarea>
          </div>
          
          <button
            @click="publishToPlatform"
            class="btn btn-primary btn-sm mt-2"
            :disabled="publishLoading || !publishForm.videoPath || !publishForm.title"
          >
            <span v-if="publishLoading" class="loading loading-spinner loading-xs"></span>
            {{ publishLoading ? '发布中...' : '发布视频' }}
          </button>
          
          <div v-if="publishResult" class="alert alert-success mt-2">
            <span>✓ 已发布到 {{ publishForm.platform }}</span>
          </div>
        </div>
      </div>

      <!-- 批量处理 -->
      <div class="card bg-base-100 border border-base-300">
        <div class="card-body">
          <h3 class="card-title text-lg">⚡ 批量处理</h3>
          <p class="text-sm text-base-content/70 mb-3">批量处理多个项目</p>
          
          <div class="form-control">
            <label class="label">
              <span class="label-text">操作类型</span>
            </label>
            <select v-model="batchForm.operation" class="select select-bordered">
              <option value="export">批量导出</option>
              <option value="publish">批量发布</option>
              <option value="dedup">批量去重</option>
            </select>
          </div>
          
          <div class="alert alert-info mt-2">
            <span>💡 将处理当前项目及其关联项目</span>
          </div>
          
          <button
            @click="batchProcess"
            class="btn btn-primary btn-sm mt-2"
            :disabled="batchLoading"
          >
            <span v-if="batchLoading" class="loading loading-spinner loading-xs"></span>
            {{ batchLoading ? '处理中...' : '开始批量处理' }}
          </button>
          
          <div v-if="batchResult" class="alert alert-success mt-2">
            <span>✓ 批量任务已启动：{{ batchResult }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import advancedAPI from '@/api/advanced'

export default {
  name: 'AdvancedServices',
  props: {
    projectId: {
      type: String,
      required: true
    },
    project: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      // AI配音
      ttsForm: {
        text: '',
        voice: 'xiaoyun',
        provider: 'aliyun'
      },
      ttsLoading: false,
      ttsResult: null,
      
      // 字幕生成
      sttForm: {
        videoPath: '',
        language: 'zh'
      },
      sttLoading: false,
      sttResult: null,
      
      // 背景音乐
      musicForm: {
        videoPath: '',
        musicPath: '',
        volume: 0.3
      },
      musicLoading: false,
      musicResult: null,
      
      // 视频去重
      dedupForm: {
        videoPath: '',
        method: 'mirror'
      },
      dedupLoading: false,
      dedupResult: null,
      
      // 平台发布
      publishForm: {
        videoPath: '',
        platform: 'douyin',
        title: '',
        description: '',
        tags: []
      },
      publishLoading: false,
      publishResult: null,
      
      // 批量处理
      batchForm: {
        operation: 'export'
      },
      batchLoading: false,
      batchResult: null
    }
  },
  methods: {
    async generateVoiceover() {
      this.ttsLoading = true
      this.ttsResult = null
      
      try {
        const response = await advancedAPI.generateVoiceover(this.projectId, {
          text: this.ttsForm.text,
          voice: this.ttsForm.voice,
          provider: this.ttsForm.provider
        })
        
        if (response.success) {
          this.ttsResult = response.audio_path
          alert('AI配音生成成功！')
        }
      } catch (error) {
        console.error('AI配音失败:', error)
        alert('AI配音失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.ttsLoading = false
      }
    },
    
    async generateSubtitles() {
      this.sttLoading = true
      this.sttResult = null
      
      try {
        const response = await advancedAPI.generateSubtitles(this.projectId, {
          video_path: this.sttForm.videoPath,
          language: this.sttForm.language
        })
        
        if (response.success) {
          this.sttResult = response.subtitles
          alert('字幕生成成功！')
        }
      } catch (error) {
        console.error('字幕生成失败:', error)
        alert('字幕生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.sttLoading = false
      }
    },
    
    async addBackgroundMusic() {
      this.musicLoading = true
      this.musicResult = null
      
      try {
        const response = await advancedAPI.addBackgroundMusic(this.projectId, {
          video_path: this.musicForm.videoPath,
          music_path: this.musicForm.musicPath,
          volume: this.musicForm.volume
        })
        
        if (response.success) {
          this.musicResult = response.output_path
          alert('背景音乐添加成功！')
        }
      } catch (error) {
        console.error('背景音乐添加失败:', error)
        alert('背景音乐添加失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.musicLoading = false
      }
    },
    
    async deduplicateVideo() {
      this.dedupLoading = true
      this.dedupResult = null
      
      try {
        const response = await advancedAPI.deduplicateVideo(this.projectId, {
          video_path: this.dedupForm.videoPath,
          method: this.dedupForm.method
        })
        
        if (response.success) {
          this.dedupResult = response.output_path
          alert('视频去重成功！')
        }
      } catch (error) {
        console.error('视频去重失败:', error)
        alert('视频去重失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.dedupLoading = false
      }
    },
    
    async publishToPlatform() {
      this.publishLoading = true
      this.publishResult = null
      
      try {
        const response = await advancedAPI.publishToPlatform(this.projectId, {
          video_path: this.publishForm.videoPath,
          platform: this.publishForm.platform,
          title: this.publishForm.title,
          description: this.publishForm.description,
          tags: this.publishForm.tags
        })
        
        if (response.success) {
          this.publishResult = response.result
          alert(`已成功发布到 ${this.publishForm.platform}！`)
        }
      } catch (error) {
        console.error('平台发布失败:', error)
        alert('平台发布失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.publishLoading = false
      }
    },
    
    async batchProcess() {
      this.batchLoading = true
      this.batchResult = null
      
      try {
        const response = await advancedAPI.batchProcess({
          project_ids: [this.projectId],
          operation: this.batchForm.operation,
          params: {}
        })
        
        if (response.success) {
          this.batchResult = response.task_id
          alert('批量处理任务已启动！')
        }
      } catch (error) {
        console.error('批量处理失败:', error)
        alert('批量处理失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.batchLoading = false
      }
    }
  }
}
</script>

<style scoped>
.advanced-services {
  max-width: 1200px;
}
</style>
