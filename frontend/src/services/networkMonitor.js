/**
 * 网络监控服务
 * 监控网络状态，处理断网重连
 */

class NetworkMonitor {
  constructor() {
    this.isOnline = navigator.onLine;
    this.listeners = [];
    this.reconnectCallbacks = [];
    this.offlineStartTime = null;
    this.init();
  }

  init() {
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
  }

  handleOnline() {
    console.log('[NetworkMonitor] 网络已恢复');
    this.isOnline = true;
    
    const offlineDuration = this.offlineStartTime 
      ? Date.now() - this.offlineStartTime 
      : 0;
    
    this.offlineStartTime = null;

    this.listeners.forEach((listener) => {
      if (listener.onOnline) {
        listener.onOnline({ offlineDuration });
      }
    });

    this.executeReconnectCallbacks();
  }

  handleOffline() {
    console.log('[NetworkMonitor] 网络已断开');
    this.isOnline = false;
    this.offlineStartTime = Date.now();

    this.listeners.forEach((listener) => {
      if (listener.onOffline) {
        listener.onOffline();
      }
    });
  }

  executeReconnectCallbacks() {
    console.log(`[NetworkMonitor] 执行 ${this.reconnectCallbacks.length} 个重连回调`);
    
    const callbacks = [...this.reconnectCallbacks];
    this.reconnectCallbacks = [];

    callbacks.forEach((callback) => {
      try {
        callback();
      } catch (error) {
        console.error('[NetworkMonitor] 重连回调执行失败:', error);
      }
    });
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener);
    };
  }

  onReconnect(callback) {
    if (this.isOnline) {
      callback();
    } else {
      this.reconnectCallbacks.push(callback);
    }
  }

  getStatus() {
    return {
      isOnline: this.isOnline,
      offlineDuration: this.offlineStartTime 
        ? Date.now() - this.offlineStartTime 
        : 0,
    };
  }
}

const networkMonitor = new NetworkMonitor();

export default networkMonitor;
