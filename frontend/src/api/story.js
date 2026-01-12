/**
 * 故事相关API
 */

import apiClient from '@/services/apiClient'

const storyAPI = {
  // 获取故事列表
  getStories(params = {}) {
    return apiClient.get('/api/v1/content/stories/', { params })
  },

  // 生成故事
  generateStory(data) {
    return apiClient.post('/api/v1/content/stories/generate/', data)
  },

  // 生成大纲
  generateOutline(data) {
    return apiClient.post('/api/v1/content/stories/generate_outline/', data)
  },

  // 基于大纲生成故事
  generateFromOutline(data) {
    return apiClient.post('/api/v1/content/stories/generate_from_outline/', data)
  },

  // 保存大纲
  saveOutline(storyId, data) {
    return apiClient.put(`/api/v1/content/stories/${storyId}/outline/`, data)
  },

  // 续写故事
  continueStory(storyId, data) {
    return apiClient.post(`/api/v1/content/stories/${storyId}/continue_story/`, data)
  },

  // 编辑故事
  editStory(storyId, data) {
    return apiClient.post(`/api/v1/content/stories/${storyId}/edit_story/`, data)
  },

  // 获取故事详情
  getStory(id) {
    return apiClient.get(`/api/v1/content/stories/${id}/`)
  },

  // 获取版本历史
  getVersionHistory(storyId) {
    return apiClient.get(`/api/v1/content/stories/${storyId}/version_history/`)
  },

  // 对比版本
  compareVersions(data) {
    return apiClient.post('/api/v1/content/stories/compare_versions/', data)
  },

  // 回滚到指定版本
  rollbackToVersion(storyId, versionId) {
    return apiClient.post(`/api/v1/content/stories/${storyId}/rollback/`, { version_id: versionId })
  },

  // 删除故事
  deleteStory(id) {
    return apiClient.delete(`/api/v1/content/stories/${id}/`)
  },

  // 导出故事
  exportStory(data) {
    return apiClient.post('/api/v1/content/stories/export/', data)
  },

  // 获取模板列表
  getTemplates(params = {}) {
    return apiClient.get('/api/v1/content/story-templates/', { params })
  },

  // 获取角色列表
  getCharacters(params = {}) {
    return apiClient.get('/api/v1/content/characters/', { params })
  },

  // 创建角色
  createCharacter(data) {
    return apiClient.post('/api/v1/content/characters/', data)
  },

  // 获取统计信息
  getStatistics() {
    return apiClient.get('/api/v1/content/stories/statistics/')
  },

  // 故事接龙 - 开始
  startStoryChain(data) {
    return apiClient.post('/api/v1/content/stories/start_chain/', data)
  },

  // 故事接龙 - 继续
  continueStoryChain(data) {
    return apiClient.post('/api/v1/content/stories/continue_chain/', data)
  },

  // 获取剧情选择
  getPlotChoices(data) {
    return apiClient.post('/api/v1/content/stories/plot_choices/', data)
  },

  // 应用剧情选择
  applyPlotChoice(data) {
    return apiClient.post('/api/v1/content/stories/apply_choice/', data)
  },

  // 保存引导式创作的故事
  saveGuidedStory(data) {
    return apiClient.post('/api/v1/content/stories/save_guided/', data)
  },

  // 生成分享卡片
  generateShareCard(data) {
    return apiClient.post('/api/v1/content/stories/share_card/', data)
  },

  // 生成二维码
  generateQRCode(data) {
    return apiClient.post('/api/v1/content/stories/qrcode/', data)
  }
}

export default storyAPI
