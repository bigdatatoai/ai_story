"""
模型使用记录
职责: 追踪AI模型的使用情况和成本
"""

import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ModelUsageRecord(models.Model):
    """模型使用记录"""
    
    USAGE_TYPE_CHOICES = [
        ('llm', 'LLM'),
        ('text2image', '文生图'),
        ('image2video', '图生视频'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 关联信息
    provider = models.ForeignKey(
        'models.ModelProvider',
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name="模型提供商"
    )
    project_id = models.UUIDField(verbose_name="项目ID", db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='model_usage_records',
        verbose_name="用户"
    )
    
    # 使用类型
    usage_type = models.CharField(
        max_length=20,
        choices=USAGE_TYPE_CHOICES,
        verbose_name="使用类型",
        db_index=True
    )
    
    # LLM相关字段
    input_tokens = models.IntegerField(default=0, verbose_name="输入Token数")
    output_tokens = models.IntegerField(default=0, verbose_name="输出Token数")
    
    # 图片生成相关
    image_count = models.IntegerField(default=0, verbose_name="生成图片数")
    
    # 视频生成相关
    video_count = models.IntegerField(default=0, verbose_name="生成视频数")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="视频时长(秒)")
    
    # 成本信息
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0'),
        verbose_name="总成本(USD)"
    )
    
    # 额外元数据
    metadata = models.JSONField(default=dict, blank=True, verbose_name="元数据")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_index=True)
    
    class Meta:
        db_table = 'model_usage_records'
        verbose_name = '模型使用记录'
        verbose_name_plural = '模型使用记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['provider', '-created_at']),
            models.Index(fields=['project_id', '-created_at']),
            models.Index(fields=['usage_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_usage_type_display()} - {self.provider.name} - ${self.total_cost}"
