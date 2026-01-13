/**
 * 视频相关API
 */

import apiClient from '@/services/apiClient'

const videoAPI = {
  // 获取项目列表
  getProjects(params = {}) {
    return apiClient.get('/content/videos/', { params })
  },

  // 创建短剧项目
  createDramaProject(data) {
    return apiClient.post('/content/videos/', data)
  },

  // 文本转视频
  textToVideo(data) {
    return apiClient.post('/content/videos/text_to_video/', data)
  },

  // 图片转视频
  imageToVideo(data) {
    return apiClient.post('/content/videos/image_to_video/', data)
  },

  // 故事板转视频
  storyboardToVideo(data) {
    return apiClient.post('/content/videos/storyboard_to_video/', data)
  },

  // 获取项目详情
  getProject(id) {
    return apiClient.get(`/content/videos/${id}/`)
  },

  // 获取项目状态
  getProjectStatus(id) {
    return apiClient.get(`/content/videos/${id}/status/`)
  },

  // 删除项目
  deleteProject(id) {
    return apiClient.delete(`/content/videos/${id}/`)
  },

  // 导出视频
  exportVideo(id, data) {
    return apiClient.post(`/content/videos/${id}/export/`, data)
  },

  // 生成动漫角色
  generateAnimeCharacter(data) {
    return apiClient.post('/content/videos/generate_anime_character/', data)
  },

  // 生成动漫场景
  generateAnimeScene(data) {
    return apiClient.post('/content/videos/generate_anime_scene/', data)
  },

  // 生成漫画分格
  generateComicPanels(data) {
    return apiClient.post('/content/videos/generate_comic_panels/', data)
  },

  // 批量生产
  batchProduce(data) {
    return apiClient.post('/content/videos/batch_produce/', data)
  },

  // 获取生产统计
  getProductionStats() {
    return apiClient.get('/content/videos/stats/')
  },

  // 生成剧本
  generateDramaScript(data) {
    return apiClient.post('/content/videos/generate_drama_script/', data)
  },

  // 生产短剧视频
  produceDramaVideo(data) {
    return apiClient.post('/content/videos/produce_drama_video/', data)
  }
}

export default videoAPI
