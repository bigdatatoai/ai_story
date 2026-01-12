"""
项目模板服务
职责: 处理项目模板的保存和加载逻辑
"""

from typing import Dict, Any
from django.db import transaction
from apps.projects.models import Project, ProjectModelConfig
from apps.projects.models_template import ProjectTemplate


class ProjectTemplateService:
    """项目模板服务"""
    
    @staticmethod
    def save_as_template(
        project: Project,
        template_name: str,
        description: str = "",
        include_model_config: bool = True,
        is_public: bool = False
    ) -> ProjectTemplate:
        """
        将项目保存为模板
        
        Args:
            project: 项目实例
            template_name: 模板名称
            description: 模板描述
            include_model_config: 是否包含模型配置
            is_public: 是否公开
            
        Returns:
            ProjectTemplate: 创建的模板实例
        """
        template_data = {
            'prompt_template_set_id': str(project.prompt_template_set_id) if project.prompt_template_set else None,
            'default_settings': {
                'description': project.description,
            }
        }
        
        # 如果包含模型配置
        if include_model_config:
            try:
                model_config = ProjectModelConfig.objects.get(project=project)
                template_data['model_config'] = {
                    'rewrite_provider_ids': list(model_config.rewrite_providers.values_list('id', flat=True)),
                    'storyboard_provider_ids': list(model_config.storyboard_providers.values_list('id', flat=True)),
                    'image_provider_ids': list(model_config.image_providers.values_list('id', flat=True)),
                    'camera_provider_ids': list(model_config.camera_providers.values_list('id', flat=True)),
                    'video_provider_ids': list(model_config.video_providers.values_list('id', flat=True)),
                    'load_balance_strategy': model_config.load_balance_strategy,
                }
            except ProjectModelConfig.DoesNotExist:
                template_data['model_config'] = None
        
        # 创建模板
        template = ProjectTemplate.objects.create(
            name=template_name,
            description=description,
            created_by=project.user,
            is_public=is_public,
            template_data=template_data
        )
        
        return template
    
    @staticmethod
    @transaction.atomic
    def create_from_template(
        template: ProjectTemplate,
        user,
        project_name: str,
        original_topic: str
    ) -> Project:
        """
        从模板创建项目
        
        Args:
            template: 模板实例
            user: 用户实例
            project_name: 项目名称
            original_topic: 原始主题
            
        Returns:
            Project: 创建的项目实例
        """
        from apps.prompts.models import PromptTemplateSet
        from apps.models.models import ModelProvider
        
        template_data = template.template_data
        
        # 创建项目
        project = Project.objects.create(
            name=project_name,
            description=template_data.get('default_settings', {}).get('description', ''),
            original_topic=original_topic,
            user=user,
            status='draft'
        )
        
        # 设置提示词模板集
        prompt_set_id = template_data.get('prompt_template_set_id')
        if prompt_set_id:
            try:
                prompt_set = PromptTemplateSet.objects.get(id=prompt_set_id)
                project.prompt_template_set = prompt_set
                project.save(update_fields=['prompt_template_set'])
            except PromptTemplateSet.DoesNotExist:
                pass
        
        # 设置模型配置
        model_config_data = template_data.get('model_config')
        if model_config_data:
            model_config = ProjectModelConfig.objects.create(
                project=project,
                load_balance_strategy=model_config_data.get('load_balance_strategy', 'weighted')
            )
            
            # 设置各阶段的模型提供商
            for stage, provider_ids in [
                ('rewrite', model_config_data.get('rewrite_provider_ids', [])),
                ('storyboard', model_config_data.get('storyboard_provider_ids', [])),
                ('image', model_config_data.get('image_provider_ids', [])),
                ('camera', model_config_data.get('camera_provider_ids', [])),
                ('video', model_config_data.get('video_provider_ids', [])),
            ]:
                if provider_ids:
                    providers = ModelProvider.objects.filter(id__in=provider_ids, is_active=True)
                    getattr(model_config, f'{stage}_providers').set(providers)
        
        # 增加模板使用次数
        template.increment_usage()
        
        return project
