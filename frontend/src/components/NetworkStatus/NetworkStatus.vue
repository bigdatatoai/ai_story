<template>
  <transition name="slide-down">
    <div v-if="!isOnline" class="network-status offline">
      <div class="status-content">
        <span class="status-icon">📡</span>
        <div class="status-text">
          <p class="status-message">网络已断开，请检查网络连接</p>
          <p v-if="offlineDuration > 0" class="status-detail">
            已断开 {{ formatDuration(offlineDuration) }}
          </p>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import networkMonitor from '@/services/networkMonitor';

export default {
  name: 'NetworkStatus',
  data() {
    return {
      isOnline: true,
      offlineDuration: 0,
      updateInterval: null,
    };
  },
  mounted() {
    this.isOnline = networkMonitor.isOnline;
    
    this.unsubscribe = networkMonitor.subscribe({
      onOnline: this.handleOnline,
      onOffline: this.handleOffline,
    });

    if (!this.isOnline) {
      this.startUpdateInterval();
    }
  },
  beforeDestroy() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    this.stopUpdateInterval();
  },
  methods: {
    handleOnline({ offlineDuration }) {
      this.isOnline = true;
      this.stopUpdateInterval();
      
      if (offlineDuration > 0) {
        this.$message.success('网络已恢复，正在重新连接～');
      }
    },
    
    handleOffline() {
      this.isOnline = false;
      this.startUpdateInterval();
    },
    
    startUpdateInterval() {
      this.updateInterval = setInterval(() => {
        const status = networkMonitor.getStatus();
        this.offlineDuration = status.offlineDuration;
      }, 1000);
    },
    
    stopUpdateInterval() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
      this.offlineDuration = 0;
    },
    
    formatDuration(ms) {
      const seconds = Math.floor(ms / 1000);
      if (seconds < 60) return `${seconds}秒`;
      const minutes = Math.floor(seconds / 60);
      return `${minutes}分钟`;
    },
  },
};
</script>

<style scoped>
.network-status {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  padding: 1rem;
  background: #fef2f2;
  border-bottom: 2px solid #dc2626;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.network-status.offline {
  background: #fef2f2;
  border-bottom-color: #dc2626;
}

.status-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-icon {
  font-size: 1.5rem;
}

.status-message {
  color: #dc2626;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.status-detail {
  color: #6b7280;
  font-size: 0.875rem;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter,
.slide-down-leave-to {
  transform: translateY(-100%);
  opacity: 0;
}
</style>
