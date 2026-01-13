/**
 * Throttle and debounce utilities for performance optimization
 */

/**
 * Throttle function - limits execution to once per specified time period
 * @param {Function} func - Function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @param {Object} options - Options
 * @returns {Function} Throttled function
 */
export function throttle(func, limit = 500, options = {}) {
  const { leading = true, trailing = true } = options;
  let inThrottle;
  let lastFunc;
  let lastRan;

  return function executedFunction(...args) {
    const context = this;

    if (!inThrottle) {
      if (leading) {
        func.apply(context, args);
      }
      lastRan = Date.now();
      inThrottle = true;
    } else {
      clearTimeout(lastFunc);
      lastFunc = setTimeout(() => {
        if (Date.now() - lastRan >= limit) {
          if (trailing) {
            func.apply(context, args);
          }
          lastRan = Date.now();
        }
      }, Math.max(limit - (Date.now() - lastRan), 0));
    }
  };
}

/**
 * Debounce function - delays execution until after specified time has elapsed
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {Object} options - Options
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 300, options = {}) {
  const { leading = false, trailing = true, maxWait = null } = options;
  let timeout;
  let lastCallTime;
  let lastInvokeTime = 0;
  let result;

  function invokeFunc(time) {
    const args = lastArgs;
    const thisArg = lastThis;

    lastArgs = lastThis = undefined;
    lastInvokeTime = time;
    result = func.apply(thisArg, args);
    return result;
  }

  function leadingEdge(time) {
    lastInvokeTime = time;
    timeout = setTimeout(timerExpired, wait);
    return leading ? invokeFunc(time) : result;
  }

  function remainingWait(time) {
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;

    return maxWait !== null
      ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
      : timeWaiting;
  }

  function shouldInvoke(time) {
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;

    return (
      lastCallTime === undefined ||
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (maxWait !== null && timeSinceLastInvoke >= maxWait)
    );
  }

  function timerExpired() {
    const time = Date.now();
    if (shouldInvoke(time)) {
      return trailingEdge(time);
    }
    timeout = setTimeout(timerExpired, remainingWait(time));
  }

  function trailingEdge(time) {
    timeout = undefined;

    if (trailing && lastArgs) {
      return invokeFunc(time);
    }
    lastArgs = lastThis = undefined;
    return result;
  }

  let lastArgs, lastThis;

  function debounced(...args) {
    const time = Date.now();
    const isInvoking = shouldInvoke(time);

    lastArgs = args;
    lastThis = this;
    lastCallTime = time;

    if (isInvoking) {
      if (timeout === undefined) {
        return leadingEdge(lastCallTime);
      }
      if (maxWait !== null) {
        timeout = setTimeout(timerExpired, wait);
        return invokeFunc(lastCallTime);
      }
    }
    if (timeout === undefined) {
      timeout = setTimeout(timerExpired, wait);
    }
    return result;
  }

  debounced.cancel = function() {
    if (timeout !== undefined) {
      clearTimeout(timeout);
    }
    lastInvokeTime = 0;
    lastArgs = lastCallTime = lastThis = timeout = undefined;
  };

  debounced.flush = function() {
    return timeout === undefined ? result : trailingEdge(Date.now());
  };

  return debounced;
}

/**
 * Request Animation Frame throttle for smooth animations
 * @param {Function} func - Function to throttle
 * @returns {Function} Throttled function
 */
export function rafThrottle(func) {
  let rafId = null;
  let lastArgs = null;

  return function throttled(...args) {
    lastArgs = args;

    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        func.apply(this, lastArgs);
        rafId = null;
        lastArgs = null;
      });
    }
  };
}

export default {
  throttle,
  debounce,
  rafThrottle,
};
