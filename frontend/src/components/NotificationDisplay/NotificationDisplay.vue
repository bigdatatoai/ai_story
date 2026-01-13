<template>
  <div class="notification-container">
    <!-- Toast通知 -->
    <transition-group name="toast" tag="div" class="toast-container">
      <div
        v-for="notification in toasts"
        :key="notification.id"
        class="toast"
        :class="`toast-${notification.level}`"
      >
        <div class="toast-content">
          <span v-if="notification.icon" class="toast-icon">{{ notification.icon }}</span>
          <span class="toast-message">{{ notification.message }}</span>
        </div>
        <button
          v-if="notification.closable"
          class="toast-close"
          @click="closeNotification(notification.id)"
        >
          ×
        </button>
      </div>
    </transition-group>

    <!-- 通知栏 -->
    <transition-group name="notification" tag="div" class="notification-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="notification-card"
        :class="`notification-${notification.level}`"
      >
        <div class="notification-header">
          <h4 v-if="notification.title" class="notification-title">
            {{ notification.title }}
          </h4>
          <button
            v-if="notification.closable"
            class="notification-close"
            @click="closeNotification(notification.id)"
          >
            ×
          </button>
        </div>
        
        <div class="notification-body">
          <p class="notification-message">{{ notification.message }}</p>
          <p v-if="notification.suggestion" class="notification-suggestion">
            💡 {{ notification.suggestion }}
          </p>
          
          <!-- 进度条 -->
          <div v-if="notification.progress !== undefined" class="notification-progress">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${notification.progress}%` }"
              ></div>
            </div>
            <span class="progress-text">{{ notification.progress }}%</span>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div v-if="hasActions(notification)" class="notification-actions">
          <button
            v-if="notification.canRetry"
            class="btn-action btn-retry"
            @click="handleRetry(notification)"
          >
            重试
          </button>
          <button
            v-if="notification.canCancel"
            class="btn-action btn-cancel"
            @click="handleCancel(notification)"
          >
            取消
          </button>
          <button
            v-for="action in notification.actions"
            :key="action.key"
            class="btn-action"
            @click="handleAction(action, notification)"
          >
            {{ action.label }}
          </button>
        </div>
      </div>
    </transition-group>

    <!-- 确认弹窗 -->
    <transition name="modal">
      <div v-if="modal" class="modal-overlay" @click="handleModalCancel">
        <div class="modal-dialog" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ modal.title }}</h3>
          </div>
          <div class="modal-body">
            <p>{{ modal.message }}</p>
          </div>
          <div class="modal-footer">
            <button class="btn-modal btn-cancel" @click="handleModalCancel">
              {{ modal.cancelText }}
            </button>
            <button class="btn-modal btn-confirm" @click="handleModalConfirm">
              {{ modal.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import notificationService, { NOTIFICATION_TYPES } from '@/services/notificationService';

export default {
  name: 'NotificationDisplay',
  data() {
    return {
      toasts: [],
      notifications: [],
      modal: null,
    };
  },
  mounted() {
    this.unsubscribe = notificationService.subscribe(this.handleNotification);
  },
  beforeDestroy() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },
  methods: {
    handleNotification(action, notification) {
      switch (action) {
        case 'show':
          this.showNotification(notification);
          break;
        case 'update':
          this.updateNotification(notification);
          break;
        case 'remove':
          this.removeNotification(notification);
          break;
        case 'clear':
          this.clearNotifications(notification.type);
          break;
      }
    },

    showNotification(notification) {
      if (notification.type === NOTIFICATION_TYPES.TOAST) {
        this.toasts.push(notification);
      } else if (notification.type === NOTIFICATION_TYPES.NOTIFICATION) {
        this.notifications.push(notification);
      } else if (notification.type === NOTIFICATION_TYPES.MODAL) {
        this.modal = notification;
      }
    },

    updateNotification(notification) {
      if (notification.type === NOTIFICATION_TYPES.TOAST) {
        const index = this.toasts.findIndex((n) => n.id === notification.id);
        if (index !== -1) {
          this.$set(this.toasts, index, notification);
        }
      } else if (notification.type === NOTIFICATION_TYPES.NOTIFICATION) {
        const index = this.notifications.findIndex((n) => n.id === notification.id);
        if (index !== -1) {
          this.$set(this.notifications, index, notification);
        }
      }
    },

    removeNotification(notification) {
      if (notification.type === NOTIFICATION_TYPES.TOAST) {
        this.toasts = this.toasts.filter((n) => n.id !== notification.id);
      } else if (notification.type === NOTIFICATION_TYPES.NOTIFICATION) {
        this.notifications = this.notifications.filter((n) => n.id !== notification.id);
      } else if (notification.type === NOTIFICATION_TYPES.MODAL) {
        if (this.modal && this.modal.id === notification.id) {
          this.modal = null;
        }
      }
    },

    clearNotifications(type) {
      if (!type || type === NOTIFICATION_TYPES.TOAST) {
        this.toasts = [];
      }
      if (!type || type === NOTIFICATION_TYPES.NOTIFICATION) {
        this.notifications = [];
      }
      if (!type || type === NOTIFICATION_TYPES.MODAL) {
        this.modal = null;
      }
    },

    closeNotification(id) {
      notificationService.remove(id);
    },

    hasActions(notification) {
      return (
        notification.canRetry ||
        notification.canCancel ||
        (notification.actions && notification.actions.length > 0)
      );
    },

    handleRetry(notification) {
      if (notification.onRetry) {
        notification.onRetry();
      }
      this.closeNotification(notification.id);
    },

    handleCancel(notification) {
      if (notification.onCancel) {
        notification.onCancel();
      }
      this.closeNotification(notification.id);
    },

    handleAction(action, notification) {
      if (action.handler) {
        action.handler();
      }
      if (action.closeOnClick !== false) {
        this.closeNotification(notification.id);
      }
    },

    handleModalConfirm() {
      if (this.modal && this.modal.onConfirm) {
        this.modal.onConfirm();
      }
      this.modal = null;
    },

    handleModalCancel() {
      if (this.modal && this.modal.onCancel) {
        this.modal.onCancel();
      }
      this.modal = null;
    },
  },
};
</script>

<style scoped>
.notification-container {
  position: fixed;
  z-index: 10000;
}

.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 10001;
}

.toast {
  min-width: 300px;
  max-width: 500px;
  padding: 1rem 1.5rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.toast-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.toast-message {
  color: #1f2937;
  font-size: 0.875rem;
}

.toast-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.toast-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.notification-list {
  position: fixed;
  top: 5rem;
  right: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-width: 400px;
  z-index: 10000;
}

.notification-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-left: 4px solid #e5e7eb;
}

.notification-info {
  border-left-color: #3b82f6;
}

.notification-success {
  border-left-color: #10b981;
}

.notification-warning {
  border-left-color: #f59e0b;
}

.notification-error {
  border-left-color: #ef4444;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.notification-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.notification-close {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 1.5rem;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s;
}

.notification-close:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.notification-message {
  color: #374151;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.notification-suggestion {
  color: #6b7280;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.notification-progress {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 1rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  transition: width 0.3s ease;
  border-radius: 1rem;
}

.progress-text {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 600;
  min-width: 3rem;
  text-align: right;
}

.notification-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-action {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  border: none;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry {
  background: #f59e0b;
  color: white;
}

.btn-retry:hover {
  background: #d97706;
}

.btn-cancel {
  background: #6b7280;
  color: white;
}

.btn-cancel:hover {
  background: #4b5563;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10002;
}

.modal-dialog {
  background: white;
  border-radius: 0.75rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.modal-body {
  padding: 1.5rem;
  color: #374151;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-modal {
  padding: 0.5rem 1.5rem;
  border-radius: 0.5rem;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-modal.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-modal.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-modal.btn-confirm {
  background: #3b82f6;
  color: white;
}

.btn-modal.btn-confirm:hover {
  background: #2563eb;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter {
  transform: translateX(100%);
  opacity: 0;
}

.toast-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter {
  transform: translateX(100%);
  opacity: 0;
}

.notification-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter,
.modal-leave-to {
  opacity: 0;
}

.modal-enter .modal-dialog,
.modal-leave-to .modal-dialog {
  transform: scale(0.9);
}
</style>
