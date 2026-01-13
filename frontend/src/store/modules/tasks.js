/**
 * 任务管理模块
 * 统一管理AI生成任务的状态、进度、错误处理
 */

const STORAGE_KEY = 'ai_story_tasks';

const TASK_STATUS = {
  PENDING: 'pending',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled',
};

const TASK_STAGES = {
  TEXT_GENERATION: { key: 'text_generation', label: '正在创作故事文本', progress: 30 },
  IMAGE_GENERATION: { key: 'image_generation', label: '正在给故事配画面', progress: 60 },
  VIDEO_SYNTHESIS: { key: 'video_synthesis', label: '正在合成视频', progress: 85 },
  AUDIO_MATCHING: { key: 'audio_matching', label: '正在添加背景音乐', progress: 100 },
};

const state = {
  tasks: [],
  currentTask: null,
  activeTaskId: null,
  taskProgress: {},
  taskErrors: {},
  wsConnections: {},
};

const getters = {
  taskById: (state) => (id) => {
    return state.tasks.find((t) => t.id === id);
  },
  tasksByStatus: (state) => (status) => {
    return state.tasks.filter((t) => t.status === status);
  },
  runningTasks: (state) => {
    return state.tasks.filter((t) => t.status === TASK_STATUS.RUNNING);
  },
  failedTasks: (state) => {
    return state.tasks.filter((t) => t.status === TASK_STATUS.FAILED);
  },
  completedTasks: (state) => {
    return state.tasks.filter((t) => t.status === TASK_STATUS.COMPLETED);
  },
  taskProgress: (state) => (taskId) => {
    return state.taskProgress[taskId] || { stage: null, progress: 0, message: '' };
  },
  taskError: (state) => (taskId) => {
    return state.taskErrors[taskId] || null;
  },
  hasRunningTask: (state) => {
    return state.tasks.some((t) => t.status === TASK_STATUS.RUNNING);
  },
};

const mutations = {
  SET_TASKS(state, tasks) {
    state.tasks = tasks;
  },
  SET_CURRENT_TASK(state, task) {
    state.currentTask = task;
  },
  SET_ACTIVE_TASK_ID(state, taskId) {
    state.activeTaskId = taskId;
  },
  ADD_TASK(state, task) {
    const existingIndex = state.tasks.findIndex((t) => t.id === task.id);
    if (existingIndex !== -1) {
      state.tasks.splice(existingIndex, 1, task);
    } else {
      state.tasks.unshift(task);
    }
  },
  UPDATE_TASK(state, { taskId, updates }) {
    const task = state.tasks.find((t) => t.id === taskId);
    if (task) {
      Object.assign(task, updates);
    }
    if (state.currentTask && state.currentTask.id === taskId) {
      Object.assign(state.currentTask, updates);
    }
  },
  REMOVE_TASK(state, taskId) {
    state.tasks = state.tasks.filter((t) => t.id !== taskId);
    if (state.currentTask && state.currentTask.id === taskId) {
      state.currentTask = null;
    }
    delete state.taskProgress[taskId];
    delete state.taskErrors[taskId];
  },
  SET_TASK_PROGRESS(state, { taskId, progress }) {
    state.taskProgress = {
      ...state.taskProgress,
      [taskId]: progress,
    };
  },
  SET_TASK_ERROR(state, { taskId, error }) {
    state.taskErrors = {
      ...state.taskErrors,
      [taskId]: error,
    };
  },
  CLEAR_TASK_ERROR(state, taskId) {
    const errors = { ...state.taskErrors };
    delete errors[taskId];
    state.taskErrors = errors;
  },
  SET_WS_CONNECTION(state, { taskId, connection }) {
    state.wsConnections = {
      ...state.wsConnections,
      [taskId]: connection,
    };
  },
  REMOVE_WS_CONNECTION(state, taskId) {
    const connections = { ...state.wsConnections };
    delete connections[taskId];
    state.wsConnections = connections;
  },
};

