"""
项目模板模型
职责: 管理项目模板的保存和加载
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectTemplate(models.Model):
    """项目模板"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="模板名称")
    description = models.TextField(blank=True, verbose_name="模板描述")
    
    # 模板创建者
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_templates',
        verbose_name="创建者"
    )
    
    # 是否公开（公开模板可被其他用户使用）
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    
    # 模板配置数据（JSON格式）
    template_data = models.JSONField(verbose_name="模板数据")
    # 包含: {
    #   "prompt_template_set_id": "xxx",
    #   "model_config": {...},
    #   "default_settings": {...}
    # }
    
    # 使用次数统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        db_table = 'project_templates'
        verbose_name = '项目模板'
        verbose_name_plural = '项目模板'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['is_public', '-usage_count']),
        ]
    
    def __str__(self):
        return f"{self.name} (by {self.created_by.username})"
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
