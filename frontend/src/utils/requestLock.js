/**
 * 请求锁工具
 * 防止重复提交和并发请求冲突
 */

class RequestLock {
  constructor() {
    this.locks = new Map();
    this.pendingRequests = new Map();
  }

  /**
   * 获取锁
   * @param {string} key - 锁的唯一标识
   * @param {number} timeout - 超时时间（毫秒）
   * @returns {boolean} 是否成功获取锁
   */
  acquire(key, timeout = 30000) {
    if (this.locks.has(key)) {
      const lockTime = this.locks.get(key);
      const now = Date.now();
      
      // 检查锁是否超时
      if (now - lockTime < timeout) {
        return false;
      }
      
      // 锁已超时，清除旧锁
      this.release(key);
    }

    this.locks.set(key, Date.now());
    return true;
  }

  /**
   * 释放锁
   * @param {string} key - 锁的唯一标识
   */
  release(key) {
    this.locks.delete(key);
    this.pendingRequests.delete(key);
  }

  /**
   * 检查是否已锁定
   * @param {string} key - 锁的唯一标识
   * @returns {boolean}
   */
  isLocked(key) {
    return this.locks.has(key);
  }

  /**
   * 清除所有锁
   */
  clearAll() {
    this.locks.clear();
    this.pendingRequests.clear();
  }

  /**
   * 包装异步函数，自动加锁和解锁
   * @param {string} key - 锁的唯一标识
   * @param {Function} fn - 异步函数
   * @param {Object} options - 配置选项
   * @returns {Promise}
   */
  async withLock(key, fn, options = {}) {
    const { timeout = 30000, onLocked = null } = options;

    // 尝试获取锁
    if (!this.acquire(key, timeout)) {
      if (onLocked) {
        onLocked();
      }
      throw new Error('操作正在进行中，请勿重复提交');
    }

    try {
      const result = await fn();
      return result;
    } finally {
      this.release(key);
    }
  }

  /**
   * 防抖执行（同一key的请求会复用结果）
   * @param {string} key - 请求标识
   * @param {Function} fn - 请求函数
   * @returns {Promise}
   */
  async deduplicate(key, fn) {
    // 如果已有相同的请求在进行中，返回该请求的Promise
    if (this.pendingRequests.has(key)) {
      console.log(`[RequestLock] 复用请求: ${key}`);
      return this.pendingRequests.get(key);
    }

    // 创建新请求
    const promise = fn()
      .then((result) => {
        this.pendingRequests.delete(key);
        return result;
      })
      .catch((error) => {
        this.pendingRequests.delete(key);
        throw error;
      });

    this.pendingRequests.set(key, promise);
    return promise;
  }
}

// 创建单例
const requestLock = new RequestLock();

/**
 * 防重复提交装饰器
 * @param {string} lockKey - 锁的key（可以是函数，接收参数返回key）
 * @param {Object} options - 配置选项
 */
export function preventDuplicate(lockKey, options = {}) {
  return function (target, propertyKey, descriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args) {
      const key = typeof lockKey === 'function' ? lockKey(...args) : lockKey;
      
      return requestLock.withLock(key, () => originalMethod.apply(this, args), options);
    };

    return descriptor;
  };
}

/**
 * 创建防重复提交的按钮状态管理器
 */
export class ButtonLockManager {
  constructor() {
    this.states = new Map();
  }

  /**
   * 设置按钮状态
   * @param {string} buttonId - 按钮ID
   * @param {boolean} loading - 是否加载中
   * @param {string} text - 按钮文本
   */
  setState(buttonId, loading, text = null) {
    this.states.set(buttonId, { loading, text, timestamp: Date.now() });
  }

  /**
   * 获取按钮状态
   * @param {string} buttonId - 按钮ID
   * @returns {Object}
   */
  getState(buttonId) {
    return this.states.get(buttonId) || { loading: false, text: null };
  }

  /**
   * 重置按钮状态
   * @param {string} buttonId - 按钮ID
   */
  reset(buttonId) {
    this.states.delete(buttonId);
  }

  /**
   * 包装按钮点击事件
   * @param {string} buttonId - 按钮ID
   * @param {Function} handler - 点击处理函数
   * @param {Object} options - 配置选项
   */
  async wrapHandler(buttonId, handler, options = {}) {
    const { loadingText = '处理中...', timeout = 30000 } = options;

    const state = this.getState(buttonId);
    if (state.loading) {
      console.warn(`[ButtonLock] 按钮 ${buttonId} 正在处理中`);
      return;
    }

    this.setState(buttonId, true, loadingText);

    try {
      const result = await Promise.race([
        handler(),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('操作超时')), timeout)
        ),
      ]);
      return result;
    } finally {
      this.reset(buttonId);
    }
  }
}

export default requestLock;
export { requestLock, ButtonLockManager };