const actions = {
  // 创建任务
  createTask({ commit, dispatch }, taskData) {
    const task = {
      id: taskData.id || `task_${Date.now()}`,
      type: taskData.type,
      status: TASK_STATUS.PENDING,
      config: taskData.config || {},
      result: null,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      ...taskData,
    };
    
    commit('ADD_TASK', task);
    dispatch('persistTasks');
    return task;
  },

  // 启动任务
  async startTask({ commit, dispatch }, taskId) {
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.RUNNING,
        startedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
    commit('SET_ACTIVE_TASK_ID', taskId);
    dispatch('persistTasks');
  },

  // 更新任务进度
  updateTaskProgress({ commit, dispatch }, { taskId, stage, progress, message }) {
    const progressData = {
      stage,
      progress,
      message: message || TASK_STAGES[stage]?.label || '',
      timestamp: Date.now(),
    };
    
    commit('SET_TASK_PROGRESS', { taskId, progress: progressData });
    commit('UPDATE_TASK', {
      taskId,
      updates: { updatedAt: new Date().toISOString() },
    });
    dispatch('persistTasks');
  },

  // 完成任务
  completeTask({ commit, dispatch }, { taskId, result }) {
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.COMPLETED,
        result,
        completedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
    commit('SET_TASK_PROGRESS', {
      taskId,
      progress: { stage: 'completed', progress: 100, message: '生成完成' },
    });
    dispatch('persistTasks');
    dispatch('disconnectTaskWS', taskId);
  },

  // 任务失败
  failTask({ commit, dispatch }, { taskId, error }) {
    const friendlyError = dispatch('getFriendlyErrorMessage', error);
    
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.FAILED,
        failedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
    commit('SET_TASK_ERROR', { taskId, error: friendlyError });
    dispatch('persistTasks');
    dispatch('disconnectTaskWS', taskId);
  },

  // 暂停任务
  pauseTask({ commit, dispatch }, taskId) {
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.PAUSED,
        pausedAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
    dispatch('persistTasks');
  },

  // 取消任务
  cancelTask({ commit, dispatch }, taskId) {
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.CANCELLED,
        cancelledAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    });
    dispatch('persistTasks');
    dispatch('disconnectTaskWS', taskId);
  },

  // 重试任务
  async retryTask({ commit, dispatch, getters }, taskId) {
    const task = getters.taskById(taskId);
    if (!task) return;

    commit('CLEAR_TASK_ERROR', taskId);
    commit('UPDATE_TASK', {
      taskId,
      updates: {
        status: TASK_STATUS.PENDING,
        result: null,
        failedAt: null,
        updatedAt: new Date().toISOString(),
      },
    });
    dispatch('persistTasks');
    
    return task;
  },

  // 删除任务
  deleteTask({ commit, dispatch }, taskId) {
    commit('REMOVE_TASK', taskId);
    dispatch('persistTasks');
    dispatch('disconnectTaskWS', taskId);
  },

  // 批量删除任务
  deleteTasks({ commit, dispatch }, taskIds) {
    taskIds.forEach((taskId) => {
      commit('REMOVE_TASK', taskId);
      dispatch('disconnectTaskWS', taskId);
    });
    dispatch('persistTasks');
  },

  // 清理已完成任务
  clearCompletedTasks({ state, dispatch }) {
    const completedIds = state.tasks
      .filter((t) => t.status === TASK_STATUS.COMPLETED)
      .map((t) => t.id);
    dispatch('deleteTasks', completedIds);
  },

  // 持久化任务到本地存储
  persistTasks({ state }) {
    try {
      const tasksToSave = state.tasks.map((task) => ({
        ...task,
        // 不保存WebSocket连接等运行时状态
        wsConnection: undefined,
      }));
      localStorage.setItem(STORAGE_KEY, JSON.stringify(tasksToSave));
    } catch (error) {
      console.error('保存任务失败:', error);
    }
  },

  // 从本地存储恢复任务
  restoreTasks({ commit }) {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const tasks = JSON.parse(saved);
        // 将运行中的任务标记为失败（因为页面刷新了）
        const restoredTasks = tasks.map((task) => {
          if (task.status === TASK_STATUS.RUNNING) {
            return {
              ...task,
              status: TASK_STATUS.FAILED,
              error: '页面刷新导致任务中断',
            };
          }
          return task;
        });
        commit('SET_TASKS', restoredTasks);
      }
    } catch (error) {
      console.error('恢复任务失败:', error);
    }
  },

  // 连接任务WebSocket
  connectTaskWS({ commit }, { taskId, connection }) {
    commit('SET_WS_CONNECTION', { taskId, connection });
  },

  // 断开任务WebSocket
  disconnectTaskWS({ state, commit }, taskId) {
    const connection = state.wsConnections[taskId];
    if (connection && typeof connection.disconnect === 'function') {
      connection.disconnect();
    }
    commit('REMOVE_WS_CONNECTION', taskId);
  },

  // 获取友好的错误消息
  getFriendlyErrorMessage(context, error) {
    if (!error) return { message: '未知错误', suggestion: '请稍后重试' };

    const errorMap = {
      'timeout': { message: '网络开小差啦', suggestion: '正在自动重试，请稍候～' },
      'network': { message: '网络连接失败', suggestion: '请检查网络后重试' },
      'text_too_long': { message: '故事文本过长啦', suggestion: '建议精简到500字内' },
      'invalid_template': { message: '模板配置有误', suggestion: '请重新选择模板' },
      'quota_exceeded': { message: '今日生成次数已用完', suggestion: '明天再来创作吧～' },
      'server_error': { message: '服务器繁忙', suggestion: '请稍后重试' },
    };

    const errorType = typeof error === 'string' ? error : error.type || error.code;
    const errorMessage = typeof error === 'string' ? error : error.message;

    const friendlyError = errorMap[errorType] || {
      message: errorMessage || '操作失败',
      suggestion: '请稍后重试或联系客服',
    };

    return {
      ...friendlyError,
      originalError: error,
      timestamp: Date.now(),
    };
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions,
};

export { TASK_STATUS, TASK_STAGES };
