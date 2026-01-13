/**
 * 全局错误处理服务
 * 统一处理各类错误，提供友好的错误提示
 */

import networkMonitor from './networkMonitor';

const ERROR_TYPES = {
  NETWORK: 'network',
  TIMEOUT: 'timeout',
  VALIDATION: 'validation',
  PERMISSION: 'permission',
  SERVER: 'server',
  BUSINESS: 'business',
  UNKNOWN: 'unknown',
};

const FRIENDLY_MESSAGES = {
  // 网络错误
  'ERR_NETWORK': '网络开小差啦，正在重试～',
  'ERR_INTERNET_DISCONNECTED': '网络已断开，请检查网络连接',
  'ECONNABORTED': '网络连接超时，请稍后重试',
  'ETIMEDOUT': '请求超时，请检查网络后重试',
  
  // 服务器错误
  '500': '服务器繁忙，请稍后重试',
  '502': '服务器维护中，请稍后重试',
  '503': '服务暂时不可用，请稍后重试',
  '504': '服务器响应超时，请稍后重试',
  
  // 客户端错误
  '400': '请求参数有误，请检查后重试',
  '401': '登录已过期，请重新登录',
  '403': '没有权限执行此操作',
  '404': '请求的资源不存在',
  '429': '操作太频繁啦，请稍后再试',
  
  // 业务错误
  'QUOTA_EXCEEDED': '今日生成次数已用完，明天再来创作吧～',
  'TEXT_TOO_LONG': '故事文本过长啦，建议精简到500字内',
  'INVALID_TEMPLATE': '模板配置有误，请重新选择模板',
  'INVALID_PARAMETERS': '参数配置不完整，请检查后重试',
  'TASK_FAILED': 'AI生成失败，请重试或调整参数',
  'RESOURCE_NOT_FOUND': '资源未找到，可能已被删除',
};

class ErrorHandler {
  constructor() {
    this.errorListeners = [];
    this.retryQueue = [];
    this.maxRetries = 3;
  }

  /**
   * 处理错误
   * @param {Error|Object} error - 错误对象
   * @param {Object} context - 上下文信息
   * @returns {Object} 处理后的错误信息
   */
  handle(error, context = {}) {
    const errorInfo = this.parseError(error);
    const friendlyMessage = this.getFriendlyMessage(errorInfo);
    
    const processedError = {
      ...errorInfo,
      ...friendlyMessage,
      context,
      timestamp: Date.now(),
    };

    console.error('[ErrorHandler] 错误:', processedError);

    // 通知监听器
    this.notifyListeners(processedError);

    // 处理特定类型的错误
    this.handleSpecificError(processedError);

    return processedError;
  }

  /**
   * 解析错误对象
   */
  parseError(error) {
    if (!error) {
      return {
        type: ERROR_TYPES.UNKNOWN,
        code: 'UNKNOWN',
        message: '未知错误',
      };
    }

    // Axios错误
    if (error.response) {
      return {
        type: this.getErrorType(error.response.status),
        code: error.response.status,
        message: error.response.data?.message || error.response.data?.error || error.message,
        data: error.response.data,
        status: error.response.status,
      };
    }

    // 请求错误（网络问题）
    if (error.request) {
      return {
        type: ERROR_TYPES.NETWORK,
        code: error.code || 'ERR_NETWORK',
        message: error.message,
      };
    }

    // 业务错误
    if (error.code || error.type) {
      return {
        type: error.type || ERROR_TYPES.BUSINESS,
        code: error.code,
        message: error.message,
        data: error.data,
      };
    }

    // 普通错误
    return {
      type: ERROR_TYPES.UNKNOWN,
      code: 'UNKNOWN',
      message: error.message || String(error),
    };
  }

  /**
   * 获取错误类型
   */
  getErrorType(status) {
    if (status >= 500) return ERROR_TYPES.SERVER;
    if (status === 401 || status === 403) return ERROR_TYPES.PERMISSION;
    if (status === 400 || status === 422) return ERROR_TYPES.VALIDATION;
    if (status === 408 || status === 504) return ERROR_TYPES.TIMEOUT;
    return ERROR_TYPES.BUSINESS;
  }

