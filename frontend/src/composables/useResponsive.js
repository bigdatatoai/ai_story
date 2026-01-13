/**
 * 响应式设备检测 Composable
 * 用于 Vue 2.7 (支持 Composition API)
 */

import { ref, onMounted, onUnmounted } from 'vue';

/**
 * 响应式设备检测
 * @returns {Object} 设备状态和工具方法
 */
export function useResponsive() {
  const windowWidth = ref(0);
  const windowHeight = ref(0);
  
  // 设备类型
  const isMobile = ref(false);
  const isTablet = ref(false);
  const isDesktop = ref(false);
  
  // 屏幕方向
  const isPortrait = ref(false);
  const isLandscape = ref(false);
  
  // 断点
  const breakpoints = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280,
    '2xl': 1536
  };
  
  /**
   * 更新设备信息
   */
  const updateDeviceInfo = () => {
    windowWidth.value = window.innerWidth;
    windowHeight.value = window.innerHeight;
    
    // 设备类型判断
    isMobile.value = windowWidth.value < breakpoints.md;
    isTablet.value = windowWidth.value >= breakpoints.md && windowWidth.value < breakpoints.lg;
    isDesktop.value = windowWidth.value >= breakpoints.lg;
    
    // 屏幕方向
    isPortrait.value = windowHeight.value > windowWidth.value;
    isLandscape.value = windowWidth.value > windowHeight.value;
  };
  
  /**
   * 检查是否大于指定断点
   * @param {string} breakpoint - 断点名称 (sm, md, lg, xl, 2xl)
   * @returns {boolean}
   */
  const isGreaterThan = (breakpoint) => {
    return windowWidth.value >= (breakpoints[breakpoint] || 0);
  };
  
  /**
   * 检查是否小于指定断点
   * @param {string} breakpoint - 断点名称
   * @returns {boolean}
   */
  const isLessThan = (breakpoint) => {
    return windowWidth.value < (breakpoints[breakpoint] || Infinity);
  };
  
  /**
   * 检查是否在指定断点范围内
   * @param {string} min - 最小断点
   * @param {string} max - 最大断点
   * @returns {boolean}
   */
  const isBetween = (min, max) => {
    const minWidth = breakpoints[min] || 0;
    const maxWidth = breakpoints[max] || Infinity;
    return windowWidth.value >= minWidth && windowWidth.value < maxWidth;
  };
  
  // 防抖的 resize 处理
  let resizeTimer = null;
  const handleResize = () => {
    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateDeviceInfo, 150);
  };
  
  // 生命周期
  onMounted(() => {
    updateDeviceInfo();
    window.addEventListener('resize', handleResize);
  });
  
  onUnmounted(() => {
    window.removeEventListener('resize', handleResize);
    if (resizeTimer) clearTimeout(resizeTimer);
  });
  
  return {
    // 尺寸
    windowWidth,
    windowHeight,
    
    // 设备类型
    isMobile,
    isTablet,
    isDesktop,
    
    // 屏幕方向
    isPortrait,
    isLandscape,
    
    // 工具方法
    isGreaterThan,
    isLessThan,
    isBetween,
    
    // 断点常量
    breakpoints
  };
}

/**
 * 简化版：仅检测是否为移动设备
 * @returns {Object}
 */
export function useIsMobile() {
  const isMobile = ref(false);
  
  const checkMobile = () => {
    isMobile.value = window.innerWidth < 768;
  };
  
  onMounted(() => {
    checkMobile();
    window.addEventListener('resize', checkMobile);
  });
  
  onUnmounted(() => {
    window.removeEventListener('resize', checkMobile);
  });
  
  return { isMobile };
}

export default {
  useResponsive,
  useIsMobile
};
