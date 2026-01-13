/**
 * 进度追踪服务
 * 统一管理WebSocket连接和任务进度更新
 */

import { createStageWSClient } from '@/utils/wsClient';
import store from '@/store';

class ProgressTracker {
  constructor() {
    this.connections = new Map();
    this.heartbeatIntervals = new Map();
  }

  /**
   * 开始追踪任务进度
   * @param {string} taskId - 任务ID
   * @param {string} projectId - 项目ID
   * @param {string} stageName - 阶段名称
   * @param {Object} callbacks - 回调函数
   */
  startTracking(taskId, projectId, stageName, callbacks = {}) {
    // 如果已存在连接，先断开
    if (this.connections.has(taskId)) {
      this.stopTracking(taskId);
    }

    const wsClient = createStageWSClient(projectId, stageName, {
      heartbeat: true,
    });

    // 连接打开
    wsClient.on('open', () => {
      console.log(`[ProgressTracker] 任务 ${taskId} 连接已建立`);
      if (callbacks.onConnect) {
        callbacks.onConnect();
      }
    });

    // 接收进度消息
    wsClient.on('message', (data) => {
      this.handleProgressMessage(taskId, data, callbacks);
    });

    // 处理特定事件类型
    wsClient.on('progress', (data) => {
      this.handleProgressUpdate(taskId, data, callbacks);
    });

    wsClient.on('completed', (data) => {
      this.handleTaskCompleted(taskId, data, callbacks);
    });

    wsClient.on('failed', (data) => {
      this.handleTaskFailed(taskId, data, callbacks);
    });

    // 连接错误
    wsClient.on('error', (error) => {
      console.error(`[ProgressTracker] 任务 ${taskId} 连接错误:`, error);
      if (callbacks.onError) {
        callbacks.onError(error);
      }
    });

    // 连接关闭
    wsClient.on('close', (event) => {
      console.log(`[ProgressTracker] 任务 ${taskId} 连接关闭`);
      this.cleanup(taskId);
      if (callbacks.onDisconnect) {
        callbacks.onDisconnect(event);
      }
    });

    this.connections.set(taskId, wsClient);
    
    // 存储到Vuex
    store.dispatch('tasks/connectTaskWS', { taskId, connection: wsClient });

    return wsClient;
  }

  /**
   * 处理进度消息
   */
  handleProgressMessage(taskId, data, callbacks) {
    console.log(`[ProgressTracker] 任务 ${taskId} 收到消息:`, data);

    if (callbacks.onMessage) {
      callbacks.onMessage(data);
    }

    // 更新Vuex状态
    if (data.progress !== undefined) {
      store.dispatch('tasks/updateTaskProgress', {
        taskId,
        stage: data.stage || data.type,
        progress: data.progress,
        message: data.message || data.status_message,
      });
    }
  }

  /**
   * 处理进度更新
   */
  handleProgressUpdate(taskId, data, callbacks) {
    const { stage, progress, message, metadata } = data;

    store.dispatch('tasks/updateTaskProgress', {
      taskId,
      stage,
      progress,
      message,
    });

    if (callbacks.onProgress) {
      callbacks.onProgress({ stage, progress, message, metadata });
    }
  }

  /**
   * 处理任务完成
   */
  handleTaskCompleted(taskId, data, callbacks) {
    console.log(`[ProgressTracker] 任务 ${taskId} 已完成:`, data);

    store.dispatch('tasks/completeTask', {
      taskId,
      result: data.result || data.data,
    });

    if (callbacks.onComplete) {
      callbacks.onComplete(data.result || data.data);
    }

    this.stopTracking(taskId);
  }

  /**
   * 处理任务失败
   */
  handleTaskFailed(taskId, data, callbacks) {
    console.error(`[ProgressTracker] 任务 ${taskId} 失败:`, data);

    store.dispatch('tasks/failTask', {
      taskId,
      error: data.error || data.message,
    });

    if (callbacks.onFail) {
      callbacks.onFail(data.error || data.message);
    }

    this.stopTracking(taskId);
  }

  /**
   * 停止追踪任务
   */
  stopTracking(taskId) {
    const connection = this.connections.get(taskId);
    if (connection) {
      connection.disconnect();
      this.connections.delete(taskId);
    }

    this.cleanup(taskId);
  }

  /**
   * 清理资源
   */
  cleanup(taskId) {
    // 清理心跳定时器
    const interval = this.heartbeatIntervals.get(taskId);
    if (interval) {
      clearInterval(interval);
      this.heartbeatIntervals.delete(taskId);
    }
  }

  /**
   * 停止所有追踪
   */
  stopAll() {
    this.connections.forEach((connection, taskId) => {
      this.stopTracking(taskId);
    });
  }

  /**
   * 获取连接状态
   */
  isTracking(taskId) {
    const connection = this.connections.get(taskId);
    return connection && connection.isConnected();
  }

  /**
   * 获取所有活动连接
   */
  getActiveConnections() {
    return Array.from(this.connections.keys());
  }
}

// 创建单例实例
const progressTracker = new ProgressTracker();

export default progressTracker;
