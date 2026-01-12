/**
 * 视频相关API
 */

import apiClient from '@/services/apiClient'

const videoAPI = {
  // 获取项目列表
  getProjects(params = {}) {
    return apiClient.get('/api/v1/content/videos/', { params })
  },

  // 创建短剧项目
  createDramaProject(data) {
    return apiClient.post('/api/v1/content/videos/', data)
  },

  // 文本转视频
  textToVideo(data) {
    return apiClient.post('/api/v1/content/videos/text_to_video/', data)
  },

  // 图片转视频
  imageToVideo(data) {
    return apiClient.post('/api/v1/content/videos/image_to_video/', data)
  },

  // 故事板转视频
  storyboardToVideo(data) {
    return apiClient.post('/api/v1/content/videos/storyboard_to_video/', data)
  },

  // 获取项目详情
  getProject(id) {
    return apiClient.get(`/api/v1/content/videos/${id}/`)
  },

  // 获取项目状态
  getProjectStatus(id) {
    return apiClient.get(`/api/v1/content/videos/${id}/status/`)
  },

  // 删除项目
  deleteProject(id) {
    return apiClient.delete(`/api/v1/content/videos/${id}/`)
  },

  // 导出视频
  exportVideo(id, data) {
    return apiClient.post(`/api/v1/content/videos/${id}/export/`, data)
  },

  // 生成动漫角色
  generateAnimeCharacter(data) {
    return apiClient.post('/api/v1/content/videos/generate_anime_character/', data)
  },

  // 生成动漫场景
  generateAnimeScene(data) {
    return apiClient.post('/api/v1/content/videos/generate_anime_scene/', data)
  },

  // 生成漫画分格
  generateComicPanels(data) {
    return apiClient.post('/api/v1/content/videos/generate_comic_panels/', data)
  },

  // 批量生产
  batchProduce(data) {
    return apiClient.post('/api/v1/content/videos/batch_produce/', data)
  },

  // 获取生产统计
  getProductionStats() {
    return apiClient.get('/api/v1/content/videos/stats/')
  }
}

export default videoAPI