  /**
   * 获取友好的错误消息
   */
  getFriendlyMessage(errorInfo) {
    const { code, message, type } = errorInfo;

    // 优先使用预定义的友好消息
    let friendlyMessage = FRIENDLY_MESSAGES[code] || FRIENDLY_MESSAGES[String(code)];

    // 如果没有预定义消息，根据类型生成
    if (!friendlyMessage) {
      switch (type) {
        case ERROR_TYPES.NETWORK:
          friendlyMessage = '网络连接失败，请检查网络';
          break;
        case ERROR_TYPES.TIMEOUT:
          friendlyMessage = '请求超时，请稍后重试';
          break;
        case ERROR_TYPES.PERMISSION:
          friendlyMessage = '没有权限执行此操作';
          break;
        case ERROR_TYPES.VALIDATION:
          friendlyMessage = '输入信息有误，请检查';
          break;
        case ERROR_TYPES.SERVER:
          friendlyMessage = '服务器繁忙，请稍后重试';
          break;
        default:
          friendlyMessage = message || '操作失败，请重试';
      }
    }

    // 生成建议
    const suggestion = this.getSuggestion(errorInfo);

    return {
      friendlyMessage,
      suggestion,
      canRetry: this.canRetry(errorInfo),
    };
  }

  /**
   * 获取错误建议
   */
  getSuggestion(errorInfo) {
    const { type, code } = errorInfo;

    if (type === ERROR_TYPES.NETWORK) {
      return '请检查网络连接后重试';
    }

    if (type === ERROR_TYPES.TIMEOUT) {
      return '网络较慢，建议稍后重试';
    }

    if (type === ERROR_TYPES.PERMISSION) {
      if (code === 401) return '请重新登录';
      return '请联系管理员获取权限';
    }

    if (type === ERROR_TYPES.VALIDATION) {
      return '请检查输入内容是否完整正确';
    }

    if (code === 'QUOTA_EXCEEDED') {
      return '明天再来创作吧～';
    }

    if (code === 'TEXT_TOO_LONG') {
      return '建议精简文本到500字以内';
    }

    return '请稍后重试或联系客服';
  }

  /**
   * 判断是否可以重试
   */
  canRetry(errorInfo) {
    const { type, code } = errorInfo;

    // 网络错误、超时错误、服务器错误可以重试
    if ([ERROR_TYPES.NETWORK, ERROR_TYPES.TIMEOUT, ERROR_TYPES.SERVER].includes(type)) {
      return true;
    }

    // 429 (Too Many Requests) 可以重试
    if (code === 429 || code === '429') {
      return true;
    }

    return false;
  }

  /**
   * 处理特定错误
   */
  handleSpecificError(errorInfo) {
    const { type, code } = errorInfo;

    // 处理401错误 - 跳转登录
    if (code === 401 || code === '401') {
      this.handleUnauthorized();
    }

    // 处理网络错误 - 添加到重试队列
    if (type === ERROR_TYPES.NETWORK && networkMonitor.isOnline) {
      // 网络在线但请求失败，可能是临时问题
      console.log('[ErrorHandler] 网络错误，将在网络恢复后重试');
    }
  }

  /**
   * 处理未授权错误
   */
  handleUnauthorized() {
    // 清除登录信息
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // 延迟跳转，给用户看到错误提示的时间
    setTimeout(() => {
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }, 1500);
  }

  /**
   * 添加错误监听器
   */
  subscribe(listener) {
    this.errorListeners.push(listener);
    return () => {
      this.errorListeners = this.errorListeners.filter((l) => l !== listener);
    };
  }

  /**
   * 通知监听器
   */
  notifyListeners(error) {
    this.errorListeners.forEach((listener) => {
      try {
        listener(error);
      } catch (err) {
        console.error('[ErrorHandler] 监听器执行失败:', err);
      }
    });
  }

  /**
   * 自动重试包装器
   */
  async withRetry(fn, options = {}) {
    const {
      maxRetries = this.maxRetries,
      retryDelay = 1000,
      retryCondition = (error) => this.canRetry(this.parseError(error)),
    } = options;

    let lastError;
    
    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        
        const shouldRetry = attempt < maxRetries && retryCondition(error);
        
        if (!shouldRetry) {
          throw error;
        }

        console.log(`[ErrorHandler] 重试 ${attempt + 1}/${maxRetries}...`);
        
        // 指数退避
        const delay = retryDelay * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }
}

const errorHandler = new ErrorHandler();

export default errorHandler;
export { ERROR_TYPES, FRIENDLY_MESSAGES };
