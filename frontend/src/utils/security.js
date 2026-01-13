/**
 * Security utilities for XSS protection and input sanitization
 */

/**
 * Sanitize HTML string to prevent XSS attacks
 * @param {string} html - HTML string to sanitize
 * @returns {string} Sanitized HTML
 */
export function sanitizeHtml(html) {
  if (!html || typeof html !== 'string') return '';

  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
}

/**
 * Sanitize user input by removing dangerous characters
 * @param {string} input - User input to sanitize
 * @param {Object} options - Sanitization options
 * @returns {string} Sanitized input
 */
export function sanitizeInput(input, options = {}) {
  if (!input || typeof input !== 'string') return '';

  const {
    allowHtml = false,
    maxLength = null,
    trim = true,
  } = options;

  let sanitized = input;

  // Trim whitespace
  if (trim) {
    sanitized = sanitized.trim();
  }

  // Remove HTML tags if not allowed
  if (!allowHtml) {
    sanitized = sanitized.replace(/<[^>]*>/g, '');
  }

  // Remove dangerous characters
  sanitized = sanitized
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+\s*=/gi, ''); // Remove event handlers

  // Apply max length
  if (maxLength && sanitized.length > maxLength) {
    sanitized = sanitized.substring(0, maxLength);
  }

  return sanitized;
}

/**
 * Escape HTML special characters
 * @param {string} str - String to escape
 * @returns {string} Escaped string
 */
export function escapeHtml(str) {
  if (!str || typeof str !== 'string') return '';

  const htmlEscapeMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };

  return str.replace(/[&<>"'/]/g, (char) => htmlEscapeMap[char]);
}

/**
 * Sanitize object properties recursively
 * @param {Object} obj - Object to sanitize
 * @param {Array} fields - Fields to sanitize (if empty, sanitize all string fields)
 * @returns {Object} Sanitized object
 */
export function sanitizeObject(obj, fields = []) {
  if (!obj || typeof obj !== 'object') return obj;

  const sanitized = Array.isArray(obj) ? [] : {};

  Object.keys(obj).forEach((key) => {
    const value = obj[key];

    // If fields array is provided, only sanitize specified fields
    const shouldSanitize = fields.length === 0 || fields.includes(key);

    if (typeof value === 'string' && shouldSanitize) {
      sanitized[key] = sanitizeInput(value);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizeObject(value, fields);
    } else {
      sanitized[key] = value;
    }
  });

  return sanitized;
}

/**
 * Validate and sanitize URL
 * @param {string} url - URL to validate
 * @returns {string|null} Sanitized URL or null if invalid
 */
export function sanitizeUrl(url) {
  if (!url || typeof url !== 'string') return null;

  // Remove whitespace
  url = url.trim();

  // Check for dangerous protocols
  const dangerousProtocols = ['javascript:', 'data:', 'vbscript:', 'file:'];
  const lowerUrl = url.toLowerCase();

  for (const protocol of dangerousProtocols) {
    if (lowerUrl.startsWith(protocol)) {
      return null;
    }
  }

  // Only allow http, https, and relative URLs
  if (!url.match(/^(https?:\/\/|\/)/i)) {
    return null;
  }

  return url;
}

/**
 * Remove sensitive information from error objects for logging
 * @param {Error|Object} error - Error object
 * @returns {Object} Sanitized error object
 */
export function sanitizeError(error) {
  if (!error) return null;

  const sanitized = {
    message: error.message || 'Unknown error',
    name: error.name || 'Error',
  };

  // In development, include more details
  if (process.env.NODE_ENV === 'development') {
    sanitized.stack = error.stack;
    
    // Include response data but sanitize sensitive fields
    if (error.response) {
      sanitized.response = {
        status: error.response.status,
        statusText: error.response.statusText,
        // Don't include headers or full data in production
      };
    }
  }

  return sanitized;
}

/**
 * Validate email format
 * @param {string} email - Email to validate
 * @returns {boolean} True if valid email
 */
export function isValidEmail(email) {
  if (!email || typeof email !== 'string') return false;
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Create a Content Security Policy meta tag
 * @returns {HTMLMetaElement} CSP meta element
 */
export function createCSPMeta() {
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Content-Security-Policy';
  meta.content = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' ws: wss:",
  ].join('; ');
  
  return meta;
}

export default {
  sanitizeHtml,
  sanitizeInput,
  escapeHtml,
  sanitizeObject,
  sanitizeUrl,
  sanitizeError,
  isValidEmail,
  createCSPMeta,
};
