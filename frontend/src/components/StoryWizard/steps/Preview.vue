<template>
  <div class="preview">
    <h3 class="step-title">预览确认</h3>
    <p class="step-description">确认配置信息，准备生成视频</p>

    <div class="preview-sections">
      <!-- 模板信息 -->
      <div class="preview-section">
        <h4 class="section-title">📋 模板</h4>
        <div class="section-content">
          <p v-if="data.template">{{ data.template.name }}</p>
          <p v-else class="empty-text">未选择模板</p>
        </div>
      </div>

      <!-- 故事内容 -->
      <div class="preview-section">
        <h4 class="section-title">📝 故事内容</h4>
        <div class="section-content">
          <div class="info-row">
            <span class="info-label">标题：</span>
            <span class="info-value">{{ data.story?.title || '未填写' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">内容：</span>
            <span class="info-value preview-text">
              {{ data.story?.content || '未填写' }}
            </span>
          </div>
          <div v-if="data.story?.outline?.length > 0" class="info-row">
            <span class="info-label">大纲：</span>
            <span class="info-value">{{ data.story.outline.length }} 个场景</span>
          </div>
        </div>
      </div>

      <!-- 素材配置 -->
      <div class="preview-section">
        <h4 class="section-title">🎨 素材</h4>
        <div class="section-content">
          <div class="info-row">
            <span class="info-label">图片：</span>
            <span class="info-value">
              {{ data.materials?.images?.length || 0 }} 张
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">背景音乐：</span>
            <span class="info-value">
              {{ getAudioLabel(data.materials?.audio) }}
            </span>
          </div>
          <div class="info-row">
            <span class="info-label">背景风格：</span>
            <span class="info-value">
              {{ getBackgroundLabel(data.materials?.background) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 参数配置 -->
      <div class="preview-section">
        <h4 class="section-title">⚙️ 参数</h4>
        <div class="section-content">
          <div class="info-row">
            <span class="info-label">时长：</span>
            <span class="info-value">{{ data.parameters?.duration || 60 }}秒</span>
          </div>
          <div class="info-row">
            <span class="info-label">分辨率：</span>
            <span class="info-value">{{ data.parameters?.resolution || '1080p' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">风格：</span>
            <span class="info-value">{{ getStyleLabel(data.parameters?.style) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">字幕：</span>
            <span class="info-value">
              {{ data.parameters?.addSubtitles ? '是' : '否' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="preview-notice">
      <div class="notice-icon">💡</div>
      <div class="notice-content">
        <p class="notice-title">温馨提示</p>
        <p class="notice-text">
          视频生成需要 3-5 分钟，请耐心等待。生成过程中可以查看实时进度。
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Preview',
  props: {
    data: {
      type: Object,
      required: true
    },
    errors: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    getAudioLabel(audio) {
      const labels = {
        happy: '欢快音乐',
        calm: '舒缓音乐',
        adventure: '冒险音乐'
      };
      return labels[audio] || '无';
    },

    getBackgroundLabel(background) {
      const labels = {
        default: '默认',
        warm: '温暖',
        cool: '清凉',
        nature: '自然'
      };
      return labels[background] || '默认';
    },

    getStyleLabel(style) {
      const labels = {
        default: '默认',
        cartoon: '卡通',
        realistic: '写实',
        watercolor: '水彩'
      };
      return labels[style] || '默认';
    }
  }
};
</script>

<style scoped>
.preview {
  padding: 2rem 0;
}

.step-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.step-description {
  color: #6b7280;
  margin-bottom: 2rem;
}

.preview-sections {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.preview-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.section-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
}

.info-label {
  font-weight: 600;
  color: #6b7280;
  min-width: 80px;
}

.info-value {
  color: #1f2937;
  flex: 1;
}

.preview-text {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.empty-text {
  color: #9ca3af;
  font-style: italic;
}

.preview-notice {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 0.5rem;
}

.notice-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.notice-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.notice-text {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}
</style>
