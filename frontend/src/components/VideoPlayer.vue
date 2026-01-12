<template>
  <div class="video-player-container">
    <div class="video-wrapper" :class="{ 'fullscreen': isFullscreen }">
      <video
        ref="videoElement"
        :src="videoUrl"
        :poster="posterUrl"
        @loadedmetadata="onLoadedMetadata"
        @timeupdate="onTimeUpdate"
        @ended="onEnded"
        @play="isPlaying = true"
        @pause="isPlaying = false"
        class="video-element"
      ></video>

      <!-- 控制栏 -->
      <div class="controls" v-show="showControls">
        <!-- 进度条 -->
        <div class="progress-bar" @click="seek">
          <div class="progress-filled" :style="{ width: progressPercent + '%' }"></div>
          <div class="progress-handle" :style="{ left: progressPercent + '%' }"></div>
        </div>

        <!-- 按钮组 -->
        <div class="controls-buttons">
          <div class="left-controls">
            <!-- 播放/暂停 -->
            <button @click="togglePlay" class="control-btn">
              <svg v-if="!isPlaying" class="icon" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <svg v-else class="icon" viewBox="0 0 24 24">
                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
              </svg>
            </button>

            <!-- 时间显示 -->
            <span class="time-display">
              {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
            </span>
          </div>

          <div class="right-controls">
            <!-- 音量控制 -->
            <div class="volume-control">
              <button @click="toggleMute" class="control-btn">
                <svg v-if="!isMuted && volume > 0.5" class="icon" viewBox="0 0 24 24">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
                </svg>
                <svg v-else-if="!isMuted && volume > 0" class="icon" viewBox="0 0 24 24">
                  <path d="M7 9v6h4l5 5V4l-5 5H7z"/>
                </svg>
                <svg v-else class="icon" viewBox="0 0 24 24">
                  <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                </svg>
              </button>
              <input
                type="range"
                min="0"
                max="100"
                v-model="volumePercent"
                @input="changeVolume"
                class="volume-slider"
              />
            </div>

            <!-- 全屏 -->
            <button @click="toggleFullscreen" class="control-btn">
              <svg v-if="!isFullscreen" class="icon" viewBox="0 0 24 24">
                <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
              </svg>
              <svg v-else class="icon" viewBox="0 0 24 24">
                <path d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoPlayer',
  props: {
    videoUrl: {
      type: String,
      required: true
    },
    posterUrl: {
      type: String,
      default: ''
    },
    autoplay: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      volume: 1,
      isMuted: false,
      isFullscreen: false,
      showControls: true,
      loading: true,
      controlsTimeout: null
    }
  },
  computed: {
    progressPercent() {
      if (!this.duration) return 0
      return (this.currentTime / this.duration) * 100
    },
    volumePercent: {
      get() {
        return this.volume * 100
      },
      set(value) {
        this.volume = value / 100
      }
    }
  },
  mounted() {
    if (this.autoplay) {
      this.play()
    }
    this.$refs.videoElement.volume = this.volume
  },
  methods: {
    togglePlay() {
      if (this.isPlaying) {
        this.pause()
      } else {
        this.play()
      }
    },
    play() {
      this.$refs.videoElement.play()
      this.isPlaying = true
      this.$emit('play')
    },
    pause() {
      this.$refs.videoElement.pause()
      this.isPlaying = false
      this.$emit('pause')
    },
    seek(event) {
      const progressBar = event.currentTarget
      const clickX = event.offsetX
      const width = progressBar.offsetWidth
      const percent = clickX / width
      this.currentTime = percent * this.duration
      this.$refs.videoElement.currentTime = this.currentTime
    },
    toggleMute() {
      this.isMuted = !this.isMuted
      this.$refs.videoElement.muted = this.isMuted
    },
    changeVolume() {
      this.$refs.videoElement.volume = this.volume
      if (this.volume > 0) {
        this.isMuted = false
        this.$refs.videoElement.muted = false
      }
    },
    toggleFullscreen() {
      const container = this.$refs.videoElement
      if (!this.isFullscreen) {
        if (container.requestFullscreen) {
          container.requestFullscreen()
        } else if (container.webkitRequestFullscreen) {
          container.webkitRequestFullscreen()
        } else if (container.mozRequestFullScreen) {
          container.mozRequestFullScreen()
        }
        this.isFullscreen = true
      } else {
        if (document.exitFullscreen) {
          document.exitFullscreen()
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen()
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen()
        }
        this.isFullscreen = false
      }
    },
    onLoadedMetadata() {
      this.duration = this.$refs.videoElement.duration
      this.loading = false
      this.$emit('loaded', { duration: this.duration })
    },
    onTimeUpdate() {
      this.currentTime = this.$refs.videoElement.currentTime
      this.$emit('timeupdate', { currentTime: this.currentTime })
    },
    onEnded() {
      this.isPlaying = false
      this.$emit('ended')
    },
    formatTime(seconds) {
      if (!seconds || isNaN(seconds)) return '00:00'
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.video-player-container {
  width: 100%;
  max-width: 100%;
}

.video-wrapper {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-wrapper.fullscreen {
  border-radius: 0;
}

.video-element {
  width: 100%;
  height: auto;
  display: block;
}

.controls {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
  padding: 20px 16px 16px;
  transition: opacity 0.3s;
}

.progress-bar {
  position: relative;
  height: 4px;
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
  cursor: pointer;
  margin-bottom: 12px;
}

.progress-filled {
  height: 100%;
  background: #3b82f6;
  border-radius: 2px;
  transition: width 0.1s;
}

.progress-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.controls-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-controls,
.right-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-btn {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.control-btn:hover {
  opacity: 0.8;
}

.icon {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

.time-display {
  color: #fff;
  font-size: 14px;
  font-family: monospace;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.volume-slider {
  width: 80px;
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
}

.volume-slider::-moz-range-thumb {
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  border: none;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
