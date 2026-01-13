<template>
  <div class="story-wizard">
    <!-- 步骤指示器 -->
    <div class="wizard-steps">
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="step-item"
        :class="{
          active: currentStep === index,
          completed: index < currentStep,
          disabled: index > currentStep,
        }"
        @click="canNavigateTo(index) && goToStep(index)"
      >
        <div class="step-number">
          <span v-if="index < currentStep">✓</span>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- 步骤内容 -->
    <div class="wizard-content">
      <transition :name="transitionName" mode="out-in">
        <component
          :is="currentStepComponent"
          :key="currentStep"
          :data="formData"
          :errors="validationErrors"
          @update="updateFormData"
          @validate="validateCurrentStep"
        />
      </transition>
    </div>

    <!-- 操作按钮 -->
    <div class="wizard-actions">
      <button
        v-if="currentStep > 0"
        class="btn btn-secondary"
        @click="previousStep"
      >
        上一步
      </button>
      
      <div class="flex-spacer"></div>
      
      <button
        v-if="!isLastStep"
        class="btn btn-primary"
        :disabled="!canProceed"
        @click="nextStep"
      >
        下一步
      </button>
      
      <button
        v-else
        class="btn btn-success"
        :disabled="!canSubmit || isSubmitting"
        @click="submit"
      >
        <span v-if="isSubmitting">
          <span class="loading-spinner"></span>
          生成中...
        </span>
        <span v-else>开始生成</span>
      </button>
    </div>

    <!-- 保存草稿按钮 -->
    <button
      v-if="hasChanges"
      class="btn-save-draft"
      @click="saveDraft"
    >
      💾 保存草稿
    </button>
  </div>
</template>

<script>
import TemplateSelection from './steps/TemplateSelection.vue';
import StoryContent from './steps/StoryContent.vue';
import MaterialConfig from './steps/MaterialConfig.vue';
import ParameterConfig from './steps/ParameterConfig.vue';
import Preview from './steps/Preview.vue';

