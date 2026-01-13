<template>
  <div class="material-config">
    <h3 class="step-title">配置素材</h3>
    <p class="step-description">上传或选择图片、音频等素材（可选）</p>

    <div class="material-section">
      <h4 class="section-title">图片素材</h4>
      <div class="upload-area">
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          multiple
          style="display: none"
          @change="handleImageUpload"
        />
        <button class="btn-upload" @click="$refs.imageInput.click()">
          📁 选择图片
        </button>
        <p class="upload-hint">支持 JPG、PNG 格式，最多上传 10 张</p>
      </div>

      <div v-if="formData.images.length > 0" class="image-list">
        <div
          v-for="(image, index) in formData.images"
          :key="index"
          class="image-item"
        >
          <img :src="image.url" :alt="`图片${index + 1}`" />
          <button class="btn-remove-image" @click="removeImage(index)">×</button>
        </div>
      </div>
    </div>

    <div class="material-section">
      <h4 class="section-title">背景音乐</h4>
      <div class="audio-selector">
        <select v-model="formData.audio" @change="handleUpdate">
          <option value="">不使用背景音乐</option>
          <option value="happy">欢快音乐</option>
          <option value="calm">舒缓音乐</option>
          <option value="adventure">冒险音乐</option>
        </select>
      </div>
    </div>

    <div class="material-section">
      <h4 class="section-title">背景风格</h4>
      <div class="background-options">
        <div
          v-for="bg in backgrounds"
          :key="bg.value"
          class="background-option"
          :class="{ selected: formData.background === bg.value }"
          @click="selectBackground(bg.value)"
        >
          <div class="bg-preview" :style="{ background: bg.color }"></div>
          <span class="bg-label">{{ bg.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaterialConfig',
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
        images: [],
        audio: null,
        background: 'default'
      },
      backgrounds: [
        { value: 'default', label: '默认', color: '#f3f4f6' },
        { value: 'warm', label: '温暖', color: '#fef3c7' },
        { value: 'cool', label: '清凉', color: '#dbeafe' },
        { value: 'nature', label: '自然', color: '#d1fae5' }
      ]
    };
  },
  mounted() {
    if (this.data.materials) {
      this.formData = { ...this.formData, ...this.data.materials };
    }
  },
  methods: {
    handleUpdate() {
      this.$emit('update', { materials: this.formData });
    },

    handleImageUpload(event) {
      const files = Array.from(event.target.files);
      files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.formData.images.push({
            url: e.target.result,
            file
          });
          this.handleUpdate();
        };
        reader.readAsDataURL(file);
      });
    },

    removeImage(index) {
      this.formData.images.splice(index, 1);
      this.handleUpdate();
    },

    selectBackground(value) {
      this.formData.background = value;
      this.handleUpdate();
    }
  }
};
</script>

<style scoped>
.material-config {
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

.material-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 1rem;
}

.upload-area {
  text-align: center;
  padding: 2rem;
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  background: white;
}

.btn-upload {
  padding: 0.75rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-upload:hover {
  background: #2563eb;
}

.upload-hint {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #9ca3af;
}

.image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 0.5rem;
  overflow: hidden;
  background: white;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  width: 24px;
  height: 24px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 1.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.audio-selector select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  background: white;
  cursor: pointer;
}

.background-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 1rem;
}

.background-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.background-option:hover {
  border-color: #3b82f6;
}

.background-option.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.bg-preview {
  width: 60px;
  height: 60px;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.bg-label {
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
}
</style>
