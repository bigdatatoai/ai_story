"""
视频相关数据模型
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Video(models.Model):
    """视频模型"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    GENERATION_TYPE_CHOICES = [
        ('text_to_video', '文本转视频'),
        ('image_to_video', '图片转视频'),
        ('storyboard_to_video', '故事板转视频'),
        ('story_to_video', '故事转视频'),
        ('drama', '短剧制作'),
        ('anime', '动漫制作'),
        ('comic', '漫画制作'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    
    # 基本信息
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    
    # 生成信息
    generation_type = models.CharField(
        max_length=50,
        choices=GENERATION_TYPE_CHOICES,
        verbose_name='生成类型'
    )
    prompt = models.TextField(blank=True, verbose_name='生成提示词')
    
    # 视频文件
    video_url = models.URLField(max_length=500, blank=True, verbose_name='视频URL')
    thumbnail_url = models.URLField(max_length=500, blank=True, verbose_name='缩略图URL')
    
    # 视频属性
    duration = models.FloatField(default=0, verbose_name='时长（秒）')
    resolution = models.CharField(max_length=20, default='1280x720', verbose_name='分辨率')
    fps = models.IntegerField(default=24, verbose_name='帧率')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小（字节）')
    
    # 状态
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    # 关联
    story = models.ForeignKey(
        'Story',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name='关联故事'
    )
    
    # 配置
    generation_config = models.JSONField(default=dict, blank=True, verbose_name='生成配置')
    
    # 统计
    view_count = models.IntegerField(default=0, verbose_name='观看次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞数')
    share_count = models.IntegerField(default=0, verbose_name='分享次数')
    
    # 标签和分类
    tags = models.JSONField(default=list, blank=True, verbose_name='标签')
    category = models.CharField(max_length=50, blank=True, verbose_name='分类')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'videos'
        verbose_name = '视频'
        verbose_name_plural = '视频'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['generation_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class VideoScene(models.Model):
    """视频场景（用于故事板转视频）"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='scenes')
    
    # 场景信息
    scene_number = models.IntegerField(verbose_name='场景序号')
    image_url = models.URLField(max_length=500, blank=True, verbose_name='场景图片')
    video_clip_url = models.URLField(max_length=500, blank=True, verbose_name='场景视频片段')
    
    # 内容
    narration = models.TextField(blank=True, verbose_name='旁白')
    dialogue = models.TextField(blank=True, verbose_name='对话')
    
    # 效果
    motion_prompt = models.TextField(blank=True, verbose_name='运动描述')
    transition = models.CharField(max_length=50, default='fade', verbose_name='转场效果')
    
    # 时长
    duration = models.FloatField(default=4.0, verbose_name='时长（秒）')
    start_time = models.FloatField(default=0, verbose_name='开始时间')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'video_scenes'
        verbose_name = '视频场景'
        verbose_name_plural = '视频场景'
        ordering = ['scene_number']
    
    def __str__(self):
        return f"场景 {self.scene_number} - {self.video.title}"


class VideoExport(models.Model):
    """视频导出记录"""
    
    FORMAT_CHOICES = [
        ('mp4', 'MP4'),
        ('mov', 'MOV'),
        ('avi', 'AVI'),
        ('webm', 'WebM'),
        ('gif', 'GIF'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='exports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # 导出配置
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name='格式')
    resolution = models.CharField(max_length=20, blank=True, verbose_name='分辨率')
    quality = models.CharField(max_length=20, default='high', verbose_name='质量')
    
    # 导出选项
    include_subtitles = models.BooleanField(default=False, verbose_name='包含字幕')
    include_watermark = models.BooleanField(default=False, verbose_name='包含水印')
    
    # 结果
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    file_url = models.URLField(max_length=500, blank=True, verbose_name='文件URL')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小')
    
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'video_exports'
        verbose_name = '视频导出'
        verbose_name_plural = '视频导出'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.video.title} - {self.format} - {self.get_status_display()}"


class VideoTemplate(models.Model):
    """视频模板"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='video_templates'
    )
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name='模板名称')
    description = models.TextField(blank=True, verbose_name='描述')
    category = models.CharField(max_length=50, blank=True, verbose_name='分类')
    
    # 模板配置
    template_config = models.JSONField(default=dict, verbose_name='模板配置')
    
    # 预览
    preview_url = models.URLField(max_length=500, blank=True, verbose_name='预览URL')
    thumbnail_url = models.URLField(max_length=500, blank=True, verbose_name='缩略图')
    
    # 使用统计
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 公开设置
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'video_templates'
        verbose_name = '视频模板'
        verbose_name_plural = '视频模板'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
