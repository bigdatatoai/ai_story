import apiClient from '@/services/apiClient';

/**
 * 高级服务 API
 * 提供 TTS、STT、音乐、去重、发布等功能
 */
export default {
  /**
   * 生成AI配音
   * @param {String} projectId - 项目ID
   * @param {Object} data - {text, voice, provider}
   */
  generateVoiceover(projectId, data) {
    return apiClient.post(`/projects/advanced/${projectId}/generate-voiceover/`, data);
  },

  /**
   * 生成字幕（语音识别）
   * @param {String} projectId - 项目ID
   * @param {Object} data - {video_path, language}
   */
  generateSubtitles(projectId, data) {
    return apiClient.post(`/projects/advanced/${projectId}/generate-subtitles/`, data);
  },

  /**
   * 添加背景音乐
   * @param {String} projectId - 项目ID
   * @param {Object} data - {video_path, music_path, volume}
   */
  addBackgroundMusic(projectId, data) {
    return apiClient.post(`/projects/advanced/${projectId}/add-background-music/`, data);
  },

  /**
   * 视频去重
   * @param {String} projectId - 项目ID
   * @param {Object} data - {video_path, method}
   */
  deduplicateVideo(projectId, data) {
    return apiClient.post(`/projects/advanced/${projectId}/deduplicate-video/`, data);
  },

  /**
   * 发布到平台
   * @param {String} projectId - 项目ID
   * @param {Object} data - {video_path, platform, title, description, tags}
   */
  publishToPlatform(projectId, data) {
    return apiClient.post(`/projects/advanced/${projectId}/publish-to-platform/`, data);
  },

  /**
   * 批量处理
   * @param {Object} data - {project_ids, operation, params}
   */
  batchProcess(data) {
    return apiClient.post('/projects/advanced/batch-process/', data);
  }
};
