/**
 * Responsive utilities for mobile device detection and adaptive UI
 */

/**
 * Breakpoints for responsive design
 */
export const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
  desktop: 1280,
};

/**
 * Check if current device is mobile
 * @returns {boolean} True if mobile device
 */
export function isMobile() {
  return window.innerWidth < BREAKPOINTS.mobile;
}

/**
 * Check if current device is tablet
 * @returns {boolean} True if tablet device
 */
export function isTablet() {
  return window.innerWidth >= BREAKPOINTS.mobile && window.innerWidth < BREAKPOINTS.tablet;
}

/**
 * Check if current device is desktop
 * @returns {boolean} True if desktop device
 */
export function isDesktop() {
  return window.innerWidth >= BREAKPOINTS.desktop;
}

/**
 * Get current device type
 * @returns {string} Device type: 'mobile', 'tablet', or 'desktop'
 */
export function getDeviceType() {
  const width = window.innerWidth;
  
  if (width < BREAKPOINTS.mobile) return 'mobile';
  if (width < BREAKPOINTS.tablet) return 'tablet';
  return 'desktop';
}

/**
 * Vue mixin for responsive behavior
 */
export const responsiveMixin = {
  data() {
    return {
      isMobile: false,
      isTablet: false,
      isDesktop: false,
      deviceType: 'desktop',
    };
  },
  mounted() {
    this.updateDeviceInfo();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    updateDeviceInfo() {
      this.isMobile = isMobile();
      this.isTablet = isTablet();
      this.isDesktop = isDesktop();
      this.deviceType = getDeviceType();
    },
    handleResize() {
      this.updateDeviceInfo();
    },
  },
};

/**
 * Debounce function for resize events
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Get responsive value based on device type
 * @param {Object} values - Values for different device types
 * @returns {*} Value for current device type
 */
export function getResponsiveValue(values) {
  const deviceType = getDeviceType();
  return values[deviceType] || values.desktop || values.default;
}

export default {
  BREAKPOINTS,
  isMobile,
  isTablet,
  isDesktop,
  getDeviceType,
  responsiveMixin,
  debounce,
  getResponsiveValue,
};
