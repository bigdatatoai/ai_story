<template>
  <div class="parameter-config">
    <h3 class="step-title">设置参数</h3>
    <p class="step-description">配置视频的生成参数</p>

    <div class="param-group">
      <label class="param-label">视频时长</label>
      <div class="duration-options">
        <button
          v-for="duration in durations"
          :key="duration.value"
          class="duration-btn"
          :class="{ active: formData.duration === duration.value }"
          @click="selectDuration(duration.value)"
        >
          {{ duration.label }}
        </button>
      </div>
    </div>

    <div class="param-group">
      <label class="param-label">视频分辨率</label>
      <select v-model="formData.resolution" class="param-select" @change="handleUpdate">
        <option value="720p">720p (标清)</option>
        <option value="1080p">1080p (高清)</option>
        <option value="4k">4K (超清)</option>
      </select>
    </div>

    <div class="param-group">
      <label class="param-label">视频风格</label>
      <div class="style-grid">
        <div
          v-for="style in styles"
          :key="style.value"
          class="style-card"
          :class="{ selected: formData.style === style.value }"
          @click="selectStyle(style.value)"
        >
          <div class="style-icon">{{ style.icon }}</div>
          <div class="style-name">{{ style.label }}</div>
        </div>
      </div>
    </div>

    <div class="param-group">
      <label class="param-label">
        <input
          v-model="formData.addSubtitles"
          type="checkbox"
          @change="handleUpdate"
        />
        添加字幕
      </label>
    </div>

    <div class="param-group">
      <label class="param-label">
        <input
          v-model="formData.addWatermark"
          type="checkbox"
          @change="handleUpdate"
        />
        添加水印
      </label>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParameterConfig',
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
  data() {
    return {
      formData: {
        duration: 60,
        resolution: '1080p',
        style: 'default',
        addSubtitles: true,
        addWatermark: false
      },
      durations: [
        { value: 30, label: '30秒' },
        { value: 60, label: '60秒' },
        { value: 120, label: '2分钟' },
        { value: 180, label: '3分钟' }
      ],
      styles: [
        { value: 'default', label: '默认', icon: '🎨' },
        { value: 'cartoon', label: '卡通', icon: '🎭' },
        { value: 'realistic', label: '写实', icon: '📸' },
        { value: 'watercolor', label: '水彩', icon: '🖌️' }
      ]
    };
  },
  mounted() {
    if (this.data.parameters) {
      this.formData = { ...this.formData, ...this.data.parameters };
    }
  },
  methods: {
    handleUpdate() {
      this.$emit('update', { parameters: this.formData });
    },

    selectDuration(value) {
      this.formData.duration = value;
      this.handleUpdate();
    },

    selectStyle(value) {
      this.formData.style = value;
      this.handleUpdate();
    }
  }
};
</script>

<style scoped>
.parameter-config {
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

.param-group {
  margin-bottom: 2rem;
}

.param-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.75rem;
}

.duration-options {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.duration-btn {
  padding: 0.75rem 1.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s;
}

.duration-btn:hover {
  border-color: #3b82f6;
}

.duration-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.param-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.style-card {
  padding: 1.5rem 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.75rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.style-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
}

.style-card.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.style-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.style-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
}
</style>
