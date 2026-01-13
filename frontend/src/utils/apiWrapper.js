/**
 * API调用包装器
 * 统一处理业务错误和响应格式
 */

/**
 * 包装API调用，统一处理响应
 * @param {Promise} apiCall - API调用Promise
 * @param {Object} options - 配置选项
 * @returns {Promise}
 */
export async function wrapApiCall(apiCall, options = {}) {
  const {
    showError = true,
    showSuccess = false,
    successMessage = '操作成功',
    errorMessage = null,
    onSuccess = null,
    onError = null,
  } = options;

  try {
    const response = await apiCall;

    // 检查响应格式
    if (typeof response !== 'object' || response === null) {
      throw new Error('无效的响应格式');
    }

    // 检查业务状态
    if (response.success === false) {
      const error = new Error(response.message || response.error || '操作失败');
      error.code = response.code;
      error.data = response.data;
      throw error;
    }

    // 成功处理
    if (showSuccess && successMessage) {
      // TODO: 显示成功提示
      console.log('[SUCCESS]', successMessage);
    }

    if (onSuccess && typeof onSuccess === 'function') {
      onSuccess(response.data);
    }

    return response.data;
  } catch (error) {
    // 错误处理
    const message = errorMessage || error.message || '请求失败';

    if (showError) {
      // TODO: 显示错误提示
      console.error('[ERROR]', message);
    }

    if (onError && typeof onError === 'function') {
      onError(error);
    }

    throw error;
  }
}

/**
 * 创建API包装器
 * @param {Object} apiModule - API模块对象
 * @returns {Object} 包装后的API对象
 */
export function createApiWrapper(apiModule) {
  const wrapped = {};

  Object.keys(apiModule).forEach((key) => {
    if (typeof apiModule[key] === 'function') {
      wrapped[key] = (...args) => {
        return wrapApiCall(apiModule[key](...args));
      };
    }
  });

  return wrapped;
}

/**
 * 提取响应数据
 * @param {Object} response - API响应
 * @returns {*} 数据部分
 */
export function extractData(response) {
  if (!response) return null;
  
  // 兼容不同的响应格式
  if (response.data !== undefined) {
    return response.data;
  }
  
  if (response.results !== undefined) {
    return response.results;
  }
  
  return response;
}

/**
 * 检查响应是否成功
 * @param {Object} response - API响应
 * @returns {boolean}
 */
export function isSuccess(response) {
  return response && response.success !== false;
}

/**
 * 获取错误消息
 * @param {Error|Object} error - 错误对象
 * @returns {string}
 */
export function getErrorMessage(error) {
  if (!error) return '未知错误';
  
  // 如果是Error对象
  if (error instanceof Error) {
    return error.message;
  }
  
  // 如果是响应对象
  if (typeof error === 'object') {
    return error.message || error.error || error.msg || '操作失败';
  }
  
  return String(error);
}

export default {
  wrapApiCall,
  createApiWrapper,
  extractData,
  isSuccess,
  getErrorMessage,
};
