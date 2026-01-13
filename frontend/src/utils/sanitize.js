/**
 * XSS 过滤和输入清理工具
 */

/**
 * 转义 HTML 特殊字符
 * @param {string} text - 需要转义的文本
 * @returns {string} 转义后的文本
 */
export function escapeHTML(text) {
  if (typeof text !== 'string') return '';
  
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  
  return text.replace(/[&<>"'/]/g, (char) => map[char]);
}

/**
 * 清理用户输入，移除危险字符
 * @param {string} input - 用户输入
 * @returns {string} 清理后的输入
 */
export function sanitizeInput(input) {
  if (typeof input !== 'string') return '';
  
  return input
    .trim()
    // 移除 script 标签
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    // 移除 iframe 标签
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    // 移除 on* 事件处理器
    .replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '')
    // 移除 javascript: 协议
    .replace(/javascript:/gi, '');
}

/**
 * 清理 URL，防止 XSS
 * @param {string} url - URL 字符串
 * @returns {string} 清理后的 URL
 */
export function sanitizeURL(url) {
  if (typeof url !== 'string') return '';
  
  // 移除危险协议
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:'];
  const lowerURL = url.toLowerCase().trim();
  
  for (const protocol of dangerousProtocols) {
    if (lowerURL.startsWith(protocol)) {
      return '';
    }
  }
  
  return url.trim();
}

/**
 * 验证并清理文件名
 * @param {string} filename - 文件名
 * @returns {string} 清理后的文件名
 */
export function sanitizeFilename(filename) {
  if (typeof filename !== 'string') return 'unnamed';
  
  return filename
    // 移除路径分隔符
    .replace(/[<>:"/\\|?*]/g, '')
    // 移除控制字符
    .replace(/[\x00-\x1f\x7f]/g, '')
    // 限制长度
    .substring(0, 255)
    .trim() || 'unnamed';
}

/**
 * 清理 JSON 数据中的字符串字段
 * @param {Object} obj - JSON 对象
 * @returns {Object} 清理后的对象
 */
export function sanitizeObject(obj) {
  if (typeof obj !== 'object' || obj === null) return obj;
  
  if (Array.isArray(obj)) {
    return obj.map(item => sanitizeObject(item));
  }
  
  const cleaned = {};
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      cleaned[key] = sanitizeInput(value);
    } else if (typeof value === 'object' && value !== null) {
      cleaned[key] = sanitizeObject(value);
    } else {
      cleaned[key] = value;
    }
  }
  
  return cleaned;
}

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
export function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证 URL 格式
 * @param {string} url - URL 字符串
 * @returns {boolean} 是否有效
 */
export function isValidURL(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 限制文本长度
 * @param {string} text - 文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 超出时的后缀
 * @returns {string} 处理后的文本
 */
export function truncateText(text, maxLength = 100, suffix = '...') {
  if (typeof text !== 'string') return '';
  if (text.length <= maxLength) return text;
  
  return text.substring(0, maxLength - suffix.length) + suffix;
}

export default {
  escapeHTML,
  sanitizeInput,
  sanitizeURL,
  sanitizeFilename,
  sanitizeObject,
  isValidEmail,
  isValidURL,
  truncateText
};
