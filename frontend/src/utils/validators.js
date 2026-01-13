/**
 * 前端参数校验工具
 * 用于校验各阶段输入参数的合法性
 */

/**
 * 运镜参数校验
 * @param {Object} params - 运镜参数对象
 * @returns {Object} { valid: boolean, errors: Array<string> }
 */
export function validateCameraMovementParams(params) {
  const errors = [];

  if (!params || typeof params !== 'object') {
    return { valid: false, errors: ['运镜参数必须是对象类型'] };
  }

  // 校验必需字段
  const requiredFields = ['speed', 'duration'];
  for (const field of requiredFields) {
    if (!(field in params)) {
      errors.push(`缺少必需字段: ${field}`);
    }
  }

  // 校验 speed
  if ('speed' in params) {
    const speed = params.speed;
    if (typeof speed !== 'number') {
      errors.push('speed 必须是数字类型');
    } else if (speed <= 0) {
      errors.push('speed 必须大于 0');
    } else if (speed > 10) {
      errors.push('speed 不能超过 10（建议范围: 0.1-5）');
    }
  }

  // 校验 duration
  if ('duration' in params) {
    const duration = params.duration;
    if (typeof duration !== 'number') {
      errors.push('duration 必须是数字类型');
    } else if (duration <= 0) {
      errors.push('duration 必须大于 0');
    } else if (duration > 30) {
      errors.push('duration 不能超过 30 秒');
    }
  }

  // 校验 easing（可选字段）
  if ('easing' in params) {
    const validEasings = ['linear', 'ease-in', 'ease-out', 'ease-in-out'];
    if (!validEasings.includes(params.easing)) {
      errors.push(`easing 必须是以下值之一: ${validEasings.join(', ')}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 分镜参数校验
 * @param {Array} scenes - 分镜数组
 * @returns {Object} { valid: boolean, errors: Array<string> }
 */
export function validateStoryboardScenes(scenes) {
  const errors = [];

  if (!Array.isArray(scenes)) {
    return { valid: false, errors: ['分镜数据必须是数组类型'] };
  }

  if (scenes.length === 0) {
    return { valid: false, errors: ['分镜数组不能为空'] };
  }

  scenes.forEach((scene, index) => {
    if (!scene.scene_description || !scene.scene_description.trim()) {
      errors.push(`第 ${index + 1} 个分镜缺少场景描述`);
    }
    if (!scene.narration_text || !scene.narration_text.trim()) {
      errors.push(`第 ${index + 1} 个分镜缺少旁白文案`);
    }
    if (!scene.image_prompt || !scene.image_prompt.trim()) {
      errors.push(`第 ${index + 1} 个分镜缺少文生图提示词`);
    }
    if (scene.duration_seconds !== undefined) {
      if (typeof scene.duration_seconds !== 'number' || scene.duration_seconds <= 0) {
        errors.push(`第 ${index + 1} 个分镜的时长必须是大于 0 的数字`);
      }
    }
  });

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * 通用 JSON 数据校验
 * @param {string} jsonString - JSON 字符串
 * @returns {Object} { valid: boolean, data: any, error: string }
 */
export function validateJSON(jsonString) {
  if (!jsonString || !jsonString.trim()) {
    return { valid: false, data: null, error: '输入不能为空' };
  }

  try {
    const data = JSON.parse(jsonString);
    return { valid: true, data, error: null };
  } catch (error) {
    return { valid: false, data: null, error: `JSON 格式错误: ${error.message}` };
  }
}

/**
 * 阶段输入数据校验（根据阶段类型）
 * @param {string} stageType - 阶段类型
 * @param {any} inputData - 输入数据
 * @returns {Object} { valid: boolean, errors: Array<string> }
 */
export function validateStageInput(stageType, inputData) {
  const errors = [];

  switch (stageType) {
    case 'rewrite':
      if (!inputData || (typeof inputData === 'string' && !inputData.trim())) {
        errors.push('文案改写阶段的输入不能为空');
      }
      break;

    case 'storyboard':
      if (!inputData || (typeof inputData === 'string' && !inputData.trim())) {
        errors.push('分镜生成阶段的输入不能为空');
      }
      break;

    case 'image_generation':
      if (typeof inputData === 'object' && inputData.scenes) {
        const validation = validateStoryboardScenes(inputData.scenes);
        if (!validation.valid) {
          errors.push(...validation.errors);
        }
      }
      break;

    case 'camera_movement':
      // 运镜阶段可能包含多个场景的运镜参数
      if (typeof inputData === 'object' && inputData.scenes) {
        inputData.scenes.forEach((scene, index) => {
          if (scene.camera_movement) {
            const validation = validateCameraMovementParams(scene.camera_movement);
            if (!validation.valid) {
              errors.push(`第 ${index + 1} 个场景的运镜参数错误: ${validation.errors.join(', ')}`);
            }
          }
        });
      }
      break;

    case 'video_generation':
      // 视频生成阶段需要图片和运镜数据
      if (typeof inputData === 'object' && inputData.scenes) {
        inputData.scenes.forEach((scene, index) => {
          if (!scene.image_url) {
            errors.push(`第 ${index + 1} 个场景缺少图片 URL`);
          }
          if (!scene.camera_movement) {
            errors.push(`第 ${index + 1} 个场景缺少运镜参数`);
          }
        });
      }
      break;
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

export default {
  validateCameraMovementParams,
  validateStoryboardScenes,
  validateJSON,
  validateStageInput,
};
