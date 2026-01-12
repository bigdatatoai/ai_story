<template>
  <div class="share-dialog-overlay" @click.self="$emit('close')">
    <div class="share-dialog">
      <div class="dialog-header">
        <h2>分享故事</h2>
        <button @click="$emit('close')" class="btn-close">×</button>
      </div>

      <div class="dialog-body">
        <!-- 分享卡片预览 -->
        <div class="card-preview">
          <img v-if="shareCardUrl" :src="shareCardUrl" alt="分享卡片" class="preview-image">
          <div v-else class="preview-loading">
            <div class="spinner"></div>
            <p>正在生成分享卡片...</p>
          </div>
        </div>

        <!-- 分享选项 -->
        <div class="share-options">
          <button @click="shareToWechat" class="share-btn wechat">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.5 12c0 .83-.67 1.5-1.5 1.5S5.5 12.83 5.5 12s.67-1.5 1.5-1.5 1.5.67 1.5 1.5zm7 0c0 .83-.67 1.5-1.5 1.5s-1.5-.67-1.5-1.5.67-1.5 1.5-1.5 1.5.67 1.5 1.5z"/>
            </svg>
            <span>微信</span>
          </button>

          <button @click="shareToWeibo" class="share-btn weibo">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20 12c0-1.1-.9-2-2-2V7c0-1.1-.9-2-2-2H8c-1.1 0-2 .9-2 2v3c-1.1 0-2 .9-2 2v5c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-5z"/>
            </svg>
            <span>微博</span>
          </button>

          <button @click="shareToXiaohongshu" class="share-btn xiaohongshu">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
            </svg>
            <span>小红书</span>
          </button>

          <button @click="copyLink" class="share-btn link">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
            </svg>
            <span>复制链接</span>
          </button>

          <button @click="downloadCard" class="share-btn download">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2z"/>
            </svg>
            <span>下载卡片</span>
          </button>

          <button @click="generateQRCode" class="share-btn qrcode">
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 11h8V3H3v8zm2-6h4v4H5V5zM3 21h8v-8H3v8zm2-6h4v4H5v-4zM13 3v8h8V3h-8zm6 6h-4V5h4v4zM13 13h2v2h-2zM15 15h2v2h-2zM13 17h2v2h-2zM15 19h2v2h-2zM17 17h2v2h-2zM17 13h2v2h-2zM19 15h2v2h-2z"/>
            </svg>
            <span>二维码</span>
          </button>
        </div>

        <!-- 二维码显示 -->
        <div v-if="showQRCode" class="qrcode-container">
          <img :src="qrcodeUrl" alt="二维码" class="qrcode-image">
          <p>扫码查看故事</p>
        </div>

        <!-- 链接输入框 -->
        <div class="link-container">
          <input
            ref="linkInput"
            :value="shareLink"
            readonly
            class="link-input"
            @click="selectLink"
          >
          <button @click="copyLink" class="btn-copy">复制</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import storyAPI from '@/api/story'

export default {
  name: 'ShareDialog',
  
  props: {
    story: {
      type: Object,
      required: true
    }
  },
  
  emits: ['close'],
  
  setup(props) {
    const shareCardUrl = ref(null)
    const qrcodeUrl = ref(null)
    const showQRCode = ref(false)
    const linkInput = ref(null)
    
    const shareLink = ref(`https://yourdomain.com/story/${props.story.id}`)
    
    const generateShareCard = async () => {
      try {
        const response = await storyAPI.generateShareCard({
          story_id: props.story.id,
          card_style: 'default'
        })
        
        if (response.success) {
          shareCardUrl.value = response.data.card_url
        }
      } catch (error) {
        console.error('生成分享卡片失败:', error)
      }
    }
    
    const shareToWechat = () => {
      if (navigator.share) {
        navigator.share({
          title: props.story.title,
          text: props.story.content.substring(0, 100) + '...',
          url: shareLink.value
        }).catch(err => console.log('分享取消', err))
      } else {
        copyLink()
        alert('链接已复制，请在微信中粘贴分享')
      }
    }
    
    const shareToWeibo = () => {
      const weiboUrl = `https://service.weibo.com/share/share.php?url=${encodeURIComponent(shareLink.value)}&title=${encodeURIComponent(props.story.title)}`
      window.open(weiboUrl, '_blank')
    }
    
    const shareToXiaohongshu = () => {
      copyLink()
      alert('链接已复制，请在小红书APP中粘贴分享')
    }
    
    const copyLink = async () => {
      try {
        await navigator.clipboard.writeText(shareLink.value)
        alert('链接已复制到剪贴板')
      } catch (error) {
        selectLink()
        document.execCommand('copy')
        alert('链接已复制')
      }
    }
    
    const selectLink = () => {
      if (linkInput.value) {
        linkInput.value.select()
      }
    }
    
    const downloadCard = () => {
      if (shareCardUrl.value) {
        const link = document.createElement('a')
        link.href = shareCardUrl.value
        link.download = `${props.story.title}_分享卡片.png`
        link.click()
      }
    }
    
    const generateQRCode = async () => {
      try {
        const response = await storyAPI.generateQRCode({
          story_id: props.story.id
        })
        
        if (response.success) {
          qrcodeUrl.value = response.data.qrcode_url
          showQRCode.value = true
        }
      } catch (error) {
        console.error('生成二维码失败:', error)
      }
    }
    
    onMounted(() => {
      generateShareCard()
    })
    
    return {
      shareCardUrl,
      qrcodeUrl,
      showQRCode,
      shareLink,
      linkInput,
      shareToWechat,
      shareToWeibo,
      shareToXiaohongshu,
      copyLink,
      selectLink,
      downloadCard,
      generateQRCode
    }
  }
}
</script>

<style scoped>
.share-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.share-dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.dialog-body {
  padding: 24px;
}

.card-preview {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.preview-loading {
  text-align: center;
  color: #999;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.share-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.share-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.share-btn:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.share-btn.wechat:hover { border-color: #07C160; }
.share-btn.weibo:hover { border-color: #E6162D; }
.share-btn.xiaohongshu:hover { border-color: #FF2442; }

.share-btn .icon {
  width: 32px;
  height: 32px;
  color: #666;
}

.share-btn:hover .icon {
  color: #667eea;
}

.share-btn.wechat:hover .icon { color: #07C160; }
.share-btn.weibo:hover .icon { color: #E6162D; }
.share-btn.xiaohongshu:hover .icon { color: #FF2442; }

.share-btn span {
  font-size: 14px;
  color: #333;
}

.qrcode-container {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 24px;
}

.qrcode-image {
  width: 200px;
  height: 200px;
  margin: 0 auto 12px;
}

.qrcode-container p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.link-container {
  display: flex;
  gap: 12px;
}

.link-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  background: #f8f9fa;
}

.btn-copy {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.btn-copy:hover {
  background: #5568d3;
}
</style>
