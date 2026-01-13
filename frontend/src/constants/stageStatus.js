/**
 * 阶段状态枚举常量
 * 与后端 ProjectStage 状态强绑定
 */

export const STAGE_STATUS = {
  PENDING: { value: 'pending', label: '待执行', type: 'info' },
  RUNNING: { value: 'running', label: '执行中', type: 'warning' },
  COMPLETED: { value: 'completed', label: '已完成', type: 'success' },
  FAILED: { value: 'failed', label: '失败', type: 'danger' },
  SKIPPED: { value: 'skipped', label: '已跳过', type: 'info' },
};

export const PROJECT_STATUS = {
  DRAFT: { value: 'draft', label: '草稿', type: 'info' },
  PROCESSING: { value: 'processing', label: '处理中', type: 'warning' },
  COMPLETED: { value: 'completed', label: '已完成', type: 'success' },
  FAILED: { value: 'failed', label: '失败', type: 'danger' },
  PAUSED: { value: 'paused', label: '已暂停', type: 'info' },
};

/**
 * 根据状态值获取状态配置
 * @param {string|undefined|null} status - 状态值
 * @returns {object} { value, label, type }
 */
export function getStageStatus(status) {
  const validStatus = typeof status === 'string' ? status.trim().toUpperCase() : '';
  return STAGE_STATUS[validStatus] || { 
    value: status,
    label: `未知状态(${status})`, 
    type: 'danger' 
  };
}

/**
 * 根据状态值获取项目状态配置
 * @param {string|undefined|null} status - 状态值
 * @returns {object} { value, label, type }
 */
export function getProjectStatus(status) {
  const validStatus = typeof status === 'string' ? status.trim().toUpperCase() : '';
  return PROJECT_STATUS[validStatus] || { 
    value: status,
    label: `未知状态(${status})`, 
    type: 'danger' 
  };
}

/**
 * 获取所有阶段状态列表
 * @returns {Array}
 */
export function getAllStageStatuses() {
  return Object.values(STAGE_STATUS);
}

/**
 * 获取所有项目状态列表
 * @returns {Array}
 */
export function getAllProjectStatuses() {
  return Object.values(PROJECT_STATUS);
}

export default {
  STAGE_STATUS,
  PROJECT_STATUS,
  getStageStatus,
  getProjectStatus,
  getAllStageStatuses,
  getAllProjectStatuses
};
