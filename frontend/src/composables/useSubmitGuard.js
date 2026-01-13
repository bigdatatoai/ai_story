/**
 * 防重复提交 Composable
 * 用于Vue 3组件
 */

import { ref } from 'vue';

export function useSubmitGuard() {
  const isSubmitting = ref(false);
  const submitTimestamp = ref(0);
  const minInterval = 1000; // 最小提交间隔（毫秒）

  /**
   * 执行带防护的提交
   * @param {Function} submitFn - 提交函数
   * @param {Object} options - 配置选项
   * @returns {Promise}
   */
  const guardedSubmit = async (submitFn, options = {}) => {
    const {
      showLoading = true,
      checkInterval = true,
      onStart = null,
      onFinish = null,
      onError = null,
    } = options;

    // 检查是否正在提交
    if (isSubmitting.value) {
      console.warn('请勿重复提交');
      return Promise.reject(new Error('请勿重复提交'));
    }

    // 检查提交间隔
    if (checkInterval) {
      const now = Date.now();
      const elapsed = now - submitTimestamp.value;
      
      if (elapsed < minInterval) {
        console.warn('提交过于频繁，请稍后再试');
        return Promise.reject(new Error('提交过于频繁'));
      }
    }

    try {
      isSubmitting.value = true;
      submitTimestamp.value = Date.now();

      if (onStart && typeof onStart === 'function') {
        onStart();
      }

      const result = await submitFn();

      if (onFinish && typeof onFinish === 'function') {
        onFinish(result);
      }

      return result;
    } catch (error) {
      if (onError && typeof onError === 'function') {
        onError(error);
      }
      throw error;
    } finally {
      isSubmitting.value = false;
    }
  };

  /**
   * 重置提交状态
   */
  const reset = () => {
    isSubmitting.value = false;
    submitTimestamp.value = 0;
  };

  return {
    isSubmitting,
    guardedSubmit,
    reset,
  };
}

/**
 * 创建防抖提交函数
 * @param {Function} fn - 原函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function}
 */
export function debounceSubmit(fn, delay = 300) {
  let timeoutId = null;

  return function (...args) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    return new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await fn.apply(this, args);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, delay);
    });
  };
}

/**
 * 创建节流提交函数
 * @param {Function} fn - 原函数
 * @param {number} interval - 间隔时间（毫秒）
 * @returns {Function}
 */
export function throttleSubmit(fn, interval = 1000) {
  let lastTime = 0;
  let pending = false;

  return async function (...args) {
    const now = Date.now();
    const elapsed = now - lastTime;

    if (pending) {
      return Promise.reject(new Error('请勿重复提交'));
    }

    if (elapsed < interval) {
      return Promise.reject(new Error('提交过于频繁'));
    }

    try {
      pending = true;
      lastTime = now;
      const result = await fn.apply(this, args);
      return result;
    } finally {
      pending = false;
    }
  };
}

export default {
  useSubmitGuard,
  debounceSubmit,
  throttleSubmit,
};
