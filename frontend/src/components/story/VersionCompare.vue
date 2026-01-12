<template>
  <div class="version-compare">
    <div class="compare-header">
      <h2>版本对比</h2>
      <button @click="$emit('close')" class="btn-close">×</button>
    </div>

    <div class="version-selectors">
      <div class="selector-group">
        <label>版本1</label>
        <select v-model="selectedVersion1" class="version-select">
          <option v-for="v in versions" :key="v.id" :value="v.id">
            版本{{ v.version }} - {{ formatDate(v.created_at) }}
            <span v-if="v.quality_score">(评分: {{ v.quality_score }})</span>
          </option>
        </select>
      </div>

      <div class="selector-group">
        <label>版本2</label>
        <select v-model="selectedVersion2" class="version-select">
          <option v-for="v in versions" :key="v.id" :value="v.id">
            版本{{ v.version }} - {{ formatDate(v.created_at) }}
            <span v-if="v.quality_score">(评分: {{ v.quality_score }})</span>
          </option>
        </select>
      </div>

      <button @click="compareVersions" class="btn btn-primary" :disabled="!canCompare">
        对比
      </button>
    </div>

    <div v-if="diffResult" class="diff-container">
      <div class="diff-stats">
        <div class="stat-item">
          <span class="stat-label">新增</span>
          <span class="stat-value added">+{{ diffResult.stats.added }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">删除</span>
          <span class="stat-value removed">-{{ diffResult.stats.removed }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">修改</span>
          <span class="stat-value modified">~{{ diffResult.stats.modified }}</span>
        </div>
      </div>

      <div class="diff-view">
        <div class="version-panel">
          <h3>版本{{ version1?.version }}</h3>
          <div class="content-display" v-html="highlightedContent1"></div>
        </div>

        <div class="version-panel">
          <h3>版本{{ version2?.version }}</h3>
          <div class="content-display" v-html="highlightedContent2"></div>
        </div>
      </div>

      <div class="diff-actions">
        <button @click="rollbackToVersion(selectedVersion1)" class="btn btn-secondary">
          回滚到版本{{ version1?.version }}
        </button>
        <button @click="rollbackToVersion(selectedVersion2)" class="btn btn-secondary">
          回滚到版本{{ version2?.version }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import storyAPI from '@/api/story'
import { diffWords } from 'diff'

export default {
  name: 'VersionCompare',
  
  props: {
    storyId: {
      type: String,
      required: true
    }
  },
  
  emits: ['close', 'rollback'],
  
  setup(props, { emit }) {
    const versions = ref([])
    const selectedVersion1 = ref(null)
    const selectedVersion2 = ref(null)
    const diffResult = ref(null)
    
    const version1 = computed(() => 
      versions.value.find(v => v.id === selectedVersion1.value)
    )
    
    const version2 = computed(() => 
      versions.value.find(v => v.id === selectedVersion2.value)
    )
    
    const canCompare = computed(() => 
      selectedVersion1.value && selectedVersion2.value && 
      selectedVersion1.value !== selectedVersion2.value
    )
    
    const highlightedContent1 = computed(() => {
      if (!diffResult.value) return ''
      return generateHighlightedHTML(diffResult.value.diff, 'left')
    })
    
    const highlightedContent2 = computed(() => {
      if (!diffResult.value) return ''
      return generateHighlightedHTML(diffResult.value.diff, 'right')
    })
    
    const loadVersions = async () => {
      try {
        const response = await storyAPI.getVersionHistory(props.storyId)
        if (response.success) {
          versions.value = response.data
          
          if (versions.value.length >= 2) {
            selectedVersion1.value = versions.value[0].id
            selectedVersion2.value = versions.value[1].id
          }
        }
      } catch (error) {
        console.error('加载版本失败:', error)
      }
    }
    
    const compareVersions = () => {
      if (!version1.value || !version2.value) return
      
      const diff = diffWords(version1.value.content, version2.value.content)
      
      const stats = {
        added: 0,
        removed: 0,
        modified: 0
      }
      
      diff.forEach(part => {
        if (part.added) stats.added += part.value.length
        else if (part.removed) stats.removed += part.value.length
        else if (part.value.trim()) stats.modified++
      })
      
      diffResult.value = {
        diff,
        stats
      }
    }
    
    const generateHighlightedHTML = (diff, side) => {
      let html = ''
      
      diff.forEach(part => {
        if (side === 'left') {
          if (part.removed) {
            html += `<span class="diff-removed">${escapeHtml(part.value)}</span>`
          } else if (!part.added) {
            html += escapeHtml(part.value)
          }
        } else {
          if (part.added) {
            html += `<span class="diff-added">${escapeHtml(part.value)}</span>`
          } else if (!part.removed) {
            html += escapeHtml(part.value)
          }
        }
      })
      
      return html
    }
    
    const escapeHtml = (text) => {
      const div = document.createElement('div')
      div.textContent = text
      return div.innerHTML
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
    
    const rollbackToVersion = async (versionId) => {
      if (confirm('确定要回滚到这个版本吗？')) {
        try {
          await storyAPI.rollbackToVersion(props.storyId, versionId)
          emit('rollback', versionId)
        } catch (error) {
          console.error('回滚失败:', error)
        }
      }
    }
    
    loadVersions()
    
    return {
      versions,
      selectedVersion1,
      selectedVersion2,
      diffResult,
      version1,
      version2,
      canCompare,
      highlightedContent1,
      highlightedContent2,
      compareVersions,
      formatDate,
      rollbackToVersion
    }
  }
}
</script>

<style scoped>
.version-compare {
  background: white;
  border-radius: 12px;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e0e0e0;
}

.compare-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.btn-close {
  width: 36px;
  height: 36px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.version-selectors {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 16px;
  margin-bottom: 24px;
}

.selector-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin-bottom: 8px;
}

.version-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.diff-stats {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.stat-value.added {
  color: #4CAF50;
}

.stat-value.removed {
  color: #f44336;
}

.stat-value.modified {
  color: #FF9800;
}

.diff-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.version-panel {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.version-panel h3 {
  margin: 0;
  padding: 12px 16px;
  background: #f5f5f5;
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
}

.content-display {
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
  line-height: 1.8;
  white-space: pre-wrap;
  font-size: 14px;
}

.diff-removed {
  background: #ffebee;
  color: #c62828;
  text-decoration: line-through;
  padding: 2px 4px;
  border-radius: 3px;
}

.diff-added {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 2px 4px;
  border-radius: 3px;
}

.diff-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
