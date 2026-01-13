/**
 * 通知服务
 * 提供分级的用户提示系统（Toast、通知栏、弹窗）
 */

const NOTIFICATION_TYPES = {
  TOAST: 'toast',
  NOTIFICATION: 'notification',
  MODAL: 'modal',
};

const NOTIFICATION_LEVELS = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
};

class NotificationService {
  constructor() {
    this.listeners = [];
    this.queue = [];
    this.maxQueue = 5;
  }

  /**
   * 显示Toast提示（轻量提示）
   * @param {string} message - 提示消息
   * @param {Object} options - 配置选项
   */
  toast(message, options = {}) {
    const notification = {
      id: `toast_${Date.now()}`,
      type: NOTIFICATION_TYPES.TOAST,
      level: options.level || NOTIFICATION_LEVELS.INFO,
      message,
      duration: options.duration || 3000,
      icon: options.icon,
      closable: options.closable !== false,
      timestamp: Date.now(),
    };

    this.show(notification);
  }

  /**
   * 显示成功提示
   */
  success(message, options = {}) {
    this.toast(message, {
      ...options,
      level: NOTIFICATION_LEVELS.SUCCESS,
      icon: options.icon || '✨',
    });
  }

  /**
   * 显示错误提示
   */
  error(message, options = {}) {
    const notification = {
      id: `error_${Date.now()}`,
      type: options.persistent ? NOTIFICATION_TYPES.NOTIFICATION : NOTIFICATION_TYPES.TOAST,
      level: NOTIFICATION_LEVELS.ERROR,
      message,
      suggestion: options.suggestion,
      duration: options.duration || 5000,
      closable: true,
      canRetry: options.canRetry,
      onRetry: options.onRetry,
      timestamp: Date.now(),
    };

    this.show(notification);
  }

  /**
   * 显示警告提示
   */
  warning(message, options = {}) {
    this.toast(message, {
      ...options,
      level: NOTIFICATION_LEVELS.WARNING,
      duration: options.duration || 4000,
    });
  }

  /**
   * 显示信息提示
   */
  info(message, options = {}) {
    this.toast(message, {
      ...options,
      level: NOTIFICATION_LEVELS.INFO,
    });
  }

  /**
   * 显示通知栏（重要提示）
   * @param {string} message - 通知消息
   * @param {Object} options - 配置选项
   */
  notify(message, options = {}) {
    const notification = {
      id: `notify_${Date.now()}`,
      type: NOTIFICATION_TYPES.NOTIFICATION,
      level: options.level || NOTIFICATION_LEVELS.INFO,
      title: options.title,
      message,
      duration: options.duration || 0, // 0表示不自动关闭
      closable: options.closable !== false,
      actions: options.actions,
      timestamp: Date.now(),
    };

    this.show(notification);
  }

  /**
   * 显示确认弹窗（关键操作确认）
   * @param {string} message - 确认消息
   * @param {Object} options - 配置选项
   * @returns {Promise<boolean>}
   */
  confirm(message, options = {}) {
    return new Promise((resolve) => {
      const notification = {
        id: `modal_${Date.now()}`,
        type: NOTIFICATION_TYPES.MODAL,
        level: options.level || NOTIFICATION_LEVELS.WARNING,
        title: options.title || '确认操作',
        message,
        confirmText: options.confirmText || '确定',
        cancelText: options.cancelText || '取消',
        onConfirm: () => resolve(true),
        onCancel: () => resolve(false),
        timestamp: Date.now(),
      };

      this.show(notification);
    });
  }

  /**
   * 显示进度通知
   * @param {string} message - 进度消息
   * @param {number} progress - 进度百分比
   * @param {Object} options - 配置选项
   */
  progress(message, progress, options = {}) {
    const notification = {
      id: options.id || `progress_${Date.now()}`,
      type: NOTIFICATION_TYPES.NOTIFICATION,
      level: NOTIFICATION_LEVELS.INFO,
      message,
      progress,
      closable: options.closable || false,
      canCancel: options.canCancel,
      onCancel: options.onCancel,
      timestamp: Date.now(),
    };

    this.show(notification);
    return notification.id;
  }

  /**
   * 更新进度通知
   */
  updateProgress(id, message, progress) {
    this.update(id, { message, progress });
  }

  /**
   * 显示网络状态通知
   */
  networkStatus(isOnline, offlineDuration = 0) {
    if (!isOnline) {
      this.notify('网络已断开，请检查网络连接', {
        id: 'network_offline',
        level: NOTIFICATION_LEVELS.WARNING,
        title: '网络状态',
        closable: false,
      });
    } else {
      // 移除离线通知
      this.remove('network_offline');
      
      if (offlineDuration > 0) {
        this.success('网络已恢复，正在重新连接～', {
          duration: 3000,
        });
      }
    }
  }

  /**
   * 显示任务完成通知
   */
  taskComplete(taskName, options = {}) {
    this.notify(`${taskName}已完成`, {
      level: NOTIFICATION_LEVELS.SUCCESS,
      title: '任务完成',
      message: options.message || '快去看看吧～',
      duration: 5000,
      actions: options.actions,
    });
  }

  /**
   * 显示任务失败通知
   */
  taskFailed(taskName, error, options = {}) {
    this.notify(`${taskName}失败`, {
      level: NOTIFICATION_LEVELS.ERROR,
      title: '任务失败',
      message: error.friendlyMessage || error.message,
      suggestion: error.suggestion,
      duration: 0,
      canRetry: error.canRetry,
      onRetry: options.onRetry,
      actions: options.actions,
    });
  }

  /**
   * 显示通知
   */
  show(notification) {
    // 检查队列长度
    if (this.queue.length >= this.maxQueue) {
      // 移除最旧的Toast通知
      const oldestToast = this.queue.find((n) => n.type === NOTIFICATION_TYPES.TOAST);
      if (oldestToast) {
        this.remove(oldestToast.id);
      }
    }

    this.queue.push(notification);
    this.notifyListeners('show', notification);

    // 自动关闭
    if (notification.duration > 0) {
      setTimeout(() => {
        this.remove(notification.id);
      }, notification.duration);
    }
  }

  /**
   * 更新通知
   */
  update(id, updates) {
    const notification = this.queue.find((n) => n.id === id);
    if (notification) {
      Object.assign(notification, updates);
      this.notifyListeners('update', notification);
    }
  }

  /**
   * 移除通知
   */
  remove(id) {
    const index = this.queue.findIndex((n) => n.id === id);
    if (index !== -1) {
      const notification = this.queue[index];
      this.queue.splice(index, 1);
      this.notifyListeners('remove', notification);
    }
  }

  /**
   * 清除所有通知
   */
  clear(type = null) {
    if (type) {
      this.queue = this.queue.filter((n) => n.type !== type);
    } else {
      this.queue = [];
    }
    this.notifyListeners('clear', { type });
  }

  /**
   * 订阅通知事件
   */
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  /**
   * 通知监听器
   */
  notifyListeners(action, data) {
    this.listeners.forEach((listener) => {
      try {
        listener(action, data);
      } catch (error) {
        console.error('[NotificationService] 监听器执行失败:', error);
      }
    });
  }

  /**
   * 获取所有通知
   */
  getAll() {
    return [...this.queue];
  }

  /**
   * 获取指定类型的通知
   */
  getByType(type) {
    return this.queue.filter((n) => n.type === type);
  }
}

const notificationService = new NotificationService();

export default notificationService;
export { NOTIFICATION_TYPES, NOTIFICATION_LEVELS };
