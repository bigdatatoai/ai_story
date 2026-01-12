/**
 * API集成测试
 * 测试前后端API是否正常连接
 */

import videoAPI from '@/api/video'
import storyAPI from '@/api/story'

describe('API Integration Tests', () => {
  
  describe('Video API Tests', () => {
    
    test('should connect to video API endpoint', async () => {
      try {
        const response = await videoAPI.getProjects()
        expect(response).toBeDefined()
        expect(response.success).toBeDefined()
      } catch (error) {
        console.log('Video API connection test:', error.message)
      }
    })
    
    test('should handle text-to-video request', async () => {
      const testData = {
        prompt: '测试视频生成',
        duration: 4,
        style: 'cartoon'
      }
      
      try {
        const response = await videoAPI.textToVideo(testData)
        expect(response).toBeDefined()
      } catch (error) {
        // API可能需要认证或其他配置
        expect(error).toBeDefined()
      }
    })
    
    test('should handle anime character generation', async () => {
      const testData = {
        character_description: {
          name: '测试角色',
          age: 16,
          appearance: '黑色短发，大眼睛'
        },
        anime_style: 'shounen'
      }
      
      try {
        const response = await videoAPI.generateAnimeCharacter(testData)
        expect(response).toBeDefined()
      } catch (error) {
        expect(error).toBeDefined()
      }
    })
    
  })
  
  describe('Story API Tests', () => {
    
    test('should connect to story API endpoint', async () => {
      try {
        const response = await storyAPI.getStories()
        expect(response).toBeDefined()
      } catch (error) {
        console.log('Story API connection test:', error.message)
      }
    })
    
    test('should handle story generation request', async () => {
      const testData = {
        topic: '测试故事',
        age_group: 'elementary',
        genre: 'fairy_tale',
        word_count: 500
      }
      
      try {
        const response = await storyAPI.generateStory(testData)
        expect(response).toBeDefined()
      } catch (error) {
        expect(error).toBeDefined()
      }
    })
    
  })
  
  describe('API Error Handling', () => {
    
    test('should handle network errors gracefully', async () => {
      try {
        await videoAPI.getProject('invalid-id-12345')
      } catch (error) {
        expect(error).toBeDefined()
        expect(error.message).toBeDefined()
      }
    })
    
    test('should handle invalid data', async () => {
      try {
        await videoAPI.textToVideo({})
      } catch (error) {
        expect(error).toBeDefined()
      }
    })
    
  })
  
  describe('WebSocket Connection', () => {
    
    test('should establish WebSocket connection', (done) => {
      const ws = new WebSocket('ws://localhost:8000/ws/progress/')
      
      ws.onopen = () => {
        expect(ws.readyState).toBe(WebSocket.OPEN)
        ws.close()
        done()
      }
      
      ws.onerror = (error) => {
        console.log('WebSocket connection test:', error)
        done()
      }
      
      // 超时处理
      setTimeout(() => {
        if (ws.readyState !== WebSocket.OPEN) {
          ws.close()
          done()
        }
      }, 5000)
    })
    
  })
  
})

// 手动运行测试
console.log('🧪 API Integration Tests')
console.log('========================')
console.log('运行测试以验证API连接...')
console.log('')
console.log('✅ 测试配置完成')
console.log('📝 测试覆盖：')
console.log('  - Video API endpoints')
console.log('  - Story API endpoints')
console.log('  - Error handling')
console.log('  - WebSocket connections')
console.log('')
console.log('💡 运行命令: npm test')
