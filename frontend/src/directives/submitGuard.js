/**
 * 防重复提交指令
 * 用于按钮和表单
 */

let submitting = false;
let lastSubmitTime = 0;

export const submitGuard = {
  mounted(el, binding) {
    const { value = {}, modifiers } = binding;
    const {
      interval = 1000,
      disableClass = 'is-disabled',
      loadingClass = 'is-loading',
    } = value;

    // 保存原始点击处理器
    const originalHandler = el.onclick;

    el.onclick = async function (event) {
      // 检查是否正在提交
      if (submitting) {
        event.preventDefault();
        event.stopPropagation();
        console.warn('请勿重复提交');
        return false;
      }

      // 检查提交间隔
      const now = Date.now();
      if (now - lastSubmitTime < interval) {
        event.preventDefault();
        event.stopPropagation();
        console.warn('提交过于频繁');
        return false;
      }

      try {
        submitting = true;
        lastSubmitTime = now;

        // 添加禁用样式
        el.classList.add(disableClass);
        if (modifiers.loading) {
          el.classList.add(loadingClass);
        }

        // 禁用按钮
        if (el.tagName === 'BUTTON') {
          el.disabled = true;
        }

        // 执行原始处理器
        if (originalHandler) {
          await originalHandler.call(this, event);
        }
      } catch (error) {
        console.error('提交失败:', error);
      } finally {
        submitting = false;

        // 移除禁用样式
        el.classList.remove(disableClass);
        if (modifiers.loading) {
          el.classList.remove(loadingClass);
        }

        // 启用按钮
        if (el.tagName === 'BUTTON') {
          el.disabled = false;
        }
      }
    };
  },

  unmounted(el) {
    // 清理
    el.onclick = null;
  },
};

/**
 * 单次点击指令
 * 确保按钮只能点击一次
 */
export const clickOnce = {
  mounted(el, binding) {
    let clicked = false;

    const originalHandler = el.onclick;

    el.onclick = function (event) {
      if (clicked) {
        event.preventDefault();
        event.stopPropagation();
        return false;
      }

      clicked = true;

      if (originalHandler) {
        originalHandler.call(this, event);
      }

      // 可选：重置点击状态
      if (binding.modifiers.reset) {
        setTimeout(() => {
          clicked = false;
        }, binding.value || 2000);
      }
    };
  },
};

export default {
  submitGuard,
  clickOnce,
};