export default {
  name: 'StoryWizard',
  components: {
    TemplateSelection,
    StoryContent,
    MaterialConfig,
    ParameterConfig,
    Preview,
  },
  data() {
    return {
      currentStep: 0,
      transitionName: 'slide-left',
      formData: {
        template: null,
        story: {
          title: '',
          content: '',
          outline: [],
        },
        materials: {
          images: [],
          audio: null,
          background: null,
        },
        parameters: {
          duration: 60,
          resolution: '1080p',
          style: 'default',
        },
      },
      validationErrors: {},
      isSubmitting: false,
      hasChanges: false,
      savedDraft: null,
    };
  },
  computed: {
    steps() {
      return [
        { key: 'template', label: '选择模板', component: 'TemplateSelection' },
        { key: 'story', label: '编写故事', component: 'StoryContent' },
        { key: 'materials', label: '配置素材', component: 'MaterialConfig' },
        { key: 'parameters', label: '设置参数', component: 'ParameterConfig' },
        { key: 'preview', label: '预览确认', component: 'Preview' },
      ];
    },
    currentStepComponent() {
      return this.steps[this.currentStep].component;
    },
    isLastStep() {
      return this.currentStep === this.steps.length - 1;
    },
    canProceed() {
      return this.validateCurrentStep();
    },
    canSubmit() {
      return this.validateAllSteps();
    },
  },
  watch: {
    formData: {
      deep: true,
      handler() {
        this.hasChanges = true;
      },
    },
  },
  mounted() {
    this.restoreDraft();
  },
  beforeDestroy() {
    if (this.hasChanges && !this.isSubmitting) {
      this.saveDraft();
    }
  },
  methods: {
    updateFormData(updates) {
      this.formData = { ...this.formData, ...updates };
      this.hasChanges = true;
    },

    validateCurrentStep() {
      const step = this.steps[this.currentStep];
      this.validationErrors = {};

      switch (step.key) {
        case 'template':
          if (!this.formData.template) {
            this.validationErrors.template = '请选择一个模板';
            return false;
          }
          break;

        case 'story':
          if (!this.formData.story.title?.trim()) {
            this.validationErrors.title = '请填写故事标题';
            return false;
          }
          if (!this.formData.story.content?.trim()) {
            this.validationErrors.content = '请填写故事内容';
            return false;
          }
          if (this.formData.story.content.length > 500) {
            this.validationErrors.content = '故事内容过长，建议精简到500字内';
            return false;
          }
          break;

        case 'materials':
          break;

        case 'parameters':
          if (!this.formData.parameters.duration) {
            this.validationErrors.duration = '请设置视频时长';
            return false;
          }
          break;

        case 'preview':
          break;
      }

      return Object.keys(this.validationErrors).length === 0;
    },

    validateAllSteps() {
      for (let i = 0; i < this.steps.length; i++) {
        this.currentStep = i;
        if (!this.validateCurrentStep()) {
          return false;
        }
      }
      return true;
    },

    canNavigateTo(stepIndex) {
      return stepIndex <= this.currentStep;
    },

    goToStep(stepIndex) {
      if (this.canNavigateTo(stepIndex)) {
        this.transitionName = stepIndex > this.currentStep ? 'slide-left' : 'slide-right';
        this.currentStep = stepIndex;
      }
    },

    nextStep() {
      if (this.validateCurrentStep() && !this.isLastStep) {
        this.transitionName = 'slide-left';
        this.currentStep++;
      }
    },

    previousStep() {
      if (this.currentStep > 0) {
        this.transitionName = 'slide-right';
        this.currentStep--;
      }
    },

    async submit() {
      if (!this.canSubmit || this.isSubmitting) return;

      this.isSubmitting = true;

      try {
        const result = await this.$store.dispatch('tasks/createTask', {
          type: 'story_generation',
          config: this.formData,
        });

        this.$emit('submit', result);
        this.hasChanges = false;
        this.clearDraft();
        
        this.$router.push({
          name: 'TaskDetail',
          params: { id: result.id },
        });
      } catch (error) {
        console.error('提交失败:', error);
        this.$message.error(error.message || '提交失败，请重试');
      } finally {
        this.isSubmitting = false;
      }
    },

    saveDraft() {
      const draft = {
        formData: this.formData,
        currentStep: this.currentStep,
        timestamp: Date.now(),
      };
      
      localStorage.setItem('story_wizard_draft', JSON.stringify(draft));
      this.savedDraft = draft;
      this.hasChanges = false;
      
      this.$message.success('草稿已保存');
    },

    restoreDraft() {
      try {
        const saved = localStorage.getItem('story_wizard_draft');
        if (saved) {
          const draft = JSON.parse(saved);
          
          const shouldRestore = confirm(
            `发现未完成的草稿（保存于 ${new Date(draft.timestamp).toLocaleString()}），是否恢复？`
          );
          
          if (shouldRestore) {
            this.formData = draft.formData;
            this.currentStep = draft.currentStep;
            this.savedDraft = draft;
            this.$message.info('草稿已恢复');
          } else {
            this.clearDraft();
          }
        }
      } catch (error) {
        console.error('恢复草稿失败:', error);
      }
    },

    clearDraft() {
      localStorage.removeItem('story_wizard_draft');
      this.savedDraft = null;
    },
  },
};
</script>

<style scoped>
.story-wizard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.wizard-steps {
  display: flex;
  justify-content: space-between;
  margin-bottom: 3rem;
  position: relative;
}

.wizard-steps::before {
  content: '';
  position: absolute;
  top: 20px;
  left: 0;
  right: 0;
  height: 2px;
  background: #e5e7eb;
  z-index: 0;
}

.step-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
  z-index: 1;
}

.step-item.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #6b7280;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.step-item.active .step-number {
  background: #3b82f6;
  color: white;
  transform: scale(1.1);
}

.step-item.completed .step-number {
  background: #10b981;
  color: white;
}

.step-label {
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}

.step-item.active .step-label {
  color: #1f2937;
  font-weight: 600;
}

.wizard-content {
  min-height: 400px;
  margin-bottom: 2rem;
}

.wizard-actions {
  display: flex;
  gap: 1rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.flex-spacer {
  flex: 1;
}

.btn {
  padding: 0.75rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  font-size: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-save-draft {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: 2px solid #3b82f6;
  color: #3b82f6;
  border-radius: 2rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.btn-save-draft:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s ease;
}

.slide-left-enter {
  transform: translateX(20px);
  opacity: 0;
}

.slide-left-leave-to {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-right-enter {
  transform: translateX(-20px);
  opacity: 0;
}

.slide-right-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
</style>
